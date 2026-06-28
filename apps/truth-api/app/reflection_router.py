from __future__ import annotations

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query

from app.reflection_models import DashboardOverviewResponse
from app.reflection_models import ReflectionMaterializeRequest
from app.reflection_models import ReflectionMaterializeResponse
from app.reflection_models import ReflectionRunReadResponse
from app.reflection_models import ReflectionWritebackRequest
from app.reflection_models import ReflectionWritebackResponse
from app.reflection_service import ReflectionWritebackService

router = APIRouter(tags=["reflection"])
service = ReflectionWritebackService()


@router.post("/api/reflection/writeback", response_model=ReflectionWritebackResponse)
def reflection_writeback(payload: ReflectionWritebackRequest) -> ReflectionWritebackResponse:
    return service.writeback(payload)


@router.post("/api/reflection/materialize", response_model=ReflectionMaterializeResponse)
def reflection_materialize(payload: ReflectionMaterializeRequest) -> ReflectionMaterializeResponse:
    return service.materialize(payload)


@router.get("/api/reflection/runs/{run_date}", response_model=ReflectionRunReadResponse)
def reflection_run(run_date: str, user_id: str = Query(..., min_length=1)) -> ReflectionRunReadResponse:
    result = service.read_run(user_id=user_id, run_date=run_date)
    if result is None:
        raise HTTPException(status_code=404, detail="reflection run not found")
    return result


@router.get("/api/reflection/dashboard/overview", response_model=DashboardOverviewResponse)
def reflection_dashboard_overview(user_id: str = Query(..., min_length=1)) -> DashboardOverviewResponse:
    return service.dashboard_overview(user_id=user_id)
