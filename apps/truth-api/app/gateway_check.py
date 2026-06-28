from __future__ import annotations

import os
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import urlunparse

import httpx

from app.config import get_embedding_model
from app.config import get_embedding_provider

OPENAI_FALLBACK_PROVIDER = "openai"
OPENCLAW_PROVIDER = "openclaw"
OLLAMA_LOCAL_PROVIDER = "ollama-local"
AUTO_PROVIDER = "auto"
ALLOWED_SCHEMES = {"http", "https"}
BLOCKED_HOSTS = {
    "0.0.0.0",
    "169.254.169.254",
}
_ALLOWED_GATEWAY_HOSTS = {
    "api.openai.com",
    "host.docker.internal",
    "localhost",
    "ollama",
    "127.0.0.1",
    "::1",
} - BLOCKED_HOSTS


def sanitize_url(url: str) -> str:
    candidate = url.strip().rstrip("/")
    parsed = urlparse(candidate)
    hostname = (parsed.hostname or "").lower()
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError("OPENAI_BASE_URL must use http or https")
    if not hostname:
        raise ValueError("OPENAI_BASE_URL must include a hostname")
    if parsed.username or parsed.password:
        raise ValueError("OPENAI_BASE_URL must not embed credentials")
    if hostname in BLOCKED_HOSTS or hostname not in _ALLOWED_GATEWAY_HOSTS:
        raise ValueError("OPENAI_BASE_URL host is not allowlisted")
    netloc = hostname
    if parsed.port is not None:
        netloc = f"{netloc}:{parsed.port}"
    return urlunparse((parsed.scheme, netloc, parsed.path, "", parsed.query, ""))


def _validated_gateway_base_url(base_url: str) -> str:
    return sanitize_url(base_url)


def _models_url(base_url: str) -> str:
    normalized = base_url.rstrip("/") + "/"
    if normalized.endswith("/v1/"):
        return urljoin(normalized, "models")
    return urljoin(normalized, "v1/models")


def _embeddings_url(base_url: str) -> str:
    normalized = base_url.rstrip("/") + "/"
    if normalized.endswith("/v1/"):
        return urljoin(normalized, "embeddings")
    return urljoin(normalized, "v1/embeddings")


def _request_headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _fetch_models(base_url: str, headers: dict[str, str]) -> tuple[int, list[str]]:
    models_url = sanitize_url(_models_url(base_url))
    response = httpx.get(models_url, headers=headers, timeout=5.0)
    if response.status_code != 200:
        return response.status_code, []

    payload = response.json()
    models = payload.get("data", [])
    return response.status_code, [
        item.get("id", "")
        for item in models
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    ]


def _embedding_probe_available(base_url: str, headers: dict[str, str], model: str) -> bool:
    embeddings_url = sanitize_url(_embeddings_url(base_url))
    probe = httpx.post(
        embeddings_url,
        headers=headers | {"Content-Type": "application/json"},
        json={"model": model, "input": "gateway health probe"},
        timeout=10.0,
    )
    return probe.status_code == 200


def _infer_provider(base_url: str, model_ids: list[str]) -> str:
    parsed = urlparse(base_url)
    hostname = (parsed.hostname or "").lower()
    normalized_base = base_url.lower()
    if hostname == "api.openai.com" or "api.openai.com" in normalized_base:
        return OPENAI_FALLBACK_PROVIDER
    if parsed.port == 11434 or hostname == "ollama" or any(model.endswith(":latest") for model in model_ids):
        return OLLAMA_LOCAL_PROVIDER
    return OPENCLAW_PROVIDER


def detect_embedding_provider() -> dict[str, bool | str]:
    base_url = os.getenv("OPENAI_BASE_URL", "").strip()
    configured_provider = get_embedding_provider()
    if not base_url:
        return {"available": False, "gateway": False, "provider": OPENAI_FALLBACK_PROVIDER}
    try:
        base_url = sanitize_url(base_url)
    except ValueError:
        fallback_provider = configured_provider if configured_provider != AUTO_PROVIDER else OPENAI_FALLBACK_PROVIDER
        return {"available": False, "gateway": False, "provider": fallback_provider}

    headers = _request_headers()
    model = get_embedding_model()

    try:
        status_code, model_ids = _fetch_models(base_url, headers)
    except Exception:
        fallback_provider = configured_provider if configured_provider != AUTO_PROVIDER else OPENAI_FALLBACK_PROVIDER
        return {"available": False, "gateway": False, "provider": fallback_provider}

    if status_code != 200:
        fallback_provider = configured_provider if configured_provider != AUTO_PROVIDER else OPENAI_FALLBACK_PROVIDER
        return {"available": False, "gateway": False, "provider": fallback_provider}

    resolved_provider = configured_provider if configured_provider != AUTO_PROVIDER else _infer_provider(base_url, model_ids)
    available = model in model_ids
    if not available:
        try:
            available = _embedding_probe_available(base_url, headers, model)
        except Exception:
            available = False

    if not available:
        return {"available": False, "gateway": False, "provider": resolved_provider}

    return {
        "available": True,
        "gateway": resolved_provider == OPENCLAW_PROVIDER,
        "provider": resolved_provider,
    }


def check_embedding_gateway() -> dict[str, bool | str]:
    detection = detect_embedding_provider()
    return {
        "gateway": bool(detection["gateway"]),
        "provider": str(detection["provider"]),
    }
