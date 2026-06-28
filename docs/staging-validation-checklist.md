# Blueprint Writeback — Staging Validation Checklist
**Version**: Phase 2  
**Updated**: 2026-03-14  
**Test environment**: `inspirit-truthos-truth-api-1` container; `POST http://localhost:18000/api/truth/query`

---

## How to observe logs during staging

```bash
# Stream all blueprint events (all lifecycle states)
docker logs -f inspirit-truthos-truth-api-1 2>&1 | grep 'blueprint_event='

# Isolate a single event type
docker logs -f inspirit-truthos-truth-api-1 2>&1 | grep 'blueprint_event=blueprint_update_failed'

# Trace a single request across all events
docker logs inspirit-truthos-truth-api-1 2>&1 | grep "request_id='<REQ_ID>'"

# Check daily cap counter state (process restart clears it; this is expected)
# (counter is in-memory — verify via 'blueprint_event=blueprint_update_blocked' with 'daily_cap_reached')
```

---

## Scenario A — Basic success path

### Pre-conditions
1. A case profile JSON exists: `data/cases/case__web__<username>.json`
2. The case has at least 3 entries in `session_memory` for that `user_id` (or use `session_count` override in request — see §D)
3. The message contains life-theme or blind-spot keywords (e.g. "界線", "anxiety", "over-explain")

### Verification steps
```bash
# Step 1: Send a query with identity fields
curl -s -XPOST http://localhost:18000/api/truth/query \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "hank",
    "login_username": "Hank",
    "preferred_name": "Hank",
    "source_channel": "web",
    "session_id": "staging-001",
    "message": "我最近一直在思考界線的問題，anxiety 很高，感覺 over-explain 了很多，boundaries 不清晰"
  }' | python3 -m json.tool

# Step 2: Check logs for the full success chain
docker logs inspirit-truthos-truth-api-1 2>&1 | grep 'blueprint_event=' | tail -10
```

### Expected log sequence
```
blueprint_event=blueprint_update_considered  case_id=... session_count=N ...
blueprint_event=blueprint_update_attempted   case_id=... conversation_char_count=N detected_theme_count=N ...
blueprint_event=blueprint_update_succeeded   updated_fields=['last_session_insight', 'life_themes', 'blind_spots'] ...
```

### Expected result
- API returns `200` with `case_id` populated
- `case__web__hank.json` file updated with new `life_themes` and/or `last_session_insight`
- No error in logs

### If it fails, check
- `skip_reason='profile_not_found'` → create the JSON file first
- `block_reason='gate:...'` → see Scenario B
- `blueprint_update_failed` → check disk space and file permissions in the container

---

## Scenario B — Gate threshold not met

### B.1 — Session count too low

```bash
# Send with a new user_id that has no session_memory rows
curl -s -XPOST http://localhost:18000/api/truth/query \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "new_user",
    "login_username": "new_user",
    "source_channel": "web",
    "session_id": "staging-b1",
    "message": "界線 anxiety over-explain boundaries relationships intimacy"
  }' | python3 -m json.tool
```

**Expected log**:
```
blueprint_event=blueprint_update_considered  session_count=0 ...
blueprint_event=blueprint_update_attempted   ...
blueprint_event=blueprint_update_blocked     block_reason='gate:case too new (0 sessions, need 3)' ...
```
**Expected result**: API returns `200`; `life_themes` NOT written to profile.

### B.2 — Conversation too short

```bash
curl -s -XPOST http://localhost:18000/api/truth/query \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "hank",
    "login_username": "Hank",
    "source_channel": "web",
    "session_id": "staging-b2",
    "message": "hi"
  }' | python3 -m json.tool
```

**Expected log**:
```
blueprint_event=blueprint_update_attempted   conversation_char_count=2 ...
blueprint_event=blueprint_update_blocked     block_reason='gate:conversation too short (2 chars, need 500)' ...
```

