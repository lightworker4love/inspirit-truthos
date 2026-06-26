# README-prod.md

# in spirit truth-api Production README

## 1. Purpose

This document defines the production-style operating rules for the local `truth-api` service on the Mac mini.

The goal is stability, recoverability, and clean separation between:
- truth-api as the policy boundary layer
- OpenClaw Gateway as the orchestration/runtime layer
- `~/.openclaw/openclaw.json` as the OpenClaw source of truth

## 2. Runtime assumptions

Production-style local assumptions:

- Host: Mac mini
- truth-api path:
  `/Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api`
- truth-api bind:
  `127.0.0.1:8010`
- OpenClaw Gateway bind:
  `127.0.0.1:18789`
- SQLite DB:
  `/Users/tongwei/.openclaw/data/in-spirit-case-auth.db`
- OpenClaw config:
  `/Users/tongwei/.openclaw/openclaw.json`

## 3. Responsibilities

truth-api is responsible for:
- authentication
- role enforcement
- mode-to-model resolution
- thread persistence
- audit persistence

truth-api is not responsible for:
- replacing OpenClaw runtime configuration
- exposing raw gateway credentials to clients
- allowing arbitrary model IDs from frontend payloads

## 4. Required files

Before enabling production-style local operation, confirm these files exist:

- `.env`
- `.venv/`
- `scripts/seed-admin.py`
- `scripts/smoke-test.sh`
- `~/Library/LaunchAgents/ai.inspirit.truth-api.plist`
- `~/.openclaw/control-plane/in-spirit-case-auth-model-routing-db-schema-v1.sql`

## 5. Daily checks

### Service health

```bash
curl -s http://127.0.0.1:8010/health
curl -s http://127.0.0.1:18789/v1/models
```

### LaunchAgent status

```bash
launchctl print gui/$(id -u)/ai.inspirit.truth-api >/dev/null && echo truth-api:OK || echo truth-api:NOT_LOADED
launchctl print gui/$(id -u)/ai.openclaw.gateway >/dev/null && echo openclaw:OK || echo openclaw:NOT_LOADED
```

### DB and logs

```bash
ls -lh /Users/tongwei/.openclaw/data/in-spirit-case-auth.db
tail -n 50 /Users/tongwei/.openclaw/logs/truth-api.stderr.log
tail -n 50 /Users/tongwei/.openclaw/logs/truth-api.stdout.log
```

## 6. Safe restart

### Restart truth-api only

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.inspirit.truth-api.plist 2>/dev/null || true
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.inspirit.truth-api.plist
```

### Verify

```bash
curl -s http://127.0.0.1:8010/health
```

## 7. Backup rule

Always run a backup before:
- editing `.env`
- rotating gateway token
- changing LaunchAgent plist
- replacing SQLite schema
- editing `openclaw.json`
- changing model policies or active prompts

Use:
```bash
./scripts/backup-restore.sh backup
```

## 8. Restore rule

If truth-api breaks after config or secret changes:

1. stop truth-api LaunchAgent
2. restore the latest known-good snapshot
3. restart truth-api
4. run smoke test
5. only then consider touching OpenClaw

Use:
```bash
./scripts/backup-restore.sh list
./scripts/backup-restore.sh restore latest
```

## 9. Secret rotation rule

Rotate these independently when possible:

- `SESSION_SECRET`
- `JWT_SECRET`
- `OPENCLAW_GATEWAY_TOKEN`
- bootstrap passwords
- future SMTP or external provider secrets

Use:
```bash
open rotate-secrets.md
```

## 10. Incident triage

### Case A: health endpoint fails
Check:
- LaunchAgent loaded
- `.venv` exists
- `.env` readable
- stderr log

### Case B: login works but `/chat` fails
Check:
- `OPENCLAW_GATEWAY_TOKEN`
- OpenClaw Gateway health
- model policy lookup
- upstream response in stderr log

### Case C: data appears missing
Check:
- DB path
- schema drift
- wrong `.env`
- accidental restore from stale snapshot

### Case D: OpenClaw changes caused downstream issues
Do not patch truth-api first.
Confirm `~/.openclaw/openclaw.json` and the active gateway state before changing app logic.

## 11. Upgrade discipline

Before any meaningful upgrade:
1. backup
2. record current git state
3. record current `.env` checksum locally
4. restart truth-api only
5. run smoke test
6. only then widen the blast radius

## 12. Principle

This service protects the boundary between identity and inference.

A good production posture here means:
- secrets are rotated deliberately
- backups are recent
- restore is tested
- OpenClaw remains the runtime truth
- truth-api remains the policy truth
```
