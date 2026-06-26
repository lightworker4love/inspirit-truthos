# README-runbooks-index.md

# truth-api Runbooks Index

## 1. Purpose

This document is the operator index for the local truth-api ops system.

Use it as the first stop when:
- something breaks
- a report looks strange
- a secret must be rotated
- a backup or restore is needed
- a new operator needs orientation

## 2. Core paths

- Project root:
  `/Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api`
- Reports root:
  `/Users/tongwei/.openclaw/reports`
- Logs root:
  `/Users/tongwei/.openclaw/logs`
- DB path:
  `/Users/tongwei/.openclaw/data/in-spirit-case-auth.db`
- OpenClaw config:
  `/Users/tongwei/.openclaw/openclaw.json`

## 3. Daily operations

### Daily service checks
- Script: `scripts/ops-daily-check.sh`
- Purpose: verify health, launchd state, DB presence, and recent logs

### Daily report rendering
- Script: `scripts/render-daily-report.py`
- Purpose: convert raw daily checks into markdown daily report

### Daily audit export
- Script: `scripts/export-audit-log.py`
- Purpose: export audit activity into markdown or csv

## 4. Weekly and monthly operations

### Weekly summary
- Script: `scripts/ops-weekly-summary.py`
- LaunchAgent: `launchd/ai.inspirit.ops-weekly-summary.plist`
- Purpose: summarize the last 7 daily reports and recent audit activity

### Monthly summary
- Script: `scripts/ops-monthly-summary.py`
- LaunchAgent: `launchd/ai.inspirit.ops-monthly-summary.plist`
- Purpose: summarize the current month’s reports, incidents, and audit trends

## 5. Health and incident response

### Fast health check
- Script: `scripts/healthcheck.sh`
- Purpose: verify truth-api, OpenClaw, LaunchAgents, DB, and logs

### Incident checklist
- File: `incident-checklist.md`
- Purpose: guide first 5 minutes, triage tree, safe commands, and recovery definition

### Incident postmortem
- Script: `scripts/render-incident-postmortem.py`
- Purpose: turn incident details into reusable operational memory

## 6. Backup and recovery

### Backup and restore
- Script: `scripts/backup-restore.sh`
- Purpose: snapshot `.env`, SQLite DB, LaunchAgent plist, and `openclaw.json`

### Production guide
- File: `README-prod.md`
- Purpose: define safe restart, backup, restore, and upgrade posture

## 7. Secrets and accounts

### Secret rotation
- File: `rotate-secrets.md`
- Purpose: define safe secret rotation order and rollback discipline

### Admin password reset
- Script: `scripts/password-reset-admin.py`
- Purpose: reset a local user password safely

### Demo case reseed
- Script: `scripts/reseed-case-demo.py`
- Purpose: recreate a clean case demo account and profile

## 8. Database inspection

### DB inspect
- Script: `scripts/db-inspect.py`
- Purpose: inspect table counts, users, case profiles, threads, prompts, and audits

## 9. Entry points

### Single manual entry point
```bash
make ops-report
```

### truth-api service
- LaunchAgent: `~/Library/LaunchAgents/ai.inspirit.truth-api.plist`

### OpenClaw gateway service
- LaunchAgent: `~/Library/LaunchAgents/ai.openclaw.gateway.plist`

## 10. Reading order

If you are new, read in this order:

1. `README-dev.md`
2. `README-prod.md`
3. `README-ops-rhythm.md`
4. `README-runbooks-index.md`

If something is broken, read in this order:

1. `incident-checklist.md`
2. `README-prod.md`
3. `rotate-secrets.md`
4. latest files under `~/.openclaw/reports/`

## 11. Principle

A runbook is not paperwork.

It is compressed memory for the next difficult moment.
