from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/truth-api"))

from scripts.run_migration_005 import run_migration as run_migration_005
from scripts.run_migration_006 import run_migration as run_migration_006


def _prepare_db(tmp_path, monkeypatch) -> Path:
    db_path = tmp_path / "truthos.db"
    monkeypatch.setenv("TRUTHOS_DB_PATH", str(db_path))
    monkeypatch.setenv("SQLITE_DB_PATH", str(db_path))
    run_migration_005()
    run_migration_006()
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO soulmaps (
              id, userid, recurringpatternsjson, limitingbeliefsjson,
              emotionalsignaturesjson, activelessonsjson, evolutionstage,
              lasttruthshiftat, createdat, updatedat, patternweightsjson,
              integrateddimensionsjson, transcendedpatternsjson,
              evolutionhistoryjson, soulmapsummary
            ) VALUES (?, ?, ?, '[]', '[]', ?, 'understanding',
              '2026-05-16T00:00:00Z', '2026-05-16T00:00:00Z',
              '2026-05-16T00:00:00Z', ?, '[]', '[]', '[]',
              'Test user has a visible Soul Map.')
            """,
            (
                "soulmap-test",
                "test-sprint006",
                json.dumps(
                    [
                        {
                            "id": "relationship:control",
                            "description": "Control pattern",
                            "dimension": "relationship",
                            "first_seen": "2026-05-16T00:00:00Z",
                        }
                    ]
                ),
                json.dumps(
                    [
                        {
                            "principle_id": "truth-001",
                            "dimension": "relationship",
                            "status": "active",
                        }
                    ]
                ),
                json.dumps(
                    {
                        "relationship:control": {
                            "frequency": 6,
                            "weight": 0.7,
                            "last_seen": "2026-05-16T00:00:00Z",
                        }
                    }
                ),
            ),
        )
        connection.execute(
            """
            INSERT INTO blindspotarchives (
              id, userid, title, triggerpattern, knowntheory,
              practicalfailuremode, suggestedanchorsjson, relatedpuzzlesjson,
              frequency, lastseenat, createdat, severity, domainsjson,
              resolutionstatus
            ) VALUES (
              'blind-test', 'test-sprint006', 'Control pattern',
              'relationship:control', 'Love cannot be controlled',
              'Tries to control outcomes', '[]', '[]', 5,
              '2026-05-16T00:00:00Z', '2026-05-16T00:00:00Z',
              'high', '["relationship"]', 'active'
            )
            """
        )
        connection.execute(
            """
            INSERT INTO hardcasebuffer
              (userid, reasons, sessionid, createdat, status)
            VALUES (
              'hard-test', '["stuck pattern"]', 'session-test',
              '2026-05-16T00:00:00Z', 'pending'
            )
            """
        )
        connection.commit()
    return db_path


def _client(tmp_path, monkeypatch) -> TestClient:
    _prepare_db(tmp_path, monkeypatch)
    from app.main import app

    return TestClient(app)


def test_console_route_returns_200(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)

    response = client.get("/console")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "TruthOS Console" in response.text


def test_soul_map_endpoint_returns_expected_fields(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)

    response = client.get("/api/soul-map/test-sprint006")

    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "test-sprint006"
    assert body["status"] == "active"
    assert "evolution_stage" in body
    assert isinstance(body["recurring_patterns"], list)


def test_blind_spots_endpoint_returns_list(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)

    response = client.get("/api/soul-map/test-sprint006/blind-spots")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["blind_spots"], list)
    assert isinstance(body["count"], int)


def test_patch_blind_spot_status(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)

    response = client.patch(
        "/api/soul-map/test-sprint006/blind-spot/blind-test",
        json={"resolution_status": "softening"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "updated"
    assert response.json()["resolution_status"] == "softening"


def test_designer_hard_cases_status_filter(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)

    response = client.get("/api/designer/hard-cases?status=pending")

    assert response.status_code == 200
    body = response.json()
    assert "hard_cases" in body
    assert isinstance(body["count"], int)
    assert all(item["status"] == "pending" for item in body["hard_cases"])
