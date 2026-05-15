from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter

from app.db import connect_db
from app.soul_map_engine import SoulMapEngine


router = APIRouter()


@router.get("/api/soul-map/{user_id}")
async def get_soul_map(user_id: str) -> dict:
    with connect_db() as connection:
        engine = SoulMapEngine(db_client=connection)
        soul_map = engine.get_soul_map(user_id)
        if not soul_map:
            return {
                "user_id": user_id,
                "status": "not_yet_built",
                "message": "This user has not yet had enough interactions to build a Soul Map.",
                "minimum_interactions_needed": 3,
            }
        top_blind_spots = _get_top_blind_spots(connection, user_id)

    return {
        "user_id": user_id,
        "status": "active",
        "evolution_stage": soul_map.get("evolution_stage"),
        "recurring_patterns": soul_map.get("recurring_patterns", []),
        "active_lessons": soul_map.get("active_lessons", []),
        "integrated_dimensions": soul_map.get("integrated_dimensions", []),
        "top_blind_spots": top_blind_spots,
        "summary": soul_map.get("soul_map_summary", ""),
        "last_truth_shift_at": soul_map.get("last_truth_shift_at"),
        "evolution_history": soul_map.get("evolution_history", []),
    }


@router.get("/api/soul-map/{user_id}/blind-spots")
async def get_blind_spots(user_id: str, status: str = "active") -> dict:
    with connect_db() as connection:
        rows = connection.execute(
            """
            SELECT *
              FROM blindspotarchives
             WHERE userid = ? AND resolutionstatus = ?
             ORDER BY frequency DESC
            """,
            (user_id, status),
        ).fetchall()
        blind_spots = [_blind_spot_row(row) for row in rows]

    return {
        "user_id": user_id,
        "blind_spots": blind_spots,
        "count": len(blind_spots),
    }


def _get_top_blind_spots(connection: Any, user_id: str) -> list[dict]:
    rows = connection.execute(
        """
        SELECT *
          FROM blindspotarchives
         WHERE userid = ?
         ORDER BY frequency DESC
         LIMIT 5
        """,
        (user_id,),
    ).fetchall()
    return [_blind_spot_row(row) for row in rows]


def _blind_spot_row(row: Any) -> dict:
    item = dict(row)
    for field in ("suggestedanchorsjson", "relatedpuzzlesjson", "domainsjson"):
        item[field] = _loads(item.get(field), [])
    return item


def _loads(raw: Any, default: Any) -> Any:
    if raw in (None, ""):
        return default
    try:
        return json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return default
