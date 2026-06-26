# OPERATIONS.md
# TruthOS Operations Runbook

## 1. Purpose

This document is the operations manual for `inspirit-truthos`.

It defines how to operate, verify, recover, and troubleshoot the TruthOS runtime.

This runbook is written for:
- human engineers
- maintainers
- operators
- future collaborators

It assumes the repository already contains:
- FastAPI application layer
- SQLite truth store
- LanceDB vector index
- OpenClaw / gateway routing
- embedding fallback logic
- retrieval fallback logic

The purpose of this runbook is simple:

**TruthOS must stay useful even when parts of the system fail.**

---

## 2. Operational Philosophy

TruthOS is not operated like a toy demo.

It is part of a larger platform intended to be:
- long-term
- memory-aware
- governable
- resilient

This matches the broader in spirit AI direction: a system designed for continuity, reflection, and governance rather than one-shot chat behavior. 

### 2.1 Operational golden rule
If a subsystem fails:
- degrade gracefully
- preserve meaning
- keep observability clear
- avoid hard crash

### 2.2 TruthOS runtime modes
TruthOS must be understood as operating in one of three modes:

#### Mode A — Full semantic mode
- gateway available
- embeddings available
- LanceDB available

Path:
- OpenClaw gateway
- LanceDB retrieval

#### Mode B — Fallback semantic mode
- gateway unavailable
- official OpenAI fallback available
- LanceDB available

Path:
- OpenAI embeddings
- LanceDB retrieval

#### Mode C — Degraded reasoning mode
- embeddings unavailable
- LanceDB unavailable or missing

Path:
- SQLite fallback retrieval
- reasoning still returns structured output

---

## 3. System Topology Reference

TruthOS runs inside a broader dual-track environment.

### 3.1 Track model
The current environment is a dual-track architecture:

- **Cloud track**
  - routed through Antigravity Proxy on port 8045
  - used for stronger or more flexible cloud models

- **Local track**
  - local llama server on port 8080
  - intended for long-term, low-cost, direct local use

- **OpenClaw**
  - acts as the gateway / routing entry

This dual-track design is already documented in your infrastructure notes. 

### 3.2 Core runtime components
TruthOS operations revolve around:

- SQLite
- LanceDB
- OpenClaw / gateway
- embedding client
- FastAPI endpoints

### 3.3 Memory-layer boundary
The platform memory model is layered:

- Mem0 = short-term interaction and session context
- Qdrant = broad semantic retrieval
- LanceDB = methods, insights, and high-precision experience memory

This must be preserved operationally and conceptually. 

---

## 4. Service Health Model

## 4.1 Primary health endpoints

### `/healthz`
Purpose:
- quick operational status
- probe readiness
- identify active embedding mode

Expected structure:

```json
{
  "status": "ok",
  "embedding_gateway": true,
  "vector_index": true,
  "embedding_mode": "gateway"
}
```

Allowed values:

- gateway
- openai
- sqlite

### `/system/status`

Purpose:

- runtime observability
- understand which path is active

Expected structure:

```json
{
  "gateway": "openclaw",
  "embedding": "gateway",
  "retrieval": "lancedb",
  "vector_index": true
}
```

### 4.2 Interpreting health states

Healthy full semantic mode

```json
{
  "status": "ok",
  "embedding_gateway": true,
  "vector_index": true,
  "embedding_mode": "gateway"
}
```

Interpretation:

- OpenClaw available
- vector index available
- full semantic retrieval active

Healthy fallback semantic mode

```json
{
  "status": "ok",
  "embedding_gateway": false,
  "vector_index": true,
  "embedding_mode": "openai"
}
```

Interpretation:

- local gateway unavailable
- OpenAI fallback active
- LanceDB still usable

Degraded reasoning mode

```json
{
  "status": "ok",
  "embedding_gateway": false,
  "vector_index": false,
  "embedding_mode": "sqlite"
}
```

Interpretation:

- embeddings unavailable
- vector retrieval unavailable
- API should still respond using SQLite fallback

## 5. Standard Daily / Per-Change Checks

