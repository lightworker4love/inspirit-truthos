from __future__ import annotations

import httpx
import pytest

from packages.hermes_truthos_bridge import TruthOSHook
from packages.hermes_truthos_bridge.truthos_client import TruthOSClient


class FakeResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class FakeAsyncClient:
    def __init__(self, post_response=None, get_response=None, exc=None, timeout=None):
        self.post_response = post_response
        self.get_response = get_response
        self.exc = exc
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *args, **kwargs):
        if self.exc:
            raise self.exc
        return self.post_response or FakeResponse(200, {})

    async def get(self, *args, **kwargs):
        if self.exc:
            raise self.exc
        return self.get_response or FakeResponse(200, {})


@pytest.mark.asyncio
async def test_truthos_client_returns_none_on_timeout(monkeypatch):
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda timeout: FakeAsyncClient(exc=httpx.TimeoutException("timeout")),
    )
    result = await TruthOSClient().query("hello", "user-1", "session-1")
    assert result is None


@pytest.mark.asyncio
async def test_truthos_client_returns_none_on_connection_error(monkeypatch):
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda timeout: FakeAsyncClient(exc=httpx.ConnectError("offline")),
    )
    result = await TruthOSClient().query("hello", "user-1", "session-1")
    assert result is None


def test_enrich_response_with_truth_context():
    hook = TruthOSHook()
    enriched = hook.enrich_response(
        "Hermes response",
        {
            "truth_map": {
                "verified_truth": True,
                "truth_score": 0.85,
                "truth_properties": ["objectivity"],
            },
        },
    )
    assert enriched["truth_layer"]["verified"] is True
    assert enriched["truth_layer"]["score"] == 0.85


def test_enrich_response_with_none_context():
    hook = TruthOSHook()
    enriched = hook.enrich_response("Hermes response", None)
    assert enriched["response"] == "Hermes response"
    assert enriched["truth_layer"] is None
    assert enriched["_truth_degraded"] is False


def test_enrich_response_marks_truth_degraded_on_guardrail_context():
    hook = TruthOSHook()
    enriched = hook.enrich_response(
        "Hermes response",
        {"_truth_degraded": True, "_truth_degraded_reason": "timeout"},
    )
    assert enriched["response"] == "Hermes response"
    assert enriched["truth_layer"] is None
    assert enriched["_truth_degraded"] is True


def test_enrich_response_includes_guidance_when_present():
    hook = TruthOSHook()
    truth_context = {
        "truth_map": {"verified_truth": True},
        "guidance": "Ask one concrete question.",
        "relevant_principles": ["truth-001"],
    }
    enriched = hook.enrich_response("Hermes response", truth_context)
    assert enriched["guidance_overlay"] == truth_context["guidance"]


@pytest.mark.asyncio
async def test_get_soul_context_extracts_key_fields(monkeypatch):
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda timeout: FakeAsyncClient(
            get_response=FakeResponse(
                200,
                {
                    "evolution_stage": "understanding",
                    "recurring_patterns": [
                        {"description": "Control pattern"},
                        {"id": "avoidance"},
                    ],
                    "top_blind_spots": [
                        {"title": "Known but not lived", "resolutionstatus": "active"}
                    ],
                    "active_lessons": [{"principle_id": "truth-001"}],
                },
            )
        ),
    )
    soul_ctx = await TruthOSHook().get_soul_context("user-1")
    assert soul_ctx["evolution_stage"] == "understanding"
    assert soul_ctx["active_patterns"] == ["Control pattern", "avoidance"]
    assert soul_ctx["active_blind_spots"] == ["Known but not lived"]
