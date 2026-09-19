"""
rag_service.py

Provides AI-powered explanations, topic learning, and tutoring for CertMind.

RAG retrieval: connects directly to the ChromaDB vector store that NetMind
maintains (at CHROMA_PATH), using the same embedding model NetMind uses
(all-MiniLM-L6-v2).  This avoids importing NetMind's src package entirely,
so there are no version conflicts between the two virtual environments.
"""

import asyncio
import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Shared singletons â€” initialised lazily on first use
# ---------------------------------------------------------------------------
_embed_model = None
_chroma_client = None
_collection = None

DEFAULT_CHROMA_PATH = str(Path(__file__).resolve().parents[1] / "data" / "chroma_db")
CHROMA_PATH     = os.getenv("CHROMA_PATH", DEFAULT_CHROMA_PATH)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "langchain"          # default name LangChain-Chroma uses


def _get_embed_model():
    global _embed_model
    if _embed_model is None:
        from sentence_transformers import SentenceTransformer
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        _embed_model = SentenceTransformer(
            EMBEDDING_MODEL, device="cpu",
            model_kwargs={"low_cpu_mem_usage": False},
        )
    return _embed_model


def _get_collection():
    global _chroma_client, _collection
    if _collection is None:
        import chromadb
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection    = _chroma_client.get_or_create_collection(COLLECTION_NAME)
    return _collection


def _retrieve(
    query: str,
    vendor_filter: Optional[str] = None,
    k: int = 6,
    source_scope: str = "official",
    user_id: Optional[str] = None,
) -> list[dict]:
    """
    Semantic search against the shared ChromaDB.
    Returns a list of {"page_content": str, "metadata": dict} dicts.
    """
    try:
        model      = _get_embed_model()
        collection = _get_collection()

        query_emb = model.encode([query], normalize_embeddings=True)[0].tolist()

        where = None
        if vendor_filter and vendor_filter not in ("all", "unknown"):
            where = {"vendor": {"$eq": vendor_filter}}

        results = collection.query(
            query_embeddings=[query_emb],
            n_results=min(max(k, 1), 12),
            where=where,
            include=["documents", "metadatas"],
        )

        docs = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            metadata = meta or {}
            metadata_scope = metadata.get("source_scope", metadata.get("source_type", "official"))
            metadata_user = metadata.get("user_id")
            if source_scope not in {"official", "personal", "both"}:
                source_scope = "official"
            if source_scope == "official" and metadata_scope == "personal":
                continue
            if source_scope == "personal" and (metadata_scope != "personal" or metadata_user != user_id):
                continue
            if source_scope == "both" and metadata_scope == "personal" and metadata_user != user_id:
                continue
            docs.append({"page_content": doc, "metadata": metadata})
            if len(docs) >= k:
                break
        return docs

    except Exception:
        return []


def _select_evidence(docs: list[dict], query: str, limit: int = 3) -> list[dict]:
    """Select high-signal, non-duplicate evidence after semantic retrieval."""
    import re
    query_terms = set(re.findall(r"[a-zA-Z0-9][a-zA-Z0-9_./-]{2,}", query.lower()))
    scored, seen = [], set()
    for index, doc in enumerate(docs):
        content = doc.get("page_content", "")
        fingerprint = " ".join(content.lower().split())[:500]
        if not content or fingerprint in seen:
            continue
        seen.add(fingerprint)
        terms = set(re.findall(r"[a-zA-Z0-9][a-zA-Z0-9_./-]{2,}", content.lower()))
        scored.append((len(query_terms & terms), -index, doc))
    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [item[2] for item in scored[:max(1, limit)]]

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def explain(
    question:    str,
    options:     list[str],
    answer_key,
    user_answer,
    topic:       Optional[str] = None,
    cert_id:     Optional[str] = None,
    source_scope: str = "official",
    user_id:      Optional[str] = None,
) -> dict:
    """Personalised explanation â€” knows what the student answered."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        vendor  = _cert_to_vendor(cert_id)
        candidates = _retrieve(question, vendor_filter=vendor, k=8, source_scope=source_scope, user_id=user_id)
        docs = _select_evidence(candidates, question, limit=3)
        context = "\n\n".join(d["page_content"] for d in docs) if docs else ""
        sources = list({d["metadata"].get("source", "") for d in docs})

        correct_str = (", ".join(answer_key) if isinstance(answer_key, list)
                       else str(answer_key))

        prompt_text = f"""You are a sharp {_cert_to_name(cert_id)} exam coach reviewing one practice question with a student.

