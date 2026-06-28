# Local Memory Phased Deployment Plan (Mem0 + Qdrant)

Status: Phase 1 + Phase 2 scaffolding COMPLETE — pending Phase 1 infra activation
Date: 2026-03-16
Scope now: Phase 1 + Phase 2 only
Scope later: Phase 3 (CaseResolver + blueprint governance), Phase 4 (LanceDB methodology memory)

## 1. Architecture Summary

### Runtime boundaries (must remain)
- OpenClaw remains the orchestration boundary and primary runtime gateway.
- `backend / truth-api / secondme-proxy` is the only governed write path for long-term memory.
- No direct memory plugin revival in OpenClaw config.
- No autonomous blueprint writeback.

### Target data/control flow
1. Client -> truth-api `/chat` with authenticated session token.
2. truth-api resolves user context (`user.id`, role, thread access) and model policy.
3. truth-api retrieves memory context from Mem0 (backed by Qdrant) before upstream prompt assembly.
4. truth-api calls OpenClaw gateway for model generation.
5. truth-api writes memory event after response generation through governed memory service.
6. Optional secondme-proxy path receives trusted `metadata.user_id` from truth-api, never raw user-supplied values.

### Phase intent
- Phase 1: local infra scaffolding (Mem0 + Qdrant, env contract, feature flags, health checks, rollback hooks).
- Phase 2: truth-api integration points for governed read-before-prompt and write-after-response.

## 2. File Placement Plan

### Documentation (planning artifacts)
- [x] CREATED: `docs/local-memory-phased-deployment-plan.md` (this file)
- [x] UPDATED: `ENVIRONMENT.md` (§5.5 expanded with full memory env contract)
- [x] UPDATED: `OPERATIONS.md` (§16 added: memory health/rollback/scope runbook)

### Infra and env scaffolding
- [x] EDITED: `docker-compose.yml` (qdrant + mem0 blocks added as commented-out services; memory env vars forwarded in truth-api block)
- [x] EDITED: `.env.example` (full memory flags with safe defaults)
- [x] EDITED: `env/truthos.dev.env` (local defaults; host-net port URLs)
- [x] EDITED: `env/truthos.staging.env` (narrow allowed scopes, all flags off)
- [x] EDITED: `env/truthos.prod.env` (narrow allowed scopes, all flags off)

### truth-api integration scaffolding
- [x] EDITED: `apps/truth-api/app/core/config.py` (memory settings group added)
- [x] EDITED: `apps/truth-api/app/models/chat_models.py` (MemoryScope type, memory_scope field, memory_resolved on response)
- [x] EDITED: `apps/truth-api/app/routes/chat_routes.py` (retrieve hook before prompt, store hook after reply, both no-op when flags off)
- [x] CREATED: `apps/truth-api/app/services/memory_types.py`
- [x] CREATED: `apps/truth-api/app/services/memory_clients.py`
- [x] CREATED: `apps/truth-api/app/services/memory_policy.py`
- [x] CREATED: `apps/truth-api/app/services/memory_service.py`
- [x] CREATED: `apps/truth-api/tests/test_memory_scope_routing.py`
- [x] CREATED: `apps/truth-api/tests/test_memory_user_id_propagation.py`
- [x] CREATED: `apps/truth-api/tests/test_memory_hooks_chat_flow.py`

### secondme-proxy governance touchpoint
- [ ] DEFERRED: `../secondme-proxy/index.js` hardening — internal trust token check
  - Blocked on: SECONDME_PROXY_INTERNAL_TOKEN rotation policy decision.
  - Current behavior is safe: memory_policy.resolve_user_id() defaults to auth; proxy_user_id is never sourced from client payload by truth-api.

## 3. Services And Ports

## Proposed local ports (collision-safe)
Known occupied local surfaces already include `8010`, `18000`, `3002`, `8000`, `8002`, `8045`, `8080`, `11434`, `18789`.

Use the following host ports to avoid overlap:
- Qdrant HTTP: `16333` -> container `6333`
- Qdrant gRPC: `16334` -> container `6334`
- Mem0 API: `18081` -> container `8000`

