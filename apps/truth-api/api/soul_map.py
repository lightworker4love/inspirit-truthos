from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db import connect_db
from app.soul_map_engine import SoulMapEngine


router = APIRouter()


class PatternStatusUpdate(BaseModel):
    pattern_id: str
    new_status: str


class BlindSpotStatusUpdate(BaseModel):
    resolution_status: str


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
        recent_patterns = _recent_patterns(soul_map.get("recurring_patterns", []))

    return {
        "user_id": user_id,
        "status": "active",
        "evolution_stage": soul_map.get("evolution_stage"),
        "recurring_patterns": soul_map.get("recurring_patterns", []),
        "recent_patterns": recent_patterns,
        "pattern_weights": soul_map.get("pattern_weights", {}),
        "active_lessons": soul_map.get("active_lessons", []),
        "integrated_dimensions": soul_map.get("integrated_dimensions", []),
        "top_blind_spots": top_blind_spots,
        "blind_spots": top_blind_spots,
        "summary": soul_map.get("soul_map_summary", ""),
        "last_truth_shift_at": soul_map.get("last_truth_shift_at"),
        "evolution_history": soul_map.get("evolution_history", []),
        "created_at": soul_map.get("created_at"),
        "updated_at": soul_map.get("updated_at"),
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


@router.patch("/api/soul-map/{user_id}/pattern")
async def update_pattern_status(user_id: str, body: PatternStatusUpdate) -> dict:
    allowed = {"softening", "integrated", "transcended"}
    if body.new_status not in allowed:
        raise HTTPException(status_code=400, detail="Invalid pattern status")

    now = datetime.now(timezone.utc).isoformat()
    with connect_db() as connection:
        engine = SoulMapEngine(db_client=connection)
        soul_map = engine.get_soul_map(user_id)
        if not soul_map:
            raise HTTPException(status_code=404, detail="Soul Map not found")

        patterns = soul_map.get("recurring_patterns", [])
        matched = None
        for pattern in patterns:
            if pattern.get("id") == body.pattern_id:
                pattern["status"] = body.new_status
                pattern["status_updated_at"] = now
                matched = pattern
                break
        if not matched:
            raise HTTPException(status_code=404, detail="Pattern not found")

        if body.new_status == "integrated":
            dimension = matched.get("dimension")
            integrated = soul_map.setdefault("integrated_dimensions", [])
            if dimension and dimension not in integrated:
                integrated.append(dimension)
        elif body.new_status == "transcended":
            transcended = soul_map.setdefault("transcended_patterns", [])
            if body.pattern_id not in transcended:
                transcended.append(body.pattern_id)

        engine._save(user_id, soul_map, now)

    return {
        "status": "updated",
        "pattern_id": body.pattern_id,
        "new_status": body.new_status,
    }


@router.patch("/api/soul-map/{user_id}/blind-spot/{blind_spot_id}")
async def update_blind_spot_status(
    user_id: str,
    blind_spot_id: str,
    body: BlindSpotStatusUpdate,
) -> dict:
    allowed = {"softening", "integrated", "transcended"}
    if body.resolution_status not in allowed:
        raise HTTPException(status_code=400, detail="Invalid blind spot status")

    now = datetime.now(timezone.utc).isoformat()
    with connect_db() as connection:
        cursor = connection.execute(
            """
            UPDATE blindspotarchives
               SET resolutionstatus = ?, resolutionat = ?
             WHERE id = ? AND userid = ?
            """,
            (body.resolution_status, now, blind_spot_id, user_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Blind spot not found")
        connection.commit()

    return {
        "status": "updated",
        "blind_spot_id": blind_spot_id,
        "resolution_status": body.resolution_status,
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


def _recent_patterns(patterns: list[dict]) -> list[str]:
    now = datetime.now(timezone.utc)
    recent = []
    for pattern in patterns:
        first_seen = pattern.get("first_seen")
        if not first_seen:
            continue
        try:
            parsed = datetime.fromisoformat(first_seen.replace("Z", "+00:00"))
        except ValueError:
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        if (now - parsed).total_seconds() <= 300:
            recent.append(pattern.get("id") or pattern.get("description") or "")
    return [pattern for pattern in recent if pattern]


def _loads(raw: Any, default: Any) -> Any:
    if raw in (None, ""):
        return default
    try:
        return json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return default
