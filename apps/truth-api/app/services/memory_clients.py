"""
memory_clients.py
Phase 1/2 scaffolding — thin HTTP wrappers around Mem0 and Qdrant.

These clients are intentionally minimal:
- They are never called unless MEMORY_LONGTERM_ENABLED=true in settings.
- All network calls go through the governed memory_service facade.
- No authentication escalation or credential injection occurs here.
- No Qdrant calls are made directly from truth-api in Phase 1/2;
  Qdrant is accessed exclusively through Mem0.  Direct Qdrant client is
  a placeholder for Phase 4 (LanceDB methodology lane planning).

TODO (Phase 1 activation):
  - Pin mem0ai SDK version in requirements.txt / pyproject.toml.
  - Verify Mem0 health endpoint path once image tag is locked.
  - Replace placeholder httpx calls with mem0 SDK calls when available.
"""

from __future__ import annotations

import httpx

from app.core.config import settings

_TIMEOUT = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)


def _mem0_headers() -> dict[str, str]:
    h = {"Content-Type": "application/json"}
    if settings.mem0_api_key:
        h["Authorization"] = f"Bearer {settings.mem0_api_key}"
    return h


def mem0_health() -> bool:
    """Return True if Mem0 is reachable.  Never raises."""
    if not settings.mem0_base_url:
        return False
    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            r = client.get(f"{settings.mem0_base_url}/health")
            return r.status_code < 400
    except Exception:
        return False


def mem0_search(*, user_id: str, query: str, top_k: int) -> list[str]:
    """
    Retrieve relevant memories from Mem0 for this user+query.

    Returns a list of plain-text memory strings.
    Raises RuntimeError on network/API failure (caller should handle).

    TODO (Phase 1 activation): Replace with mem0 Python SDK call:
        from mem0 import MemoryClient
        client = MemoryClient(api_key=settings.mem0_api_key, base_url=...)
        results = client.search(query, user_id=user_id, limit=top_k)
    """
    url = f"{settings.mem0_base_url}/v1/memories/search"
    payload = {"query": query, "user_id": user_id, "limit": top_k}
    with httpx.Client(timeout=_TIMEOUT) as client:
        r = client.post(url, json=payload, headers=_mem0_headers())
        r.raise_for_status()
    data = r.json()
    # Mem0 API returns {"results": [{"memory": "...", ...}, ...]}
    results = data.get("results") or []
    return [item.get("memory", "") for item in results if item.get("memory")]


def mem0_add(
    *,
    user_id: str,
    messages: list[dict],
    metadata: dict | None = None,
) -> bool:
    """
    Persist a conversation turn to Mem0.

    Returns True on success.  Raises RuntimeError on failure.

    TODO (Phase 1 activation): Replace with mem0 Python SDK:
        client.add(messages, user_id=user_id, metadata=metadata or {})
    """
    url = f"{settings.mem0_base_url}/v1/memories"
    payload: dict = {"messages": messages, "user_id": user_id}
    if metadata:
        payload["metadata"] = metadata
    with httpx.Client(timeout=_TIMEOUT) as client:
        r = client.post(url, json=payload, headers=_mem0_headers())
        r.raise_for_status()
    return True
