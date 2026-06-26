from fastapi import APIRouter, Depends

from app.core.security import get_session_token
from app.models.chat_models import ChatRequest, ChatResponse
from app.services.auth_service import get_current_user
from app.services.policy_service import resolve_model, load_active_prompt
from app.services.thread_service import get_accessible_thread, append_message
from app.services.openclaw_adapter import chat as upstream_chat
from app.services.audit_service import log_event
from app.services import memory_service, memory_policy
from app.services.memory_types import MemoryReadRequest, MemoryWriteRequest

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, response_model_exclude_none=True)
def chat_route(payload: ChatRequest, session_token: str = Depends(get_session_token)):
    user = get_current_user(session_token)
    thread = get_accessible_thread(user, payload.threadId)

    mode = payload.mode or thread["selected_mode_key"]
    resolved = resolve_model(user["role"], mode)
    system_prompt = load_active_prompt(user["role"])

    # --- D: Identity governance -----------------------------------------------
    # user_id for memory is ALWAYS derived from the verified auth session.
    # Client-supplied user_id values are never used here.
    memory_user_id = memory_policy.resolve_user_id(auth_user_id=user["id"])
    effective_scope = memory_policy.resolve_scope(payload.memory_scope)

    # --- Phase 2 hook: memory retrieval (before prompt assembly) --------------
    # No-op when MEMORY_LONGTERM_ENABLED=false or MEMORY_READ_ENABLED=false
    # or effective_scope="none".  Failures are silenced when fail-open=true.
    mem_read = memory_service.retrieve(
        MemoryReadRequest(
            user_id=memory_user_id,
            thread_id=thread["id"],
            query=payload.message,
            scope=effective_scope,  # type: ignore[arg-type]
        )
    )
    memory_context_block = memory_service.format_context_block(mem_read.memories)

    # Build system messages; prepend memory context when present.
    system_messages = [{"role": "system", "content": system_prompt}]
    if memory_context_block:
        system_messages.append({"role": "system", "content": memory_context_block})

    upstream_payload = {
        "model": resolved["model_id"],
        "messages": [
            *system_messages,
            {"role": "user", "content": payload.message},
        ],
    }

    append_message(thread["id"], "user", payload.message)
    result = upstream_chat(upstream_payload)
    reply = result["content"] or ""

    append_message(thread["id"], "assistant", reply)

    # --- Phase 2 hook: memory write (after response generation) ---------------
    # No-op when MEMORY_LONGTERM_ENABLED=false or MEMORY_WRITE_ENABLED=false
    # or effective_scope="none" or reply is too short.  Never raises.
    memory_service.store(
        MemoryWriteRequest(
            user_id=memory_user_id,
            thread_id=thread["id"],
            user_message=payload.message,
            assistant_reply=reply,
            scope=effective_scope,  # type: ignore[arg-type]
            metadata={"mode": resolved["mode"], "model_id": resolved["model_id"]},
        )
    )

    log_event(
        user["id"],
        "chat_response_success",
        "success",
        "thread",
        thread["id"],
        resolved["model_id"],
        {"mode": resolved["mode"], "memory_scope": effective_scope},
    )

    return {
        "threadId": thread["id"],
        "resolvedModelId": resolved["model_id"],
        "reply": reply,
        "memory_resolved": None if effective_scope == "none" else effective_scope,
    }
