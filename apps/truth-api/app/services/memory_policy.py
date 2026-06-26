"""
memory_policy.py
Phase 1/2 scaffolding — scope gating and identity governance rules.

ALL scope validation for memory operations funnels through this module.
Callers must not implement scope logic themselves.

Governance rules (must not be weakened without explicit review):
1. Scope is resolved server-side; client-supplied scope is a request, not a grant.
2. MEMORY_USER_ID_SOURCE=auth (default) means user_id MUST come from
   get_current_user(), never from client payload or secondme-proxy metadata.
3. Proxy trust is off by default (MEMORY_TRUST_PROXY_USER_ID=false).
4. experiment and session write scopes have separate enabling flags.
5. All resolve decisions are logged by the caller via audit_service.
"""

from __future__ import annotations

from app.core.config import settings
from app.models.chat_models import MemoryScope


# ---- Public contracts -------------------------------------------------------

def resolve_scope(requested: str | None) -> str:
    """
    Resolve the effective memory scope for a chat turn.

    - If memory is globally disabled, always returns "none".
    - If requested scope is not in MEMORY_ALLOWED_SCOPES, falls back to
      MEMORY_DEFAULT_SCOPE (no error raised — fail-safe).
    - experiment scope is additionally gated by MEMORY_EXPERIMENT_SCOPE_ENABLED.
    - session scope write is additionally gated by MEMORY_SESSION_SCOPE_WRITE_ENABLED.
    """
    if not settings.memory_longterm_enabled:
        return "none"

    allowed = {s.strip() for s in settings.memory_allowed_scopes.split(",")}
    effective = requested if requested in allowed else settings.memory_default_scope

    if effective == "experiment" and not settings.memory_experiment_scope_enabled:
        effective = settings.memory_default_scope

    return effective


def is_read_permitted(scope: str) -> bool:
    """Return True when a memory read should proceed for this scope."""
    if scope == "none":
        return False
    return settings.memory_read_enabled


def is_write_permitted(scope: str, content_length: int) -> bool:
    """Return True when a memory write should proceed for this scope."""
    if scope == "none":
        return False
    if not settings.memory_write_enabled:
        return False
    if scope == "session" and not settings.memory_session_scope_write_enabled:
        return False
    if content_length < settings.memory_write_min_chars:
        return False
    return True


def resolve_user_id(*, auth_user_id: str, proxy_user_id: str | None = None) -> str:
    """
    Return the canonical user_id to use for all memory operations.

    MEMORY_USER_ID_SOURCE=auth (default): always returns auth_user_id.

    MEMORY_USER_ID_SOURCE=proxy: returns proxy_user_id only when
    MEMORY_TRUST_PROXY_USER_ID=true AND proxy_user_id is non-empty.
    Falls back to auth_user_id otherwise.

    Callers must never pass client-supplied user_id directly as proxy_user_id
    without first verifying the request carries a valid internal token.
    """
    if (
        settings.memory_user_id_source == "proxy"
        and settings.memory_trust_proxy_user_id
        and proxy_user_id
        and proxy_user_id.strip()
    ):
        return proxy_user_id.strip()
    return auth_user_id


def assert_scope_valid(scope: str) -> None:
    """Raise ValueError if scope is not in the allowed set.  Used by tests."""
    allowed = {s.strip() for s in settings.memory_allowed_scopes.split(",")}
    if scope not in allowed:
        raise ValueError(f"scope '{scope}' not in MEMORY_ALLOWED_SCOPES ({allowed})")
