import asyncio
import hashlib
import json
import logging
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from pydantic import BaseModel

from database.db import get_db
from routers.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


async def _record_llm_run(db, user_id: str, prompt: str, result: dict):
    await db.execute(
        """INSERT INTO llm_runs
           (id, user_id, model, prompt_hash, status, latency_ms, input_tokens, output_tokens, estimated_cost_usd, error)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (
            str(uuid.uuid4()), user_id,
            result.get("model", "unknown"),
            hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            result.get("status", "completed"), result.get("latency_ms"),
            result.get("input_tokens", 0), result.get("output_tokens", 0),
            result.get("estimated_cost_usd", 0), result.get("error"),
        ),
    )


@router.post("/knowledge/upload")
async def upload_personal_knowledge(
    file: UploadFile = File(...),
    cert_id: Optional[str] = Form(None),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    filename = (file.filename or "").strip()
    if Path(filename).suffix.lower() not in {".md", ".markdown", ".mdown"}:
        raise HTTPException(400, "Only Markdown files are accepted.")
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(413, "Markdown file too large. Maximum size is 5MB.")
    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(400, "Markdown file must be UTF-8 encoded.")
    from services.personal_knowledge_service import content_hash, index_markdown
    source_id = str(uuid.uuid4())
    await db.execute(
        "INSERT INTO knowledge_sources (id, user_id, name, filename, cert_id, content_hash, status) VALUES (?,?,?,?,?,?,?)",
        (source_id, user["id"], filename, filename, cert_id, content_hash(content), "processing"),
    )
    await db.commit()
    asyncio.create_task(index_markdown(source_id, user["id"], filename, text_content, cert_id))
    return {"source_id": source_id, "filename": filename, "status": "processing"}


@router.get("/knowledge/sources")
async def list_personal_knowledge(user=Depends(get_current_user), db=Depends(get_db)):
    async with db.execute("SELECT id, name, filename, cert_id, chunk_count, status, error, created_at FROM knowledge_sources WHERE user_id = ? ORDER BY created_at DESC", (user["id"],)) as cur:
        return [dict(row) for row in await cur.fetchall()]


class ExplainBody(BaseModel):
    question:    str
    options:     list[str]
    answer_key:  str | list[str]
    user_answer: str | list[str]
    topic:       Optional[str] = None
    cert_id:     Optional[str] = "hcip-datacom"
    attempt_id:  Optional[str] = None
    source_scope: str = "official"


class LearnBody(BaseModel):
    topic:   str
    cert_id: Optional[str] = "hcip-datacom"
    depth:   str = "standard"


class GenerateBody(BaseModel):
    cert_id:   str
    topic:     Optional[str] = None
    count:     int = 10
    q_types:   Optional[list[str]] = None


class BackfillBody(BaseModel):
    cert_id: Optional[str] = None
    limit:   int = 100


class TutorBody(BaseModel):
    message:  str
    cert_id:  Optional[str] = "hcip-datacom"
    history:  list[dict] = []


class EvaluateBody(BaseModel):
    name: str = "Untitled evaluation"
    response: str
    expected: Optional[str] = None
    required_phrases: list[str] = []
    forbidden_phrases: list[str] = []
    max_length: Optional[int] = None
    require_json: bool = False



class RetrievalCase(BaseModel):
    query: str
    expected_sources: list[str] = []
    relevant_terms: list[str] = []


class RetrievalEvaluationBody(BaseModel):
    cases: list[RetrievalCase]
    cert_id: Optional[str] = "hcip-datacom"
    k: int = 3


class AnswerQualityBody(BaseModel):
    response: str
    expected: Optional[str] = None
    evidence: list[str] = []
    sources: list[str] = []


class RedTeamBody(BaseModel):
    response: str
    attacks: list[str] = []


class AdvancedEvaluationBody(BaseModel):
    response: str
    expected: str
    evidence: list[str] = []
    rubric: list[str] = ["correctness", "groundedness", "instruction_following"]


class ExperimentCandidate(BaseModel):
    name: str
    response: str


class ExperimentBody(BaseModel):
    name: str = "Response comparison"
    candidates: list[ExperimentCandidate]
    expected: Optional[str] = None
    required_phrases: list[str] = []
    forbidden_phrases: list[str] = []
    max_length: Optional[int] = None


class RunPromptBody(BaseModel):
    prompt: str
    model: str = "gemini-2.5-flash"


class CompareModelsBody(BaseModel):
    prompt: str
    models: list[str] = ["gemini-2.5-flash"]


@router.post("/run-prompt")
async def run_prompt(body: RunPromptBody, user=Depends(get_current_user)):
    if len(body.prompt.strip()) < 1:
        raise HTTPException(422, "Prompt cannot be empty.")
    if len(body.prompt) > 100_000:
        raise HTTPException(413, "Prompt is too large.")
    try:
        from services.model_runner import run_gemini
        result = await run_gemini(body.prompt, body.model)
        result["status"] = "completed"
        from database.db import get_db as _get_db
        async for db in _get_db():
            await _record_llm_run(db, user["id"], body.prompt, result)
            await db.commit()
        return result
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
    except Exception:
        raise HTTPException(502, "The model provider could not complete the request.")


@router.post("/compare-models")
async def compare_models(body: CompareModelsBody, user=Depends(get_current_user)):
    if not body.prompt.strip():
        raise HTTPException(422, "Prompt cannot be empty.")
    if not body.models or len(body.models) > 5:
        raise HTTPException(422, "Choose between 1 and 5 models.")
    from services.model_runner import run_gemini
    from database.db import get_db as _get_db
    results = []
    async for db in _get_db():
        for model in body.models:
            try:
                result = {"model": model, "status": "completed", **(await run_gemini(body.prompt, model))}
            except RuntimeError as exc:
                result = {"model": model, "status": "unavailable", "error": str(exc)}
            except Exception:
                result = {"model": model, "status": "failed", "error": "Provider request failed."}
            await _record_llm_run(db, user["id"], body.prompt, result)
            results.append(result)
        await db.commit()
    return {"prompt": body.prompt, "results": results}


@router.get("/runs")
async def list_model_runs(limit: int = 50, user=Depends(get_current_user), db=Depends(get_db)):
    limit = min(max(limit, 1), 200)
    async with db.execute("SELECT id, model, prompt_hash, status, latency_ms, input_tokens, output_tokens, estimated_cost_usd, error, created_at FROM llm_runs WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user["id"], limit)) as cur:
        return [dict(row) for row in await cur.fetchall()]


@router.get("/observability")
async def observability(user=Depends(get_current_user), db=Depends(get_db)):
    async with db.execute(
        "SELECT model, status, latency_ms, input_tokens, output_tokens, estimated_cost_usd, error, created_at FROM llm_runs WHERE user_id = ? ORDER BY created_at DESC LIMIT 1000",
        (user["id"],),
    ) as cur:
        rows = [dict(row) for row in await cur.fetchall()]
    completed = [row for row in rows if row["status"] == "completed"]
    latencies = sorted(row["latency_ms"] for row in completed if row["latency_ms"] is not None)
    total_cost = round(sum(row["estimated_cost_usd"] or 0 for row in rows), 6)
    model_summary = {}
    for row in rows:
        bucket = model_summary.setdefault(row["model"], {"model": row["model"], "runs": 0, "failures": 0, "cost": 0, "latency_ms": []})
        bucket["runs"] += 1
        bucket["failures"] += int(row["status"] != "completed")
        bucket["cost"] += row["estimated_cost_usd"] or 0
        if row["latency_ms"] is not None:
            bucket["latency_ms"].append(row["latency_ms"])
    for bucket in model_summary.values():
        values = bucket.pop("latency_ms")
        bucket["avg_latency_ms"] = round(sum(values) / len(values), 1) if values else 0
        bucket["cost"] = round(bucket["cost"], 6)
    return {
        "total_runs": len(rows),
        "successful_runs": len(completed),
        "failed_runs": len(rows) - len(completed),
        "total_cost_usd": total_cost,
        "latency_ms": {
            "p50": _percentile(latencies, 0.50),
            "p95": _percentile(latencies, 0.95),
            "p99": _percentile(latencies, 0.99),
        },
        "models": list(model_summary.values()),
        "recent_runs": rows[:20],
    }


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0
    index = min(len(values) - 1, max(0, round((len(values) - 1) * percentile)))
    return round(values[index], 1)


@router.post("/retrieval-evaluate")
async def retrieval_evaluate(body: RetrievalEvaluationBody, user=Depends(get_current_user), db=Depends(get_db)):
    if not body.cases or len(body.cases) > 100:
        raise HTTPException(422, "Provide between 1 and 100 retrieval cases.")
    if body.k < 1 or body.k > 10:
        raise HTTPException(422, "k must be between 1 and 10.")
    from services.rag_service import _retrieve
    from services.retrieval_eval import evaluate_retrieval
    vendor = None
    try:
        from services.rag_service import _cert_to_vendor
        vendor = _cert_to_vendor(body.cert_id)
    except Exception:
        pass
    retrieved = [
        _retrieve(case.query, vendor_filter=vendor, k=max(body.k, 8))
        for case in body.cases
    ]
    metrics = evaluate_retrieval(
        retrieved,
        [case.expected_sources for case in body.cases],
        [case.relevant_terms for case in body.cases],
        k=body.k,
    )
    return {
        "cert_id": body.cert_id,
        "k": body.k,
        "metrics": metrics,
        "cases": [
            {
                "query": case.query,
                "retrieved_sources": [
                    (doc.get("metadata") or {}).get("source", "")
                    for doc in retrieved[index][:body.k]
                ],
            }
            for index, case in enumerate(body.cases)
        ],
    }


@router.post("/answer-evaluate")
async def answer_quality_evaluate(body: AnswerQualityBody, user=Depends(get_current_user), db=Depends(get_db)):
    if not body.response.strip():
        raise HTTPException(422, "Response cannot be empty.")
    if len(body.response) > 50_000:
        raise HTTPException(413, "Response is too large.")
    from services.answer_quality import evaluate_answer_quality
    result = evaluate_answer_quality(body.response, body.expected, body.evidence, body.sources)
    await db.execute(
        "INSERT INTO evaluations (id, user_id, name, response, score, result) VALUES (?,?,?,?,?,?)",
        (str(uuid.uuid4()), user["id"], "Grounded answer quality", body.response, result["score"], json.dumps(result)),
    )
    await db.commit()
    return result


@router.post("/advanced-evaluate")
async def advanced_evaluate(body: AdvancedEvaluationBody, user=Depends(get_current_user), db=Depends(get_db)):
    if not body.response.strip() or not body.expected.strip():
        raise HTTPException(422, "Response and expected answer are required.")
    from services.advanced_evaluation import lexical_similarity
    result = {"lexical_similarity": lexical_similarity(body.response, body.expected)}
    try:
        from services.advanced_evaluation import semantic_similarity
        result["semantic_similarity"] = semantic_similarity(body.response, body.expected)
    except Exception as exc:
        result["semantic_error"] = str(exc)
    result.update({"response": body.response, "expected": body.expected, "rubric": body.rubric, "mode": "semantic_baseline"})
    await db.execute(
        "INSERT INTO evaluations (id, user_id, name, response, score, result) VALUES (?,?,?,?,?,?)",
        (str(uuid.uuid4()), user["id"], "Advanced semantic evaluation", body.response,
         round(result.get("semantic_similarity", result["lexical_similarity"]) * 100, 1), json.dumps(result)),
    )
    await db.commit()
    return result


@router.post("/judge-evaluate")
async def judge_evaluate(body: AdvancedEvaluationBody, user=Depends(get_current_user), db=Depends(get_db)):
    if not body.response.strip() or not body.expected.strip():
        raise HTTPException(422, "Response and expected answer are required.")
    from services.provider_manager import invoke_gemini
    from services.advanced_evaluation import parse_judge_response
    evidence_text = "\n\n".join(body.evidence[:3])
    rubric_text = ", ".join(body.rubric)
    prompt = f"""You are an evaluation judge. Score the response from 0 to 5 using only the expected answer and evidence.
Expected answer:
{body.expected}
Evidence:
{evidence_text}
Response:
{body.response}
Criteria: {rubric_text}
Return ONLY JSON: {{"score": 0, "reason": "...", "criteria": {{"correctness": 0}}}}"""
    try:
        provider = await invoke_gemini(prompt, "gemini-2.5-flash", 250)
        result = parse_judge_response(provider["text"])
        result.update({"mode": "llm_judge", "model": provider["model"], "latency_ms": provider["latency_ms"]})
    except Exception as exc:
        raise HTTPException(503, f"Judge evaluation unavailable: {exc}")
    await db.execute(
        "INSERT INTO evaluations (id, user_id, name, response, score, result) VALUES (?,?,?,?,?,?)",
        (str(uuid.uuid4()), user["id"], "LLM judge evaluation", body.response,
         result["score"] * 20, json.dumps(result)),
    )
    await db.commit()
    return result


@router.post("/experiment")
async def run_experiment(body: ExperimentBody, user=Depends(get_current_user), db=Depends(get_db)):
    if not body.candidates or len(body.candidates) > 20:
        raise HTTPException(422, "Provide between 1 and 20 candidates.")
    from services.evaluation_service import evaluate_response as run_evaluation
    results = []
    for candidate in body.candidates:
        evaluation = run_evaluation(candidate.response, body.expected, body.required_phrases, body.forbidden_phrases, body.max_length)
        results.append({"name": candidate.name, "score": evaluation["score"], "passed": evaluation["passed"], "checks": evaluation["checks"]})
    winner = max(results, key=lambda item: item["score"])["name"]
    await db.execute("INSERT INTO experiments (id, user_id, name, definition, results, winner) VALUES (?,?,?,?,?,?)", (str(uuid.uuid4()), user["id"], body.name, json.dumps(body.model_dump()), json.dumps(results), winner))
    await db.commit()
    return {"name": body.name, "winner": winner, "results": results}


@router.post("/evaluate")
async def evaluate_response(body: EvaluateBody, user=Depends(get_current_user), db=Depends(get_db)):
    from services.evaluation_service import evaluate_response as run_evaluation
    result = run_evaluation(
        response=body.response,
        expected=body.expected,
        required_phrases=body.required_phrases,
        forbidden_phrases=body.forbidden_phrases,
        max_length=body.max_length,
        require_json=body.require_json,
    )
    await db.execute(
        "INSERT INTO evaluations (id, user_id, name, response, score, result) VALUES (?,?,?,?,?,?)",
        (str(uuid.uuid4()), user["id"], body.name, body.response, result["score"], json.dumps(result)),
    )
    await db.commit()
    return result


def _get_rag_services():
    try:
        from services.rag_service import explain, learn_topic, tutor_chat
        return explain, learn_topic, tutor_chat
    except Exception:
        return None, None, None


@router.post("/explain")
async def explain_answer(body: ExplainBody, user=Depends(get_current_user), db=Depends(get_db)):
    explain, _, _ = _get_rag_services()
    if not explain:
        raise HTTPException(503, "RAG service unavailable. Check ChromaDB and API key.")

    # Check cache first
    cache_result = await _check_cache(db, "explanation", body.question[:100] + str(body.answer_key))
    if cache_result:
        return cache_result

    result = await explain(
        question=body.question,
        options=body.options,
        answer_key=body.answer_key,
        user_answer=body.user_answer,
        topic=body.topic,
        cert_id=body.cert_id,
        source_scope=body.source_scope,
        user_id=user["id"],
    )

    if body.attempt_id:
        await db.execute(
            "UPDATE attempts SET ai_explanation = ?, ai_sources = ? WHERE id = ?",
            (
                result.get("explanation", ""),
                json.dumps(result.get("sources", [])),
                body.attempt_id,
            ),
        )
        await db.commit()

    # Cache the result
    if result.get("explanation") and not result.get("error"):
        await _set_cache(db, "explanation", body.question[:100] + str(body.answer_key), result)

    return result


@router.post("/learn")
async def learn_topic(body: LearnBody, user=Depends(get_current_user)):
    _, learn, _ = _get_rag_services()
    if not learn:
        raise HTTPException(503, "RAG service unavailable.")

    # Check cache
    from database.db import get_db as _get_db_gen
    import aiosqlite
    from database.db import DB_PATH
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cache_result = await _check_cache(db, "learn", f"{body.cert_id}:{body.topic}:{body.depth}")
        if cache_result:
            return cache_result

    result = await learn(
        topic=body.topic,
        cert_id=body.cert_id,
        depth=body.depth,
    )

    # Cache if successful
    if result.get("content") and "Could not load" not in result["content"]:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            await _set_cache(db, "learn", f"{body.cert_id}:{body.topic}:{body.depth}", result)

    return result


@router.post("/generate")
async def generate_questions_route(
    body: GenerateBody,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    try:
        from services.rag_service import generate_questions
    except Exception:
        raise HTTPException(503, "RAG service unavailable. Check ChromaDB and API key.")

    result = await generate_questions(
        cert_id=body.cert_id,
        topic=body.topic,
        count=body.count,
        q_types=body.q_types,
    )
    if result.get("error"):
        logger.error("Question generation failed for user %s: %s", user["id"], result["error"])
        if not os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY", "").startswith("your_"):
            raise HTTPException(503, "Question generation requires a configured GOOGLE_API_KEY in backend/.env.")
        raise HTTPException(503, "The AI question generator is temporarily unavailable. Check the backend logs.")
    if not result.get("questions"):
        raise HTTPException(502, "The model returned no valid questions. Try a smaller question count or different topic.")

    bank_id = str(uuid.uuid4())
    await db.execute(
        "INSERT INTO question_banks (id, cert_id, user_id, source_type, source_name, total_questions) VALUES (?,?,?,?,?,?)",
        (bank_id, body.cert_id, user["id"], "generated", f"Generated questions: {body.topic or 'Mixed'}", len(result["questions"])),
    )

    # Do not fan out explanation calls here. Free-tier providers can throttle
    # a generated practice session if every question immediately triggers an
    # additional model request. Explanations are generated on demand when the
    # learner answers each question.
    questions = result["questions"]

    for q in questions:
        await db.execute(
            "INSERT OR REPLACE INTO questions (id, bank_id, cert_id, type, topic, question, options, answer_key, explanation, sources, difficulty) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                q["id"], bank_id, body.cert_id, q.get("type"), q.get("topic"), q.get("question"),
                json.dumps(q.get("options", [])),
                json.dumps(q["answer_key"]) if isinstance(q.get("answer_key"), list) else q.get("answer_key"),
                q.get("explanation"), json.dumps(q.get("sources", [])), q.get("difficulty", "medium"),
            ),
        )
    await db.commit()

    # Record study activity
    from datetime import date
    today = date.today().isoformat()
    try:
        await db.execute(
            "INSERT OR IGNORE INTO study_streaks (id, user_id, date, activity) VALUES (?, ?, ?, ?)",
            (str(uuid.uuid4()), user["id"], today, "generate"),
        )
        await db.commit()
    except Exception:
        pass

    return {
        "bank_id": bank_id,
        "questions": questions,
        "sources": result.get("sources", []),
    }


@router.post("/backfill")
async def backfill_explanations(
    body: BackfillBody,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    try:
        from services.rag_service import ensure_explanations
    except Exception:
        raise HTTPException(503, "RAG service unavailable.")

    where_clauses = ["(q.explanation IS NULL OR TRIM(q.explanation) = '')"]
    params = []

    # Only backfill questions from user's banks
    where_clauses.append("(qb.user_id = ? OR qb.user_id IS NULL)")
    params.append(user["id"])

    if body.cert_id:
        where_clauses.append("q.cert_id = ?")
        params.append(body.cert_id)

    query = f"SELECT q.* FROM questions q LEFT JOIN question_banks qb ON q.bank_id = qb.id WHERE {' AND '.join(where_clauses)} LIMIT ?"
    async with db.execute(query, params + [body.limit]) as cur:
        rows = await cur.fetchall()

    questions = []
    for row in rows:
        q = dict(row)
        try:
            q["options"] = json.loads(q["options"])
        except Exception:
            pass
        try:
            q["answer_key"] = json.loads(q["answer_key"])
        except Exception:
            pass
        questions.append(q)

    if not questions:
        return {"processed": 0, "updated": 0, "message": "No questions require backfill."}

    results = await ensure_explanations(questions)
    updated = 0
    for result in results:
        if not result.get("explanation"):
            continue
        await db.execute(
            "UPDATE questions SET explanation = ?, sources = ? WHERE id = ?",
            (
                result["explanation"], json.dumps(result.get("sources", [])), result["id"],
            ),
        )
        updated += 1

    await db.commit()
    return {"processed": len(questions), "updated": updated}


@router.post("/tutor")
async def tutor(body: TutorBody, user=Depends(get_current_user)):
    _, _, chat = _get_rag_services()
    if not chat:
        raise HTTPException(503, "RAG service unavailable.")

    result = await chat(
        message=body.message,
        cert_id=body.cert_id,
        history=body.history,
    )

    # Record study activity
    import aiosqlite
    from database.db import DB_PATH
    from datetime import date
    today = date.today().isoformat()
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT OR IGNORE INTO study_streaks (id, user_id, date, activity) VALUES (?, ?, ?, ?)",
                (str(uuid.uuid4()), user["id"], today, "tutor"),
            )
            await db.commit()
    except Exception:
        pass

    return result


@router.post("/red-team/assess")
async def red_team_assess(body: RedTeamBody, user=Depends(get_current_user)):
    from services.red_team import assess_response
    return assess_response(body.response, body.attacks or None)


@router.get("/cache-stats")
async def cache_stats(user=Depends(get_current_user), db=Depends(get_db)):
    async with db.execute(
        "SELECT cache_type, COUNT(*) AS entries, COALESCE(SUM(hit_count), 0) AS hits "
        "FROM ai_cache GROUP BY cache_type"
    ) as cur:
        rows = [dict(row) for row in await cur.fetchall()]
    total_entries = sum(row["entries"] for row in rows)
    total_hits = sum(row["hits"] for row in rows)
    return {
        "entries": total_entries,
        "hits": total_hits,
        "hit_rate": round(total_hits / max(1, total_hits + total_entries), 4),
        "by_type": rows,
    }


@router.get("/certifications")
async def list_certifications():
    return [
        {"id": "hcip-datacom",  "vendor": "Huawei", "name": "HCIP Datacom Core"},
        {"id": "hcip-security", "vendor": "Huawei", "name": "HCIP Security"},
        {"id": "hcia-datacom",  "vendor": "Huawei", "name": "HCIA Datacom"},
        {"id": "ccna",          "vendor": "Cisco",  "name": "CCNA"},
        {"id": "ccnp-ent",      "vendor": "Cisco",  "name": "CCNP Enterprise"},
        {"id": "aws-saa",       "vendor": "AWS",    "name": "AWS Solutions Architect"},
    ]


# ---------------------------------------------------------------------------
# Cache helpers (inline for simplicity â€” Phase 3)
# ---------------------------------------------------------------------------
import hashlib
from datetime import datetime, timedelta, timezone


def _cache_key(cache_type: str, identifier: str) -> str:
    """Generate a stable cache key."""
    raw = f"{cache_type}:{identifier}"
    return hashlib.sha256(raw.encode()).hexdigest()


async def _check_cache(db, cache_type: str, identifier: str) -> Optional[dict]:
    """Check if a cached result exists and is still valid."""
    key = _cache_key(cache_type, identifier)
    try:
        async with db.execute(
            "SELECT content, expires_at FROM ai_cache WHERE cache_key = ?", (key,)
        ) as cur:
            row = await cur.fetchone()
        if not row:
            return None

        # Check expiry
        if row["expires_at"]:
            expires = datetime.fromisoformat(row["expires_at"])
            if datetime.now(timezone.utc) > expires.replace(tzinfo=timezone.utc):
                await db.execute("DELETE FROM ai_cache WHERE cache_key = ?", (key,))
                await db.commit()
                return None

        # Update hit count
        await db.execute(
            "UPDATE ai_cache SET hit_count = hit_count + 1 WHERE cache_key = ?", (key,)
        )
        await db.commit()

        return json.loads(row["content"])
    except Exception:
        return None


async def _set_cache(db, cache_type: str, identifier: str, content: dict, ttl_days: int = 7):
    """Store a result in cache."""
    key = _cache_key(cache_type, identifier)
    expires = (datetime.now(timezone.utc) + timedelta(days=ttl_days)).isoformat()
    try:
        await db.execute(
            "INSERT OR REPLACE INTO ai_cache (cache_key, cache_type, content, expires_at) VALUES (?, ?, ?, ?)",
            (key, cache_type, json.dumps(content), expires),
        )
        await db.commit()
    except Exception:
        pass

