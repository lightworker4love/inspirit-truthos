# rotate-secrets.md

# truth-api Secret Rotation Guide

## 1. Purpose

This guide defines the safe procedure for rotating secrets used by the local truth-api service.

Rotate secrets deliberately, with backup and validation before and after every change.

## 2. Secrets in scope

Current truth-api scope:

- `SESSION_SECRET`
- `JWT_SECRET`
- `OPENCLAW_GATEWAY_TOKEN`
- `ADMIN_BOOTSTRAP_PASSWORD`
- `CASE_BOOTSTRAP_PASSWORD`

Potential future scope:
- SMTP credentials
- external provider API keys
- Keychain-backed secrets

## 3. Golden rules

1. Backup first.
2. Rotate one class of secret at a time.
3. Validate after each rotation.
4. Keep one known-good rollback point.
5. Do not combine secret rotation with schema changes or routing refactors.

## 4. Pre-rotation checklist

Before rotating anything:

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api
./scripts/backup-restore.sh backup
curl -s http://127.0.0.1:8010/health
curl -s http://127.0.0.1:18789/v1/models
```

Also confirm:
- you can edit `.env`
- you know the current LaunchAgent plist location
- you have a local terminal on the Mac mini
- you can restore quickly if auth breaks

## 5. Rotation order

Recommended order:

### A. Application secrets
Rotate first:
- `SESSION_SECRET`
- `JWT_SECRET`

Impact:
- existing sessions may become invalid
- users may need to log in again

### B. Bootstrap passwords
Rotate next:
- `ADMIN_BOOTSTRAP_PASSWORD`
- `CASE_BOOTSTRAP_PASSWORD`

Important:
- bootstrap variables do not retroactively change existing hashes unless you intentionally re-seed or run a password reset flow

### C. Gateway token
Rotate last:
- `OPENCLAW_GATEWAY_TOKEN`

Impact:
- truth-api to OpenClaw calls fail immediately if token mismatch occurs

## 6. How to rotate application secrets

1. Open `.env`
2. Replace:
   - `SESSION_SECRET`
   - `JWT_SECRET`
3. Save file
4. Restart truth-api:
```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.inspirit.truth-api.plist 2>/dev/null || true
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.inspirit.truth-api.plist
```
5. Validate:
```bash
curl -s http://127.0.0.1:8010/health
```
6. Run smoke test:
```bash
/Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api/scripts/smoke-test.sh
```

## 7. How to rotate bootstrap passwords

1. Update in `.env`:
   - `ADMIN_BOOTSTRAP_PASSWORD`
   - `CASE_BOOTSTRAP_PASSWORD`
2. Decide one of these paths:

### Path 1: bootstrap variables only
Use this only for future seed runs.
Existing accounts remain unchanged.

### Path 2: force password refresh
Update the actual password hashes in the DB with a dedicated reset script or admin tool.
Do not assume seed script will safely overwrite existing users.

## 8. How to rotate OpenClaw gateway token

1. Create a backup first.
2. Update the token in the OpenClaw side according to your gateway auth flow.
3. Update `OPENCLAW_GATEWAY_TOKEN` in truth-api `.env`.
4. Restart truth-api.
5. Validate:
```bash
curl -s http://127.0.0.1:8010/health
/Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api/scripts/smoke-test.sh
```

Important:
- if `/auth/login` works but `/chat` fails, suspect gateway token mismatch first

## 9. Rollback

If rotation fails:

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api
./scripts/backup-restore.sh list
./scripts/backup-restore.sh restore latest
```

Then verify:
```bash
curl -s http://127.0.0.1:8010/health
/Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api/scripts/smoke-test.sh
```

## 10. Future hardening

Preferred future state:
- move high-value secrets to Keychain or another secure secret store
- avoid plaintext long-term storage where possible
- keep launchd environment and app environment aligned
- document last rotation date for each secret class

## 11. Principle

A secret is not truly rotated unless:
- the new value is active
- the service restarted cleanly
- smoke test passed
- rollback remains available
```
