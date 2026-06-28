import sqlite3
from contextlib import contextmanager

from app.core.config import settings


def _sqlite_path_from_url(database_url: str) -> str:
    prefix = "sqlite:///"
    if database_url.startswith(prefix):
        return database_url[len(prefix):]
    return database_url


DB_PATH = _sqlite_path_from_url(settings.database_url)


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(f"PRAGMA busy_timeout = {settings.sqlite_busy_timeout_ms}")
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
