from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.db import connect_db
from app.designer_agent import DesignerAgent


router = APIRouter()


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
