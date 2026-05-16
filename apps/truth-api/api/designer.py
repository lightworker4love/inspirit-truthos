from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.db import connect_db
from app.designer_agent import DesignerAgent


router = APIRouter()
STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


class CoachReviewRequest(BaseModel):
    note: str
    action: str
    new_principle_proposed: str | None = None


@router.get("/console", include_in_schema=False)
async def truth_console():
    return FileResponse(STATIC_DIR / "truth-console.html")


@router.get("/api/designer/hard-cases")
async def get_hard_cases(status: str = "pending", limit: int = 20) -> dict:
    with connect_db() as connection:
        rows = connection.execute(
            """
            SELECT *
              FROM hardcasebuffer
             WHERE COALESCE(status, 'pending') = ?
             ORDER BY createdat DESC
             LIMIT ?
            """,
            (status, limit),
        ).fetchall()
        hard_cases = [_hard_case_row(row) for row in rows]

    return {"status": status, "hard_cases": hard_cases, "count": len(hard_cases)}


@router.post("/api/designer/hard-cases/{hardcase_id}/review")
async def review_hard_case(hardcase_id: str) -> dict:
    try:
        with connect_db() as connection:
            return DesignerAgent(db_client=connection).review_hard_case(hardcase_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/api/designer/hard-cases/review-pending")
async def review_pending_hard_cases(limit: int = 5) -> dict:
    with connect_db() as connection:
        return DesignerAgent(db_client=connection).review_pending(limit=limit)


@router.post("/api/designer/coach-review/{hardcase_id}")
async def submit_coach_review(hardcase_id: str, body: CoachReviewRequest) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    review_id = f"hr_{uuid4().hex}"
    evolution_id = f"ke_{uuid4().hex}"
    findings = {
        "note": body.note,
        "new_principle_proposed": body.new_principle_proposed,
    }
    target_status = _status_for_coach_action(body.action)

    with connect_db() as connection:
        hard_case = connection.execute(
            "SELECT userid FROM hardcasebuffer WHERE userid = ?",
            (hardcase_id,),
        ).fetchone()
        if not hard_case:
            raise HTTPException(status_code=404, detail="Hard case not found")

        connection.execute(
            """
            INSERT INTO designerreviews (
              id, hardcaseid, reviewedby, findingsjson, newprincipleproposed,
              promptwinner, action, createdat
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                review_id,
                hardcase_id,
                "human_coach",
                json.dumps(findings, ensure_ascii=False),
                int(bool(body.new_principle_proposed)),
                None,
                body.action,
                now,
            ),
        )
        connection.execute(
            """
            INSERT INTO knowledgeevolutions (
              id, sourcetype, sourceid, changetype, targetid, rationaljson, createdat
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evolution_id,
                "designerreviews",
                review_id,
                "human_coach_review",
                hardcase_id,
                json.dumps({"action": body.action, "note": body.note}, ensure_ascii=False),
                now,
            ),
        )
        connection.execute(
            """
            UPDATE hardcasebuffer
               SET status = ?, resolutionnote = ?, resolvedat = ?
             WHERE userid = ?
            """,
            (
                target_status,
                body.note,
                now if target_status == "resolved" else None,
                hardcase_id,
            ),
        )
        connection.commit()

    return {
        "status": "recorded",
        "hardcase_id": hardcase_id,
        "review_id": review_id,
        "knowledge_evolution_id": evolution_id,
        "hard_case_status": target_status,
    }


@router.get("/api/designer/reviews")
async def get_designer_reviews(limit: int = 30) -> dict:
    with connect_db() as connection:
        rows = connection.execute(
            """
            SELECT *
              FROM designerreviews
             ORDER BY createdat DESC
             LIMIT ?
            """,
            (limit,),
        ).fetchall()
        reviews = [_review_row(row) for row in rows]
    return {"reviews": reviews, "count": len(reviews)}


@router.get("/api/designer/knowledge-evolution")
async def get_knowledge_evolution(limit: int = 30) -> dict:
    with connect_db() as connection:
        rows = connection.execute(
            """
            SELECT *
              FROM knowledgeevolutions
             ORDER BY createdat DESC
             LIMIT ?
            """,
            (limit,),
        ).fetchall()
        entries = [_knowledge_row(row) for row in rows]
    return {"knowledge_evolutions": entries, "count": len(entries)}


def _hard_case_row(row: Any) -> dict:
    item = dict(row)
    item["reasons"] = _loads(item.get("reasons"), [])
    item["summaryjson"] = _loads(item.get("summaryjson"), None)
    item["status"] = item.get("status") or "pending"
    return item


def _review_row(row: Any) -> dict:
    item = dict(row)
    item["findingsjson"] = _loads(item.get("findingsjson"), {})
    item["newprincipleproposed"] = bool(item.get("newprincipleproposed"))
    return item


def _knowledge_row(row: Any) -> dict:
    item = dict(row)
    item["rationaljson"] = _loads(item.get("rationaljson"), {})
    return item


def _status_for_coach_action(action: str) -> str:
    mapping = {
        "resolved": "resolved",
        "integrated": "resolved",
        "new_puzzle_needed": "in_review",
        "prompt_update_needed": "in_review",
        "escalate": "escalated_to_coach",
        "escalated_to_coach": "escalated_to_coach",
    }
    return mapping.get(action, "in_review")


def _loads(raw: Any, default: Any) -> Any:
    if raw in (None, ""):
        return default
    try:
        return json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return default
