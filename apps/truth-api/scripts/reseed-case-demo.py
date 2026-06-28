#!/usr/bin/env python3
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sqlite_path_from_database_url(database_url: str) -> str:
    prefix = "sqlite:///"
    return database_url[len(prefix):] if database_url.startswith(prefix) else database_url


def env(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    return value.strip() if value else default


def main():
    database_url = env("DATABASE_URL", "sqlite:////Users/tongwei/.openclaw/data/in-spirit-case-auth.db")
    db_path = sqlite_path_from_database_url(database_url)

    case_username = env("CASE_BOOTSTRAP_USERNAME", "hank")
    case_password = env("CASE_BOOTSTRAP_PASSWORD", "secret")
    case_email = env("CASE_BOOTSTRAP_EMAIL", "hank@example.local")
    case_display_name = env("CASE_BOOTSTRAP_DISPLAY_NAME", "Hank")
    admin_username = env("ADMIN_BOOTSTRAP_USERNAME", "lightworker-admin")

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    admin = conn.execute(
        "SELECT id FROM users WHERE username = ? LIMIT 1",
        (admin_username,),
    ).fetchone()

    if not admin:
        conn.close()
        raise SystemExit(f"[error] admin not found: {admin_username}")

    existing = conn.execute(
        "SELECT id FROM users WHERE username = ? LIMIT 1",
        (case_username,),
    ).fetchone()

    if existing:
        case_id = existing["id"]

        conn.execute("DELETE FROM case_entries WHERE thread_id IN (SELECT id FROM case_threads WHERE case_user_id = ?)", (case_id,))
        conn.execute("DELETE FROM case_threads WHERE case_user_id = ?", (case_id,))
        conn.execute("DELETE FROM auth_sessions WHERE user_id = ?", (case_id,))
        conn.execute("DELETE FROM case_profiles WHERE user_id = ?", (case_id,))
        conn.execute("DELETE FROM users WHERE id = ?", (case_id,))
        print(f"[reseed] removed existing demo case: {case_username}")

    now = utcnow_iso()
    new_case_id = f"usr_case_{uuid4().hex[:12]}"

    conn.execute(
        """
        INSERT INTO users (
            id, username, password_hash, role, status, email, created_at, updated_at
        ) VALUES (?, ?, ?, 'case_client', 'active', ?, ?, ?)
        """,
        (
            new_case_id,
            case_username,
            pwd_context.hash(case_password),
            case_email,
            now,
            now,
        ),
    )

    conn.execute(
        """
        INSERT INTO case_profiles (
            id, user_id, display_name, legal_name, preferred_language,
            intake_status, consent_version, assigned_admin_id, created_at, updated_at
        ) VALUES (?, ?, ?, ?, 'zh-TW', 'active', 'v1', ?, ?, ?)
        """,
        (
            f"case_profile_{uuid4().hex[:12]}",
            new_case_id,
            case_display_name,
            case_display_name,
            admin["id"],
            now,
            now,
        ),
    )

    conn.commit()
    conn.close()

    print(f"[reseed] created demo case: {case_username}")
    print(f"[reseed] display name: {case_display_name}")
    print("[reseed] done")


if __name__ == "__main__":
    main()
