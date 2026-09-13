import asyncio
import json
import logging
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from database.db import get_db, DB_PATH
from routers.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("./data/dumps")


@router.post("/upload")
async def upload_dump(
    file:      UploadFile = File(...),
    cert_id:   str = Form(...),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    filename = (file.filename or "").strip()
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files accepted.")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    bank_id  = str(uuid.uuid4())
    pdf_path = UPLOAD_DIR / f"{bank_id}.pdf"
    content  = await file.read()

    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(413, "File too large. Max 50MB.")

    pdf_path.write_bytes(content)

    await db.execute(
        """INSERT INTO question_banks (id, cert_id, user_id, source_type, source_name)
           VALUES (?,?,?,?,?)""",
        (bank_id, cert_id, user["id"], "dump", filename),
    )
    await db.commit()

    return {
        "bank_id":   bank_id,
        "cert_id":   cert_id,
        "filename":  filename,
        "status":    "uploaded",
        "message":   "PDF uploaded. Call /api/dumps/{bank_id}/process to extract questions.",
    }


@router.post("/{bank_id}/process")
async def process_dump(bank_id: str, user=Depends(get_current_user), db=Depends(get_db)):
    async with db.execute(
        "SELECT * FROM question_banks WHERE id = ? AND user_id = ?", (bank_id, user["id"])
    ) as cur:
        bank = await cur.fetchone()

    if not bank:
        raise HTTPException(404, "Question bank not found.")

    pdf_path = UPLOAD_DIR / f"{bank_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(404, "PDF file not found.")

    try:
        from services.dump_service import extract_questions_from_pdf
        from services.question_validation import deduplicate_questions
        questions = await extract_questions_from_pdf(
            pdf_path=pdf_path,
            cert_id=bank["cert_id"],
            bank_id=bank_id,
        )
    except Exception as e:
        raise HTTPException(500, f"Processing failed: {str(e)}")

    if not questions:
        raise HTTPException(422, "No questions could be extracted from this PDF.")

    questions, rejected_count = deduplicate_questions(questions)
    if not questions:
        raise HTTPException(422, "No valid, unique questions could be extracted from this PDF.")

    # Save questions to DB first
    for q in questions:
        await db.execute(
            """INSERT OR IGNORE INTO questions
               (id, bank_id, cert_id, type, topic, question, options, answer_key, difficulty, needs_review)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                q["id"], bank_id, bank["cert_id"],
                q["type"], q.get("topic"),
                q["question"],
                json.dumps(q["options"]),
                json.dumps(q["answer_key"]) if isinstance(q.get("answer_key"), list)
                else q.get("answer_key") or "",
                q.get("difficulty", "medium"),
                1 if q.get("needs_review") else 0,
                q.get("fingerprint"),
                1 if q.get("needs_review") else 0,
            ),
        )

    await db.execute(
        "UPDATE question_banks SET total_questions = ?, explanation_progress = ? WHERE id = ?",
        (len(questions), f"0/{len(questions)}", bank_id),
    )
    await db.commit()

    # Fire background explanation generation — does NOT block the response
    asyncio.create_task(
        _generate_explanations_background(bank_id, questions, bank["cert_id"])
    )
    logger.info(
        "Dump %s processed: %d questions extracted. Explanation generation started in background.",
        bank_id[:8], len(questions),
    )

    return {
        "bank_id":         bank_id,
        "questions_added": len(questions),
        "questions_rejected": rejected_count,
        "status":          "processed",
        "explanation_status": "generating",
    }


async def _generate_explanations_background(
    bank_id: str, questions: list[dict], cert_id: str
) -> None:
    """Background task that generates explanations for all extracted questions."""
    try:
        from services.rag_service import background_generate_explanations
        await background_generate_explanations(
            bank_id=bank_id,
            questions=questions,
            db_path=str(DB_PATH),
            concurrency=6,
        )
    except Exception as e:
        logger.error("Background explanation generation failed for bank %s: %s", bank_id[:8], e)
        # Mark as failed so the frontend knows
        try:
            import aiosqlite
            async with aiosqlite.connect(str(DB_PATH)) as db:
                await db.execute(
                    "UPDATE question_banks SET explanation_progress = ? WHERE id = ?",
                    ("failed", bank_id),
                )
                await db.commit()
        except Exception:
            pass


@router.get("/{bank_id}/status")
async def get_bank_status(bank_id: str, user=Depends(get_current_user), db=Depends(get_db)):
    """Check explanation generation progress for a question bank."""
    async with db.execute(
        "SELECT id, total_questions, explanation_progress FROM question_banks WHERE id = ? AND user_id = ?",
        (bank_id, user["id"]),
    ) as cur:
        bank = await cur.fetchone()

    if not bank:
        raise HTTPException(404, "Question bank not found.")

    progress = bank["explanation_progress"]

    # Count how many questions actually have explanations
    async with db.execute(
        "SELECT COUNT(*) as cnt FROM questions WHERE bank_id = ? AND explanation IS NOT NULL AND TRIM(explanation) != ''",
        (bank_id,),
    ) as cur:
        row = await cur.fetchone()
    with_explanation = row["cnt"] if row else 0

    return {
        "bank_id":          bank_id,
        "total_questions":  bank["total_questions"] or 0,
        "with_explanation": with_explanation,
        "progress":         progress,
        "is_complete":      progress == "complete",
    }


@router.get("/")
async def list_banks(cert_id: Optional[str] = None, source_type: Optional[str] = None, user=Depends(get_current_user), db=Depends(get_db)):
    """List question banks. By default only shows 'dump' banks (uploaded PDFs).
    Pass source_type='all' to see everything, or source_type='generated' for AI banks."""
    conditions = ["user_id = ?"]
    params = [user["id"]]

    # Default: only show dumps (uploaded PDFs), not AI-generated banks
    if source_type == "all":
        pass  # no filter
    elif source_type:
        conditions.append("source_type = ?")
        params.append(source_type)
    else:
        conditions.append("source_type = 'dump'")

    if cert_id:
        conditions.append("cert_id = ?")
        params.append(cert_id)

    where = "WHERE " + " AND ".join(conditions)
    async with db.execute(
        f"SELECT * FROM question_banks {where} ORDER BY created_at DESC",
        params,
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


@router.put("/{bank_id}/save")
async def save_bank(bank_id: str, user=Depends(get_current_user), db=Depends(get_db)):
    """Convert a generated bank into a saved bank so it appears in Dump Manager."""
    # Verify ownership
    async with db.execute(
        "SELECT id, source_type FROM question_banks WHERE id = ? AND user_id = ?",
        (bank_id, user["id"]),
    ) as cur:
        bank = await cur.fetchone()
        if not bank:
            raise HTTPException(404, "Question bank not found.")

    await db.execute(
        "UPDATE question_banks SET source_type = 'dump', source_name = REPLACE(source_name, 'Generated questions:', 'Saved AI Bank:') WHERE id = ?",
        (bank_id,)
    )
    await db.commit()
    return {"saved": True, "bank_id": bank_id}

@router.delete("/{bank_id}")
async def delete_bank(bank_id: str, user=Depends(get_current_user), db=Depends(get_db)):
    # Verify ownership
    async with db.execute(
        "SELECT id FROM question_banks WHERE id = ? AND user_id = ?",
        (bank_id, user["id"]),
    ) as cur:
        if not await cur.fetchone():
            raise HTTPException(404, "Question bank not found.")

    await db.execute("DELETE FROM questions WHERE bank_id = ?",      (bank_id,))
    await db.execute("DELETE FROM question_banks WHERE id = ?",      (bank_id,))
    await db.commit()
    pdf_path = UPLOAD_DIR / f"{bank_id}.pdf"
    if pdf_path.exists():
        pdf_path.unlink()
    return {"deleted": True}

