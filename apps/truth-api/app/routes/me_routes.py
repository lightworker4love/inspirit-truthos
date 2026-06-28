from fastapi import APIRouter, Depends

from app.core.security import get_session_token
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("/me")
def me(session_token: str = Depends(get_session_token)):
    user = get_current_user(session_token)
    capabilities = {
        "canViewAdminAudit": user["role"] == "admin_builder",
        "canEditPromptVersions": user["role"] == "admin_builder",
    }
    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "displayName": user["displayName"],
        "capabilities": capabilities,
    }
