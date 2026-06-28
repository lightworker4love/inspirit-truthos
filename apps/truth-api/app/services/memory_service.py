"""
memory_service.py
Phase 1/2 scaffolding — governed read/write facade for long-term memory.

This is the ONLY module that calls memory_clients.  All memory I/O in
truth-api must go through retrieve() and store() here.

Design rules:
- retrieve() is fail-open by default (MEMORY_FAIL_OPEN_READ=true).
  A failed retrieval never aborts the chat response.
- store() is fail-open by default (MEMORY_FAIL_OPEN_WRITE=true).
  A failed write never aborts the chat response.
- Both functions no-op when feature flags are false (no network calls).
- user_id is always resolved via memory_policy.resolve_user_id() before
  being passed to the wire client.

No autonomous writeback of blueprint or governance data happens here.
"""

from __future__ import annotations

import logging

from app.core.config import settings
from app.services import memory_clients, memory_policy
from app.services.memory_types import (
    MemoryReadRequest,
    MemoryReadResult,
    MemoryWriteRequest,
    MemoryWriteResult,
)

logger = logging.getLogger(__name__)


def retrieve(req: MemoryReadRequest) -> MemoryReadResult:
    """
    Retrieve relevant long-term memories to inject before prompt assembly.

    Returns MemoryReadResult.skipped=True when:
    - MEMORY_LONGTERM_ENABLED=false, or
    - MEMORY_READ_ENABLED=false, or
    - resolved scope is "none".

    Never raises; failures are captured in result.error when fail-open.

    Note: resolve_scope() is called here even though the caller (chat_routes)
    has already resolved the scope.  This is intentional: memory_service is
    designed to be callable directly (e.g., from future services that bypass
    chat_routes), and each boundary must enforce its own policy.  The call is
    idempotent — resolve_scope("none") returns "none", and a resolved scope
    like "default" resolves to itself.
    """
    scope = memory_policy.resolve_scope(req.scope)
    if not memory_policy.is_read_permitted(scope):
        return MemoryReadResult(skipped=True, scope_used=scope)

    if not settings.mem0_base_url:
        return MemoryReadResult(
            skipped=True,
            scope_used=scope,
            error="MEM0_BASE_URL not configured",
        )

    try:
        raw_memories = memory_clients.mem0_search(
            user_id=req.user_id,
            query=req.query,
            top_k=req.top_k,
        )
        # Enforce character budget
        out: list[str] = []
        budget = req.max_chars
        for m in raw_memories:
            chunk = m[:budget]
            out.append(chunk)
            budget -= len(chunk)
            if budget <= 0:
                break
        return MemoryReadResult(memories=out, scope_used=scope)
    except Exception as exc:
        msg = f"memory retrieve failed: {exc}"
        logger.warning(msg)
        if settings.memory_fail_open_read:
            return MemoryReadResult(skipped=True, scope_used=scope, error=msg)
        raise


def store(req: MemoryWriteRequest) -> MemoryWriteResult:
    """
    Persist a conversation turn to long-term memory after response generation.

    Returns MemoryWriteResult.skipped=True when:
    - MEMORY_LONGTERM_ENABLED=false, or
    - MEMORY_WRITE_ENABLED=false, or
    - resolved scope is "none", or
    - combined content is shorter than MEMORY_WRITE_MIN_CHARS.

    Never raises; failures are captured in result.error when fail-open.

    Note: resolve_scope() is re-evaluated here for the same reason as
    retrieve() — defense-in-depth for direct callers.  It is idempotent
    on already-resolved scope values.
    """
    scope = memory_policy.resolve_scope(req.scope)
    combined_len = len(req.user_message) + len(req.assistant_reply)
    if not memory_policy.is_write_permitted(scope, combined_len):
        return MemoryWriteResult(skipped=True)

    if not settings.mem0_base_url:
        return MemoryWriteResult(
            skipped=True,
            error="MEM0_BASE_URL not configured",
        )

    messages = [
        {"role": "user", "content": req.user_message},
        {"role": "assistant", "content": req.assistant_reply},
    ]
    # Metadata: only non-content governance fields.
    # MEMORY_AUDIT_REDACT_CONTENT=true means user/assistant text is NOT
    # included in metadata; it travels in the messages payload only.
    meta: dict = {
        "thread_id": req.thread_id,
        "scope": scope,
        **{k: v for k, v in req.metadata.items() if k not in ("user_message", "reply")},
    }

    try:
        memory_clients.mem0_add(
            user_id=req.user_id,
            messages=messages,
            metadata=meta,
        )
        return MemoryWriteResult(stored=True)
    except Exception as exc:
        msg = f"memory store failed: {exc}"
        logger.warning(msg)
        if settings.memory_fail_open_write:
            return MemoryWriteResult(skipped=True, error=msg)
        raise


def format_context_block(memories: list[str]) -> str:
    """
    Format retrieved memory strings into an injectable system-message block.

    Returns an empty string when memories is empty.
    """
    if not memories:
        return ""
    items = "\n".join(f"- {m.strip()}" for m in memories if m.strip())
    if not items:
        return ""
    return f"## Relevant Memory Context\n{items}"
