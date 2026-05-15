from __future__ import annotations

import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/truth-api"))


def test_migration_005_adds_soul_map_depth_columns(tmp_path, monkeypatch):
    db_path = tmp_path / "truthos.db"
    monkeypatch.setenv("SQLITE_DB_PATH", str(db_path))

    with sqlite3.connect(db_path) as connection:
        connection.executescript((ROOT / "migrations/sql/001_init.sql").read_text())
        connection.commit()

    from scripts.run_migration_005 import run_migration

    run_migration()
    run_migration()

    with sqlite3.connect(db_path) as connection:
        soulmap_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(soulmaps)")
        }
        blindspot_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(blindspotarchives)")
        }
        hardcase_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(hardcasebuffer)")
        }

    assert {
        "patternweightsjson",
        "integrateddimensionsjson",
        "transcendedpatternsjson",
        "evolutionhistoryjson",
        "soulmapsummary",
    } <= soulmap_columns
    assert {
        "severity",
        "domainsjson",
        "resolutionstatus",
        "resolutionat",
    } <= blindspot_columns
    assert {"userid", "reasons", "sessionid", "createdat"} <= hardcase_columns
