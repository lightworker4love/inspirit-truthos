# Host Operator Environment Discovery Guide

**Purpose:** Determine the correct LLM provider base URL and model alias available to the `truth-api` container, without editing any application code.

> [!IMPORTANT]
> Run these commands from the host machine terminal only. Do NOT modify any Python files or environment variables during this discovery phase. Record outputs for use in a future Phase 1C reactivation request.

---

## Step 1: Rebuild the Docker Image Properly

This ensures the `jsonschema` dependency (added to `requirements.txt` in Phase 1B) is baked into the image, not just hot-installed.

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos
docker compose build truth-api
docker compose up -d truth-api
```

**Expected output:** Container starts healthy. Confirm with:
```bash
docker ps | grep truth-api
# Should show: Up X minutes (healthy)
```

---

## Step 2: Inspect Container Environment Variables

Check what `OPENAI_API_BASE`, `MODEL_FAST`, `OPENAI_API_KEY`, and related vars are visible inside the container.

```bash
# Show all Model/API-related env vars (names and values)
docker exec inspirit-truthos-truth-api-1 env | grep -E 'MODEL|OPENAI|API_BASE|API_KEY'
```

**Record the output. Key values needed:**
- `OPENAI_API_BASE` — the base URL for the LLM proxy
- `MODEL_FAST` — the model alias for fast generation
- `OPENAI_API_KEY` — confirm it is present (do not share value publicly)

> [!NOTE]
> If no `MODEL_FAST` is set, the agent defaults to `gpt-4o-mini`. If no `OPENAI_API_BASE` is set, it attempts to infer the local proxy at `http://host.docker.internal:8080/v1`.

---

## Step 3: Inspect `.env` Keys Without Exposing Secrets

```bash
# Show key names only (not values) from the .env file
docker exec inspirit-truthos-truth-api-1 cat /app/.env | grep -E '^[A-Z]' | cut -d'=' -f1
```

**Expected output example:**
```
OPENAI_API_KEY
OPENAI_API_BASE
MODEL_FAST
TRUTHOS_ENV
BLUEPRINT_WRITEBACK_ENABLED
...
```

---

## Step 4: Test Model Listing from Inside the Container

This confirms the proxy is reachable and shows what models are actually available.

```bash
docker exec inspirit-truthos-truth-api-1 python3 -c "
import openai, os
base = os.getenv('OPENAI_API_BASE', 'http://host.docker.internal:8080/v1')
key = os.getenv('OPENAI_API_KEY', 'placeholder')
client = openai.Client(api_key=key, base_url=base)
try:
    models = client.models.list()
    for m in models.data:
        print(m.id)
except Exception as e:
    print(f'ERROR: {e}')
"
```

**Expected output:** A list of model IDs that the proxy endpoint supports, e.g.:
```
gemini-3-flash
gemini-3.1-pro-high
gpt-4o-mini
claude-sonnet-4-6
```

**[VERIFY]** If `http://host.docker.internal:8080/v1` returns a connection error, the Antigravity/OpenClaw proxy port may differ. Check the host with:
```bash
# Check which port the OpenClaw gateway is listening on
lsof -i -P -n | grep LISTEN | grep 8080
# Or check the standard Antigravity port
curl -s http://localhost:8080/v1/models
curl -s http://localhost:18789/v1/models
```

---

## Step 5: Run the Phase 1B Validation Script

After the rebuild, confirm the approved baseline still passes all checks.

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos
./scripts/validate_phase1b.sh
```

**All 4 checks must pass:**
- ✅ Schema validation for all `minimal_test_payloads/*.json`
- ✅ Invalid `case_reflection` payload correctly rejected
- ✅ V1 baseline query returns `TruthQueryResponse`
- ✅ `dry_run=true` query returns `{ "mode": "dry_run", "validation_status": "schema_loader_ready" }`

---

## What to Record and Pass Back

After completing the above steps, report the following before any Phase 1C reactivation:

| Item | Value |
|------|-------|
| `OPENAI_API_BASE` confirmed | _______________ |
| `MODEL_FAST` confirmed (or default) | _______________ |
| Available model IDs (from listing) | _______________ |
| Docker build completed successfully | Yes / No |
| `validate_phase1b.sh` all 4 checks passed | Yes / No |

**[VERIFY]** If the Antigravity proxy is on a different port than `8080`, update the `.env` file's `OPENAI_API_BASE` value accordingly before Phase 1C reactivation. Do **not** hardcode the port in Python files.
