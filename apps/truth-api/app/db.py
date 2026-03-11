from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from app.config import get_root_path, resolve_path


def get_db_path() -> Path:
    default_path = get_root_path() / "data/truthos.db"
    configured = os.getenv("TRUTHOS_DB_PATH")
    if not configured:
        return default_path
    return resolve_path(configured)


def connect_db() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection
