from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/truth-api"))

from app.db import connect_db, get_db_path


NEW_COLUMNS = [
    ("soulmaps", "patternweightsjson", "TEXT"),
    ("soulmaps", "integrateddimensionsjson", "TEXT"),
    ("soulmaps", "transcendedpatternsjson", "TEXT"),
    ("soulmaps", "evolutionhistoryjson", "TEXT"),
    ("soulmaps", "soulmapsummary", "TEXT"),
    ("blindspotarchives", "severity", "TEXT DEFAULT 'medium'"),
    ("blindspotarchives", "domainsjson", "TEXT"),
    ("blindspotarchives", "resolutionstatus", "TEXT DEFAULT 'active'"),
    ("blindspotarchives", "resolutionat", "TEXT"),
]


def _connect() -> sqlite3.Connection:
    configured = os.environ.get("SQLITE_DB_PATH")
    if configured:
        path = Path(configured)
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path)
        connection.row_factory = sqlite3.Row
        return connection
    return connect_db()


def _add_column_if_missing(
    connection: sqlite3.Connection,
    table: str,
    column: str,
    column_type: str,
) -> None:
    columns = {
        row[1] for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
    }
    if column in columns:
        print(f"  = {table}.{column} already exists, skipping")
        return
    connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
    print(f"  + Added {table}.{column}")


def run_migration() -> None:
    with _connect() as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript((ROOT / "migrations/005_soulmap_depth.sql").read_text())
        for table, column, column_type in NEW_COLUMNS:
            _add_column_if_missing(connection, table, column, column_type)
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_blindspotarchives_resolution
              ON blindspotarchives(userid, resolutionstatus)
            """
        )
        connection.commit()

    target = os.environ.get("SQLITE_DB_PATH") or str(get_db_path())
    print(f"Migration 005 complete for {target}.")


if __name__ == "__main__":
    run_migration()
