from __future__ import annotations

from contextlib import contextmanager
import logging
from pathlib import Path
import sys
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

_TEST_DIR = Path(__file__).resolve().parent
_TRUTH_API_ROOT = _TEST_DIR.parent
if str(_TRUTH_API_ROOT) not in sys.path:
    sys.path.insert(0, str(_TRUTH_API_ROOT))

import app.case_resolver as case_resolver_module
import app.main as main_module
from app.case_models import CaseProfile
from app.main import app


@contextmanager
def _healthy_connection():
    class _Conn:
        def execute(self, _sql: str):
            return 1

        def commit(self) -> None:
            return None

    yield _Conn()


def _sample_puzzles() -> list[dict[str, str]]:
    return [
        {
            "id": "pz-install-1",
            "dimension_code": "relationship",
            "principle_code": "REL_001",
            "title": "Boundary Drift",
            "statement": "trying to help becomes pressure",
            "misbelief": "If I help more, conflict will disappear",
            "truth_reframe": "Support is different from rescue",
            "coach_prompt": "What responsibility belongs to the other person?",
        }
    ]


def _patch_query_runtime(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(case_resolver_module, "CASE_STORE_DIR", tmp_path)
    monkeypatch.setattr(main_module, "connect_db", lambda: _healthy_connection())
    monkeypatch.setattr(main_module, "_write_session_memory", lambda **_kwargs: None)
    monkeypatch.setattr(main_module, "get_embedding_mode", lambda: "sqlite")
    monkeypatch.setattr(main_module, "classify_dimensions", lambda _message: ["relationship"])
    monkeypatch.setattr(
        main_module,
        "retrieve_puzzles",
        lambda _message, dimensions, limit: {
            "puzzles": _sample_puzzles(),
            "retrieval_mode": "sqlite",
        },
    )


def test_healthz_reports_blueprint_writeback_flag(monkeypatch):
    client = TestClient(app)
    monkeypatch.setattr(main_module, "_BLUEPRINT_WRITEBACK_ENABLED", False)
    monkeypatch.setattr(
        main_module,
        "check_embedding_gateway",
        lambda: {"gateway": False, "provider": "ollama-local"},
    )
    monkeypatch.setattr(main_module, "get_embedding_mode", lambda: "sqlite")
    monkeypatch.setattr(main_module, "vector_index_exists", lambda: False)
    monkeypatch.setattr(main_module, "get_retrieval_mode", lambda: "sqlite")

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json()["blueprint_writeback_enabled"] is False


def test_query_stays_healthy_with_writeback_kill_switch_off(monkeypatch, tmp_path, caplog):
    _patch_query_runtime(monkeypatch, tmp_path)
    client = TestClient(app)
    monkeypatch.setattr(main_module, "_BLUEPRINT_WRITEBACK_ENABLED", False)
    mock_load = MagicMock()
    monkeypatch.setattr(main_module, "load_case_profile", mock_load)

    with caplog.at_level(logging.INFO, logger="app.main"):
        response = client.post(
            "/api/truth/query",
            json={
                "user_id": "hank-login",
                "session_id": "sess-install-off",
                "message": "I tried to help someone but it turned into conflict.",
                "preferred_name": "Hank",
                "login_username": "hank-login",
                "display_name": "Case Hank",
                "source_channel": "web",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["case_id"] == "case:web:hank-login"
    assert payload["mirror"].startswith("Hank，")
    mock_load.assert_not_called()
    assert any(
        "blueprint_event=blueprint_writeback_disabled" in record.message
        for record in caplog.records
    )


def test_query_can_enter_writeback_gate_when_enabled(monkeypatch, tmp_path, caplog):
    _patch_query_runtime(monkeypatch, tmp_path)
    client = TestClient(app)
    monkeypatch.setattr(main_module, "_BLUEPRINT_WRITEBACK_ENABLED", True)
    monkeypatch.setattr(main_module, "_count_case_sessions", lambda _user_id: 5)
    mock_load = MagicMock(
        return_value=CaseProfile(
            case_id="case:web:hank-login",
            login_username="hank-login",
            preferred_name="Hank",
            source_channel="web",
            memory_namespace="cases/web/hank-login",
        )
    )
    mock_update = MagicMock()
    monkeypatch.setattr(main_module, "load_case_profile", mock_load)
    monkeypatch.setattr(main_module.case_insight_service, "update_case_blueprint_from_conversation", mock_update)

    with caplog.at_level(logging.INFO, logger="app.main"):
        response = client.post(
            "/api/truth/query",
            json={
                "user_id": "hank-login",
                "session_id": "sess-install-on",
                "message": "I tried to help someone but it turned into conflict.",
                "preferred_name": "Hank",
                "login_username": "hank-login",
                "display_name": "Case Hank",
                "source_channel": "web",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mirror"].startswith("Hank，")
    mock_load.assert_called_once_with("case:web:hank-login")
    mock_update.assert_called_once()
    assert any(
        "blueprint_event=blueprint_update_considered" in record.message
        for record in caplog.records
    )