This is the baseline routine after:

- code changes
- dependency changes
- environment changes
- gateway config changes
- model routing changes
- vector index rebuilds

### 5.1 Compile check

Run:

```bash
python -m compileall apps/truth-api/app scripts/build_vector_index.py
```

Expected:

- no syntax errors
- no import-time failure

### 5.2 API health check

Run:

```bash
curl http://127.0.0.1:8000/healthz
```

Expected:

- JSON response
- `status=ok`

### 5.3 System status check

Run:

```bash
curl http://127.0.0.1:8000/system/status
```

Expected:

- current gateway / embedding / retrieval mode visible

### 5.4 Query sanity check

Run:

```bash
curl -X POST http://127.0.0.1:8000/api/truth/query \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id":"ops_test",
    "session_id":"ops_session",
    "message":"我明明想幫家人，最後卻變成爭吵。"
  }'
```

Expected:

- HTTP 200
- structured response with:
  - mirror
  - truth_view
  - coach_question
  - action
  - dimension
  - principles

### 5.5 Vector index status

Check LanceDB path:

```bash
ls -la data/lancedb
```

Expected:

- LanceDB files exist
- `truth_puzzles` table present

## 6. Index Rebuild Procedures

### 6.1 When to rebuild the LanceDB index

Rebuild the vector index when:

- index files are missing
- schema of vector rows changed
- embedding_text generation changed
- seed dataset changed materially
- embeddings provider changed and you want a clean index
- retrieval quality clearly drifted after data updates

### 6.2 Manual rebuild command

Run:

```bash
python scripts/build_vector_index.py
```

Expected behavior:

- read `truth_puzzles` from SQLite
- embed `embedding_text`
- write vector rows to LanceDB

### 6.3 Safe rebuild sequence

If doing a clean rebuild:

```bash
mv data/lancedb data/lancedb.backup.$(date +%Y%m%d-%H%M%S)
python scripts/build_vector_index.py
```

Then verify:

```bash
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/system/status
```

### 6.4 If rebuild fails

Do not panic and do not keep retrying blindly like a caffeinated woodpecker.

Follow this sequence:

- confirm embedding provider availability
- confirm SQLite source exists
- inspect error logs
- decide:
  - fallback to OpenAI
  - or remain in SQLite degraded mode

Important

If rebuild fails but SQLite fallback is operational, the system remains serviceable.

## 7. Gateway Fallback Operations

### 7.1 What the gateway does

OpenClaw is the routing layer.

It is responsible for:

- model endpoint mediation
- OpenAI-compatible routing
- local / proxied provider access

It is not the same as:

- the Python `openai` client
- LanceDB itself
- the SQLite truth store

### 7.2 Expected gateway path

The local environment documentation shows:

- cloud-oriented traffic routed through 8045 proxy
- local model on 8080
- OpenClaw as the standard gateway path in the cloud-oriented lane

### 7.3 Gateway health test

Run:

```bash
curl http://localhost:11435/v1/models
```

or the configured `OPENAI_BASE_URL` equivalent.

Healthy result

- HTTP 200
- model list includes the configured embedding model

Unhealthy result

- 502
- 404
- empty response
- model not listed

### 7.4 Gateway failure handling

If gateway fails:

- verify current `.env`
- confirm `OPENAI_BASE_URL`
- confirm `EMBEDDING_MODEL`
- switch to official OpenAI fallback if configured
- re-run vector build if necessary

Operational principle

Gateway failure should change the runtime mode, not kill the service.

## 8. SQLite Fallback Operations

### 8.1 Why SQLite fallback exists

SQLite fallback exists to preserve useful reasoning when:

- embeddings are down
- gateway is down
- vector index is missing
- LanceDB unavailable

### 8.2 What SQLite fallback should still do

In degraded mode, the system should still:

- classify likely dimension
- retrieve related principle / puzzle candidates
- produce reasoning output

It will be less semantically rich than LanceDB mode, but it must remain usable.

### 8.3 Verifying SQLite fallback

To test degraded mode intentionally:

