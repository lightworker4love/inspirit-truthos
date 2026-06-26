# Phase 1C Reactivation Gate

**Status: 🔴 LOCKED**

Phase 1C (LLM Draft Generation) is **not active** and **must not be reactivated** until all conditions below are explicitly confirmed by the host operator and approved for the next implementation session.

---

## Gate Conditions

All items below must be checked **YES** before Phase 1C may resume:

| # | Condition | Status |
|---|-----------|--------|
| 1 | `docker compose build truth-api` completes successfully | ⬜ Unconfirmed |
| 2 | `docker compose up -d truth-api` brings container up healthy | ⬜ Unconfirmed |
| 3 | `./scripts/validate_phase1b.sh` — all 4 checks pass | ⬜ Unconfirmed |
| 4 | `OPENAI_API_BASE` confirmed and reachable from inside container | ⬜ Unconfirmed |
| 5 | A valid fast model alias confirmed via model listing | ⬜ Unconfirmed |
| 6 | No Python application code was modified during env discovery | ⬜ Unconfirmed |
| 7 | Explicit operator approval for Phase 1C reactivation granted | ⬜ Unconfirmed |
| 8 | `dry_run=true` returns `schema_loader_ready` stub in current build | ⬜ Unconfirmed |

---

## What Phase 1C Is Allowed to Do (Scope Definition)

Upon reactivation, Phase 1C is strictly limited to:

- Call `execute_v2_dry_run_pipeline()` from `v2_dry_run_agent.py` only when `payload.dry_run == True`
- Generate **one artifact only**: `blueprint_instance`
- Strip LLM Markdown JSON safely via `strip_markdown_json()`
- Inject a locally generated UUID as `reference_id` (no LLM-generated IDs trusted)
- Validate generated dict against `schemas/blueprint_instance.schema.json`
- Return the result inside the dry-run envelope
- **No writeback** to SQLite, LanceDB, or any file
- **No session memory write**
- **No canonical promotion**
- **No calls to `case_insight_service.py`**
- **No modifications to secondme-proxy**
- **No changes to `BLUEPRINT_WRITEBACK_ENABLED`**

---

## What Phase 1C Is NOT Allowed to Do

- Call any writeback or persistence path
- Enable `canonical_promotion_executed: true`
- Enable `session_memory_written: true`
- Call `case_insight_service.py` directly or indirectly
- Hardcode model names or API keys into Python files
- Bypass the schema validation step
- Skip the `strip_markdown_json()` guard

---

## Files That May Be Modified in Phase 1C

| File | Allowed Modification |
|------|---------------------|
| `apps/truth-api/app/main.py` | Route `dry_run=True` to `execute_v2_dry_run_pipeline()` (single targeted block only) |
| `apps/truth-api/app/v2_dry_run_agent.py` | Update model alias and `OPENAI_API_BASE` usage based on verified env vars |
| `scripts/validate_phase1c.sh` | New validation script for success + failure path tests |

---

## Files That Must NOT Be Modified in Phase 1C

- `apps/truth-api/app/v2_schema_loader.py`
- `apps/truth-api/app/v2_validation.py`
- `apps/truth-api/app/models.py`
- `apps/truth-api/app/reasoning.py`
- `apps/truth-api/app/case_insight_service.py`
- `apps/truth-api/requirements.txt` (unless adding a non-LLM utility lib)
- `secondme-proxy/*`
- `.env` (during implementation; only the host operator may update env vars)

---

## Tests Required Before Merging Phase 1C

```bash
# 1. Regression — confirm Phase 1B.5 still passes
./scripts/validate_phase1b.sh

# 2. Success path test
curl -s -X POST http://localhost:18000/api/truth/query \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_v2", "message": "感覺我一直在討好對方", "dry_run": true}' \
  | python3 -m json.tool
# Expected: "dry_run_status": "success"

# 3. Failure path test (send a request that forces JSON parse to fail)
# Expected: "dry_run_status": "json_parse_failed" or "schema_validation_failed"
# (This can be achieved by temporarily corrupting the prompt to force bad LLM output — document the test approach in Phase 1C session)
```

---

## How to Record Gate Completion

When all 8 conditions above are met, the host operator should communicate the following before beginning Phase 1C:

```
PHASE 1C GATE REPORT
Date: YYYY-MM-DD
OPENAI_API_BASE: [value]
MODEL_FAST: [value]
Available models: [list]
docker build: PASS
validate_phase1b.sh: PASS (all 4 checks)
No code changes during discovery: CONFIRMED
Approval to reactivate Phase 1C: GRANTED
```

> [!CAUTION]
> Do not skip any gate condition. Partial confirmation is not sufficient. A failed model alias was the proximate cause of Phase 1C instability. Preventing a repeat requires confirming the full provider path before any LLM call is wired into the runtime.
