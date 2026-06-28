from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_session_token
from app.repositories.audit_repo import list_audit_logs
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("/audit")
def admin_audit(session_token: str = Depends(get_session_token), limit: int = 100):
    user = get_current_user(session_token)
    if user["role"] != "admin_builder":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    rows = list_audit_logs(limit=limit)
    return {
        "items": [
            {
                "id": row["id"],
                "actorUserId": row["actor_user_id"],
                "action": row["action"],
                "targetType": row["target_type"],
                "targetId": row["target_id"],
                "resolvedModelId": row["resolved_model_id"],
                "result": row["result"],
                "metadataJson": row["metadata_json"],
                "createdAt": row["created_at"],
            }
            for row in rows
        ]
    }
