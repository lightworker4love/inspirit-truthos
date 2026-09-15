from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "apps/truth-api"))

from app.main import app as truth_api_app
from apps.hermes_agent.api import app as hermes_agent_app


TRUTHOS_WEB_ORIGIN = "https://truthos-web-production.up.railway.app"
UNTRUSTED_ORIGIN = "https://example.invalid"


def test_truth_api_allows_truthos_web_origin() -> None:
    response = TestClient(truth_api_app).get(
        "/health",
        headers={"Origin": TRUTHOS_WEB_ORIGIN},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == TRUTHOS_WEB_ORIGIN


def test_truth_api_accepts_soul_map_preflight_from_truthos_web() -> None:
    response = TestClient(truth_api_app).options(
        "/api/soul-map/canary",
        headers={
            "Origin": TRUTHOS_WEB_ORIGIN,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == TRUTHOS_WEB_ORIGIN
    assert "GET" in response.headers["access-control-allow-methods"]
    assert "Content-Type" in response.headers["access-control-allow-headers"]


def test_truth_api_rejects_untrusted_origin() -> None:
    response = TestClient(truth_api_app).get(
        "/health",
        headers={"Origin": UNTRUSTED_ORIGIN},
    )

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_hermes_agent_accepts_chat_preflight_from_truthos_web() -> None:
    response = TestClient(hermes_agent_app).options(
        "/chat",
        headers={
            "Origin": TRUTHOS_WEB_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == TRUTHOS_WEB_ORIGIN
    assert "POST" in response.headers["access-control-allow-methods"]
    assert "Content-Type" in response.headers["access-control-allow-headers"]


def test_hermes_agent_rejects_untrusted_origin() -> None:
    response = TestClient(hermes_agent_app).options(
        "/chat",
        headers={
            "Origin": UNTRUSTED_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
