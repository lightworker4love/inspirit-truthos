# Blueprint Update Architecture: Sync-First Recommendation

**Decision**: Start with **synchronous inline update** (v1). Async job queue is the planned Phase 3 path.  
**Date**: 2026-05  
**Applies to**: `update_case_blueprint_from_conversation()` call site in `POST /api/truth/query`

---

## 1. Sync-First (v1) — Adopted

### Design

The blueprint update runs **inline** at the end of `POST /api/truth/query`, after the
AI model response is generated and before the HTTP response is returned:

```python
# In POST /api/truth/query handler (main.py)
response_data = await call_model(...)              # AI call
updated_profile = update_case_blueprint_from_conversation(
    case_profile,
    conversation_messages=request.messages,
    model_response=response_data,
    metadata={"session_id": request.session_id, "session_count": session_count},
)
return TruthResponse(answer=response_data, case_context=updated_profile)
```

### Constraints that justify sync

| Constraint | Detail |
|---|---|
| Single-process API | One Uvicorn worker — no race conditions on JSON file writes |
| Pattern-based extraction | <5 ms per call — negligible latency addition |
| JSON persistence | Atomic `os.replace(tmp, target)` — no partial-write risk |
| No LLM in the critical path | Extraction is regex/keyword — no external API dependency |

### Idempotency guard

Before each write, `_should_update_blueprint()` is evaluated:
- If all thresholds pass → write proceeds.
- If any threshold fails → original profile returned, no write, reason logged.
- No retry or queue needed — next session will re-evaluate.

**Daily write cap** (`_MAX_DAILY_BLUEPRINT_WRITES = 3`) is a future guard for the
full LLM extraction path. It is not enforced in the current pattern-based sync path
because the cost is negligible.

### Failure handling

If `save_case_profile()` raises (disk full, permission error, etc.), the exception
propagates to the request handler, which returns a 500. The AI response data is
**not** returned because the handler would need to be restructured to catch and
degrade gracefully. Recommended handler pattern:

```python
try:
    updated_profile = update_case_blueprint_from_conversation(...)
except Exception:
    logger.exception("blueprint update failed — serving response without save")
    updated_profile = case_profile   # continue with original profile
```

This try/except should be added before Task 1 closes.

---

## 2. Why Not Async Yet

| Concern | Reason to defer |
|---|---|
| Pattern extraction is &lt;5 ms | Async overhead would be larger than the saved latency |
| No LLM in path | Job queue is valuable when the task is slow/expensive; not yet |
| Single writer | Async task would need its own file-lock to avoid concurrent JSON writes |
| No retry semantics needed | Pattern match is deterministic; failures don't benefit from retry |
| Queue infrastructure cost | Adding Redis/Celery/Dramatiq for a 5 ms task is over-engineering |

---

## 3. Async Upgrade Path (Phase 3)

When the extraction step becomes expensive (LLM structured extraction, mem0 upsert),
migrate to this pattern:

```python
# Step 1: Extract to a BlueprintUpdater facade
class BlueprintUpdater:
    def update(self, profile, messages, response, metadata) -> CaseProfile:
        ...  # current sync logic

# Step 2: Make the call site fire-and-forget
import asyncio

async def handle_query(request):
    response_data = await call_model(...)
    asyncio.create_task(
        run_in_threadpool(updater.update, profile, messages, response_data, metadata)
    )
    return TruthResponse(answer=response_data)
```

`asyncio.create_task` + `run_in_threadpool` keeps the HTTP response fast while the
update runs in the background thread pool. No external queue needed for Phase 3a.

For Phase 3b (LLM extraction + mem0 upsert with retries):
- Move to a lightweight job queue: **Dramatiq** (in-process, no Redis required) or
  **ARQ** (asyncio-native, Redis-backed).
- Add `dry_run=True` mode to `BlueprintUpdater.update()` for integration tests.

---

## 4. Design Constraints (Applies to Both Paths)

Regardless of sync/async, these invariants must hold:

1. **Idempotency**: Two calls with the same conversation produce the same field values
   (dedup logic ensures this).
2. **No fabrication**: Extraction must never write a field value not derivable from
   the actual conversation text.
3. **Privacy fence**: `preferred_name`, `display_name`, `login_username` are never
   auto-written by this function.
4. **Observable**: Every call emits a structured log line (`case_blueprint_writeback`)
   that includes gate decision, updated fields, and skip reasons.
5. **Recoverable**: The JSON store uses atomic file replace — a crash mid-write leaves
   the old file intact.

---

## 5. Current Call Site Status

`update_case_blueprint_from_conversation()` is **implemented** but **not yet wired**
into `POST /api/truth/query`. Hook it in as the final step of the handler with the
try/except degradation wrapper described in §1.

The function is currently called only in:
- Unit tests (`workspace/soul-guardian/test_case_resolver.py`)
- Direct imports for testing
