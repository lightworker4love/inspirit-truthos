#!/usr/bin/env python3
import os
import re
import sqlite3
import socket
from datetime import datetime, timezone
from pathlib import Path


APP_DIR = Path("/Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api")
REPORT_ROOT = Path("/Users/tongwei/.openclaw/reports")
TEMPLATE_PATH = APP_DIR / "daily-report.md.template"
OPS_LATEST_PATH = REPORT_ROOT / "ops-daily-check-latest.txt"
AUDIT_LATEST_PATH = REPORT_ROOT / "audit-latest.md"


def sqlite_path_from_database_url(database_url: str) -> str:
    prefix = "sqlite:///"
    return database_url[len(prefix):] if database_url.startswith(prefix) else database_url


def get_database_path() -> Path:
    database_url = os.getenv(
        "DATABASE_URL",
        "sqlite:////Users/tongwei/.openclaw/data/in-spirit-case-auth.db",
    )
    return Path(sqlite_path_from_database_url(database_url))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def fetch_scalar(conn, sql: str, params=()):
    row = conn.execute(sql, params).fetchone()
    return row[0] if row else 0


def recent_actions(conn, keyword: str, limit: int = 5) -> str:
    rows = conn.execute(
        """
        SELECT created_at, action, result
        FROM audit_logs
        WHERE action LIKE ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (f"%{keyword}%", limit),
    ).fetchall()
    if not rows:
        return "none"
    return "; ".join([f"{r['created_at']} {r['action']}={r['result']}" for r in rows])


def summarize_ops_lines(ops_text: str, prefix: str) -> str:
    lines = [line.strip() for line in ops_text.splitlines() if line.strip().startswith(prefix)]
    return "; ".join(lines[:5]) if lines else "none"


def infer_health(ops_text: str, needle: str) -> str:
    if f"[OK] {needle}" in ops_text:
        return "OK"
    if f"[FAIL] {needle}" in ops_text:
        return "FAIL"
    return "UNKNOWN"


def infer_launchd(ops_text: str, needle: str) -> str:
    if f"[OK] {needle}" in ops_text:
        return "LOADED"
    if f"[WARN] {needle}" in ops_text:
        return "NOT_LOADED"
    return "UNKNOWN"


def render(template: str, mapping: dict[str, str]) -> str:
    text = template
    for key, value in mapping.items():
        text = text.replace(f"{{{{{key}}}}}", str(value))
    return text


def main():
    db_path = get_database_path()
    if not db_path.exists():
        raise SystemExit(f"[error] database not found: {db_path}")

    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    daily_dir = REPORT_ROOT / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    output_path = daily_dir / f"daily-report-{today}.md"

    template = read_text(TEMPLATE_PATH)
    if not template:
        template = """# in spirit truth-api Daily Ops Report

- Date: {{DATE}}
- Host: {{HOSTNAME}}
- Operator: {{OPERATOR}}
- Service: truth-api
- Environment: {{ENVIRONMENT}}

## Health summary

- truth-api health: {{TRUTH_API_HEALTH}}
- OpenClaw health: {{OPENCLAW_HEALTH}}
- truth-api LaunchAgent: {{TRUTH_API_LAUNCHD}}
- OpenClaw LaunchAgent: {{OPENCLAW_LAUNCHD}}

## Database snapshot

- DB path: {{DB_PATH}}
- users count: {{USERS_COUNT}}
- case_profiles count: {{CASE_PROFILES_COUNT}}
- case_threads count: {{CASE_THREADS_COUNT}}
- case_entries count: {{CASE_ENTRIES_COUNT}}
- audit_logs count: {{AUDIT_LOGS_COUNT}}

## Audit highlights

- latest login events: {{LOGIN_EVENTS}}
- latest thread events: {{THREAD_EVENTS}}
- latest chat success/failure: {{CHAT_EVENTS}}

## Recent anomalies

- stderr summary: {{STDERR_SUMMARY}}
- stdout summary: {{STDOUT_SUMMARY}}
- open items: {{OPEN_ITEMS}}

## Actions taken today

1. {{ACTION_1}}
2. {{ACTION_2}}
3. {{ACTION_3}}

## Next checks

- {{NEXT_CHECK_1}}
- {{NEXT_CHECK_2}}
- {{NEXT_CHECK_3}}
"""

    ops_text = read_text(OPS_LATEST_PATH)
    audit_text = read_text(AUDIT_LATEST_PATH)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    mapping = {
        "DATE": today,
        "HOSTNAME": socket.gethostname(),
        "OPERATOR": os.getenv("USER", "unknown"),
        "ENVIRONMENT": os.getenv("APP_ENV", "development"),
        "TRUTH_API_HEALTH": infer_health(ops_text, "truth-api reachable"),
        "OPENCLAW_HEALTH": infer_health(ops_text, "OpenClaw reachable"),
        "TRUTH_API_LAUNCHD": infer_launchd(ops_text, "truth-api LaunchAgent loaded"),
        "OPENCLAW_LAUNCHD": infer_launchd(ops_text, "OpenClaw LaunchAgent loaded"),
        "DB_PATH": str(db_path),
        "USERS_COUNT": str(fetch_scalar(conn, "SELECT COUNT(*) FROM users")),
        "CASE_PROFILES_COUNT": str(fetch_scalar(conn, "SELECT COUNT(*) FROM case_profiles")),
        "CASE_THREADS_COUNT": str(fetch_scalar(conn, "SELECT COUNT(*) FROM case_threads")),
        "CASE_ENTRIES_COUNT": str(fetch_scalar(conn, "SELECT COUNT(*) FROM case_entries")),
        "AUDIT_LOGS_COUNT": str(fetch_scalar(conn, "SELECT COUNT(*) FROM audit_logs")),
        "LOGIN_EVENTS": recent_actions(conn, "login"),
        "THREAD_EVENTS": recent_actions(conn, "thread"),
        "CHAT_EVENTS": recent_actions(conn, "chat"),
        "STDERR_SUMMARY": summarize_ops_lines(ops_text, "[FAIL]") or "none",
        "STDOUT_SUMMARY": "audit export present" if audit_text else "no audit export found",
        "OPEN_ITEMS": summarize_ops_lines(ops_text, "[WARN]"),
        "ACTION_1": "Automated daily check executed.",
        "ACTION_2": "Latest audit snapshot exported.",
        "ACTION_3": "Rendered markdown daily report.",
        "NEXT_CHECK_1": "Review WARN or FAIL lines if present.",
        "NEXT_CHECK_2": "Confirm smoke test still passes after any config change.",
        "NEXT_CHECK_3": "Inspect weekly summary on Monday.",
    }

    conn.close()

    content = render(template, mapping)
    output_path.write_text(content, encoding="utf-8")
    print(f"[ok] rendered daily report: {output_path}")


if __name__ == "__main__":
    main()
