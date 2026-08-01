import json
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from database.db import get_db
from routers.auth import get_current_user

router = APIRouter()


class QuestionCreate(BaseModel):
    bank_id:     str
    cert_id:     str
    type:        str
    topic:       Optional[str] = None
    question:    str
    options:     list[str]
    answer_key:  str | list[str]
    explanation: Optional[str] = None
    difficulty:  str = "medium"


@router.get("/")
async def list_questions(
    cert_id:    Optional[str] = None,
    bank_id:    Optional[str] = None,
    topic:      Optional[str] = None,
    q_type:     Optional[str] = None,
    limit:      int = Query(60, le=500),
    offset:     int = 0,
    randomize:  bool = False,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    conditions = []
    params     = []

    if cert_id:
        conditions.append("q.cert_id = ?")
        params.append(cert_id)
    if bank_id:
        conditions.append("q.bank_id = ?")
        params.append(bank_id)
    if topic:
        conditions.append("q.topic LIKE ?")
        params.append(f"%{topic}%")
    if q_type:
        conditions.append("q.type = ?")
        params.append(q_type)

    # Only show questions from banks this user owns (or system banks)
    conditions.append("(qb.user_id = ? OR qb.user_id IS NULL)")
    params.append(user["id"])

    where  = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    order  = "ORDER BY RANDOM()" if randomize else "ORDER BY q.rowid"
    params += [limit, offset]

    async with db.execute(
        f"SELECT q.* FROM questions q LEFT JOIN question_banks qb ON q.bank_id = qb.id {where} {order} LIMIT ? OFFSET ?",
        params,
    ) as cur:
        rows = await cur.fetchall()

    return [_parse_question(dict(r)) for r in rows]


@router.get("/topics")
async def list_topics(cert_id: Optional[str] = None, user=Depends(get_current_user), db=Depends(get_db)):
    conditions = []
    params = []

    if cert_id:
        conditions.append("q.cert_id = ?")
        params.append(cert_id)

    # Only show topics from user's banks
    conditions.append("(qb.user_id = ? OR qb.user_id IS NULL)")
    params.append(user["id"])

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    async with db.execute(
        f"SELECT DISTINCT q.topic, COUNT(*) as count "
        f"FROM questions q LEFT JOIN question_banks qb ON q.bank_id = qb.id "
        f"{where} GROUP BY q.topic ORDER BY q.topic",
        params,
    ) as cur:
        rows = await cur.fetchall()
    return [{"topic": r["topic"], "count": r["count"]} for r in rows]


@router.get("/wrong")
async def list_wrong_questions(cert_id: Optional[str] = None, user=Depends(get_current_user), db=Depends(get_db)):
    conditions = ["wq.user_id = ?"]
    params = [user["id"]]

    if cert_id:
        conditions.append("wq.cert_id = ?")
        params.append(cert_id)

    where = "WHERE " + " AND ".join(conditions)

    async with db.execute(
        f"""SELECT q.*, wq.times_wrong, wq.last_seen,
                   (SELECT a.selected FROM attempts a
                    WHERE a.question_id = q.id
                    ORDER BY a.created_at DESC LIMIT 1) AS last_selected,
                   (SELECT a.ai_explanation FROM attempts a
                    WHERE a.question_id = q.id AND a.ai_explanation IS NOT NULL
                    ORDER BY a.created_at DESC LIMIT 1) AS ai_explanation,
                   (SELECT a.ai_sources FROM attempts a
                    WHERE a.question_id = q.id AND a.ai_explanation IS NOT NULL
                    ORDER BY a.created_at DESC LIMIT 1) AS ai_sources
            FROM wrong_questions wq
            JOIN questions q ON q.id = wq.question_id
            {where}
            ORDER BY wq.times_wrong DESC""",
        params,
    ) as cur:
        rows = await cur.fetchall()
    return [_parse_question(dict(r)) for r in rows]


@router.post("/")
async def create_question(body: QuestionCreate, user=Depends(get_current_user), db=Depends(get_db)):
    qid = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO questions
           (id, bank_id, cert_id, type, topic, question, options, answer_key, explanation, difficulty)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (
            qid, body.bank_id, body.cert_id, body.type, body.topic,
            body.question,
            json.dumps(body.options),
            json.dumps(body.answer_key) if isinstance(body.answer_key, list)
            else body.answer_key,
            body.explanation, body.difficulty,
        ),
    )
    await db.commit()
    return {"id": qid}


@router.post("/batch")
async def create_questions_batch(questions: list[QuestionCreate], user=Depends(get_current_user), db=Depends(get_db)):
    ids = []
    for q in questions:
        qid = str(uuid.uuid4())
        await db.execute(
            """INSERT INTO questions
               (id, bank_id, cert_id, type, topic, question, options, answer_key, explanation, difficulty)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                qid, q.bank_id, q.cert_id, q.type, q.topic,
                q.question,
                json.dumps(q.options),
                json.dumps(q.answer_key) if isinstance(q.answer_key, list)
                else q.answer_key,
                q.explanation, q.difficulty,
            ),
        )
        ids.append(qid)
    await db.commit()

    if questions:
        await db.execute(
            "UPDATE question_banks SET total_questions = "
            "(SELECT COUNT(*) FROM questions WHERE bank_id = ?) WHERE id = ?",
            (questions[0].bank_id, questions[0].bank_id),
        )
        await db.commit()

    return {"created": len(ids), "ids": ids}


def _parse_question(row: dict) -> dict:
    try:
        row["options"]    = json.loads(row["options"])
    except Exception:
        pass
    try:
        row["answer_key"] = json.loads(row["answer_key"])
    except Exception:
        pass
    if row.get("last_selected"):
        try:
            row["last_selected"] = json.loads(row["last_selected"])
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