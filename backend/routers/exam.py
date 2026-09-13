import json
import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database.db import get_db, DB_PATH
from routers.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# How many explanation-generation calls can run at the same time. Higher means
# a full exam's worth of questions gets ready faster, but too high risks
# hitting Gemini rate limits. 6 is a conservative starting point.
_PREGEN_CONCURRENCY = 6


class StartExamBody(BaseModel):
    cert_id:      str
    bank_id:      Optional[str] = None
    total:        int = 60
    q_types:      Optional[list[str]] = None
    topic:        Optional[str] = None
    session_type: str = "exam"
    exclude_dump_questions: bool = False


class SubmitAnswerBody(BaseModel):
    question_id: str
    selected:    str | list[str]
    confidence:  Optional[str] = None
    time_taken_s: Optional[int] = None


@router.post("/start")
async def start_exam(body: StartExamBody, user=Depends(get_current_user), db=Depends(get_db)):
    if body.total < 1 or body.total > 200:
        raise HTTPException(422, "total must be between 1 and 200.")
    if body.session_type not in {"exam", "practice", "review"}:
        raise HTTPException(422, "Invalid session type.")
    params     = [body.cert_id]
    where_clauses = ["q.cert_id = ?", "COALESCE(q.needs_review, 0) = 0"]

    if body.bank_id:
        async with db.execute(
            "SELECT id FROM question_banks WHERE id = ? AND cert_id = ? AND (user_id = ? OR user_id IS NULL)",
            (body.bank_id, body.cert_id, user["id"]),
        ) as cur:
            if not await cur.fetchone():
                raise HTTPException(404, "Question bank not found or access denied.")
        where_clauses.append("q.bank_id = ?")
        params.append(body.bank_id)
    else:
        # When no specific bank_id, only use banks owned by this user
        where_clauses.append("(qb.user_id = ? OR qb.user_id IS NULL)")
        params.append(user["id"])

    if body.q_types:
        placeholders = ",".join("?" * len(body.q_types))
        where_clauses.append(f"q.type IN ({placeholders})")
        params.extend(body.q_types)
    if body.topic:
        where_clauses.append("q.topic LIKE ?")
        params.append(f"%{body.topic}%")
    if body.exclude_dump_questions:
        where_clauses.append("(qb.source_type IS NULL OR qb.source_type != 'dump')")

    where   = "WHERE " + " AND ".join(where_clauses)
    params_q = params + [body.total]

    async with db.execute(
        f"SELECT q.* FROM questions q LEFT JOIN question_banks qb ON q.bank_id = qb.id {where} ORDER BY RANDOM() LIMIT ?",
        params_q,
    ) as cur:
        rows = await cur.fetchall()

    if not rows:
        raise HTTPException(404, "No questions found for this configuration.")

    session_id = str(uuid.uuid4())
    questions  = [_parse_q(dict(r)) for r in rows]

    # ── Pre-generate explanations INLINE before returning ──────────────
    # This ensures every question has an explanation ready when the user
    # clicks an answer. The trade-off is a slightly longer load time on
    # "Start Exam / Start Practice", but zero wait time during the session.
    missing = [q for q in questions if not (q.get("explanation") or "").strip()]
    if missing:
        logger.info(
            "Exam %s: %d/%d questions missing explanations — generating inline before start",
            session_id[:8], len(missing), len(questions),
        )
        try:
            from services.rag_service import ensure_explanations
            results = await ensure_explanations(missing, concurrency=_PREGEN_CONCURRENCY)

            # Merge generated explanations back into the questions list
            # and write them to DB so they persist for replays
            result_map = {r["id"]: r for r in results}
            for q in questions:
                if q["id"] in result_map:
                    exp = result_map[q["id"]]
                    q["explanation"] = exp.get("explanation", "")
                    q["sources"]     = exp.get("sources", [])
                    # Persist to DB
                    await db.execute(
                        "UPDATE questions SET explanation = ?, sources = ? WHERE id = ?",
                        (q["explanation"], json.dumps(q["sources"]), q["id"]),
                    )
            await db.commit()
            logger.info("Exam %s: inline explanation generation complete", session_id[:8])
        except Exception as e:
            logger.error("Exam %s: inline explanation generation failed: %s", session_id[:8], e)
            # Session can still start — some explanations may just show fallback text

    await db.execute(
        """INSERT INTO exam_sessions
           (id, cert_id, user_id, bank_id, session_type, total_questions)
           VALUES (?,?,?,?,?,?)""",
        (session_id, body.cert_id, user["id"], body.bank_id,
         body.session_type, len(questions)),
    )
    await db.commit()

    # Record study activity for streak tracking
    await _record_activity(db, user["id"], "exam")

    return {
        "session_id": session_id,
        "questions":  questions,
        "total":      len(questions),
    }


