from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

_TEST_DIR = Path(__file__).resolve().parent
_TRUTH_API_ROOT = _TEST_DIR.parent
if str(_TRUTH_API_ROOT) not in sys.path:
    sys.path.insert(0, str(_TRUTH_API_ROOT))

from app.db import connect_db
from app.dimension_classifier import classify_dimensions
from app.main import app


def _prepare_db(monkeypatch, tmp_path: Path) -> Path:
    db_path = tmp_path / "truthos-test.db"
    monkeypatch.setenv("TRUTHOS_DB_PATH", str(db_path))
    with connect_db() as connection:
        now = "2026-03-13T00:00:00+00:00"
        connection.execute(
            """
            INSERT INTO truth_dimensions (id, code, name_zh, name_en, description, order_index, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("dim_relationship", "relationship", "關係", "Relationship", "Boundaries, roles, and attachment.", 4, now, now),
        )
        connection.execute(
            """
            INSERT INTO truth_dimensions (id, code, name_zh, name_en, description, order_index, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("dim_emotion", "emotion", "情緒", "Emotion", "Emotional patterns and charge.", 3, now, now),
        )
        connection.execute(
            """
            INSERT INTO core_principles (id, dimension_code, code, title, axiom, explanation, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "cp_rel_01",
                "relationship",
                "P-REL-01",
                "Clear Boundaries",
                "Boundaries protect truth.",
                "Practice explicit boundaries in close relationships.",
                now,
                now,
            ),
        )
        connection.commit()
    return db_path


def _sample_puzzles() -> list[dict[str, str]]:
    return [
        {
            "id": "pz-1",
            "dimension_code": "relationship",
            "principle_code": "P-REL-01",
            "title": "Boundary Spiral",
            "statement": "你在關係裡反覆過度解釋自己",
            "misbelief": "只有說得更清楚，別人才會理解我",
            "truth_reframe": "界線與真誠可以同時存在",
            "coach_prompt": "這段關係裡，你最需要守住的是哪個界線？",
        }
    ]


def test_dimension_classifier_llm_fallback(monkeypatch):
    import app.dimension_classifier as classifier_module

    monkeypatch.setattr(classifier_module, "get_dimension_classifier_llm_fallback", lambda: True)
    monkeypatch.setattr(
        classifier_module,
        "_llm_dimension_fallback",
        lambda message, top_k: ["discernment", "belief", "emotion"],
    )

    result = classify_dimensions("我最近很複雜，不知道怎麼說", top_k=3)

    assert result == ["discernment", "belief", "emotion"]


def test_dimensions_and_principles_endpoints(monkeypatch, tmp_path):
    _prepare_db(monkeypatch, tmp_path)
    client = TestClient(app)

    dimensions_response = client.get("/api/truth/dimensions")
    assert dimensions_response.status_code == 200
    dimensions_payload = dimensions_response.json()
    assert dimensions_payload["dimensions"][0]["code"] == "emotion"
    assert any(item["code"] == "relationship" for item in dimensions_payload["dimensions"])

    principles_response = client.get("/api/truth/principles?dimension=relationship")
    assert principles_response.status_code == 200
    principles_payload = principles_response.json()
    assert principles_payload["principles"] == [
        {
            "dimension_code": "relationship",
            "code": "P-REL-01",
            "title": "Clear Boundaries",
            "axiom": "Boundaries protect truth.",
            "explanation": "Practice explicit boundaries in close relationships.",
        }
    ]


def test_truth_query_returns_extended_fields_and_session_memory(monkeypatch, tmp_path):
    _prepare_db(monkeypatch, tmp_path)
    client = TestClient(app)

    import app.main as main_module

    monkeypatch.setattr(main_module, "get_embedding_mode", lambda: "sqlite")
    monkeypatch.setattr(main_module, "classify_dimensions", lambda _message: ["relationship", "emotion", "belief"])
    monkeypatch.setattr(
        main_module,
        "retrieve_puzzles",
        lambda _message, dimensions, limit: {
            "puzzles": _sample_puzzles(),
            "retrieval_mode": "sqlite",
        },
    )

    response = client.post(
        "/api/truth/query",
        json={
            "user_id": "anonymous",
            "session_id": "sess-200",
            "message": "我在關係裡總是過度解釋，然後越來越焦慮。",
            "mode": "mentor",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == "sess-200"
    assert payload["dimensions_triggered"] == ["relationship", "emotion", "belief"]
    assert payload["matched_puzzles_count"] == 1
    assert payload["embedding_mode"] in {"gateway", "openai", "sqlite"}
    assert payload["mirror"].startswith("你，")

    history_response = client.get("/api/truth/session/anonymous")
    assert history_response.status_code == 200
    history_payload = history_response.json()
    assert history_payload["user_id"] == "anonymous"
    assert history_payload["history"][0]["dimension"] == "relationship"
    assert history_payload["history"][0]["principle"] == "P-REL-01"
    assert "過度解釋" in history_payload["history"][0]["snippet"]
