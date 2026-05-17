from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter

from app.db import connect_db


router = APIRouter()


@router.get("/api/sessions/recent")
async def get_recent_sessions(minutes: int = 10, limit: int = 50) -> dict:
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=minutes)).isoformat()
    with connect_db() as connection:
        rows = connection.execute(
            """
            SELECT session_id, user_id, MAX(created_at) AS last_activity
              FROM truth_evals
             WHERE created_at >= ? AND session_id IS NOT NULL
             GROUP BY session_id, user_id
             ORDER BY last_activity DESC
             LIMIT ?
            """,
            (cutoff, limit),
        ).fetchall()
    return {"sessions": [dict(row) for row in rows], "count": len(rows)}


@router.get("/api/sessions/{session_id}/truth-scores")
async def get_session_truth_scores(session_id: str) -> dict:
    with connect_db() as connection:
        rows = connection.execute(
            """
            SELECT id, user_id, session_id, question, verification_track,
                   life_evidence_confirmed, discovery_triggered, created_at
              FROM truth_evals
             WHERE session_id = ?
             ORDER BY created_at ASC
            """,
            (session_id,),
        ).fetchall()
    evaluations = [_truth_eval_row(row) for row in rows]
    return {"session_id": session_id, "evaluations": evaluations}


@router.get("/api/sessions/stats/summary")
async def get_session_stats() -> dict:
    cutoff_1h = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    with connect_db() as connection:
        rows = connection.execute(
            """
            SELECT id, session_id, verification_track,
                   life_evidence_confirmed, discovery_triggered
              FROM truth_evals
             WHERE created_at >= ?
            """,
            (cutoff_1h,),
        ).fetchall()
        hard_cases_pending = 0
        if _table_exists(connection, "hardcasebuffer"):
            if _column_exists(connection, "hardcasebuffer", "status"):
                hard_cases = connection.execute(
                    """
                    SELECT COUNT(*) AS pending
                      FROM hardcasebuffer
                     WHERE COALESCE(status, 'pending') = 'pending'
                    """
                ).fetchone()
            else:
                hard_cases = connection.execute(
                    "SELECT COUNT(*) AS pending FROM hardcasebuffer"
                ).fetchone()
            hard_cases_pending = int(hard_cases["pending"] if hard_cases else 0)

    scores = [_score(row) for row in rows]
    avg_score = round(sum(scores) / len(scores), 3) if scores else 0
    return {
        "sessions_last_1h": len({row["session_id"] for row in rows if row["session_id"]}),
        "queries_last_1h": len(rows),
        "avg_truth_score_1h": avg_score,
        "hard_cases_pending": hard_cases_pending,
    }


def _truth_eval_row(row: Any) -> dict:
    item = dict(row)
    item["query_text"] = item.get("question") or ""
    item["truth_score"] = _score(row)
    item["verified_truth"] = item["truth_score"] >= 0.7
    return item


def _score(row: Any) -> float:
    track = row["verification_track"]
    score = 0.55
    if track == "stillness":
        score = 0.9
    elif track == "evidence":
        score = 0.8
    elif track == "dialogue":
        score = 0.68
    if row["life_evidence_confirmed"]:
        score += 0.08
    if row["discovery_triggered"]:
        score += 0.06
    return round(min(score, 1.0), 3)


def _table_exists(connection: Any, table_name: str) -> bool:
    row = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _column_exists(connection: Any, table_name: str, column_name: str) -> bool:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    names = set()
    for row in rows:
        if hasattr(row, "keys") and "name" in row.keys():
            names.add(row["name"])
        else:
            names.add(row[1])
    return column_name in names
