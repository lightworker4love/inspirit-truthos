from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "apps/truth-api"))

from app.db import connect_db, get_db_path
from app.seed_loader import load_seed_files
from scripts.run_migration_004 import run_migration as run_migration_004


def run_migration() -> None:
    migration_sql = (ROOT / "migrations/sql/001_init.sql").read_text()
    with connect_db() as connection:
        connection.executescript(migration_sql)
        connection.commit()
    run_migration_004()


def main() -> int:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    run_migration()
    counts = load_seed_files(ROOT / "data/seeds")
    print(f"Imported seeds into {db_path}: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
