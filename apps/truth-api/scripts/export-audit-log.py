#!/usr/bin/env python3
import argparse
import csv
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


def fetch_rows(conn, limit: int):
    return conn.execute(
        """
        SELECT id, actor_user_id, action, target_type, target_id,
               resolved_model_id, result, metadata_json, created_at
        FROM audit_logs
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()


def write_csv(rows, output_path: str):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id", "actor_user_id", "action", "target_type", "target_id",
            "resolved_model_id", "result", "metadata_json", "created_at"
        ])
        for row in rows:
            writer.writerow([
                row["id"],
                row["actor_user_id"],
                row["action"],
                row["target_type"],
                row["target_id"],
                row["resolved_model_id"],
                row["result"],
                row["metadata_json"],
                row["created_at"],
            ])


def write_md(rows, output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# truth-api Audit Export\n\n")
        f.write("| created_at | action | result | actor_user_id | target_type | target_id | model |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for row in rows:
            f.write(
                f"| {row['created_at']} | {row['action']} | {row['result']} | "
                f"{row['actor_user_id'] or ''} | {row['target_type'] or ''} | "
                f"{row['target_id'] or ''} | {row['resolved_model_id'] or ''} |\n"
            )


def main():
    parser = argparse.ArgumentParser(description="Export truth-api audit logs")
    parser.add_argument("--limit", type=int, default=100, help="max rows to export")
    parser.add_argument("--format", choices=["md", "csv"], default="md")
    parser.add_argument("--output", required=True, help="output file path")
    args = parser.parse_args()

    db_path = get_database_path()
    if not Path(db_path).exists():
        raise SystemExit(f"[error] database not found: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = fetch_rows(conn, args.limit)
    conn.close()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    if args.format == "csv":
        write_csv(rows, args.output)
    else:
        write_md(rows, args.output)

    print(f"[ok] exported {len(rows)} audit rows to {args.output}")


if __name__ == "__main__":
    main()