- stop or break gateway access
- temporarily move or disable LanceDB path
- call `/api/truth/query`

Expected:

- HTTP 200
- `retrieval_mode=sqlite`
- `embedding_mode=sqlite`

If the endpoint hard crashes here, the fallback logic is broken.

## 9. Troubleshooting Playbooks

### 9.1 Symptom: /healthz returns gateway false, vector true

Example:

```json
{
  "status":"ok",
  "embedding_gateway": false,
  "vector_index": true,
  "embedding_mode": "openai"
}
```

Interpretation:

- gateway unavailable
- fallback provider working
- LanceDB still usable

Action:

- no immediate outage
- investigate gateway separately
- service can continue

### 9.2 Symptom: /healthz returns vector false

Interpretation:

- LanceDB index missing or unreadable

Action:

- inspect `data/lancedb`
- run `python scripts/build_vector_index.py`
- re-check `/healthz`

If still false:

- move to embedding diagnostics
- keep service on SQLite fallback

### 9.3 Symptom: build_vector_index fails

Possible causes:

- gateway failure
- OpenAI key missing
- embedding model unavailable
- corrupted SQLite rows
- LanceDB write error

Procedure:

- confirm `.env`
- confirm gateway health
- test official OpenAI fallback
- inspect stack trace
- rebuild after correcting provider path

### 9.4 Symptom: /api/truth/query returns 200 but poor relevance

Possible causes:

- stale LanceDB index
- weak `embedding_text`
- classifier drift
- overly narrow retrieval or wrong `top_k`

Procedure:

- inspect current retrieval mode
- verify current index date
- sample retrieved puzzles
- consider index rebuild
- inspect `embedding_text` quality
- verify `top_k` has not been reduced aggressively

### 9.5 Symptom: /api/truth/query crashes

This should be treated as a severity-1 bug.

Possible causes:

- uncaught exception in retriever
- reasoning composer assumptions too strict
- fallback chain broken
- runtime contract mismatch

Immediate actions:

- capture traceback
- test `/healthz`
- test `/system/status`
- test SQLite-only path
- patch to restore degraded mode first

Rule:
Restore degraded operability before optimizing elegance.

## 10. Logs and Observability

### 10.1 What to log

Useful operational logs include:

- gateway reachable / unreachable
- embedding provider in use
- LanceDB index found / missing / rebuilt
- retrieval mode used
- fallback transitions
- query timing
- build timing

### 10.2 What not to log

Do not log:

- raw API keys
- full secrets
- unnecessary sensitive payload content
- provider credentials
- internal tokens

This aligns with your broader governance and security posture, which already emphasizes redaction, guardrails, auditability, and clear public/private boundaries.

### 10.3 Recommended metrics

As the system matures, track at least:

- query count
- retrieval mode count
- fallback frequency
- vector build duration
- embedding failure rate
- average query latency

This is also consistent with your LanceDB operations notes, which call out monitoring of query volume, write volume, latency, and error rate.

## 11. Backup and Recovery

### 11.1 What should be backed up

At minimum:

- `data/truthos.db`
- `data/lancedb/`
- seed datasets
- environment templates
- architecture and operations docs

### 11.2 Backup guidance

TruthOS should back up:

- SQLite as canonical structured state
- LanceDB as semantic acceleration layer

If LanceDB is lost but SQLite survives:

- system can be restored
- vector index can be rebuilt

This is exactly why SQLite remains the structured source of truth.

### 11.3 Recommended backup order

- stop writes if possible
- back up SQLite
- back up LanceDB
- record current runtime mode and build version

## 12. Change Release Checklist

Before merging any significant runtime change:

### 12.1 Validate dependencies

- requirements updated
- no hidden global dependency assumptions

### 12.2 Validate runtime

- compile check passes
- `/healthz` passes
- `/system/status` passes
- `/api/truth/query` passes

### 12.3 Validate failure modes

- gateway failure path works
- missing LanceDB path works
- SQLite fallback still returns reasoning

### 12.4 Validate docs

If runtime behavior changes, update:

