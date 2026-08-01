from typing import Optional
from fastapi import APIRouter, Depends
from database.db import get_db
from routers.auth import get_current_user

router = APIRouter()


@router.get("/overview")
async def get_overview(cert_id: Optional[str] = None, user=Depends(get_current_user), db=Depends(get_db)):
    conditions = ["status='completed'", "user_id = ?"]
    params = [user["id"]]

    if cert_id:
        conditions.append("cert_id = ?")
        params.append(cert_id)

    where = "WHERE " + " AND ".join(conditions)

    async with db.execute(
        f"SELECT COUNT(*) as total, AVG(score) as avg_score, "
        f"MAX(score) as best_score FROM exam_sessions {where}",
        params,
    ) as cur:
        row = await cur.fetchone()

    wq_conditions = ["user_id = ?"]
    wq_params = [user["id"]]
    if cert_id:
        wq_conditions.append("cert_id = ?")
        wq_params.append(cert_id)
    wq_where = "WHERE " + " AND ".join(wq_conditions)

    async with db.execute(
        f"SELECT COUNT(*) as total FROM wrong_questions {wq_where}", wq_params
    ) as cur:
        wq = await cur.fetchone()

    # Study streak
    streak = await _calc_streak(db, user["id"])

    return {
        "total_exams":   row["total"] or 0,
        "avg_score":     round(row["avg_score"] or 0, 1),
        "best_score":    round(row["best_score"] or 0, 1),
        "wrong_count":   wq["total"] or 0,
        "study_streak":  streak,
    }


@router.get("/topics")
async def get_topic_performance(cert_id: Optional[str] = None, user=Depends(get_current_user), db=Depends(get_db)):
    conditions = ["es.user_id = ?"]
    params = [user["id"]]

    if cert_id:
        conditions.append("q.cert_id = ?")
        params.append(cert_id)

    where = "WHERE " + " AND ".join(conditions)

    async with db.execute(
        f"""SELECT q.topic,
               COUNT(*) as total,
               SUM(a.is_correct) as correct,
               ROUND(SUM(a.is_correct) * 100.0 / COUNT(*), 1) as accuracy
            FROM attempts a
            JOIN questions q ON q.id = a.question_id
            JOIN exam_sessions es ON es.id = a.session_id
            {where}
            GROUP BY q.topic
            ORDER BY accuracy ASC""",
        params,
    ) as cur:
        rows = await cur.fetchall()

    results = [dict(r) for r in rows]
    weak    = [r for r in results if r["accuracy"] < 60]
    strong  = [r for r in results if r["accuracy"] >= 80]

    return {
        "all":    results,
        "weak":   weak,
        "strong": strong,
    }


@router.get("/history")
async def get_exam_history(
    cert_id: Optional[str] = None,
    limit:   int = 20,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    conditions = ["status='completed'", "user_id = ?"]
    params = [user["id"]]

    if cert_id:
        conditions.append("cert_id = ?")
        params.append(cert_id)

    where = "WHERE " + " AND ".join(conditions)

    async with db.execute(
        f"SELECT * FROM exam_sessions {where} "
        f"ORDER BY started_at DESC LIMIT ?",
        params + [limit],
    ) as cur:
        rows = await cur.fetchall()

    return [dict(r) for r in rows]


@router.get("/accuracy-trend")
async def get_accuracy_trend(
    cert_id: Optional[str] = None,
    limit:   int = 10,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    conditions = ["status='completed'", "user_id = ?"]
    params = [user["id"]]

    if cert_id:
        conditions.append("cert_id = ?")
        params.append(cert_id)

    where = "WHERE " + " AND ".join(conditions)

    async with db.execute(
        f"SELECT score, started_at FROM exam_sessions {where} "
        f"ORDER BY started_at DESC LIMIT ?",
        params + [limit],
    ) as cur:
        rows = await cur.fetchall()

    trend = list(reversed([dict(r) for r in rows]))
    return trend


@router.get("/confidence")
async def get_confidence_analysis(cert_id: Optional[str] = None, user=Depends(get_current_user), db=Depends(get_db)):
    conditions = ["es.user_id = ?", "a.confidence IS NOT NULL"]
    params = [user["id"]]

    if cert_id:
        conditions.append("q.cert_id = ?")
        params.append(cert_id)

    where = "WHERE " + " AND ".join(conditions)

    async with db.execute(
        f"""SELECT a.confidence,
               COUNT(*) as total,
               SUM(a.is_correct) as correct,
               ROUND(SUM(a.is_correct)*100.0/COUNT(*),1) as accuracy
            FROM attempts a
            JOIN questions q ON q.id = a.question_id
            JOIN exam_sessions es ON es.id = a.session_id
            {where}
            GROUP BY a.confidence""",
        params,
    ) as cur:
        rows = await cur.fetchall()

    return [dict(r) for r in rows]


@router.get("/recommendations")
async def get_recommendations(cert_id: Optional[str] = None, user=Depends(get_current_user), db=Depends(get_db)):
    conditions = ["es.user_id = ?"]
    params = [user["id"]]

    if cert_id:
        conditions.append("q.cert_id = ?")
        params.append(cert_id)

    where = "WHERE " + " AND ".join(conditions)

    async with db.execute(
        f"""SELECT q.topic,
               ROUND(SUM(a.is_correct)*100.0/COUNT(*),1) as accuracy,
               COUNT(*) as attempts
            FROM attempts a
            JOIN questions q ON q.id = a.question_id
            JOIN exam_sessions es ON es.id = a.session_id
            {where}
            GROUP BY q.topic
            HAVING accuracy < 70 AND attempts >= 3
            ORDER BY accuracy ASC
            LIMIT 5""",
        params,
    ) as cur:
        rows = await cur.fetchall()

    return {
        "study_now": [dict(r) for r in rows],
        "message":   "Focus on these topics before your next exam.",
    }


@router.get("/streak")
async def get_streak(user=Depends(get_current_user), db=Depends(get_db)):
    """Get the user's current study streak and activity history."""
    streak = await _calc_streak(db, user["id"])

    async with db.execute(
        "SELECT date, activity FROM study_streaks WHERE user_id = ? ORDER BY date DESC LIMIT 30",
        (user["id"],),
    ) as cur:
        rows = await cur.fetchall()

    return {
        "current_streak": streak,
        "history": [dict(r) for r in rows],
    }


async def _calc_streak(db, user_id: str) -> int:
    """Calculate the current consecutive-day study streak."""
    from datetime import date, timedelta

    async with db.execute(
        "SELECT DISTINCT date FROM study_streaks WHERE user_id = ? ORDER BY date DESC",
        (user_id,),
    ) as cur:
        rows = await cur.fetchall()

    if not rows:
        return 0

    dates = [r["date"] for r in rows]
    today = date.today()
    streak = 0

    # Start from today or yesterday
    check = today
    if dates[0] != today.isoformat():
        if dates[0] == (today - timedelta(days=1)).isoformat():
            check = today - timedelta(days=1)
        else:
            return 0

    for d in dates:
        if d == check.isoformat():
            streak += 1
            check -= timedelta(days=1)
        else:
            break

    return streak
