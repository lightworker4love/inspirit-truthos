from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/truth-api"))


def test_truth_eval_writeback_records_verification_fields(tmp_path, monkeypatch):
    db_path = tmp_path / "truthos.db"
    monkeypatch.setenv("TRUTHOS_DB_PATH", str(db_path))

    with sqlite3.connect(db_path) as connection:
        connection.executescript((ROOT / "migrations/sql/001_init.sql").read_text())
        connection.commit()

    from scripts.run_migration_004 import run_migration

    run_migration()

    from app.truth_eval import write_truth_eval

    eval_id = write_truth_eval(
        user_id="test-001",
        session_id="sess-001",
        question="What is true here?",
        verification_track="dialogue",
        life_evidence_confirmed=False,
        discovery_triggered=True,
    )

    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            "SELECT verification_track, life_evidence_confirmed, discovery_triggered FROM truth_evals WHERE id = ?",
            (eval_id,),
        ).fetchone()

    assert row == ("dialogue", 0, 1)
