from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from urllib import error, request

from fastapi import FastAPI

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/truth-api"))

from app.models import BridgeQueryRequest

TRUTHOS_INTERNAL_URL = os.getenv("TRUTHOS_INTERNAL_URL", "http://localhost:18000").rstrip("/")

app = FastAPI(title="TruthOS OpenClaw Bridge", version="0.1.0")


def _post_truthos(payload: dict, timeout: float = 3.0) -> dict:
    endpoint = f"{TRUTHOS_INTERNAL_URL}/api/truth/query"
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


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
    except (TimeoutError, error.URLError, error.HTTPError, ValueError):
        return {"mirror": None, "error": "TruthOS unavailable"}


@app.post("/bridge/truth/query")
async def bridge_truth_query(payload: BridgeQueryRequest) -> dict:
    return await query_truthos(
        user_id=payload.user_id,
        session_id=payload.session_id,
        message=payload.message,
        mode=payload.mode,
    )
