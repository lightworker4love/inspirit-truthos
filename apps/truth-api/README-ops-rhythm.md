# README-ops-rhythm.md

# truth-api Ops Rhythm

## 1. Purpose

This document defines the operating rhythm for the local truth-api service.

The goal is to turn raw checks into durable operational memory:
- daily awareness
- weekly reflection
- monthly pattern recognition
- incident learning

## 2. Layers

Current local rhythm assumes two main layers:

- truth-api = policy boundary layer
- OpenClaw Gateway = runtime/orchestration layer

Do not blur these layers during routine changes or incidents.

## 3. Daily rhythm

Run automatically every day:
- `scripts/ops-daily-check.sh`
- `scripts/export-audit-log.py`
- `scripts/render-daily-report.py`

Outputs:
- `~/.openclaw/reports/ops-daily-check-latest.txt`
- `~/.openclaw/reports/audit-latest.md`
- `~/.openclaw/reports/daily/daily-report-YYYY-MM-DD.md`

Daily intention:
- verify health
- observe warnings
- retain one written trace of the day

## 4. Weekly rhythm

Run automatically every Monday:
- `scripts/ops-weekly-summary.py`

Output:
- `~/.openclaw/reports/weekly/weekly-summary-YYYY-MM-DD.md`

Weekly intention:
- detect repeating warnings
- notice missing daily reports
- identify recurring failure classes

## 5. Monthly rhythm

Run on the first day of each month, or manually after month-end:
- `scripts/ops-monthly-summary.py`

Output:
- `~/.openclaw/reports/monthly/monthly-summary-YYYY-MM.md`

Monthly intention:
- review trends instead of isolated errors
- assess whether operations are becoming calmer or more chaotic
- decide what should become policy, automation, or a new runbook

## 6. Incident rhythm

When a real incident occurs:

1. stabilize the boundary
2. confirm health endpoints
3. reduce blast radius
4. restore service
5. render a postmortem

Use:
- `scripts/healthcheck.sh`
- `scripts/backup-restore.sh`
- `scripts/render-incident-postmortem.py`

Incident output:
- `~/.openclaw/reports/incidents/incident-YYYY-MM-DD-<id>.md`

## 7. Human discipline

A useful ops rhythm depends on restraint.

Do not:
- rotate secrets during unrelated incidents
- patch truth-api and OpenClaw blindly at the same time
- treat terminal scrollback as documentation
- postpone writing the postmortem until details fade

## 8. Suggested cadence

### Every morning
- review the latest daily report
- scan WARN and FAIL lines
- confirm no silent drift

### Every Monday
- read the weekly summary
- convert repeated issues into tasks or runbooks

### Every month
- read the monthly summary slowly
- ask which problems are structural, not accidental
- decide the next layer of automation

## 9. Principle

Operations mature when memory becomes ritual.

Daily checks protect the present.
Weekly summaries reveal patterns.
Monthly summaries teach direction.
Postmortems turn pain into architecture.
