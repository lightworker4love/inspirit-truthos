#!/usr/bin/env python3
import os
import re
import sqlite3
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


REPORT_ROOT = Path("/Users/tongwei/.openclaw/reports")
DAILY_DIR = REPORT_ROOT / "daily"
WEEKLY_DIR = REPORT_ROOT / "weekly"
INCIDENT_DIR = REPORT_ROOT / "incidents"
MONTHLY_DIR = REPORT_ROOT / "monthly"


def sqlite_path_from_database_url(database_url: str) -> str:
    prefix = "sqlite:///"
    return database_url[len(prefix):] if database_url.startswith(prefix) else database_url


def get_database_path() -> Path:
    database_url = os.getenv(
        "DATABASE_URL",
        "sqlite:////Users/tongwei/.openclaw/data/in-spirit-case-auth.db",
    )
    return Path(sqlite_path_from_database_url(database_url))


def in_current_month(path: Path) -> bool:
    m = re.search(r"(\d{4}-\d{2}-\d{2})", path.name)
    if not m:
        return False
    try:
        d = datetime.strptime(m.group(1), "%Y-%m-%d").date()
    except ValueError:
        return False
    today = datetime.now().date()
    return d.year == today.year and d.month == today.month


def list_month_files(directory: Path, pattern: str):
    return sorted([p for p in directory.glob(pattern) if in_current_month(p)])


def load_recent_audits(conn, since_iso: str):
    return conn.execute(
        """
        SELECT action, result, created_at
        FROM audit_logs
        WHERE created_at >= ?
        ORDER BY created_at DESC
        """,
        (since_iso,),
    ).fetchall()


def main():
    MONTHLY_DIR.mkdir(parents=True, exist_ok=True)

    today = datetime.now().date()
    month_key = today.strftime("%Y-%m")
    output_path = MONTHLY_DIR / f"monthly-summary-{month_key}.md"

    daily_files = list_month_files(DAILY_DIR, "daily-report-*.md")
    weekly_files = list_month_files(WEEKLY_DIR, "weekly-summary-*.md")
    incident_files = list_month_files(INCIDENT_DIR, "incident-*.md")

    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    month_start = today.replace(day=1)
    since_dt = datetime.combine(month_start, datetime.min.time(), tzinfo=timezone.utc)
    audit_rows = load_recent_audits(conn, since_dt.isoformat())

    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_threads = conn.execute("SELECT COUNT(*) FROM case_threads").fetchone()[0]
    total_entries = conn.execute("SELECT COUNT(*) FROM case_entries").fetchone()[0]
    total_audit = conn.execute("SELECT COUNT(*) FROM audit_logs").fetchone()[0]
    conn.close()

    action_counter = Counter([row["action"] for row in audit_rows])
    result_counter = Counter([row["result"] for row in audit_rows])

    lines = []
    lines.append("# truth-api Monthly Ops Summary")
    lines.append("")
    lines.append(f"- Month: {month_key}")
    lines.append(f"- Daily reports this month: {len(daily_files)}")
    lines.append(f"- Weekly summaries this month: {len(weekly_files)}")
    lines.append(f"- Incident postmortems this month: {len(incident_files)}")
    lines.append("")

    lines.append("## Current database totals")
    lines.append("")
    lines.append(f"- users: {total_users}")
    lines.append(f"- case_threads: {total_threads}")
    lines.append(f"- case_entries: {total_entries}")
    lines.append(f"- audit_logs: {total_audit}")
    lines.append("")

    lines.append("## Audit activity this month")
    lines.append("")
    if action_counter:
        for action, count in action_counter.most_common(20):
            lines.append(f"- {action}: {count}")
    else:
        lines.append("- none")
    lines.append("")

    lines.append("## Audit outcomes this month")
    lines.append("")
    if result_counter:
        for result, count in result_counter.most_common():
            lines.append(f"- {result}: {count}")
    else:
        lines.append("- none")
    lines.append("")

    lines.append("## Files generated this month")
    lines.append("")
    lines.append("### Daily reports")
    if daily_files:
        for p in daily_files[-10:]:
            lines.append(f"- {p.name}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("### Weekly summaries")
    if weekly_files:
        for p in weekly_files:
            lines.append(f"- {p.name}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("### Incident postmortems")
    if incident_files:
        for p in incident_files:
            lines.append(f"- {p.name}")
    else:
        lines.append("- none")
    lines.append("")

    lines.append("## Operator reflections")
    lines.append("")
    lines.append("- Which failures repeated more than once this month?")
    lines.append("- Which manual checks should become scripts next month?")
    lines.append("- Which boundary changes touched both truth-api and OpenClaw and increased risk?")
    lines.append("")

    lines.append("## Next month focus")
    lines.append("")
    lines.append("- Keep daily and weekly report cadence intact.")
    lines.append("- Convert repeated incident patterns into runbooks or alerts.")
    lines.append("- Protect the boundary between policy layer and runtime layer.")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[ok] rendered monthly summary: {output_path}")


if __name__ == "__main__":
    main()
