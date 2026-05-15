from __future__ import annotations

import sqlite3

from scripts.run_migration_006 import run_migration


def test_migration_006_is_idempotent(tmp_path, monkeypatch):
    db_path = tmp_path / "truthos.db"
    monkeypatch.setenv("SQLITE_DB_PATH", str(db_path))

    run_migration()
    run_migration()

    connection = sqlite3.connect(db_path)
    hardcase_columns = {
        row[1] for row in connection.execute("PRAGMA table_info(hardcasebuffer)")
    }
    assert {"status", "summaryjson", "resolvedat", "resolutionnote"}.issubset(
        hardcase_columns
    )

    expected_tables = {
        "promptversions",
        "promptabtests",
        "designerreviews",
        "knowledgeevolutions",
    }
    tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    assert expected_tables.issubset(tables)

    promptversion_columns = {
        row[1] for row in connection.execute("PRAGMA table_info(promptversions)")
    }
    assert {
        "id",
        "hardcaseid",
        "prompttemplate",
        "promptlabel",
        "prompttype",
        "version",
        "parentversionid",
        "createdat",
    }.issubset(promptversion_columns)


def test_migration_006_preserves_existing_hard_cases(tmp_path, monkeypatch):
    db_path = tmp_path / "truthos.db"
    connection = sqlite3.connect(db_path)
    connection.execute(
        """
        CREATE TABLE hardcasebuffer (
          userid TEXT PRIMARY KEY,
          reasons TEXT NOT NULL,
          sessionid TEXT,
          createdat TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        INSERT INTO hardcasebuffer (userid, reasons, sessionid, createdat)
        VALUES ('user-001', '["stuck"]', 'session-001', '2026-05-16T00:00:00Z')
        """
    )
    connection.commit()
    connection.close()

    monkeypatch.setenv("SQLITE_DB_PATH", str(db_path))
    run_migration()

    connection = sqlite3.connect(db_path)
    row = connection.execute(
        "SELECT userid, status FROM hardcasebuffer WHERE userid = 'user-001'"
    ).fetchone()
    assert row == ("user-001", "pending")
