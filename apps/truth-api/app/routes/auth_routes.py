from fastapi import APIRouter, Depends, Request

from app.core.security import get_session_token
from app.models.auth_models import LoginRequest, LoginResponse
from app.services.auth_service import login, logout

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login_route(payload: LoginRequest, request: Request):
    return login(request, payload.username, payload.password)


@router.post("/logout")
def logout_route(session_token: str = Depends(get_session_token)):
    logout(session_token)
    return {"ok": True}
