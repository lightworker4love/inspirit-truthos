from __future__ import annotations

import os
from urllib.parse import urljoin

import httpx

from app.config import get_embedding_model

OPENAI_FALLBACK_PROVIDER = "openai"
OPENCLAW_PROVIDER = "openclaw"


def _models_url(base_url: str) -> str:
    normalized = base_url.rstrip("/") + "/"
    if normalized.endswith("/v1/"):
        return urljoin(normalized, "models")
    return urljoin(normalized, "v1/models")


def check_embedding_gateway() -> dict[str, bool | str]:
    base_url = os.getenv("OPENAI_BASE_URL", "").strip()
    if not base_url:
        return {"gateway": False, "provider": OPENAI_FALLBACK_PROVIDER}

    headers: dict[str, str] = {}
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        response = httpx.get(_models_url(base_url), headers=headers, timeout=5.0)
        if response.status_code != 200:
            return {"gateway": False, "provider": OPENAI_FALLBACK_PROVIDER}
        payload = response.json()
    except Exception:
        return {"gateway": False, "provider": OPENAI_FALLBACK_PROVIDER}

    model = get_embedding_model()
    models = payload.get("data", [])
    available = any(item.get("id") == model for item in models if isinstance(item, dict))
    if not available:
        return {"gateway": False, "provider": OPENAI_FALLBACK_PROVIDER}

    return {"gateway": True, "provider": OPENCLAW_PROVIDER}