Internal compose DNS (preferred by truth-api):
- `http://qdrant:6333`
- `http://mem0:8000`

Host-level debug URLs:
- `http://127.0.0.1:16333`
- `http://127.0.0.1:18081`

## Service policies
- `restart: unless-stopped`
- Persistent volumes:
  - Qdrant: named volume `qdrant_data`
  - Mem0: named volume `mem0_data` (if Mem0 container stores local state/cache)
- Health checks:
  - Qdrant: `GET /readyz` (or `/healthz` fallback if image/version differs)
  - Mem0: `GET /health` (fallback to `/v1/health` if image path differs)

## 4. Env Variables

Keep memory features disabled by default in shared templates, enabled only in local dev when explicitly set.

## Core toggles
- `MEMORY_LONGTERM_ENABLED=false`
- `MEMORY_READ_ENABLED=false`
- `MEMORY_WRITE_ENABLED=false`
- `MEMORY_PROVIDER=mem0`
- `MEMORY_STRICT_MODE=true`
- `MEMORY_FAIL_OPEN_READ=true`
- `MEMORY_FAIL_OPEN_WRITE=true`

## Endpoints and auth
- `MEM0_BASE_URL=http://mem0:8000`
- `MEM0_API_KEY=`
- `QDRANT_URL=http://qdrant:6333`
- `QDRANT_API_KEY=`

## Retrieval/write policy
- `MEMORY_TOP_K=5`
- `MEMORY_MAX_CONTEXT_CHARS=2400`
- `MEMORY_WRITE_MIN_CHARS=24`
- `MEMORY_WRITE_COOLDOWN_SECONDS=15`

## Scope and governance
- `MEMORY_ALLOWED_SCOPES=default,none,session,experiment`
- `MEMORY_DEFAULT_SCOPE=default`
- `MEMORY_EXPERIMENT_SCOPE_ENABLED=false`
- `MEMORY_SESSION_SCOPE_WRITE_ENABLED=false`

## Identity trust controls
- `MEMORY_USER_ID_SOURCE=auth`  # auth | proxy
- `MEMORY_TRUST_PROXY_USER_ID=false`
- `SECONDME_PROXY_TRUSTED_HEADER=x-inspirit-user-id`
- `SECONDME_PROXY_REQUIRE_INTERNAL_TOKEN=true`
- `SECONDME_PROXY_INTERNAL_TOKEN=`

## Audit
- `MEMORY_AUDIT_ENABLED=true`
- `MEMORY_AUDIT_REDACT_CONTENT=true`

## 5. Files To Edit/Create

## Exact files to edit
- `docker-compose.yml`
- `.env.example`
- `env/truthos.dev.env`
- `env/truthos.staging.env`
- `env/truthos.prod.env`
- `apps/truth-api/app/core/config.py`
- `apps/truth-api/app/models/chat_models.py`
- `apps/truth-api/app/routes/chat_routes.py`
- `apps/truth-api/README-dev.md`
- `ENVIRONMENT.md`
- `OPERATIONS.md`
- `../secondme-proxy/index.js` (governance hardening only)

## Exact files to create
- `apps/truth-api/app/services/memory_service.py`
- `apps/truth-api/app/services/memory_clients.py`
- `apps/truth-api/app/services/memory_policy.py`
- `apps/truth-api/app/services/memory_types.py`
- `apps/truth-api/tests/test_memory_scope_routing.py`
- `apps/truth-api/tests/test_memory_user_id_propagation.py`
- `apps/truth-api/tests/test_memory_hooks_chat_flow.py`

## Proposed docker-compose changes (Phase 1 plan)

