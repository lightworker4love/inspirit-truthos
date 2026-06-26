# README-dev.md

# in spirit truth-api Dev README

## 1. Purpose

This service provides the local identity, role policy, and model routing layer for the in spirit platform.

It sits in front of OpenClaw Gateway and ensures:
- authenticated access
- role-based model allowlists
- auditable thread creation
- safe upstream routing into the existing OpenClaw stack

## 2. Local architecture

Current local assumptions:

- truth-api path:
  `/Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api`
- OpenClaw Gateway:
  `http://127.0.0.1:18789`
- SQLite DB:
  `~/.openclaw/data/in-spirit-case-auth.db`
- Schema file:
  `~/.openclaw/control-plane/in-spirit-case-auth-model-routing-db-schema-v1.sql`

The backend should be treated as the policy enforcement layer.
Case clients must not call raw OpenClaw Gateway directly.

## 3. First-time setup

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api
cp .env.template .env
```

Edit `.env` and fill at least:
- `SESSION_SECRET`
- `JWT_SECRET`
- `OPENCLAW_GATEWAY_TOKEN`
- `ADMIN_BOOTSTRAP_PASSWORD`
- `CASE_BOOTSTRAP_PASSWORD`

Then run:

```bash
make bootstrap
```

## 4. Start in dev mode

```bash
./run-dev.sh
```

or:

```bash
make run
```

Default local URL:
- `http://127.0.0.1:8010`

Health check:
```bash
curl -s http://127.0.0.1:8010/health
```

## 5. Smoke test

In another terminal:

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api
make smoke
```

This verifies:
- health endpoint
- login
- allowed modes
- thread creation
- chat route

## 6. Tests

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api
source .venv/bin/activate
pytest
```

## 7. launchd workflow

Recommended plist location:

```text
~/Library/LaunchAgents/ai.inspirit.truth-api.plist
```

Typical commands:

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.inspirit.truth-api.plist 2>/dev/null || true
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.inspirit.truth-api.plist
launchctl print gui/$(id -u)/ai.inspirit.truth-api
```

## 8. Logs

Suggested stdout log:
- `~/.openclaw/logs/truth-api.stdout.log`

Suggested stderr log:
- `~/.openclaw/logs/truth-api.stderr.log`

Tail logs:

```bash
tail -f ~/.openclaw/logs/truth-api.stdout.log
tail -f ~/.openclaw/logs/truth-api.stderr.log
```

## 9. Daily operator checklist

1. Confirm OpenClaw Gateway is healthy:
```bash
curl -s http://127.0.0.1:18789/v1/models
```

2. Confirm truth-api is healthy:
```bash
curl -s http://127.0.0.1:8010/health
```

3. Confirm local DB exists:
```bash
ls -lh ~/.openclaw/data/in-spirit-case-auth.db
```

4. Confirm launchd job is loaded:
```bash
launchctl print gui/$(id -u)/ai.inspirit.truth-api >/dev/null && echo OK || echo NOT_LOADED
```

## 10. Failure notes

### Auth works but chat fails
Check:
- `OPENCLAW_GATEWAY_TOKEN`
- OpenClaw upstream health
- selected role/mode policy
- stderr log

### Mode denied
Check:
- `model_policies` table
- current user role
- `/models/allowed`

### Upstream schema errors
Do not send UI-only fields like `display_name` or `login_username` into raw upstream payload root fields.

## 11. Principle

This service is not a general-purpose chat relay.

It is the local boundary layer that protects:
- role clarity
- model boundaries
- session integrity
- auditability
```