Question: {question}
Options:
{chr(10).join(options)}
Correct answer: {correct_str}
Student selected: {user_answer}

Official documentation context:
{context if context else "Use your expert networking knowledge."}

Write a structured explanation following this EXACT format and style:

1. Start with the correct answer stated clearly â€” e.g. "The correct answer is B." or "TRUE." or "FALSE."
2. Explain WHY the correct answer is right in 1-2 sentences, grounded in the documentation context above. Include specific technical values where relevant (timer values, port numbers, address ranges, default values).
3. Then go through EVERY option with a verdict, using this format:
   - For correct options: "A â€” [brief reason] âœ“"
   - For wrong options: "B â€” WRONG: [why it's wrong]. [If this concept actually belongs to a different protocol/mechanism/context, say WHERE it belongs]."
4. End with one short memorable takeaway sentence.

Critical rules:
- EVERY wrong option must explain WHERE that concept actually belongs if it describes a real thing from a different context. This cross-referencing is the most valuable teaching tool.
- Use specific technical values (e.g. "default Hello=10s, Dead=40s" or "TCP port 179" or "TTL=1 for EBGP") â€” do not be vague.
- Keep the total explanation between 40 and 88 words. Do not pad it or restate the question and all options.
- No markdown headers. Plain text only. Use âœ“ for correct and WRONG: label for incorrect.
- Base claims on the documentation context. If context doesn't cover something, use expert knowledge but keep it factual."""

        llm   = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
        chain = ChatPromptTemplate.from_messages([("human", "{input}")]) | llm | StrOutputParser()
        text  = await asyncio.wait_for(chain.ainvoke({"input": prompt_text}), timeout=60)

        return {"explanation": text, "sources": sources}

    except Exception as e:
        error_text = str(e)
        retryable = any(code in error_text.lower() for code in ("429", "too many", "resource_exhausted", "503", "service unavailable"))
        return {
            "explanation": "",
            "sources":     [],
            "error":       error_text,
            "retryable":   retryable,
        }