```yaml
services:
  qdrant:
    image: qdrant/qdrant:v1.13.4
    restart: unless-stopped
    ports:
      - "16333:6333"
      - "16334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://127.0.0.1:6333/readyz || wget -qO- http://127.0.0.1:6333/healthz"]
      interval: 15s
      timeout: 5s
      retries: 5
      start_period: 20s

  mem0:
    image: mem0ai/mem0:latest  # BLOCKER: pin to specific tag before activation (see §9)
    restart: unless-stopped
    depends_on:
      qdrant:
        condition: service_healthy
    ports:
      - "18081:8000"
    environment:
      MEM0_VECTOR_STORE: qdrant
      QDRANT_URL: http://qdrant:6333
      QDRANT_API_KEY: ${QDRANT_API_KEY:-}
      MEM0_API_KEY: ${MEM0_API_KEY:-}
    volumes:
      - mem0_data:/var/lib/mem0
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://127.0.0.1:8000/health || wget -qO- http://127.0.0.1:8000/v1/health"]
      interval: 15s
      timeout: 5s
      retries: 5
      start_period: 20s

volumes:
  qdrant_data:
  mem0_data:
```

Note: final Mem0 image tag and health endpoint should be pinned after one-time local image verification in a separate execution step (outside this planning-only change set).

## 6. Validation Plan (No Runtime Execution In This Step)

## Static validation checklist
- Compose diff only adds `qdrant` and `mem0`; no OpenClaw service rewiring.
- Env templates include new memory vars with safe defaults (`false` for write/read).
- `chat_models.py` contract includes `memory_scope` enum: `default | none | session | experiment`.
- `chat_routes.py` integration point order is explicit:
  1) auth + thread access
  2) memory retrieval (conditional)
  3) prompt construction
  4) upstream call
  5) memory write (conditional)
- `memory_user_id` source is always `get_current_user(...)["id"]` unless trusted proxy mode is explicitly enabled.
- No write path bypasses `memory_service.py`.
- All memory writes emit audit event with redacted payload metadata.
- Test files cover scope gating and user_id propagation.

## Deferred execution checklist (future runbook step)
- `docker compose config` parses after edits.
- `pytest -k memory` passes in truth-api package.
- Service health endpoints return ready state.
- End-to-end chat request with each `memory_scope` value behaves as expected.

## 7. Rollback Plan

Rollback must be local-first and reversible by file + env toggles.

## Fast rollback switches
- Set `MEMORY_LONGTERM_ENABLED=false`
- Set `MEMORY_READ_ENABLED=false`
- Set `MEMORY_WRITE_ENABLED=false`
- Keep `MEMORY_USER_ID_SOURCE=auth`

## Infra rollback
- Remove or comment `mem0` and `qdrant` service blocks from compose.
- Remove `qdrant_data` and `mem0_data` volume references from compose only (do not delete data unless explicitly requested).

## App rollback
- Revert `chat_routes.py` to upstream-only flow without memory hooks.
- Revert `chat_models.py` if API contract rollback is required.
- Keep `memory_service.py` files in tree if desired, but do not import them when feature flags are off.

## Policy rollback guard
- Ensure no OpenClaw config/plugin changes were introduced.
- Ensure blueprint writeback remains disabled.

## 8. Risks And Guardrails

## Primary risks
- Identity drift: client-supplied `user_id` could poison memory continuity if not pinned to auth context.
- Scope leakage: `experiment` or `session` scope might unintentionally persist long-term memory.
- Over-retrieval: large memory context may degrade prompt quality or exceed token budgets.
- Operational ambiguity: Mem0 image/health endpoints can vary by version.

## Guardrails
- Default all long-term memory features to OFF until explicitly enabled.
- Enforce `auth` as default source of `metadata.user_id`.
- Gate proxy trust with explicit flag + internal token header.
- Centralize all memory writes in one governed service.
- Keep retrieval bounded (`top_k`, max context chars).
- Keep memory write asynchronous/fail-open in early rollout to avoid chat hard failures.
- No autonomous blueprint writeback in Phase 1/2.
- No OpenClaw plugin/config revival for stale memory-lancedb-pro paths.

## Forward phases (not in current implementation scope)
- Phase 3: CaseResolver + blueprint governance layer with human review and explicit writeback policy gates.
- Phase 4: LanceDB methodology memory as a separate, non-conversational knowledge/method retrieval lane.

---

## 9. Phase 1 Activation Checklist

Status: **BLOCKED** — do not proceed until all ✗ items are resolved.

### Hard blockers (must resolve before uncommenting services)

