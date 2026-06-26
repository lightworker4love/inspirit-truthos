#!/usr/bin/env python3
import os
import sqlite3
from pathlib import Path


def sqlite_path_from_database_url(database_url: str) -> str:
    prefix = "sqlite:///"
    return database_url[len(prefix):] if database_url.startswith(prefix) else database_url


def get_database_path() -> str:
    database_url = os.getenv(
        "DATABASE_URL",
        "sqlite:////Users/tongwei/.openclaw/data/in-spirit-case-auth.db",
    )
    return sqlite_path_from_database_url(database_url)


def fetch_count(conn, table_name: str) -> int:
    row = conn.execute(f"SELECT COUNT(*) AS c FROM {table_name}").fetchone()
    return int(row["c"])


def main():
    db_path = get_database_path()

    if not Path(db_path).exists():
        raise SystemExit(f"[error] database not found: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    print("== db inspect ==")
    print(f"db_path={db_path}")
    print()

    tables = [
        "users",
        "case_profiles",
        "auth_sessions",
        "model_policies",
        "case_threads",
        "case_entries",
        "audit_logs",
        "prompt_versions",
    ]

    print("-- table counts --")
    for table in tables:
        try:
            count = fetch_count(conn, table)
            print(f"{table}: {count}")
        except sqlite3.Error as exc:
            print(f"{table}: ERROR ({exc})")
    print()

    print("-- users --")
    for row in conn.execute("""
        SELECT id, username, role, status, created_at, updated_at
        FROM users
        ORDER BY created_at ASC
        LIMIT 20
    """):
        print(dict(row))
    print()

    print("-- case profiles --")
    for row in conn.execute("""
        SELECT id, user_id, display_name, intake_status, assigned_admin_id
        FROM case_profiles
        ORDER BY created_at ASC
        LIMIT 20
    """):
        print(dict(row))
    print()

    print("-- model policies --")
    for row in conn.execute("""
        SELECT role, mode_key, mode_label, model_id, is_default, enabled
        FROM model_policies
        ORDER BY role, mode_key ASC
    """):
        print(dict(row))
    print()

    print("-- active prompts --")
    for row in conn.execute("""
        SELECT audience, version, is_active, created_at
        FROM prompt_versions
        WHERE is_active = 1
        ORDER BY created_at DESC
    """):
        print(dict(row))
    print()

    print("-- recent threads --")
    for row in conn.execute("""
        SELECT id, case_user_id, selected_mode_key, resolved_model_id, title, created_at
        FROM case_threads
        ORDER BY created_at DESC
        LIMIT 10
    """):
        print(dict(row))
    print()

    print("-- recent audit logs --")
    for row in conn.execute("""
        SELECT id, actor_user_id, action, result, resolved_model_id, created_at
        FROM audit_logs
        ORDER BY created_at DESC
        LIMIT 20
    """):
        print(dict(row))
    print()

    conn.close()
    print("Inspect complete.")


if __name__ == "__main__":
    main()