def _explain_generic_sync(
    question:    str,
    options:     list[str],
    answer_key,
    topic:       Optional[str] = None,
    cert_id:     Optional[str] = None,
    max_retries: int = 3,
) -> dict:
    """
    Generic explanation (pre-generated before anyone answers).
    Runs synchronously so asyncio.to_thread can parallelise it.
    Retries up to max_retries times with exponential backoff on failure.
    """
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    vendor  = _cert_to_vendor(cert_id)
    docs    = _retrieve(topic or question[:80], vendor_filter=vendor, k=6)
    context = "\n\n".join(d["page_content"] for d in docs) if docs else ""
    sources = list({d["metadata"].get("source", "") for d in docs})

    correct_str = (", ".join(answer_key) if isinstance(answer_key, list)
                   else str(answer_key))

    prompt_text = f"""You are a sharp {_cert_to_name(cert_id)} exam coach explaining one practice question to a student.

Question: {question}
Options:
{chr(10).join(options)}
Correct answer: {correct_str}

Official documentation context:
{context if context else "Use your expert networking knowledge."}

Write a structured explanation following this EXACT format and style:

1. Start with the correct answer stated clearly â€” e.g. "The correct answer is B." or "TRUE." or "FALSE."
2. Explain WHY the correct answer is right in 1-2 sentences, grounded in the documentation context above. Include specific technical values where relevant (timer values, port numbers, address ranges, default values).
3. Then go through EVERY option with a verdict, using this format:
   - For correct options: "A â€” [brief reason] âœ“"
   - For wrong options: "B â€” WRONG: [why it's wrong]. [If this concept actually belongs to a different protocol/mechanism/context, say WHERE it belongs]."
4. End with one short memorable takeaway sentence.

Critical rules:
- EVERY wrong option must explain WHERE that concept actually belongs if it describes a real thing from a different context. This cross-referencing is the most valuable teaching tool.
- Use specific technical values (e.g. "default Hello=10s, Dead=40s" or "TCP port 179" or "TTL=1 for EBGP") â€” do not be vague.
- Keep the total explanation between 60-120 words. Dense and precise, not paddy.
- No markdown headers. Plain text only. Use âœ“ for correct and WRONG: label for incorrect.
- Base claims on the documentation context. If context doesn't cover something, use expert knowledge but keep it factual."""

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            llm   = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.1,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
            )
            chain = ChatPromptTemplate.from_messages([("human", "{input}")]) | llm | StrOutputParser()
            text  = chain.invoke({"input": prompt_text})

            if text and text.strip():
                logger.debug("Explanation generated (attempt %d) for: %s...", attempt, question[:50])
                return {"explanation": text.strip(), "sources": sources}
            else:
                last_error = "Empty response from LLM"
                logger.warning("Empty LLM response (attempt %d/%d) for: %s...", attempt, max_retries, question[:50])

        except Exception as e:
            last_error = str(e)
            logger.warning(
                "Explanation generation failed (attempt %d/%d) for: %s... â€” %s",
                attempt, max_retries, question[:50], e,
            )

        if attempt < max_retries:
            backoff = 2 ** attempt  # 2s, 4s
            time.sleep(backoff)

    logger.error("All %d attempts failed for: %s... â€” last error: %s", max_retries, question[:50], last_error)
    return {
        "explanation": "",
        "sources":     [],
        "error":       last_error,
    }


async def explain_generic(
    question:    str,
    options:     list[str],
    answer_key,
    topic:       Optional[str] = None,
    cert_id:     Optional[str] = None,
) -> dict:
    """Async wrapper â€” runs the blocking LLM call in a thread pool."""
    return await asyncio.to_thread(
        _explain_generic_sync, question, options, answer_key, topic, cert_id
    )


def _fallback_explanation_sync(
    question:    str,
    options:     list[str],
    answer_key,
    cert_id:     Optional[str] = None,
) -> str:
    """Lightweight fallback: generates a simple explanation using only the
    LLM's general knowledge (no RAG retrieval, no retries).

    Used when the full RAG-based explanation fails (e.g. rate limit).
    This is intentionally simpler and cheaper to maximise success.
    """
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        correct_str = (", ".join(answer_key) if isinstance(answer_key, list)
                       else str(answer_key))

        prompt_text = f"""You are a networking exam coach. Explain this question using your expert knowledge.

Question: {question}
Options:
{chr(10).join(options)}
Correct answer: {correct_str}

Write a structured explanation:
1. State why {correct_str} is correct in 1-2 sentences with specific technical details (values, ports, defaults).
2. Go through each wrong option briefly: "[Letter] â€” WRONG: [why]. [Where this concept actually belongs if applicable]."
3. One takeaway sentence.

Keep it 60-100 words total. Use âœ“ for correct options and WRONG: for incorrect. Plain text, no markdown headers."""

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
        chain = ChatPromptTemplate.from_messages([("human", "{input}")]) | llm | StrOutputParser()
        text = chain.invoke({"input": prompt_text})

        if text and text.strip():
            logger.info("Fallback explanation generated for: %s...", question[:50])
            return text.strip()
    except Exception as e:
        logger.error("Fallback explanation also failed for: %s... â€” %s", question[:50], e)

    return ""