> **EXCEPTION NOTE**: Local-only bring-up exception approved. The `mem0` image using `latest` is temporarily allowed for this first local validation only. This does not satisfy final pinned-tag policy. No shared rollout is allowed under this exception. A verified non-latest tag is still required after upstream publishes one.

| # | Item | Status | Notes |
|---|------|--------|-------|
| B1 | Verify `mem0ai` version pin in `pyproject.toml` (source of truth) | ✗ | Confirm `mem0ai>=0.1.25,<0.2` on PyPI; update `pyproject.toml` if needed |
| B2 | Install `mem0ai` Python SDK in truth-api venv | ✗ | `cd apps/truth-api && .venv/bin/pip install -e '.[memory]'` |
| B3 | Replace memory_clients.py httpx placeholders with mem0ai SDK calls | ✗ | Not a blocker for first local activation; required immediately after first successful local bring-up and before any shared rollout |
| B4 | Resolve `mem0ai/mem0` Docker image tag — replace `:latest` | ✗ | Pick stable tag and update `docker-compose.yml` line 61 |
| B5 | Determine Mem0 container health endpoint path for pinned tag | ✗ | Tag may expose `/health`, `/v1/health`, or other — confirm before trusting §16.1 |
| B6 | Run full memory test suite and confirm all 33 tests pass | ✗ | `cd apps/truth-api && .venv/bin/pytest -k memory -v` — not yet run |

### Upstream artifact blocker

Status: blocked pending upstream publishable non-latest tag. citeturn0view0
Local-only exception approved: this first local Mem0 validation may temporarily rely on `mem0/mem0-api-server:latest`, but it does not satisfy the final pinned-tag policy, does not authorize any shared rollout, and still requires an upstream-published non-latest tag before activation can be formalized. citeturn0view0
Phase 1 first local activation remains blocked by upstream Mem0 image-tag availability rather than by local scaffolding or truth-api memory governance. citeturn0view0
External verification currently supports `mem0/mem0-api-server` as the official Mem0 REST API Server image, while the previously used `mem0ai/mem0` identity is not verified as a pullable official image for this rollout path. citeturn0view0turn1search7
However, the official Docker Hub tags page currently exposes only `latest`, and no externally verifiable non-latest concrete tag is available to satisfy the compose pinning requirement. citeturn0view0
For that reason, `docker-compose.yml` must not be treated as activation-ready until a real non-latest tag is verified and substituted into the Mem0 image line. citeturn0view0

### Handoff note

Next verification action:
1. Re-check the official Docker Hub repository for `mem0/mem0-api-server` and confirm whether a concrete non-latest tag has been published. citeturn0view0
2. If a verified non-latest tag becomes available, update the compose image line to `mem0/mem0-api-server:<verified-concrete-tag>`. citeturn0view0
3. Re-confirm the health endpoint for that exact image/tag before restarting the first local activation checklist; the current expected primary endpoint is `/health`. citeturn1search0
4. Keep activation blocked until these external artifact conditions are met. citeturn0view0

This blocker does not require changes to OpenClaw runtime config, plugin routing, or truth-api code at the current stage.

### Soft prerequisites (complete before first traffic, not before uncomment)

| # | Item | Status | Notes |
|---|------|--------|-------|
| S1 | Confirm no `TODO: Replace with mem0 Python SDK` markers remain | ✗ | Must be true after completing hard blocker B3 |
| S2 | Set `MEM0_API_KEY` if Mem0 instance requires token auth | ✗ | Leave blank only if running unauthenticated local instance |
| S3 | Confirm Qdrant v1.13.4 `/readyz` path is correct for that tag | ✓ | Pinned in compose; healthcheck uses `wget -qO-` fallback |
| S4 | Decide `MEMORY_WRITE_MIN_CHARS` floor value before enabling writes | ✗ | Currently 24 chars — may be too low for meaningful content |
| S5 | Review and set `MEMORY_TOP_K` and `MEMORY_MAX_CONTEXT_CHARS` | ✗ | Defaults (5 / 2400) are conservative but unvalidated |

### Activation sequence (after all hard blockers resolved)

