from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/truth-api"))

from app.db import connect_db, get_db_path


NEW_COLUMNS = [
    ("core_principles", "worldly_example", "TEXT"),
    ("core_principles", "spiritual_example", "TEXT"),
    ("core_principles", "objectivity_statement", "TEXT"),
    ("core_principles", "truth_property_primary", "TEXT"),
    ("truth_puzzles", "truth_property_tags", "TEXT"),
    ("truth_puzzles", "verification_mode", "TEXT DEFAULT 'dialogue'"),
    ("truth_puzzles", "fact_layer", "TEXT"),
    ("truth_puzzles", "reality_layer", "TEXT"),
]


def run_migration() -> None:
    with _connect() as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        _ensure_truth_evals(connection)
        for table, column, column_type in NEW_COLUMNS:
            _add_column_if_missing(connection, table, column, column_type)
        connection.commit()
    target = os.environ.get("SQLITE_DB_PATH") or str(get_db_path())
    print(f"Migration 004 complete for {target}")


def _connect() -> sqlite3.Connection:
    configured = os.environ.get("SQLITE_DB_PATH")
    if configured:
        path = Path(configured)
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path)
        connection.row_factory = sqlite3.Row
        return connection
    return connect_db()


def _ensure_truth_evals(connection: sqlite3.Connection) -> None:
    sql = (ROOT / "migrations/sql/004_truth_properties.sql").read_text()
    connection.executescript(sql)


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


if __name__ == "__main__":
    run_migration()
