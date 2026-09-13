import asyncio
import json
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from pydantic import BaseModel

from database.db import get_db
from routers.auth import get_current_user

router = APIRouter()


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
        from services.rag_service import generate_questions, ensure_explanations
    except Exception:
        raise HTTPException(503, "RAG service unavailable. Check ChromaDB and API key.")

    result = await generate_questions(
        cert_id=body.cert_id,
        topic=body.topic,
        count=body.count,
        q_types=body.q_types,
    )
    if not result.get("questions"):
        raise HTTPException(500, "Could not generate questions.")

    bank_id = str(uuid.uuid4())
    await db.execute(
        "INSERT INTO question_banks (id, cert_id, user_id, source_type, source_name, total_questions) VALUES (?,?,?,?,?,?)",
        (bank_id, body.cert_id, user["id"], "generated", f"Generated questions: {body.topic or 'Mixed'}", len(result["questions"])),
    )

    questions = result["questions"]
    if any(not q.get("explanation") for q in questions):
        explanations = await ensure_explanations(questions)
        for q in questions:
            match = next((r for r in explanations if r["id"] == q["id"]), None)
            if match:
                q["explanation"] = match.get("explanation")
                q["sources"]     = match.get("sources")

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
# Cache helpers (inline for simplicity — Phase 3)
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

