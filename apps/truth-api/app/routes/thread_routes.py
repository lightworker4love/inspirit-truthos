from fastapi import APIRouter, Depends

from app.core.security import get_session_token
from app.models.thread_models import CreateThreadRequest, CreateThreadResponse, ThreadResponse
from app.services.auth_service import get_current_user
from app.services.policy_service import resolve_model
from app.services.thread_service import create_role_bound_thread, get_thread_with_entries, get_accessible_thread
from app.services.audit_service import log_event

router = APIRouter()


@router.post("", response_model=CreateThreadResponse)
def create_thread_route(payload: CreateThreadRequest, session_token: str = Depends(get_session_token)):
    user = get_current_user(session_token)
    resolved = resolve_model(user["role"], payload.mode)
    thread_id = create_role_bound_thread(user, resolved, payload.title)
    log_event(user["id"], "thread_created", "success", "thread", thread_id, resolved["model_id"])
    return {
        "threadId": thread_id,
        "mode": resolved["mode"],
        "resolvedModelId": resolved["model_id"],
    }


@router.get("/{thread_id}", response_model=ThreadResponse)
def get_thread_route(thread_id: str, session_token: str = Depends(get_session_token)):
    user = get_current_user(session_token)
    thread = get_accessible_thread(user, thread_id)
    _, entries = get_thread_with_entries(thread_id)
    return {
        "threadId": thread["id"],
        "mode": thread["selected_mode_key"],
        "resolvedModelId": thread["resolved_model_id"],
        "title": thread["title"],
        "entries": [
            {
                "id": row["id"],
                "speaker": row["speaker"],
                "content": row["content"],
                "createdAt": row["created_at"],
            }
            for row in entries
        ],
    }
