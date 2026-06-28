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


def sqlite_path_from_database_url(database_url: str) -> str:
    prefix = "sqlite:///"
    return database_url[len(prefix):] if database_url.startswith(prefix) else database_url


def get_database_path() -> Path:
    database_url = os.getenv(
        "DATABASE_URL",
        "sqlite:////Users/tongwei/.openclaw/data/in-spirit-case-auth.db",
    )
    return Path(sqlite_path_from_database_url(database_url))


def parse_date_from_filename(path: Path):
    m = re.search(r"daily-report-(\d{4}-\d{2}-\d{2})\.md$", path.name)
    if not m:
        return None
    return datetime.strptime(m.group(1), "%Y-%m-%d").date()


def collect_daily_reports(days: int = 7):
    files = sorted(DAILY_DIR.glob("daily-report-*.md"))
    dated = []
    for f in files:
        d = parse_date_from_filename(f)
        if d:
            dated.append((d, f))
    dated.sort(key=lambda x: x[0], reverse=True)
    return dated[:days]


def count_report_statuses(reports):
    truth_ok = 0
    openclaw_ok = 0
    warnings = 0

    for _, path in reports:
        text = path.read_text(encoding="utf-8")
        if "- truth-api health: OK" in text:
            truth_ok += 1
        if "- OpenClaw health: OK" in text:
            openclaw_ok += 1
        warnings += text.count("[WARN]") + text.count("WARN")

    return truth_ok, openclaw_ok, warnings


def load_recent_audits(conn, since_iso: str):
    rows = conn.execute(
        """
        SELECT action, result, created_at
        FROM audit_logs
        WHERE created_at >= ?
        ORDER BY created_at DESC
        """,
        (since_iso,),
    ).fetchall()
    return rows


def main():
    WEEKLY_DIR.mkdir(parents=True, exist_ok=True)
    reports = collect_daily_reports(7)

    today = datetime.now().date()
    week_start = today - timedelta(days=6)
    output_path = WEEKLY_DIR / f"weekly-summary-{today.strftime('%Y-%m-%d')}.md"

    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    since_dt = datetime.now(timezone.utc) - timedelta(days=7)
    since_iso = since_dt.isoformat()

    audit_rows = load_recent_audits(conn, since_iso)
    conn.close()

    action_counter = Counter([r["action"] for r in audit_rows])
    result_counter = Counter([r["result"] for r in audit_rows])

    truth_ok, openclaw_ok, warnings = count_report_statuses(reports)

    expected_dates = {today - timedelta(days=i) for i in range(7)}
    actual_dates = {d for d, _ in reports}
    missing_dates = sorted(expected_dates - actual_dates)

    lines = []
    lines.append("# truth-api Weekly Ops Summary")
    lines.append("")
    lines.append(f"- Week window: {week_start.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}")
    lines.append(f"- Daily reports found: {len(reports)}/7")
    lines.append(f"- truth-api OK days: {truth_ok}")
    lines.append(f"- OpenClaw OK days: {openclaw_ok}")
    lines.append(f"- warning markers found: {warnings}")
    lines.append("")

    lines.append("## Daily files")
    lines.append("")
    if reports:
        for d, path in sorted(reports, key=lambda x: x[0]):
            lines.append(f"- {d.strftime('%Y-%m-%d')}: {path}")
    else:
        lines.append("- none")
    lines.append("")

    lines.append("## Missing dates")
    lines.append("")
    if missing_dates:
        for d in missing_dates:
            lines.append(f"- {d.strftime('%Y-%m-%d')}")
    else:
        lines.append("- none")
    lines.append("")

    lines.append("## Audit action totals")
    lines.append("")
    if action_counter:
        for action, count in action_counter.most_common(15):
            lines.append(f"- {action}: {count}")
    else:
        lines.append("- none")
    lines.append("")

    lines.append("## Audit result totals")
    lines.append("")
    if result_counter:
        for result, count in result_counter.most_common():
            lines.append(f"- {result}: {count}")
    else:
        lines.append("- none")
    lines.append("")

    lines.append("## Focus for next week")
    lines.append("")
    lines.append("- Review any missing daily reports and confirm LaunchAgent schedule.")
    lines.append("- Investigate repeated failure actions if result=failure appears more than expected.")
    lines.append("- Keep truth-api and OpenClaw boundary changes isolated to reduce blast radius.")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[ok] rendered weekly summary: {output_path}")


if __name__ == "__main__":
    main()