async def fallback_explanation(
    question: str, options: list[str], answer_key, cert_id: Optional[str] = None,
) -> str:
    """Async wrapper for the fallback explanation generator."""
    return await asyncio.to_thread(
        _fallback_explanation_sync, question, options, answer_key, cert_id
    )


def _format_answer_key(answer_key) -> str:
    if isinstance(answer_key, list):
        return ", ".join(str(a) for a in answer_key)
    return str(answer_key)


def _parse_json_array(text: str) -> list[dict]:
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            payload = text[start:end + 1]
            try:
                return json.loads(payload)
            except Exception:
                return []
    return []


async def generate_questions(
    cert_id:   str,
    topic:     Optional[str] = None,
    count:     int = 5,
    q_types:   Optional[list[str]] = None,
) -> dict:
    """Generate fresh exam questions from the RAG knowledge base."""
    try:
        api_key = os.getenv("GOOGLE_API_KEY", "").strip()
        if not api_key or api_key.startswith("your_"):
            return {"questions": [], "sources": [], "error": "GOOGLE_API_KEY is missing or still a placeholder."}
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        vendor = _cert_to_vendor(cert_id)
        docs   = _retrieve(topic or "general networking", vendor_filter=vendor, k=8)
        context = "\n\n".join(d["page_content"] for d in docs) if docs else ""
        sources = list({d["metadata"].get("source", "") for d in docs})

        q_type_desc = "mixed single-choice, multiple-choice, and true/false questions"
        if q_types:
            if q_types == ["single"]:
                q_type_desc = "single-choice questions"
            elif q_types == ["multiple"]:
                q_type_desc = "multiple-choice questions with more than one correct answer"
            elif q_types == ["truefalse"]:
                q_type_desc = "true/false questions"
            else:
                q_type_desc = "a mix of questions"

        prompt_text = f"""You are a skilled networking exam question writer for {_cert_to_name(cert_id)}.

Create {count} {q_type_desc} about {topic or 'core networking topics'}.

Use the documentation below as the only source for your questions:
{context if context else 'No specific documentation found. Use your expert networking knowledge.'}

Return ONLY valid JSON in this exact form:
[
  {{
    "question": "...",
    "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "answer_key": "A" or ["A","C"],
    "topic": "...",
    "difficulty": "medium"
  }},
  ...
]

Rules:
- Provide exactly {count} items.
- Use 4 options for single and multiple questions.
- Use exactly 2 options for true/false questions: "A. True", "B. False".
- Use uppercase letters A-D for option labels.
- Do not include any explanatory text outside the JSON array.
- Keep every question self-contained and exam-style.
"""

        llm   = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
        chain = ChatPromptTemplate.from_messages([("human", "{input}")]) | llm | StrOutputParser()
        response = await asyncio.wait_for(chain.ainvoke({"input": prompt_text}), timeout=60)
        text = response

        questions = _parse_json_array(text)
        valid = []
        for q in questions:
            if not q.get("question") or not q.get("options") or not q.get("answer_key"):
                continue
            valid.append({
                "id": str(uuid.uuid4()),
                "bank_id": None,
                "cert_id": cert_id,
                "type": _detect_type(q["question"], q["options"], q.get("answer_key")),
                "topic": q.get("topic") or topic or "General",
                "question": q["question"],
                "options": q["options"],
                "answer_key": q["answer_key"],
                "difficulty": q.get("difficulty", "medium"),
            })
            if len(valid) >= count:
                break

        return {"questions": valid, "sources": sources}

    except Exception as e:
        return {"questions": [], "sources": [], "error": str(e)}


def _parse_lesson_json(text: str) -> dict | None:
    """Parse a structured lesson while tolerating Markdown code fences."""
    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].rstrip()
    try:
        payload = json.loads(cleaned)
    except Exception:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start < 0 or end <= start:
            return None
        try:
            payload = json.loads(cleaned[start:end + 1])
        except Exception:
            return None
    if not isinstance(payload, dict) or not isinstance(payload.get("sections"), list):
        return None
    payload.setdefault("key_facts", [])
    payload.setdefault("exam_points", [])
    payload.setdefault("common_mistakes", [])
    payload.setdefault("quick_check", [])
    return payload