- `AGENTS.md`
- `PROJECT_RULES.md`
- `ARCHITECTURE.md`
- `OPERATIONS.md`

## 13. Incident Response Model

### 13.1 Severity model

SEV-1

- `/api/truth/query` crashes
- `/healthz` unavailable
- no usable degraded mode

SEV-2

- gateway unavailable
- fallback works
- service degraded but operating

SEV-3

- retrieval relevance drift
- index stale
- health endpoints okay

### 13.2 Incident response priorities

- restore service operability
- restore degraded mode if full mode unavailable
- identify root cause
- patch and document
- write back methodology if new

This matches the LanceDB “iron rules” mindset: do not just solve once; record the fix and the principle for future reuse.

## 14. Troubleshooting Cheat Sheet

Gateway check

```bash
curl http://localhost:11435/v1/models
```

API health

```bash
curl http://127.0.0.1:8000/healthz
```

Runtime status

```bash
curl http://127.0.0.1:8000/system/status
```

Build vector index

```bash
python scripts/build_vector_index.py
```

Compile check

```bash
python -m compileall apps/truth-api/app scripts/build_vector_index.py
```

Inspect LanceDB folder

```bash
ls -la data/lancedb
```

Inspect SQLite file

```bash
ls -la data/truthos.db
```

## 15. Final Rule

TruthOS operations are successful when the system can still preserve meaning under imperfect conditions.

That means:

- if gateway fails, fallback
- if embeddings fail, degrade
- if vector index disappears, rebuild or fall back
- if semantics weaken, remain useful
- if something truly breaks, make the break visible and recoverable

This is not just a convenience principle.
It is the operational signature of the entire project.

TruthOS is not here to look magical.

---

## 16. Long-Term Memory Operations (Phase 1/2 Scaffolding)

### 16.1 Service health checks

> **EXCEPTION NOTE**: Local-only bring-up exception approved. `latest` is temporarily allowed for this first local validation only. This does not satisfy final pinned-tag policy. No shared rollout is allowed under this exception. A verified non-latest tag is still required after upstream publishes one.

Before enabling memory, verify infra is alive:

```bash
# Qdrant HTTP readiness (host-net port)
curl -s http://127.0.0.1:16333/readyz

# Mem0 health (host-net port)
curl -s http://127.0.0.1:18081/health
```

Expected: both return HTTP 200.

### 16.2 Enable memory (Phase 1 activation sequence)

1. Uncomment qdrant and mem0 service blocks in `docker-compose.yml`.
2. Uncomment the `volumes:` stanza (`qdrant_data`, `mem0_data`).
3. Keep memory flags OFF in `.env` during infra validation.
4. Start infra only (not truth-api) from the compose file directory:
  ```bash
  cd /Users/tongwei/.openclaw/inspirit-truthos
  docker compose up -d qdrant mem0
  ```
5. Verify health endpoints (§16.1).
6. Install optional memory dependencies into truth-api venv:
  ```bash
  cd /Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api
  .venv/bin/pip install -e '.[memory]'
  ```
7. Run memory tests using the project venv:
  ```bash
  cd /Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api
  .venv/bin/pytest -k memory -v
  ```
8. Only after tests pass, enable memory flags in `.env`:
   ```
   MEMORY_LONGTERM_ENABLED=true
   MEMORY_READ_ENABLED=true
   MEMORY_WRITE_ENABLED=true
   MEM0_BASE_URL=http://mem0:8000
   QDRANT_URL=http://qdrant:6333
   ```
9. Restart truth-api so the new environment values are loaded.

### 16.3 Fast rollback

Step 1: Disable memory by setting `MEMORY_LONGTERM_ENABLED=false` in your `.env`
file.  This single flag is sufficient — no service restart required.

```
# /Users/tongwei/.openclaw/inspirit-truthos/.env  (this is file content, not a shell command)
MEMORY_LONGTERM_ENABLED=false
```

Secondary flags are optional belt-and-suspenders (only meaningful when LONGTERM is true):
```
MEMORY_READ_ENABLED=false
MEMORY_WRITE_ENABLED=false
```

