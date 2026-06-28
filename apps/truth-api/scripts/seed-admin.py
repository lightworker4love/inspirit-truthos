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
    if value is None:
        return default
    return value.strip()


def main():
    database_url = env("DATABASE_URL", "sqlite:////Users/tongwei/.openclaw/data/in-spirit-case-auth.db")
    db_path = sqlite_path_from_database_url(database_url)

    admin_username = env("ADMIN_BOOTSTRAP_USERNAME", "lightworker-admin")
    admin_password = env("ADMIN_BOOTSTRAP_PASSWORD", "replace-me")
    admin_email = env("ADMIN_BOOTSTRAP_EMAIL", "admin@example.local")

    case_username = env("CASE_BOOTSTRAP_USERNAME", "hank")
    case_password = env("CASE_BOOTSTRAP_PASSWORD", "secret")
    case_email = env("CASE_BOOTSTRAP_EMAIL", "hank@example.local")
    case_display_name = env("CASE_BOOTSTRAP_DISPLAY_NAME", "Hank")

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    now = utcnow_iso()

    admin_user = conn.execute(
        "SELECT id FROM users WHERE username = ? LIMIT 1",
        (admin_username,),
    ).fetchone()

    if not admin_user:
        admin_id = f"usr_admin_{uuid4().hex[:12]}"
        conn.execute(
            """
            INSERT INTO users (
                id, username, password_hash, role, status, email, created_at, updated_at
            ) VALUES (?, ?, ?, 'admin_builder', 'active', ?, ?, ?)
            """,
            (
                admin_id,
                admin_username,
                pwd_context.hash(admin_password),
                admin_email,
                now,
                now,
            ),
        )
        print(f"[seed] created admin_builder: {admin_username}")
    else:
        admin_id = admin_user["id"]
        print(f"[seed] admin_builder exists: {admin_username}")

    case_user = conn.execute(
        "SELECT id FROM users WHERE username = ? LIMIT 1",
        (case_username,),
    ).fetchone()

    if not case_user:
        case_id = f"usr_case_{uuid4().hex[:12]}"
        conn.execute(
            """
            INSERT INTO users (
                id, username, password_hash, role, status, email, created_at, updated_at
            ) VALUES (?, ?, ?, 'case_client', 'active', ?, ?, ?)
            """,
            (
                case_id,
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
                case_id,
                case_display_name,
                case_display_name,
                admin_id,
                now,
                now,
            ),
        )
        print(f"[seed] created case_client: {case_username}")
    else:
        print(f"[seed] case_client exists: {case_username}")

    conn.commit()
    conn.close()
    print("[seed] done")


if __name__ == "__main__":
    main()