def _lesson_text(payload: dict) -> str:
    """Create a readable plain-text representation of a lesson."""
    parts = []
    for key in ("title", "objective", "overview"):
        if payload.get(key):
            parts.append(str(payload[key]))
    for section in payload.get("sections", []):
        if isinstance(section, dict):
            if section.get("title"):
                parts.append(str(section["title"]))
            if section.get("content"):
                parts.append(str(section["content"]))
    for key, label in (("key_facts", "Key facts"), ("exam_points", "Exam points"), ("common_mistakes", "Common mistakes"), ("quick_check", "Quick check")):
        values = payload.get(key) or []
        if values:
            parts.append(label)
            parts.extend(f"- {value}" for value in values)
    return "\n\n".join(parts)


def _detect_type(question: str, options: list[str], answer_key) -> str:
    if isinstance(answer_key, list) and len(answer_key) > 1:
        return "multiple"

    q_lower = question.lower()
    if any(kw in q_lower for kw in ["true or false", "true/false", "yes or no"]):
        return "truefalse"

    if len(options) == 2:
        opts = [o.lower() for o in options]
        if any("true" in o or "false" in o for o in opts):
            return "truefalse"

    if "select all" in q_lower or "which of the following are" in q_lower:
        return "multiple"

    return "single"


async def ensure_explanations(
    questions: list[dict],
    concurrency: int = 6,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> list[dict]:
    """Generate or fallback explanations for a list of question records.

    Args:
        questions: List of question dicts needing explanations.
        concurrency: Max parallel Gemini calls.
        progress_callback: Optional callable(done, total) called after each
                           question completes, so callers can track progress.
    """
    total = len(questions)
    done_count = 0
    done_lock = asyncio.Lock()
    semaphore = asyncio.Semaphore(min(concurrency, max(1, total)))

    logger.info("Generating explanations for %d questions (concurrency=%d)", total, concurrency)

    async def _generate(q):
        nonlocal done_count
        async with semaphore:
            try:
                result = await explain_generic(
                    question=q["question"],
                    options=q["options"],
                    answer_key=q["answer_key"],
                    topic=q.get("topic"),
                    cert_id=q.get("cert_id"),
                )
                explanation = (result.get("explanation") or "").strip()
                sources     = result.get("sources") or []
            except Exception as e:
                logger.error("ensure_explanations failed for q=%s: %s", q["id"][:8], e)
                explanation = ""
                sources     = []

            # Fallback: if the full RAG-based explanation failed (rate limit,
            # timeout, etc.), try a lightweight LLM call without RAG context.
            # This is simpler and cheaper, so it's more likely to succeed.
            if not explanation:
                logger.info("Trying fallback explanation for q=%s", q["id"][:8])
                explanation = await fallback_explanation(
                    question=q["question"],
                    options=q["options"],
                    answer_key=q["answer_key"],
                    cert_id=q.get("cert_id"),
                )
                sources = []

            # Last resort: if even the fallback failed, show a minimal message
            if not explanation:
                explanation = f"The correct answer is {_format_answer_key(q['answer_key'])}. The explanation could not be generated at this time."
                sources = []

            async with done_lock:
                done_count += 1
                if progress_callback:
                    try:
                        progress_callback(done_count, total)
                    except Exception:
                        pass

            return {
                "id": q["id"],
                "explanation": explanation,
                "sources": sources,
            }

    results = await asyncio.gather(*(_generate(q) for q in questions))
    logger.info("Explanation generation complete: %d/%d done", done_count, total)
    return results


async def background_generate_explanations(
    bank_id: str,
    questions: list[dict],
    db_path: str,
    concurrency: int = 6,
) -> None:
    """Background task: generates explanations for all questions in a bank,
    writes each to the DB, and updates the bank's progress field.

    Designed to be fired via asyncio.create_task() so it doesn't block
    the HTTP response.
    """
    import aiosqlite
    import json as _json

    total = len(questions)
    logger.info("[bg] Starting explanation generation for bank %s (%d questions)", bank_id[:8], total)

    # Filter to only questions without explanations
    missing = [q for q in questions if not (q.get("explanation") or "").strip()]
    if not missing:
        logger.info("[bg] All %d questions already have explanations â€” nothing to do", total)
        async with aiosqlite.connect(db_path) as db:
            await db.execute(
                "UPDATE question_banks SET explanation_progress = ? WHERE id = ?",
                ("complete", bank_id),
            )
            await db.commit()
        return

    done_so_far = total - len(missing)

    async def _on_progress(done, batch_total):
        nonlocal done_so_far
        current = done_so_far + done
        progress_str = f"{current}/{total}"
        try:
            async with aiosqlite.connect(db_path) as db:
                await db.execute(
                    "UPDATE question_banks SET explanation_progress = ? WHERE id = ?",
                    (progress_str, bank_id),
                )
                await db.commit()
        except Exception as e:
            logger.warning("[bg] Failed to update progress: %s", e)

    # We need a sync-compatible callback for the async ensure_explanations
    # Since progress_callback is called inside an async context, we can use it directly
    # But ensure_explanations expects a sync callback â€” let's use a wrapper
    progress_state = {"done": 0}

    def sync_progress(done, batch_total):
        progress_state["done"] = done

    try:
        results = await ensure_explanations(
            missing,
            concurrency=concurrency,
            progress_callback=sync_progress,
        )
    except Exception as e:
        logger.error("[bg] ensure_explanations crashed for bank %s: %s", bank_id[:8], e)
        results = []

    # Write results to DB
    written = 0
    try:
        async with aiosqlite.connect(db_path) as db:
            for result in results:
                explanation = (result.get("explanation") or "").strip()
                sources     = result.get("sources") or []
                if not explanation:
                    continue
                await db.execute(
                    "UPDATE questions SET explanation = ?, sources = ? WHERE id = ?",
                    (explanation, _json.dumps(sources), result["id"]),
                )
                written += 1

            await db.execute(
                "UPDATE question_banks SET explanation_progress = ? WHERE id = ?",
                ("complete", bank_id),
            )
            await db.commit()
    except Exception as e:
        logger.error("[bg] DB write failed for bank %s: %s", bank_id[:8], e)

    logger.info(
        "[bg] Finished bank %s: %d/%d explanations written",
        bank_id[:8], written, len(missing),
    )


async def learn_topic(
    topic:   str,
    cert_id: Optional[str] = None,
    depth:   str = "standard",
) -> dict:
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        vendor  = _cert_to_vendor(cert_id)
        docs    = _retrieve(topic, vendor_filter=vendor, k=6)
        context = "\n\n".join(d["page_content"] for d in docs) if docs else ""

        depth_instruction = (
            "Teach this as a deep-dive lesson, but keep it in clear sections. Include one practical scenario, troubleshooting, and advanced exam traps."
            if depth == "deep" else
            "Teach only the foundation first. Keep it concise enough to finish in one sitting and prepare the learner for a later deep dive."
        )

        prompt = f"""You are an elite {_cert_to_name(cert_id)} instructor.

Topic: {topic}
{depth_instruction}

Retrieved documentation (use it as evidence, but rewrite it; never paste it verbatim):
{context if context else "Use your expert knowledge."}

Return ONLY valid JSON with this shape:
{
  "title": "short topic title",
  "objective": "one sentence",
  "overview": "brief overview",
  "sections": [{"title": "section title", "content": "concise explanation"}],
  "key_facts": ["..."],
  "exam_points": ["..."],
  "common_mistakes": ["..."],
  "quick_check": ["question"]
}
Do not include Markdown fences or commentary. The frontend owns presentation.
Write a clean lesson for a student. Do not copy the Markdown formatting from the documentation.

For a standard lesson, use exactly:

1. Overview (2-3 sentences)
2. Learning objectives (3 short items)
3. Core idea (simple explanation)
4. Key concepts (5-7 numbered items)
5. Quick check (3 questions, without answers)
6. Next step: tell the learner what the deep dive would cover.

For a deep lesson, use exactly:

1. Deep overview
2. How it works (numbered sequence)
3. Configuration or verification example
4. Edge cases and troubleshooting
5. Exam traps
6. Quick reference

{depth_instruction}

Rules:
- Rewrite and teach the source; do not return retrieved chunks as-is.
- Never invent vendor commands or values. If the source does not support a detail, say so.
- Keep standard lessons under 300 words and deep lessons under 600 words. Prefer short paragraphs and compact numbered items.
- Use clean plain text headings and numbered lists; no asterisk-based Markdown.

"""

        llm   = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
        chain = ChatPromptTemplate.from_messages([("human", "{input}")]) | llm | StrOutputParser()
        text  = await asyncio.wait_for(chain.ainvoke({"input": prompt}), timeout=60)

        lesson = _parse_lesson_json(text)
        sources = [d["metadata"].get("source", "") for d in docs]
        if lesson:
            return {"content": _lesson_text(lesson), "lesson": lesson, "topic": topic, "sources": sources}
        return {"content": text, "topic": topic, "sources": sources, "lesson": None}

    except Exception as e:
        return {"content": f"Could not load topic: {e}", "topic": topic, "sources": []}


async def tutor_chat(
    message: str,
    cert_id: Optional[str] = None,
    history: list[dict] = [],
) -> dict:
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        vendor  = _cert_to_vendor(cert_id)
        docs    = _retrieve(message, vendor_filter=vendor, k=5)
        context = "\n\n".join(d["page_content"] for d in docs) if docs else ""

        history_str = "\n".join(
            f"{'User' if m['role']=='user' else 'Assistant'}: {m['content']}"
            for m in history[-6:]
        )

        prompt = f"""You are an AI tutor for {_cert_to_name(cert_id)} certification.
Answer ONLY from the documentation provided. If not found, say so clearly.

Previous conversation:
{history_str}

Documentation:
{context if context else "No specific documentation found. Use expert knowledge."}

User question: {message}

Respond directly and technically. Use Huawei VRP syntax where relevant."""

        llm   = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.15,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
        chain = ChatPromptTemplate.from_messages([("human", "{input}")]) | llm | StrOutputParser()
        text  = await asyncio.wait_for(chain.ainvoke({"input": prompt}), timeout=60)

        sources = list(dict.fromkeys(d["metadata"].get("source", "") for d in docs if d["metadata"].get("source")))
        return {"response": _clean_display_text(text), "sources": sources}

    except Exception as e:
        return {"response": f"Tutor unavailable: {e}", "sources": []}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_display_text(text: str) -> str:
    """Remove presentation Markdown before plain-text UI rendering."""
    import re
    cleaned = str(text or "")
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\1", cleaned)
    cleaned = re.sub(r"^\s*#{1,6}\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*\*\s+", "• ", cleaned, flags=re.MULTILINE)
    return cleaned.strip()


def _cert_to_vendor(cert_id: Optional[str]) -> str:
    if not cert_id:
        return "huawei"
    mapping = {
        "hcip-datacom": "huawei", "hcip-security": "huawei",
        "hcia-datacom": "huawei", "ccna": "cisco", "ccnp-ent": "cisco",
        "aws-saa": "aws",
    }
    return mapping.get(cert_id, "huawei")


def _cert_to_name(cert_id: Optional[str]) -> str:
    mapping = {
        "hcip-datacom":  "HCIP Datacom Core",
        "hcip-security": "HCIP Security",
        "hcia-datacom":  "HCIA Datacom",
        "ccna":          "CCNA",
        "ccnp-ent":      "CCNP Enterprise",
        "aws-saa":       "AWS Solutions Architect",
    }
    return mapping.get(cert_id or "", "Network Certification")