Step 2 (optional): stop infra containers:
```bash
cd /Users/tongwei/.openclaw/inspirit-truthos
docker compose stop mem0 qdrant
```

Step 3: verify truth-api chat still works normally:
```bash
curl -s http://127.0.0.1:8010/health
```

Data in named volumes is preserved unless you explicitly run:
```bash
cd /Users/tongwei/.openclaw/inspirit-truthos
docker compose down -v  # removes qdrant_data and mem0_data — DESTRUCTIVE
```
Do not run `down -v` unless you intend to purge all saved memory.

### 16.4 Memory governance guardrails

- `MEMORY_USER_ID_SOURCE` must remain `auth` unless a formal trust-proxy
  review is completed and `SECONDME_PROXY_INTERNAL_TOKEN` is rotated.
- Never set `MEMORY_TRUST_PROXY_USER_ID=true` in staging or prod without a
  dedicated token in `SECONDME_PROXY_INTERNAL_TOKEN`.
- No blueprint data is autonomously written to Mem0 in Phase 1/2.
- All write failures must appear in truth-api stderr log.

### 16.5 Scope semantics

| Scope       | Read | Write | Notes |
|-------------|------|-------|-------|
| `default`   | ✓    | ✓     | follows global flags |
| `none`      | ✗    | ✗     | skip all memory for this turn |
| `session`   | ✓    | gated | write requires `MEMORY_SESSION_SCOPE_WRITE_ENABLED=true` |
| `experiment`| gated| gated | requires `MEMORY_EXPERIMENT_SCOPE_ENABLED=true` |

### 16.6 First Local Activation Runbook

#### Scope

This runbook applies only to the first local activation of long-term memory in
`inspirit-truthos/apps/truth-api` using local Mem0 and Qdrant services.
It does not authorize broader/shared rollout, production rollout, OpenClaw
runtime config changes, plugin revival in `openclaw.json`, or blueprint
writeback expansion.

#### Purpose

The goal of this phase is to validate local infrastructure wiring, memory flag
gating, scope governance, health checks, and fail-open behavior in `truth-api`
before any broader rollout decision.
The first local activation is a controlled bring-up step, not a final
hardening milestone.

#### Dependency authority

`apps/truth-api/pyproject.toml` is the dependency source of truth for
memory-related Python packages.
`apps/truth-api/requirements.txt` is a mirrored operator workflow file and
must not become the authoritative source when versions drift.

#### Hard blockers before first local activation

The following items must all be completed before enabling memory flags for the
first local activation:

1. Verify the `mem0ai` version pin in `apps/truth-api/pyproject.toml` and
  confirm the selected range matches the currently available package release
  path.
2. Install the memory dependency group into the `truth-api` virtual
  environment before any activation attempt.
3. Replace `mem0ai/mem0:latest` with a pinned Mem0 image tag in
  `docker-compose.yml` before uncommenting or starting the Mem0 service.
4. Confirm the correct health endpoint path for the selected pinned Mem0 image
  tag before treating the Mem0 container as ready.
5. Start local Qdrant and Mem0 infrastructure and require successful container
  health checks before enabling any memory flags.
6. Run the memory-focused test suite in `apps/truth-api` and require a full
  pass before local activation proceeds.

#### Not a first-local-activation blocker

Replacing the current HTTP placeholder implementation in `memory_clients.py`
with the official `mem0ai` SDK is not a hard blocker for the first local
activation.
This step is recommended immediately after the first successful local
bring-up and is required before broader/shared rollout because the official
Mem0 Python path is provided through the supported SDK interface.

#### Activation sequence

Execute the first local activation in the following order only:

1. Verify the `mem0ai` version pin in `apps/truth-api/pyproject.toml`.
2. Install the memory dependency group into the `truth-api` virtual
  environment.
3. Replace the floating Mem0 image reference with a pinned image tag in
  `docker-compose.yml`.
4. Confirm the Mem0 health endpoint path for the pinned tag.
5. Uncomment the Mem0 and Qdrant service blocks in `docker-compose.yml` only
  after steps 1 through 4 are complete.
