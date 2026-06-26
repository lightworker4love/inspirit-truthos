#!/usr/bin/env python3
import json
import os
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime


APP_DIR = Path("/Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api")
REPORT_ROOT = Path("/Users/tongwei/.openclaw/reports")
LOG_ROOT = Path("/Users/tongwei/.openclaw/logs")
DB_DEFAULT = "sqlite:////Users/tongwei/.openclaw/data/in-spirit-case-auth.db"

TRUTH_API_URL = os.getenv("TRUTH_API_URL", "http://127.0.0.1:8010/health")
OPENCLAW_URL = os.getenv("OPENCLAW_URL", "http://127.0.0.1:18789/v1/models")


def sqlite_path_from_database_url(database_url: str) -> str:
    prefix = "sqlite:///"
    return database_url[len(prefix):] if database_url.startswith(prefix) else database_url


def run(cmd: list[str]) -> tuple[int, str]:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        return 0, out.strip()
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output.strip()


def curl_ok(url: str) -> bool:
    code, _ = run(["curl", "-fsS", url])
    return code == 0


def launchd_loaded(label: str) -> bool:
    code, _ = run(["launchctl", "print", f"gui/{os.getuid()}/{label}"])
    return code == 0


def file_tail(path: Path, n: int = 5) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    return text[-n:]


def db_counts(db_path: Path) -> dict:
    if not db_path.exists():
        return {"exists": False}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    tables = [
        "users",
        "case_profiles",
        "auth_sessions",
        "case_threads",
        "case_entries",
        "audit_logs",
        "model_policies",
        "prompt_versions",
    ]
    counts = {"exists": True}
    for table in tables:
        try:
            counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        except sqlite3.Error:
            counts[table] = None
    recent = conn.execute("""
        SELECT action, result, created_at
        FROM audit_logs
        ORDER BY created_at DESC
        LIMIT 5
    """).fetchall()
    counts["recent_audit"] = [dict(r) for r in recent]
    conn.close()
    return counts


def main():
    db_url = os.getenv("DATABASE_URL", DB_DEFAULT)
    db_path = Path(sqlite_path_from_database_url(db_url))

    status = {
        "generated_at": datetime.now().isoformat(),
        "host": os.uname().nodename,
        "paths": {
            "app_dir": str(APP_DIR),
            "report_root": str(REPORT_ROOT),
            "log_root": str(LOG_ROOT),
            "db_path": str(db_path),
        },
        "health": {
            "truth_api": curl_ok(TRUTH_API_URL),
            "openclaw": curl_ok(OPENCLAW_URL),
        },
        "launchd": {
            "truth_api": launchd_loaded("ai.inspirit.truth-api"),
            "openclaw": launchd_loaded("ai.openclaw.gateway"),
            "ops_daily": launchd_loaded("ai.inspirit.ops-daily-check"),
            "ops_weekly": launchd_loaded("ai.inspirit.ops-weekly-summary"),
            "ops_monthly": launchd_loaded("ai.inspirit.ops-monthly-summary"),
        },
        "reports": {
            "daily_latest": str(REPORT_ROOT / "daily"),
            "weekly_latest": str(REPORT_ROOT / "weekly"),
            "monthly_latest": str(REPORT_ROOT / "monthly"),
            "incident_dir": str(REPORT_ROOT / "incidents"),
        },
        "db": db_counts(db_path),
        "logs": {
            "truth_api_stdout_tail": file_tail(LOG_ROOT / "truth-api.stdout.log"),
            "truth_api_stderr_tail": file_tail(LOG_ROOT / "truth-api.stderr.log"),
            "ops_daily_stdout_tail": file_tail(LOG_ROOT / "ops-daily-check.stdout.log"),
            "ops_daily_stderr_tail": file_tail(LOG_ROOT / "ops-daily-check.stderr.log"),
        },
    }

    print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
