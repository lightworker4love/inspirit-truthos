from __future__ import annotations

import json
import os
from urllib import request

import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_E2E") != "true",
    reason="Set RUN_E2E=true to run Docker-backed integration tests.",
)


TRUTHOS_URL = os.getenv("TRUTHOS_URL", "http://localhost:18000").rstrip("/")
HERMES_URL = os.getenv("HERMES_URL", "http://localhost:8001").rstrip("/")


def test_hermes_chat_writes_truthos_session() -> None:
    payload = {
        "user_id": "e2e-user",
        "session_id": "e2e-session",
        "message": "I know I should trust the process, but I keep forcing outcomes.",
    }
    chat = _post_json(f"{HERMES_URL}/chat", payload)

    assert chat["session_id"] == "e2e-session"
    assert "response" in chat

    stats = _get_json(f"{TRUTHOS_URL}/api/sessions/stats/summary")
    assert "sessions_last_1h" in stats
    assert "queries_last_1h" in stats


def test_live_monitor_session_endpoints_shape() -> None:
    recent = _get_json(f"{TRUTHOS_URL}/api/sessions/recent?minutes=10&limit=10")
    assert "sessions" in recent
    assert "count" in recent

    scores = _get_json(f"{TRUTHOS_URL}/api/sessions/e2e-session/truth-scores")
    assert scores["session_id"] == "e2e-session"
    assert "evaluations" in scores


def _post_json(url: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_json(url: str) -> dict:
    with request.urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))
