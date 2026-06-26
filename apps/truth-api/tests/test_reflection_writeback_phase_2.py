from __future__ import annotations

import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient

_TEST_DIR = Path(__file__).resolve().parent
_TRUTH_API_ROOT = _TEST_DIR.parent
if str(_TRUTH_API_ROOT) not in sys.path:
    sys.path.insert(0, str(_TRUTH_API_ROOT))

from app.db import connect_db
from app.main import app


def _prepare_db(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "truthos-reflection-phase2.db"
    monkeypatch.setenv("TRUTHOS_DB_PATH", str(db_path))
    with connect_db() as connection:
        now = "2026-03-13T00:00:00+00:00"
        connection.execute(
            """
            INSERT OR IGNORE INTO truth_dimensions
              (id, code, name_zh, name_en, description, order_index, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("dim_relationship", "relationship", "關係", "Relationship", "Boundaries and attachment.", 4, now, now),
        )
        connection.execute(
            """
            INSERT OR IGNORE INTO core_principles
              (id, dimension_code, code, title, axiom, explanation, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "cp_rel_boundary",
                "relationship",
                "REL_001",
                "愛不等於接管",
                "Support without takeover.",
                "A seed principle for governance tests.",
                now,
                now,
            ),
        )
        connection.commit()


def _payload() -> dict:
    path = Path(__file__).resolve().parents[3] / "docs" / "daily-reflection" / "examples" / "phase2_smoke_payload.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_reflection_writeback_contract(monkeypatch, tmp_path):
    _prepare_db(monkeypatch, tmp_path)
    client = TestClient(app)

    response = client.post("/api/reflection/writeback", json=_payload())

    assert response.status_code == 200
    body = response.json()
    assert "reflection_runs" in body["accepted_streams"]
    assert body["written_records"]["reflection_runs"] == 1
    assert body["written_records"]["dashboard_daily_metrics"] == 1

    run_response = client.get("/api/reflection/runs/2026-03-13?user_id=smoke-user")
    assert run_response.status_code == 200
    run_body = run_response.json()
    assert run_body["run_payload"]["reflection_run"]["summary"].startswith("這是一筆用於驗證")
    assert any(item["mapping_type"] == "dimension" for item in run_body["truth_mappings"])


def test_duplicate_guard_prevents_duplicate_explosion(monkeypatch, tmp_path):
    _prepare_db(monkeypatch, tmp_path)
    client = TestClient(app)
    payload = _payload()

    first = client.post("/api/reflection/writeback", json=payload)
    second = client.post("/api/reflection/writeback", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    second_body = second.json()
    assert second_body["duplicate_keys"] == ["smoke-user:2026-03-13"]
    assert "reflection_runs" in second_body["skipped_streams"]

    with connect_db() as connection:
        runs_count = connection.execute("SELECT COUNT(*) AS count FROM reflection_runs").fetchone()["count"]
        blind_count = connection.execute("SELECT COUNT(*) AS count FROM blind_spot_candidate_events").fetchone()["count"]
    assert runs_count == 1
    assert blind_count == 1


def test_schema_validation_rejects_mismatched_run_date(monkeypatch, tmp_path):
    _prepare_db(monkeypatch, tmp_path)
    client = TestClient(app)
    payload = _payload()
    payload["dashboard_snapshot"]["run_date"] = "2026-03-14"

    response = client.post("/api/reflection/writeback", json=payload)

    assert response.status_code == 422


def test_materializer_generates_overview_and_trend(monkeypatch, tmp_path):
    _prepare_db(monkeypatch, tmp_path)
    client = TestClient(app)
    client.post("/api/reflection/writeback", json=_payload())

    materialize = client.post(
        "/api/reflection/materialize",
        json={"user_id": "smoke-user", "run_date": "2026-03-13", "rebuild_all": False},
    )
    assert materialize.status_code == 200
    materialize_body = materialize.json()
    assert "dashboard_overview_view" in materialize_body["materialized_views"]
    assert materialize_body["generated_records"]["dimension_trends_view"] >= 1

    overview = client.get("/api/reflection/dashboard/overview?user_id=smoke-user")
    assert overview.status_code == 200
    overview_body = overview.json()
    assert {item["window_days"] for item in overview_body["windows"]} == {7, 30, 90}


def test_governance_keeps_drafts_out_of_canonical_tables(monkeypatch, tmp_path):
    _prepare_db(monkeypatch, tmp_path)
    client = TestClient(app)

    with connect_db() as connection:
        canonical_before = connection.execute("SELECT COUNT(*) AS count FROM core_principles").fetchone()["count"]
        puzzle_before = connection.execute("SELECT COUNT(*) AS count FROM truth_puzzles").fetchone()["count"]

    response = client.post("/api/reflection/writeback", json=_payload())
    assert response.status_code == 200

    with connect_db() as connection:
        canonical_after = connection.execute("SELECT COUNT(*) AS count FROM core_principles").fetchone()["count"]
        puzzle_after = connection.execute("SELECT COUNT(*) AS count FROM truth_puzzles").fetchone()["count"]
        draft_count = connection.execute(
            "SELECT COUNT(*) AS count FROM core_principle_draft_events WHERE status = 'draft'"
        ).fetchone()["count"]
    assert canonical_before == canonical_after
    assert puzzle_before == puzzle_after
    assert draft_count == 1
