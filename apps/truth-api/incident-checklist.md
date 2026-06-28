# incident-checklist.md

# truth-api Incident Checklist

## 1. Purpose

This checklist is for local production-style incidents affecting:
- truth-api
- auth/session flow
- thread creation
- chat routing
- OpenClaw upstream reachability

Use it during real incidents.
Do not improvise config changes before narrowing the failure domain.

## 2. Severity guide

### SEV-1
Core user path is down:
- `/health` fails
- `/auth/login` fails for all users
- `/chat` fails for all users

### SEV-2
Partial degradation:
- login works but chat fails
- only one role is affected
- audit path or thread reads fail

### SEV-3
Non-blocking:
- log noise
- stale sessions
- missing optional exports
- minor admin-only defects

## 3. First 5 minutes

1. Stop changing files.
2. Record current time and symptoms.
3. Confirm scope:
   - all users or one user
   - login or chat or admin only
   - truth-api only or OpenClaw also
4. Run:
```bash
cd /Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api
./scripts/healthcheck.sh
```
5. Capture:
```bash
tail -n 100 ~/.openclaw/logs/truth-api.stderr.log
tail -n 100 ~/.openclaw/logs/truth-api.stdout.log
```

## 4. Triage tree

### A. `/health` fails
Check:
- LaunchAgent status
- `.venv` still exists
- `.env` readable
- recent stderr log
- whether the plist was edited recently

Actions:
1. `launchctl print gui/$(id -u)/ai.inspirit.truth-api`
2. if needed, restart truth-api only
3. do not touch OpenClaw yet

### B. `/auth/login` fails
Check:
- DB file exists
- users table readable
- recent password reset or secret rotation happened
- wrong `.env` or wrong database path

Actions:
1. inspect DB path
2. confirm target user exists
3. if required, use password reset script
4. retest login

### C. login works but `/chat` fails
Check:
- OpenClaw health
- gateway token mismatch
- model policy resolution
- upstream route/schema errors

Actions:
1. `curl -s http://127.0.0.1:18789/v1/models`
2. run app smoke test
3. inspect stderr for upstream errors
4. suspect `OPENCLAW_GATEWAY_TOKEN` before rewriting app logic

### D. threads fail but health is OK
Check:
- SQLite schema drift
- missing `case_threads` / `case_entries`
- accidental restore of stale DB

Actions:
1. inspect tables
2. compare with latest backup manifest
3. restore only if schema or DB corruption is confirmed

## 5. Safe commands

### Health
```bash
curl -s http://127.0.0.1:8010/health
curl -s http://127.0.0.1:18789/v1/models
```

### LaunchAgent
```bash
launchctl print gui/$(id -u)/ai.inspirit.truth-api
launchctl print gui/$(id -u)/ai.openclaw.gateway
```

### Logs
```bash
tail -n 100 ~/.openclaw/logs/truth-api.stderr.log
tail -n 100 ~/.openclaw/logs/truth-api.stdout.log
```

### Backup and restore
```bash
./scripts/backup-restore.sh backup
./scripts/backup-restore.sh list
./scripts/backup-restore.sh restore latest
```

### Password reset
```bash
source .venv/bin/activate
python scripts/password-reset-admin.py --username lightworker-admin --password 'new-password' --admin-only
```

## 6. Unsafe actions during incident

Do not do these in the first response window:

- rotate secrets and edit schema in the same incident
- change truth-api and OpenClaw config simultaneously
- re-seed blindly into an unknown DB state
- overwrite `openclaw.json` without a backup
- patch code before confirming whether the issue is configuration or runtime reachability

## 7. Recovery definition

Incident is only considered resolved when all are true:

1. `truth-api /health` returns OK
2. OpenClaw `/v1/models` returns OK
3. login works
4. one thread can be created
5. one chat request succeeds
6. logs stop showing new critical errors

## 8. Aftercare

After recovery:

1. write a short timeline
2. record root cause
3. note what changed
4. create or update the relevant runbook
5. decide whether backup cadence or rotation cadence needs improvement

## 9. Principle

During incidents, clarity beats speed.

A fast wrong fix creates a second incident.
A slow clean boundary check usually restores the field.
```
