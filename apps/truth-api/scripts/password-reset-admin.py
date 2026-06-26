#!/usr/bin/env python3
import argparse
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sqlite_path_from_database_url(database_url: str) -> str:
    prefix = "sqlite:///"
    return database_url[len(prefix):] if database_url.startswith(prefix) else database_url


def get_database_path() -> str:
    database_url = os.getenv(
        "DATABASE_URL",
        "sqlite:////Users/tongwei/.openclaw/data/in-spirit-case-auth.db",
    )
    return sqlite_path_from_database_url(database_url)


def reset_password(username: str, new_password: str, require_admin_role: bool):
    db_path = get_database_path()
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    user = conn.execute(
        "SELECT id, username, role, status FROM users WHERE username = ? LIMIT 1",
        (username,),
    ).fetchone()

    if not user:
        conn.close()
        raise SystemExit(f"[error] user not found: {username}")

    if require_admin_role and user["role"] != "admin_builder":
        conn.close()
        raise SystemExit(f"[error] user is not admin_builder: {username}")

    password_hash = pwd_context.hash(new_password)

    conn.execute(
        """
        UPDATE users
        SET password_hash = ?, updated_at = ?
        WHERE username = ?
        """,
        (password_hash, utcnow_iso(), username),
    )
    conn.commit()
    conn.close()

    print(f"[ok] password reset for: {username}")


def main():
    parser = argparse.ArgumentParser(description="Reset local truth-api user password")
    parser.add_argument("--username", required=True, help="target username")
    parser.add_argument("--password", required=True, help="new plaintext password")
    parser.add_argument(
        "--admin-only",
        action="store_true",
        help="require the target user role to be admin_builder",
    )
    args = parser.parse_args()

    reset_password(
        username=args.username,
        new_password=args.password,
        require_admin_role=args.admin_only,
    )


if __name__ == "__main__":
    main()
