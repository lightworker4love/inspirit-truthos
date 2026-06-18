from __future__ import annotations

from contextlib import contextmanager
import logging
from pathlib import Path
import sys

from fastapi.testclient import TestClient


_TEST_DIR = Path(__file__).resolve().parent
_TRUTH_API_ROOT = _TEST_DIR.parent
if str(_TRUTH_API_ROOT) not in sys.path:
    sys.path.insert(0, str(_TRUTH_API_ROOT))

from app.case_insight_service import infer_soul_age, update_case_blueprint_from_conversation
from app.case_models import CaseProfile, CaseResolutionInput
from app.case_resolver import CaseResolver, load_case_profile
from app.main import app
from app.models import TruthQueryRequest
from app.prompt_builder import PromptBuilder
from app.reasoning import compose_response


def _sample_puzzles() -> list[dict[str, str]]:
    return [
        {
            "title": "Boundary Drift",
            "statement": "trying to stay safe by staying overly available",
            "dimension_code": "identity",
            "principle_code": "boundaries",
            "misbelief": "I have to over-explain so people will understand me",
            "truth_reframe": "clarity and boundaries can coexist",
            "coach_prompt": "What boundary would reduce the pressure here?",
        }
    ]


@contextmanager
def _healthy_connection():
    class _Conn:
        def execute(self, _sql: str) -> int:
            return 1

    yield _Conn()


def _patch_truth_query(monkeypatch, tmp_path):
    import app.case_resolver as case_resolver_module
    import app.main as main_module

    monkeypatch.setattr(case_resolver_module, "CASE_STORE_DIR", tmp_path)
    monkeypatch.setattr(main_module, "connect_db", lambda: _healthy_connection())
    monkeypatch.setattr(main_module, "classify_dimensions", lambda _message: ["identity"])
    monkeypatch.setattr(
        main_module,
        "retrieve_puzzles",
        lambda _message, dimensions, limit: {
            "puzzles": _sample_puzzles(),
            "retrieval_mode": "sqlite",
        },
    )


def test_hank_preferred_name_full_path(monkeypatch, tmp_path):
    _patch_truth_query(monkeypatch, tmp_path)
    client = TestClient(app)

    session_payload = {
        "preferredName": "Hank",
        "loginUsername": "hank-login",
        "displayName": "Case Hank",
        "sourceChannel": "web",
    }
    frontend_state = {
        "preferredName": session_payload["preferredName"],
        "loginUsername": session_payload["loginUsername"],
        "displayName": session_payload["displayName"],
        "sourceChannel": session_payload["sourceChannel"],
    }
    assert frontend_state["preferredName"] == "Hank"

    chat_body = {
        "user_id": "hank-login",
        "session_id": "sess-hank-1",
        "message": "I keep over-explaining and feel pressure at work.",
        "preferred_name": frontend_state["preferredName"],
        "login_username": frontend_state["loginUsername"],
        "display_name": frontend_state["displayName"],
        "source_channel": frontend_state["sourceChannel"],
    }
    assert chat_body["preferred_name"] == "Hank"

    request_model = TruthQueryRequest.model_validate(chat_body)
    assert request_model.preferred_name == "Hank"

    resolver_input = CaseResolutionInput(
        login_username=request_model.login_username,
        preferred_name=request_model.preferred_name,
        display_name=request_model.display_name,
        source_channel=request_model.source_channel,
        external_user_id=request_model.user_id,
        session_id=request_model.session_id,
        workspace_default_name="外文大哥",
    )
    case_ctx, _ = CaseResolver().resolve(resolver_input)
    assert case_ctx.address_as == "Hank"

    prompt_message = PromptBuilder().build_case_context_message(case_ctx)
    assert "Address as: Hank" in prompt_message["content"]

    composed = compose_response(chat_body["message"], _sample_puzzles(), case_ctx=case_ctx)
    assert composed["mirror"].startswith("Hank，")

    response = client.post("/api/truth/query", json=chat_body)
    assert response.status_code == 200
    payload = response.json()
    assert payload["case_id"] == "case:web:hank-login"
    assert payload["mirror"].startswith("Hank，")
    assert "soul_age" not in payload

    stored = load_case_profile("case:web:hank-login")
    assert stored is not None
    assert stored.preferred_name == "Hank"
    assert stored.last_session_insight is not None


def test_fallback_when_no_preferred_name(monkeypatch, tmp_path):
    _patch_truth_query(monkeypatch, tmp_path)
    client = TestClient(app)

    chat_body = {
        "user_id": "yvonne-login",
        "session_id": "sess-yvonne-1",
        "message": "I need help naming what I feel.",
        "preferred_name": None,
        "login_username": "yvonne-login",
        "display_name": "Yvonne Case",
        "source_channel": "web",
    }

    response = client.post("/api/truth/query", json=chat_body)
    assert response.status_code == 200
    payload = response.json()
    assert payload["mirror"].startswith("yvonne-login，")
    assert "soul_age" not in payload


def test_minimal_blueprint_writeback_preserves_identity(monkeypatch, tmp_path):
    _patch_truth_query(monkeypatch, tmp_path)
    profile = CaseProfile(
        case_id="case:web:hank",
        login_username="hank-login",
        preferred_name="Hank",
        display_name="Case Hank",
        memory_namespace="cases/web/hank",
        source_channel="web",
    )

    updated = update_case_blueprint_from_conversation(
        profile,
        conversation_messages=[
            {"role": "user", "content": "I keep over-explaining and struggle with boundaries at work."}
        ],
        model_response={
            "truth_view": "Boundaries and self-worth are the central thread here.",
            "action": "Practice one clear boundary this week.",
        },
    )

    assert updated.last_session_insight == "Boundaries and self-worth are the central thread here."
    assert "boundaries and self-worth" in updated.life_themes
    assert updated.preferred_name == "Hank"
    assert updated.case_id == "case:web:hank"


def test_blueprint_writeback_observability_logs(monkeypatch, tmp_path, caplog):
    _patch_truth_query(monkeypatch, tmp_path)
    profile = CaseProfile(
        case_id="case:web:yvonne",
        login_username="yvonne-login",
        display_name="Yvonne",
        memory_namespace="cases/web/yvonne",
        source_channel="web",
    )

    with caplog.at_level(logging.INFO):
        update_case_blueprint_from_conversation(
            profile,
            conversation_messages=[
                {"role": "user", "content": "I keep delaying and avoiding difficult tasks."}
            ],
            model_response={"truth_view": "Avoidance under pressure is the repeated loop."},
            metadata={"session_id": "sess-yvonne-obs", "source_channel": "web"},
        )

    logs = "\n".join(caplog.messages)
    assert "case_blueprint_writeback" in logs
    assert "case:web:yvonne" in logs
    assert "updated_fields" in logs
    assert "skip_reason" in logs
    assert "soul_age_guard" in logs


def test_soul_age_not_emitted_when_history_is_insufficient():
    profile = CaseProfile(
        case_id="case:web:test",
        memory_namespace="cases/web/test",
    )

    result = infer_soul_age(
        profile,
        [
            {"role": "user", "content": "I want to control every outcome."},
            {"role": "assistant", "content": "What feels unsafe if you do not?"},
        ],
    )

    assert result["eligible"] is False
    assert result["soul_age"] is None
    assert "Need at least" in result["why_not_eligible"]


def test_schema_version_default_is_present():
    profile = CaseProfile(
        case_id="case:web:test",
        memory_namespace="cases/web/test",
    )
    assert profile.schema_version == 1
