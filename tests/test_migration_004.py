from __future__ import annotations

import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_migration_004_adds_truth_property_columns(tmp_path, monkeypatch):
    db_path = tmp_path / "truthos.db"
    monkeypatch.setenv("TRUTHOS_DB_PATH", str(db_path))

    with sqlite3.connect(db_path) as connection:
        connection.executescript((ROOT / "migrations/sql/001_init.sql").read_text())
        connection.commit()

    import sys

    sys.path.insert(0, str(ROOT / "apps/truth-api"))
    from scripts.run_migration_004 import run_migration

    run_migration()
    run_migration()

    with sqlite3.connect(db_path) as connection:
        core_columns = {row[1] for row in connection.execute("PRAGMA table_info(core_principles)")}
        puzzle_columns = {row[1] for row in connection.execute("PRAGMA table_info(truth_puzzles)")}
        eval_columns = {row[1] for row in connection.execute("PRAGMA table_info(truth_evals)")}

    assert {
        "worldly_example",
        "spiritual_example",
        "objectivity_statement",
        "truth_property_primary",
    } <= core_columns
    assert {
        "truth_property_tags",
        "verification_mode",
        "fact_layer",
        "reality_layer",
    } <= puzzle_columns
    assert {
        "verification_track",
        "life_evidence_confirmed",
        "discovery_triggered",
    } <= eval_columns