6. Start local Mem0 and Qdrant infrastructure and wait for health checks to
  pass.
7. Run the memory-focused test suite in `apps/truth-api` and require a full
  pass before enabling memory flags.
8. Enable memory flags only after infrastructure and tests are both confirmed
  healthy.
9. Schedule immediate post-activation migration from the temporary HTTP client
  path to the official `mem0ai` SDK path.

#### Commands

1. Enter the project root:

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos
```

2. Enter the `truth-api` app and install memory dependencies:

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api
.venv/bin/pip install -e '.[memory]'
```

#### Blocker note

Status: Mem0 blocked by upstream image/config behavior.
First local activation is currently blocked by the upstream `mem0-api-server:latest` image eagerly instantiating a hardcoded `pgvector` DEFAULT_CONFIG before it can read external config contracts (like `MEM0_CONFIG_PATH`), causing the Python process to crash on missing `psycopg2` dependencies.
Local testing confirms that truth-api editable packaging is fixed, local Qdrant is healthy, and the `OPENAI_API_KEY` + explicit Qdrant config contract are correctly formatted.

Local-only exception approved: this first local Mem0 validation used `mem0/mem0-api-server:latest`, but it does not satisfy the final pinned-tag policy, shared rollout is prohibited, and the upstream crash renders it inoperable locally anyway.

#### Handoff note

Next operator action: Wait for an official upstream publishable non-latest tag to be released for `mem0/mem0-api-server` that defers evaluating configuration or ships correct dependencies.
Once a verified non-latest tag is available, update `docker-compose.yml` to use `mem0/mem0-api-server:<verified-concrete-tag>`, re-run local compose validation, and confirm that `mem0` no longer falls back to `pgvector` at import/startup.
Confirm the `/health` endpoint responds successfully from the container.
No OpenClaw runtime config, legacy plugin configuration, or truth-api activation flow should be changed or experimented on while this upstream image blocker remains unresolved.

3. Return to the compose root:

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos
```

4. Start local infrastructure only after Mem0 image pinning is complete:

```bash
docker compose up -d qdrant mem0
```

5. Verify Qdrant health:

```bash
curl -s http://127.0.0.1:16333/readyz
```

6. Verify Mem0 health:

```bash
curl -s http://127.0.0.1:18081/health
```

7. Run memory tests before enabling flags:

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api
.venv/bin/pytest -k memory -v
```

#### Flag enablement rule

Do not enable memory flags until all hard blockers are cleared, local
infrastructure is healthy, and the memory-focused tests pass.
For the first local activation, infrastructure validation and test validation
must come before flag activation, not after.

#### Immediate post-activation requirement

After the first successful local bring-up, replace the temporary HTTP client
implementation in `memory_clients.py` with the official `mem0ai` SDK path as
the next required hardening step.
This post-activation step is mandatory before any broader/shared rollout
decision.

#### Guardrails

- Do not modify OpenClaw runtime config during this phase.
- Do not revive legacy memory plugin configuration in `openclaw.json`.
- Do not expand blueprint writeback behavior during this phase.
- Do not treat first local activation as production readiness.

#### Exit criteria

This runbook phase is complete only when:
- local Qdrant and Mem0 services are healthy,
- memory tests pass in `apps/truth-api`,
- memory flags are enabled only after validation,
- and the SDK migration task is scheduled as the immediate next hardening step.

It is here to stay clear, observable, and useful when reality gets messy.

---

## 最後給你的落地建議

現在你已經有四塊正式檔案了：

- `AGENTS.md`
- `PROJECT_RULES.md`
- `ARCHITECTURE.md`
- `OPERATIONS.md`

最好的擺法是全部放在 repo 根目錄，然後在你給 Codex 的任務開頭加這句：

```text
Before making changes, read AGENTS.md, PROJECT_RULES.md, ARCHITECTURE.md, and OPERATIONS.md and follow them as the repository constitution, blueprint, and runbook.
```

這樣 agent 不只知道怎麼改，還知道怎麼活、怎麼壞、怎麼救。
