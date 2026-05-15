from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/truth-api"))

from core.designer_agent import DesignerAgent, EVAL_RUBRIC
from scripts.run_migration_005 import run_migration as run_migration_005
from scripts.run_migration_006 import run_migration as run_migration_006


def _connection(tmp_path, monkeypatch) -> sqlite3.Connection:
    db_path = tmp_path / "truthos.db"
    monkeypatch.setenv("SQLITE_DB_PATH", str(db_path))
    run_migration_005()
    run_migration_006()
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def _insert_hard_case(connection: sqlite3.Connection, user_id: str = "user-001") -> None:
    connection.execute(
        """
        INSERT OR REPLACE INTO hardcasebuffer
          (userid, reasons, sessionid, createdat, status)
        VALUES (?, ?, 'session-001', '2026-05-16T00:00:00Z', 'pending')
        """,
        (
            user_id,
            json.dumps(
                ["Pattern(s) ['relationship:control'] recurring 5+ times with high weight"]
            ),
        ),
    )


def _insert_soul_map(connection: sqlite3.Connection, user_id: str = "user-001") -> None:
    connection.execute(
        """
        INSERT INTO soulmaps (
          id, userid, recurringpatternsjson, limitingbeliefsjson,
          emotionalsignaturesjson, activelessonsjson, evolutionstage,
          lasttruthshiftat, createdat, updatedat, patternweightsjson,
          integrateddimensionsjson, transcendedpatternsjson,
          evolutionhistoryjson, soulmapsummary
        ) VALUES (?, ?, ?, '[]', '[]', '[]', 'understanding', NULL,
          '2026-05-16T00:00:00Z', '2026-05-16T00:00:00Z',
          ?, '[]', '[]', '[]', 'Control pattern is active.')
        """,
        (
            "soulmap-001",
            user_id,
            json.dumps(
                [
                    {
                        "id": "relationship:control",
                        "description": "Control pattern in relationship",
                    }
                ]
            ),
            json.dumps(
                {
                    "relationship:control": {
                        "frequency": 6,
                        "weight": 0.6988,
                        "last_seen": "2026-05-16T00:00:00Z",
                    }
                }
            ),
        ),
    )


def _insert_blind_spot(connection: sqlite3.Connection, user_id: str = "user-001") -> None:
    connection.execute(
        """
        INSERT INTO blindspotarchives (
          id, userid, title, triggerpattern, knowntheory,
          practicalfailuremode, suggestedanchorsjson, relatedpuzzlesjson,
          frequency, lastseenat, createdat, severity, domainsjson,
          resolutionstatus
        ) VALUES (
          'blind-001', ?, 'Control pattern', 'relationship:control',
          'Love cannot be controlled', 'Tries to control outcomes',
          '[]', '[]', 7, '2026-05-16T00:00:00Z',
          '2026-05-16T00:00:00Z', 'critical',
          '["relationship", "career", "self-worth"]', 'active'
        )
        """,
        (user_id,),
    )


def test_eval_rubric_weights_sum_to_one():
    assert round(sum(item["weight"] for item in EVAL_RUBRIC.values()), 10) == 1.0


def test_review_hard_case_completes_knowledge_loop(tmp_path, monkeypatch):
    connection = _connection(tmp_path, monkeypatch)
    _insert_hard_case(connection)
    _insert_soul_map(connection)
    _insert_blind_spot(connection)
    connection.commit()

    result = DesignerAgent(connection).review_hard_case("user-001")

    assert result["evaluation"]["status"] == "completed"
    assert result["evaluation"]["winner_id"]
    assert result["designer_review"]["action"] == "apply_prompt_winner"
    assert result["knowledge_evolution"]["changetype"] == "prompt_variant_won"

    status = connection.execute(
        "SELECT status FROM hardcasebuffer WHERE userid = 'user-001'"
    ).fetchone()["status"]
    assert status == "resolved"

    for table in (
        "promptversions",
        "promptabtests",
        "designerreviews",
        "knowledgeevolutions",
    ):
        count = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        assert count >= 1


def test_review_pending_processes_pending_cases(tmp_path, monkeypatch):
    connection = _connection(tmp_path, monkeypatch)
    _insert_hard_case(connection)
    _insert_soul_map(connection)
    connection.commit()

    result = DesignerAgent(connection).review_pending(limit=5)

    assert result["processed"] == 1
    assert result["reviews"][0]["hardcase_id"] == "user-001"


def test_inconclusive_review_escalates_to_human_coach(tmp_path, monkeypatch):
    connection = _connection(tmp_path, monkeypatch)
    connection.execute(
        """
        INSERT INTO hardcasebuffer
          (userid, reasons, sessionid, createdat, status)
        VALUES ('user-empty', '[]', 'session-002', '2026-05-16T00:00:00Z', 'pending')
        """
    )
    connection.commit()

    result = DesignerAgent(connection).review_hard_case("user-empty")

    assert result["evaluation"]["status"] == "inconclusive"
    assert result["evaluation"]["recommended_action"] == "escalate_to_human_coach"
    row = connection.execute(
        "SELECT status, resolvedat FROM hardcasebuffer WHERE userid = 'user-empty'"
    ).fetchone()
    assert row["status"] == "coach_review"
    assert row["resolvedat"] is None