```bash
# 1. Verify compose config parses cleanly
cd /Users/tongwei/.openclaw/inspirit-truthos
docker compose config --quiet

# 2. Start infra containers only (truth-api stays on current host process)
docker compose up -d qdrant mem0

# 3. Verify infra health
curl -s http://127.0.0.1:16333/readyz
curl -s http://127.0.0.1:18081/health

# 4. Install memory SDK into venv
cd /Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api
.venv/bin/pip install -e '.[memory]'

# 5. Run memory test suite
.venv/bin/pytest -k memory -v

# 6. Only after all tests pass, enable flags in .env and restart truth-api
```

---

## 10. Scaffolding Status: Safe / Required / Deferred

### Already landed — safe now (no further action required)

| File | Change | Safe because |
|------|--------|-------------|
| `app/core/config.py` | 20 typed memory settings, all `False` by default | Pydantic `extra="ignore"` means unused at runtime until enabled |
| `app/models/chat_models.py` | `MemoryScope` Literal, `memory_scope` on request, `memory_resolved` on response | `response_model_exclude_none=True` suppresses `memory_resolved` from wire when disabled |
| `app/routes/chat_routes.py` | Retrieve hook before prompt, store hook after reply | Both hooks no-op when `MEMORY_LONGTERM_ENABLED=false` — zero network calls |
| `app/services/memory_policy.py` | Scope and identity governance | Master flag short-circuits all paths before any read/write gate is checked |
| `app/services/memory_service.py` | Retrieve/store facade with fail-open | `retrieve()` and `store()` skip and return immediately when flags off |
| `app/services/memory_clients.py` | httpx placeholder wrappers | Never called unless `mem0_base_url` is non-empty AND flags are enabled |
| `app/services/memory_types.py` | Frozen dataclass I/O contracts | No runtime impact; pure typing |
| `tests/test_memory_*.py` (×3) | 33 test skeletons | No live network; all run with patched settings |
| `docker-compose.yml` | qdrant + mem0 blocks fully commented out | Services do not start; host ports unreachable |
| `env/*.env`, `.env.example` | Full memory flag block with all defaults `false` | Safe defaults; no live traffic to memory layer |
| `ENVIRONMENT.md §5.5` | Memory env contract documentation | Docs only |
| `OPERATIONS.md §16` | Health/rollback/scope runbook | Docs only |

### Required before Phase 1 activation (blocking)

| # | Action | File |
|---|--------|------|
| R1 | Resolve and pin `mem0ai/mem0` Docker image tag (replace `:latest`) | `docker-compose.yml` line ~61 |
| R2 | Verify and pin `mem0ai` Python SDK version in source-of-truth metadata | `apps/truth-api/pyproject.toml`, venv |
| R2a | Mirror the same pin in `requirements.txt` comment block for operators using requirements workflow | `apps/truth-api/requirements.txt` |
| R3 | Replace `memory_clients.py` httpx stubs with `mem0ai` SDK calls | `app/services/memory_clients.py` |
| R4 | Confirm Mem0 container health endpoint path for pinned tag | `docker-compose.yml` healthcheck, `OPERATIONS.md §16.1` |
| R5 | Run `pytest -k memory -v` and confirm 33/33 pass | `apps/truth-api/.venv` |
| R6 | Verify Qdrant + Mem0 `curl` health checks return HTTP 200 | Manual step post `docker compose up` |

### Deferred — later phases or policy gates

| Item | Phase | Blocked on |
|------|-------|-----------|
| `secondme-proxy/index.js` internal trust token check | Phase 2 hardening | `SECONDME_PROXY_INTERNAL_TOKEN` rotation policy decision |
| `MEMORY_TRUST_PROXY_USER_ID=true` enablement | Phase 2+ | Trust-proxy review + internal token in place |
| CaseResolver + blueprint governance layer | Phase 3 | Architecture decision; no scaffolding started |
| LanceDB methodology memory lane | Phase 4 | Separate retrieval architecture; no scaffolding started |
| OpenClaw `memory-lancedb-pro` plugin revival | Indefinitely deferred | Requires explicit review; current config has no plugin block |
| `MEMORY_AUDIT_ENABLED=true` enforcement | Phase 2 hardening | Audit service not yet wired to memory write path |