@router.post("/{session_id}/answer")
async def submit_answer(
    session_id: str,
    body: SubmitAnswerBody,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    # Verify session belongs to user
    async with db.execute(
        "SELECT id, status FROM exam_sessions WHERE id = ? AND user_id = ?",
        (session_id, user["id"]),
    ) as cur:
        session = await cur.fetchone()
        if not session:
            raise HTTPException(403, "Session not found or access denied.")
        if session["status"] != "active":
            raise HTTPException(409, "This exam session is no longer active.")

    async with db.execute(
        """SELECT q.* FROM questions q
           JOIN exam_sessions s ON s.id = ?
           WHERE q.id = ? AND q.cert_id = s.cert_id
             AND (s.bank_id IS NULL OR q.bank_id = s.bank_id)""",
        (session_id, body.question_id),
    ) as cur:
        row = await cur.fetchone()

    if not row:
        raise HTTPException(404, "Question not found.")

    q          = _parse_q(dict(row))
    answer_key = q["answer_key"]
    selected   = body.selected

    if isinstance(answer_key, list):
        correct_set  = set(a.upper() for a in answer_key)
        selected_set = set(a.upper() for a in (selected if isinstance(selected, list) else [selected]))
        is_correct   = correct_set == selected_set
    else:
        is_correct = str(selected).upper().strip() == str(answer_key).upper().strip()

    attempt_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO attempts
           (id, session_id, question_id, selected, is_correct, confidence, time_taken_s)
           VALUES (?,?,?,?,?,?,?)""",
        (
            attempt_id, session_id, body.question_id,
            json.dumps(selected) if isinstance(selected, list) else selected,
            1 if is_correct else 0,
            body.confidence, body.time_taken_s,
        ),
    )

    if not is_correct:
        async with db.execute(
            "SELECT id, times_wrong FROM wrong_questions WHERE question_id = ? AND user_id = ?",
            (body.question_id, user["id"]),
        ) as cur:
            existing = await cur.fetchone()

        if existing:
            await db.execute(
                "UPDATE wrong_questions SET times_wrong = times_wrong + 1, "
                "last_seen = datetime('now'), session_id = ? WHERE id = ?",
                (session_id, existing["id"]),
            )
        else:
            async with db.execute(
                "SELECT cert_id, topic FROM questions WHERE id = ?",
                (body.question_id,),
            ) as cur:
                qinfo = await cur.fetchone()
            await db.execute(
                """INSERT INTO wrong_questions
                   (id, question_id, session_id, cert_id, user_id, topic)
                   VALUES (?,?,?,?,?,?)""",
                (str(uuid.uuid4()), body.question_id, session_id,
                 qinfo["cert_id"], user["id"], qinfo["topic"]),
            )

    await db.commit()

    return {
        "is_correct":  is_correct,
        "correct_key": answer_key,
        "attempt_id":  attempt_id,
    }


@router.post("/{session_id}/finish")
async def finish_exam(session_id: str, time_taken_s: int = 0, user=Depends(get_current_user), db=Depends(get_db)):
    # Verify session belongs to user
    async with db.execute(
        "SELECT id, status FROM exam_sessions WHERE id = ? AND user_id = ?",
        (session_id, user["id"]),
    ) as cur:
        session = await cur.fetchone()
        if not session:
            raise HTTPException(403, "Session not found or access denied.")
        if session["status"] != "active":
            raise HTTPException(409, "This exam session is already finished.")

    async with db.execute(
        "SELECT COUNT(*) as total, SUM(is_correct) as correct "
        "FROM attempts WHERE session_id = ?",
        (session_id,),
    ) as cur:
        row = await cur.fetchone()

    total   = row["total"] or 0
    correct = row["correct"] or 0
    score   = round((correct / total * 100), 1) if total else 0

    await db.execute(
        """UPDATE exam_sessions SET status='completed',
           completed_at=datetime('now'), score=?, time_taken_s=?
           WHERE id=?""",
        (score, time_taken_s, session_id),
    )
    await db.commit()

    async with db.execute(
        """SELECT q.topic, COUNT(*) as total, SUM(a.is_correct) as correct
           FROM attempts a JOIN questions q ON q.id = a.question_id
           WHERE a.session_id = ? GROUP BY q.topic""",
        (session_id,),
    ) as cur:
        topic_rows = await cur.fetchall()

    topic_breakdown = [
        {
            "topic":    r["topic"],
            "total":    r["total"],
            "correct":  r["correct"],
            "accuracy": round(r["correct"] / r["total"] * 100, 1),
        }
        for r in topic_rows
    ]

    # Check if the exam used a generated bank (for auto-cleanup)
    bank_info = None
    async with db.execute(
        "SELECT bank_id FROM exam_sessions WHERE id = ?", (session_id,)
    ) as cur:
        sess_row = await cur.fetchone()
    if sess_row and sess_row["bank_id"]:
        async with db.execute(
            "SELECT id, source_type, source_name, total_questions FROM question_banks WHERE id = ?",
            (sess_row["bank_id"],),
        ) as cur:
            bank_row = await cur.fetchone()
        if bank_row:
            bank_info = {
                "bank_id": bank_row["id"],
                "source_type": bank_row["source_type"],
                "source_name": bank_row["source_name"],
                "total_questions": bank_row["total_questions"],
            }
            # We no longer delete the generated bank here because deleting questions
            # breaks the exam history/replay (which joins on the questions table).
            # Generated banks are already hidden from the Dump Manager natively.

    return {
        "session_id":      session_id,
        "score":           score,
        "correct":         correct,
        "total":           total,
        "time_taken_s":    time_taken_s,
        "topic_breakdown": topic_breakdown,
        "bank_info":       bank_info,
    }


@router.get("/{session_id}/replay")
async def get_replay(session_id: str, user=Depends(get_current_user), db=Depends(get_db)):
    # Verify session belongs to user
    async with db.execute(
        "SELECT id FROM exam_sessions WHERE id = ? AND user_id = ?",
        (session_id, user["id"]),
    ) as cur:
        if not await cur.fetchone():
            raise HTTPException(403, "Session not found or access denied.")

    async with db.execute(
        """SELECT a.*, q.question, q.options, q.answer_key,
                  q.explanation, q.sources, q.topic, q.type
           FROM attempts a JOIN questions q ON q.id = a.question_id
           WHERE a.session_id = ? ORDER BY a.rowid""",
        (session_id,),
    ) as cur:
        rows = await cur.fetchall()

    return [_parse_attempt(dict(r)) for r in rows]


@router.get("/sessions")
async def list_sessions(cert_id: Optional[str] = None, limit: int = 20, user=Depends(get_current_user), db=Depends(get_db)):
    limit = min(max(limit, 1), 100)
    conditions = ["user_id = ?"]
    params = [user["id"]]

    if cert_id:
        conditions.append("cert_id = ?")
        params.append(cert_id)

    where = "WHERE " + " AND ".join(conditions)
    async with db.execute(
        f"SELECT * FROM exam_sessions {where} ORDER BY started_at DESC LIMIT ?",
        params + [limit],
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def _record_activity(db, user_id: str, activity: str):
    """Record daily study activity for streak tracking."""
    from datetime import date
    today = date.today().isoformat()
    try:
        await db.execute(
            "INSERT OR IGNORE INTO study_streaks (id, user_id, date, activity) VALUES (?, ?, ?, ?)",
            (str(uuid.uuid4()), user_id, today, activity),
        )
    except Exception:
        pass  # Non-critical


def _parse_q(row: dict) -> dict:
    for k in ("options", "answer_key"):
        try:
            row[k] = json.loads(row[k])
        except Exception:
            pass
    if row.get("answer_key") == "":
        row["answer_key"] = None
    try:
        row["sources"] = json.loads(row.get("sources") or "[]")
    except Exception:
        row["sources"] = []
    return row




def _parse_attempt(row: dict) -> dict:
    for k in ("options", "answer_key", "selected"):
        try:
            row[k] = json.loads(row[k])
        except Exception:
            pass

    if row.get("ai_explanation"):
        row["explanation"] = row["ai_explanation"]
        try:
            row["sources"] = json.loads(row.get("ai_sources") or "[]")
        except Exception:
            row["sources"] = []
    else:
        try:
            row["sources"] = json.loads(row.get("sources") or "[]")
        except Exception:
            row["sources"] = []

    return row

