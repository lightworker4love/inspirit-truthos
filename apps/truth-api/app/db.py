from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from threading import Lock

from app.config import get_root_path, resolve_path

_MIGRATION_LOCK = Lock()
_MIGRATED_DATABASES: set[str] = set()


def get_db_path() -> Path:
    default_path = get_root_path() / "data/truthos.db"
    configured = os.getenv("TRUTHOS_DB_PATH")
    if not configured:
        return default_path
    return resolve_path(configured)


def _migration_files() -> list[Path]:
    root = get_root_path()
    candidates: list[Path] = []
    for directory in (root / "migrations" / "sql", root / "migrations"):
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.sql")):
            candidates.append(path)
    return candidates


def _apply_migrations(connection: sqlite3.Connection) -> None:
    connection.execute("PRAGMA foreign_keys = ON")
    for migration_path in _migration_files():
        connection.executescript(migration_path.read_text(encoding="utf-8"))
    connection.commit()


def ensure_migrations(connection: sqlite3.Connection, db_path: Path | None = None) -> None:
    target_path = str((db_path or get_db_path()).resolve())
    with _MIGRATION_LOCK:
        if target_path in _MIGRATED_DATABASES:
            return
        _apply_migrations(connection)
        _MIGRATED_DATABASES.add(target_path)


def connect_db() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    ensure_migrations(connection, db_path)
    return connection
