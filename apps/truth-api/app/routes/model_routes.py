from fastapi import APIRouter, Depends

from app.core.security import get_session_token
from app.models.policy_models import AllowedModesResponse
from app.services.auth_service import get_current_user
from app.services.policy_service import list_allowed_modes

router = APIRouter()


@router.get("/allowed", response_model=AllowedModesResponse)
def allowed_models(session_token: str = Depends(get_session_token)):
    user = get_current_user(session_token)
    return {"modes": list_allowed_modes(user["role"])}