### B.3 — Signal density too low

```bash
# Long message with no theme/blind-spot keywords
curl -s -XPOST http://localhost:18000/api/truth/query \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "hank",
    "login_username": "Hank",
    "source_channel": "web",
    "session_id": "staging-b3",
    "message": "今天天氣很好我去公園散步然後吃了一頓好飯心情不錯打算明天繼續維持這個習慣每天走路一小時應該對健康有益希望可以持續下去讓自己更好"
  }' | python3 -m json.tool
```

**Expected log**:
```
blueprint_event=blueprint_update_blocked     block_reason='gate:insufficient signal density ...' ...
```

---

## Scenario C — SOUL_AGE_INFERENCE_ENABLED=False (default)

### Verification
```bash
# Send a query rich in soul_age signals ("status", "win", "control", "prove")
curl -s -XPOST http://localhost:18000/api/truth/query \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "hank",
    "login_username": "Hank",
    "source_channel": "web",
    "session_id": "staging-c",
    "message": "我一直想要 status，想要 win，想要 prove 自己，control everything，beat competition。界線 anxiety over-explain"
  }' | python3 -m json.tool

# Check the case profile — soul_age must be null
cat /path/to/data/cases/case__web__hank.json | python3 -m json.tool | grep soul_age
```

**Expected log**:
- `blueprint_event=blueprint_update_succeeded` with `soul_age_enabled=False`
- `skip_reasons=...soul_age_flag_off...`

**Expected result**: `soul_age` field in JSON file remains `null`.  
**NOT acceptable**: Any non-null `soul_age` value when flag is `False`.

### To test with flag ON (staging only)
```python
# Temporarily flip the flag for one request (inside container repl):
docker exec -it inspirit-truthos-truth-api-1 python -c "
import sys; sys.path.insert(0, '/app/apps/truth-api')
import app.case_insight_service as svc
svc.SOUL_AGE_INFERENCE_ENABLED = True
print('Flag is now:', svc.SOUL_AGE_INFERENCE_ENABLED)
"
# Note: this only affects the module in that one process call — not the running server.
# To properly test with flag on: restart the container with SOUL_AGE_INFERENCE_ENABLED=True env var.
# Do NOT do this in production.
```

---

## Scenario D — Admin backfill with force=True

**This path is NOT accessible through `POST /api/truth/query`. It requires direct Python invocation.**

```python
# Access via container exec (never from production traffic path)
docker exec -it inspirit-truthos-truth-api-1 python -c "
import sys
sys.path.insert(0, '/app/apps/truth-api')
from app.case_resolver import load_case_profile
from app.case_insight_service import update_case_blueprint_from_conversation

profile = load_case_profile('web__hank')
if profile is None:
    print('ERROR: profile not found')
else:
    result = update_case_blueprint_from_conversation(
        profile,
        conversation_messages=[{'role': 'user', 'content': '界線' * 100 + ' anxiety' * 50 + ' over-explain' * 30}],
        model_response={'mirror': 'Backfill test insight.'},
        metadata={'session_count': 0, 'source_channel': 'backfill', 'request_id': 'backfill-001'},
        force=True,  # <-- bypasses session_count and char_count gates
    )
    print('life_themes:', result.life_themes)
    print('last_session_insight:', result.last_session_insight)
"
```

**Expected log** (inside container logs):
```
blueprint_event=blueprint_update_attempted   force=True ...
blueprint_event=blueprint_update_succeeded   updated_fields=[...] ...
```

**Check**: The log must show `force=True`. If `force=True` appears outside a deliberate admin invocation, that is a bug.  
**NOT acceptable**: `force=True` appearing in any normal user query path.

---

## Scenario E — Failure isolation

Simulate a disk write failure and confirm the main API response is unaffected.

