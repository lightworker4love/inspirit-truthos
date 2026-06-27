from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.parse import urlunparse

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/truth-api"))

ALLOWED_SCHEMES = {"http", "https"}
BLOCKED_HOSTS = {
    "0.0.0.0",
    "169.254.169.254",
}
_ALLOWED_TRUTHOS_HOSTS = {"localhost", "127.0.0.1", "::1"} - BLOCKED_HOSTS


def sanitize_internal_url(raw_url: str) -> str:
    candidate = raw_url.strip().rstrip("/")
    parsed = urlparse(candidate)
    hostname = (parsed.hostname or "").lower()
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError("TRUTHOS_INTERNAL_URL must use http or https")
    if not hostname:
        raise ValueError("TRUTHOS_INTERNAL_URL must include a hostname")
    if parsed.username or parsed.password:
        raise ValueError("TRUTHOS_INTERNAL_URL must not embed credentials")
    if hostname in BLOCKED_HOSTS or hostname not in _ALLOWED_TRUTHOS_HOSTS:
        raise ValueError("TRUTHOS_INTERNAL_URL host is not allowlisted")
    netloc = hostname
    if parsed.port is not None:
        netloc = f"{netloc}:{parsed.port}"
    return urlunparse((parsed.scheme, netloc, parsed.path, "", parsed.query, ""))


def _validated_truthos_internal_url(raw_url: str) -> str:
    return sanitize_internal_url(raw_url)


app = FastAPI(title="TruthOS OpenClaw Bridge", version="0.1.0")


class BridgeQueryRequest(BaseModel):
    user_id: str
    session_id: str | None = None
    message: str
    mode: str = "mentor"


def _truthos_internal_url() -> str:
    raw_url = os.getenv("TRUTHOS_INTERNAL_URL", "http://localhost:18000")
    return sanitize_internal_url(raw_url)


def _post_truthos(payload: dict, timeout: float = 3.0) -> dict:
    endpoint = sanitize_internal_url(f"{_truthos_internal_url()}/api/truth/query")
    response = httpx.post(
        endpoint,
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


async def query_truthos(
    user_id: str,
    session_id: str | None,
    message: str,
    mode: str = "mentor",
) -> dict:
    payload = {
        "user_id": user_id,
        "session_id": session_id,
        "message": message,
        "mode": mode,
    }
    try:
        return await asyncio.to_thread(_post_truthos, payload, 3.0)
    except (TimeoutError, httpx.HTTPError, ValueError, json.JSONDecodeError):
        return {"mirror": None, "error": "TruthOS unavailable"}


@app.post("/bridge/truth/query")
async def bridge_truth_query(payload: BridgeQueryRequest) -> dict:
    return await query_truthos(
        user_id=payload.user_id,
        session_id=payload.session_id,
        message=payload.message,
        mode=payload.mode,
    )
