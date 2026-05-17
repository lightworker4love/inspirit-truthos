from __future__ import annotations

import os
import sys
import time
import uuid
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "apps/truth-api"))

from scripts.seed_import import run_migration


HERMES_URL = os.getenv("HERMES_URL", "http://localhost:8001")
TRUTHOS_URL = os.getenv("TRUTHOS_URL", "http://localhost:18000")


def _client(tmp_path, monkeypatch) -> TestClient:
    db_path = tmp_path / "truthos.db"
    monkeypatch.setenv("TRUTHOS_DB_PATH", str(db_path))
    monkeypatch.setenv("SQLITE_DB_PATH", str(db_path))
    run_migration()
    from app.main import app

    return TestClient(app)


def test_soul_map_auto_created_on_first_query(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)
    new_user = f"test-new-{uuid.uuid4().hex[:8]}"

    response = client.post(
        "/api/truth/query",
        json={
            "query": "I always give up when things get hard",
            "user_id": new_user,
            "session_id": "test-session",
        },
    )

    assert response.status_code == 200
    soul_map = client.get(f"/api/soul-map/{new_user}")
    assert soul_map.status_code == 200
    body = soul_map.json()
    assert body["status"] == "active"
    assert body["evolution_stage"] == "awakening"
    assert body["updated_at"]


def test_query_returns_soul_map_delta(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)

    response = client.post(
        "/api/truth/query",
        json={
            "query": "test delta tracking",
            "user_id": "test-delta-user",
            "session_id": "test-delta-session",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["soul_map_updated"] is True
    assert "soul_map_delta" in body
    assert "new_patterns" in body["soul_map_delta"]


def test_get_or_create_soul_map_is_idempotent(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)
    user = f"test-idempotent-{uuid.uuid4().hex[:8]}"

    first = client.post(
        "/api/truth/query",
        json={"query": "test", "user_id": user, "session_id": "s1"},
    )
    second = client.post(
        "/api/truth/query",
        json={"query": "test again", "user_id": user, "session_id": "s1"},
    )
    soul_map = client.get(f"/api/soul-map/{user}")

    assert first.status_code == 200
    assert second.status_code == 200
    assert soul_map.status_code == 200
    assert soul_map.json()["user_id"] == user
    assert soul_map.json()["evolution_stage"] == "awakening"


@pytest.mark.skipif(
    os.getenv("RUN_E2E") != "true",
    reason="Set RUN_E2E=true to run Docker-backed Hermes conversation checks.",
)
def test_hermes_chat_triggers_soul_map():
    user = f"test-hermes-{uuid.uuid4().hex[:8]}"
    response = httpx.post(
        f"{HERMES_URL}/chat",
        json={
            "user_id": user,
            "session_id": "hermes-test",
            "message": "I keep repeating the same mistakes in relationships",
        },
        timeout=15,
    )

    assert response.status_code == 200
    assert "response" in response.json()


@pytest.mark.skipif(
    os.getenv("RUN_E2E") != "true",
    reason="Set RUN_E2E=true to run Docker-backed Live Monitor checks.",
)
def test_live_monitor_shows_session_after_chat():
    user = f"test-live-{uuid.uuid4().hex[:8]}"
    httpx.post(
        f"{HERMES_URL}/chat",
        json={
            "user_id": user,
            "session_id": "live-test-session",
            "message": "testing live monitor",
        },
        timeout=10,
    )
    time.sleep(2)

    response = httpx.get(f"{TRUTHOS_URL}/api/sessions/recent?minutes=2", timeout=5)

    assert response.status_code == 200
    assert "sessions" in response.json()