```python
# Monkey-patch save in the container (for one call)
docker exec -it inspirit-truthos-truth-api-1 python -c "
import sys
sys.path.insert(0, '/app/apps/truth-api')
import app.case_insight_service as svc
from app.case_models import CaseProfile

_original_save = svc.save_case_profile

def fail_save(p):
    raise OSError('Simulated disk full')

svc.save_case_profile = fail_save

profile = CaseProfile(case_id='web__test', login_username='test', memory_namespace='web__test')
try:
    svc.update_case_blueprint_from_conversation(
        profile,
        conversation_messages=[{'role': 'user', 'content': '界線' * 100 + ' anxiety' * 50}],
        model_response={'mirror': 'Test insight.'},
        metadata={'session_count': 5},
    )
    print('ERROR: should have raised')
except OSError as e:
    print('Correctly re-raised:', e)
finally:
    svc.save_case_profile = _original_save
"
```

**Expected log**:
```
blueprint_event=blueprint_update_attempted ...
blueprint_event=blueprint_update_failed  error_type='OSError' error='Simulated disk full' ...
```

For the full end-to-end isolation test (real HTTP):
```bash
# The main query must succeed even if writeback fails; the response payload must be intact
# Start a temp mock that breaks save, then verify the API response is still 200.
# In practice: verify that when you see blueprint_update_failed in logs, the HTTP 
# response code was still 200 and mirror/truth_view fields are populated.
docker logs inspirit-truthos-truth-api-1 2>&1 | grep -A2 'blueprint_event=blueprint_update_failed' | head -20
```

---

## Scenario F — Daily cap (3 writes/day per case)

```bash
# Send 4 queries for the same case on the same day
for i in 1 2 3 4; do
  curl -s -XPOST http://localhost:18000/api/truth/query \
    -H 'Content-Type: application/json' \
    -d "{
      \"user_id\": \"hank\",
      \"login_username\": \"Hank\",
      \"source_channel\": \"web\",
      \"session_id\": \"staging-cap-$i\",
      \"message\": \"界線 anxiety over-explain relationships boundaries intimacy emotional regulation\"
    }" > /dev/null
  echo "Request $i sent"
done

# Check logs
docker logs inspirit-truthos-truth-api-1 2>&1 | grep 'blueprint_event=' | tail -20
```

**Expected log sequence**:
- Calls 1–3: `blueprint_event=blueprint_update_succeeded` (3 successful writes)
- Call 4: `blueprint_event=blueprint_update_blocked  block_reason='daily_cap_reached:3/3'`

**Expected result**: Call 4's API response still returns `200` with a valid answer.  
**Check**: `_MAX_DAILY_BLUEPRINT_WRITES = 3` (in `case_insight_service.py`). Counter resets on container restart.

---

## Summary: Expected event → log token map

| Scenario | Expected `blueprint_event=` token |
|---|---|
| A (success) | `blueprint_update_considered` → `blueprint_update_attempted` → `blueprint_update_succeeded` |
| B (gate blocked) | `blueprint_update_considered` → `blueprint_update_attempted` → `blueprint_update_blocked` |
| B (profile missing) | `blueprint_update_skipped` (skip_reason='profile_not_found') |
| C (flag off) | `blueprint_update_succeeded` with `skip_reasons=...soul_age_flag_off...` |
| D (force backfill) | `blueprint_update_attempted force=True` → `blueprint_update_succeeded` |
| E (save failure) | `blueprint_update_attempted` → `blueprint_update_failed` |
| F (daily cap) | 1st–3rd: `blueprint_update_succeeded` / 4th+: `blueprint_update_blocked` with `daily_cap_reached` |

---

## Rollback / disable

To fully disable blueprint writeback without a redeploy: currently no env-var kill switch exists (Phase 3 item). Fastest path is to remove the `if case_ctx:` block from `_attempt_blueprint_writeback` in `main.py` and restart the container. Adding an env-var `BLUEPRINT_WRITEBACK_ENABLED=false` is the recommended Phase 3 hardening step.
