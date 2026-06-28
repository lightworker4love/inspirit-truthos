# ENVIRONMENT.md
# TruthOS Environment and Configuration Manual

## 1. Purpose

This document defines the environment model and configuration contract for `inspirit-truthos`.

It standardizes:

- `.env` variables
- gateway endpoint conventions
- embedding provider configuration
- LanceDB path configuration
- dev / staging / prod environment structure
- local-first operational assumptions

The goal is to eliminate configuration ambiguity.

TruthOS must be reproducible, inspectable, and environment-aware.
It must not depend on accidental machine state.

---

## 2. Environment Philosophy

TruthOS runs inside a broader in spirit ecosystem that already assumes:
- multiple personas
- multiple environments
- multiple routing layers
- dual-track local + cloud operation

This is consistent with your earlier environment and deployment design:
- dev / staging / prod environment templates
- per-agent configuration and multi-persona structure
- separate gateway location by environment
- model provider selection driven by config, not hardcoded assumptions. :contentReference[oaicite:3]{index=3}

### 2.1 Configuration principles

1. **No hardcoded secrets**
2. **No hidden machine-only assumptions**
3. **Every runtime dependency must be expressible in config**
4. **Fallback behavior must be environment-aware**
5. **Local-first remains the default design bias**

### 2.2 TruthOS configuration layers

TruthOS configuration should be thought of as four layers:

- **Environment layer**
  - dev / staging / prod
- **Routing layer**
  - gateway / fallback endpoints
- **Model layer**
  - embedding provider / embedding model / local LLM path
- **Storage layer**
  - SQLite / LanceDB / optional memory integrations

---

## 3. Environment Types

TruthOS should support at least three formal environments.

## 3.1 dev

Purpose:
- active development
- local debugging
- rapid iteration
- fallback experiments

Typical characteristics:
- local filesystem paths
- local SQLite
- local LanceDB
- gateway may be unstable
- OpenAI fallback may be enabled
- verbose logs acceptable
- smallest blast radius

## 3.2 staging

Purpose:
- pre-release validation
- integration rehearsal
- environment parity testing
- fallback path validation

Typical characteristics:
- same schema as prod
- realistic gateway routing
- controlled provider keys
- observability required
- more stable than dev
- safe to test failures

## 3.3 prod

Purpose:
- stable serving
- real user traffic
- operational continuity

Typical characteristics:
- guarded configuration changes
- low-noise logging
- secrets managed correctly
- health endpoints monitored
- graceful degradation mandatory
- no experimental rewiring without review

This dev / staging / prod split directly matches your earlier multi-environment deployment guidance. :contentReference[oaicite:4]{index=4}

---

## 4. Local Architecture Assumptions

TruthOS currently lives in a dual-track infrastructure.

## 4.1 Cloud track

Cloud-oriented models are routed through:
- Antigravity Proxy
- OpenClaw-compatible gateway paths
- centralized provider aggregation

In your current environment notes, this is represented by the 8045 proxy path and cloud model routing. :contentReference[oaicite:5]{index=5}

## 4.2 Local track

Local model services are typically exposed through:
- Local Llama server at port 8080
- direct local inference path
- Second Me direct-connect behavior for local use

This is already part of your documented topology and M2 Pro operating assumptions. 

## 4.3 Gateway role

OpenClaw acts as:
- routing gateway
- provider abstraction layer
- fallback-capable access point

It should not be confused with:
- the Python `openai` package
- the local vector store
- SQLite structured storage

---

## 5. Required `.env` Contract

TruthOS must define its runtime through environment variables.

Below is the recommended baseline contract.

## 5.1 Core application variables

```env
TRUTHOS_ENV=dev
TRUTHOS_LOG_LEVEL=info
TRUTHOS_DB_PATH=./data/truthos.db
LANCEDB_PATH=./data/lancedb
```

Meaning

`TRUTHOS_ENV`

- current environment
- allowed: `dev`, `staging`, `prod`

`TRUTHOS_LOG_LEVEL`

- logging verbosity

recommended:

- `dev = debug or info`
- `staging = info`
- `prod = info or warning`

`TRUTHOS_DB_PATH`

- SQLite file path

`LANCEDB_PATH`

- root path for LanceDB storage

## 5.2 Gateway and embedding variables

```env
OPENAI_BASE_URL=http://localhost:11435/v1
OPENAI_API_KEY=dummy
OPENAI_FALLBACK_BASE_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small
```

Meaning

`OPENAI_BASE_URL`

- primary OpenAI-compatible endpoint
- may point to OpenClaw or a local gateway

`OPENAI_API_KEY`

- API key or placeholder token for primary endpoint

`OPENAI_FALLBACK_BASE_URL`

- official OpenAI endpoint for fallback behavior

`EMBEDDING_MODEL`

- embedding model name

default:
`text-embedding-3-small`

## 5.3 Optional local model variables

```env
LOCAL_LLM_BASE_URL=http://127.0.0.1:8080/v1
LOCAL_LLM_MODEL=qwen2.5-3b-instruct
```

Meaning

`LOCAL_LLM_BASE_URL`

- local llama-compatible endpoint

`LOCAL_LLM_MODEL`

- local inference model identifier

This reflects your current local deployment pattern in which local inference can run separately from the cloud/proxy track.

## 5.4 Optional proxy variables

```env
CLOUD_PROXY_BASE_URL=http://127.0.0.1:8045/v1beta
CLOUD_PROXY_TOKEN=
```

Meaning

`CLOUD_PROXY_BASE_URL`

- Antigravity Proxy / cloud routing endpoint

`CLOUD_PROXY_TOKEN`

- token for proxy-authenticated calls if needed

This matches your documented cloud aggregation path around port 8045. 

9️⃣999-管理網域：架構檢測與藍圖規劃

## 5.5 Long-term memory integration variables (Phase 1/2)

All memory flags default to false.  Enable only after reviewing
`docs/local-memory-phased-deployment-plan.md`.

```env
# Feature flags (all default OFF)
MEMORY_LONGTERM_ENABLED=false
MEMORY_READ_ENABLED=false
MEMORY_WRITE_ENABLED=false
MEMORY_PROVIDER=mem0
MEMORY_STRICT_MODE=true
MEMORY_FAIL_OPEN_READ=true
MEMORY_FAIL_OPEN_WRITE=true

# Retrieval policy
MEMORY_TOP_K=5
MEMORY_MAX_CONTEXT_CHARS=2400
MEMORY_WRITE_MIN_CHARS=24

# Scope governance
# Allowed values: default | none | session | experiment
MEMORY_ALLOWED_SCOPES=default,none,session,experiment
MEMORY_DEFAULT_SCOPE=default
MEMORY_EXPERIMENT_SCOPE_ENABLED=false
MEMORY_SESSION_SCOPE_WRITE_ENABLED=false

# Identity governance
# MEMORY_USER_ID_SOURCE must stay "auth" unless proxy trust is explicitly reviewed.
MEMORY_USER_ID_SOURCE=auth
MEMORY_TRUST_PROXY_USER_ID=false

# Audit
MEMORY_AUDIT_ENABLED=true
MEMORY_AUDIT_REDACT_CONTENT=true

# Service endpoints
MEM0_BASE_URL=
MEM0_API_KEY=
QDRANT_URL=
QDRANT_API_KEY=
```

Meaning

`MEMORY_LONGTERM_ENABLED`: master switch for the entire Phase 1/2 memory layer.
When false, no network calls are made to Mem0 or Qdrant from truth-api.

`MEMORY_USER_ID_SOURCE`: controls where memory operations source the user identity.
Default `auth` pins identity to the verified session.  `proxy` mode requires
`MEMORY_TRUST_PROXY_USER_ID=true` and an internal token to be present.

`MEMORY_FAIL_OPEN_READ/WRITE`: when true, a failed Mem0 call does not abort the
chat response.  Failures are logged and the turn completes without memory.

`MEM0_BASE_URL`: use compose DNS (`http://mem0:8000`) inside Docker or
`http://127.0.0.1:18081` for local host-net dev.

`QDRANT_URL`: use `http://qdrant:6333` inside Docker or
`http://127.0.0.1:16333` for local host-net dev.

## 6. Recommended .env.example

This is the recommended repository baseline:

```env
TRUTHOS_ENV=dev
TRUTHOS_LOG_LEVEL=info

TRUTHOS_DB_PATH=./data/truthos.db
LANCEDB_PATH=./data/lancedb

OPENAI_BASE_URL=http://localhost:11435/v1
OPENAI_API_KEY=dummy
OPENAI_FALLBACK_BASE_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small

LOCAL_LLM_BASE_URL=http://127.0.0.1:8080/v1
LOCAL_LLM_MODEL=qwen2.5-3b-instruct

CLOUD_PROXY_BASE_URL=http://127.0.0.1:8045/v1beta
CLOUD_PROXY_TOKEN=

MEM0_BASE_URL=
QDRANT_URL=
QDRANT_API_KEY=
```

## 7. Environment-Specific Configuration Profiles

### 7.1 dev profile

Recommended `.env.dev`:

```env
TRUTHOS_ENV=dev
TRUTHOS_LOG_LEVEL=debug

TRUTHOS_DB_PATH=./data/truthos.db
LANCEDB_PATH=./data/lancedb

OPENAI_BASE_URL=http://localhost:11435/v1
OPENAI_API_KEY=dummy
OPENAI_FALLBACK_BASE_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small

LOCAL_LLM_BASE_URL=http://127.0.0.1:8080/v1
LOCAL_LLM_MODEL=qwen2.5-3b-instruct

CLOUD_PROXY_BASE_URL=http://127.0.0.1:8045/v1beta
CLOUD_PROXY_TOKEN=
```

dev goals

- easy local startup
- visible fallback behavior
- easy rebuild of LanceDB
- simple endpoint inspection

dev expectations

- gateway may fail
- fallback should be exercised regularly
- operators should be able to inspect files directly

### 7.2 staging profile

Recommended `.env.staging`:

```env
TRUTHOS_ENV=staging
TRUTHOS_LOG_LEVEL=info

TRUTHOS_DB_PATH=/srv/inspirit-truthos/data/truthos.db
LANCEDB_PATH=/srv/inspirit-truthos/data/lancedb

OPENAI_BASE_URL=https://staging-openclaw.example.com/v1
OPENAI_API_KEY=${STAGING_OPENCLAW_KEY}
OPENAI_FALLBACK_BASE_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small

LOCAL_LLM_BASE_URL=http://127.0.0.1:8080/v1
LOCAL_LLM_MODEL=qwen2.5-3b-instruct

CLOUD_PROXY_BASE_URL=https://staging-proxy.example.com/v1beta
CLOUD_PROXY_TOKEN=${STAGING_PROXY_TOKEN}
```

staging goals

- realistic integration tests
- pre-prod routing validation
- gateway + fallback verification
- controlled secrets and closer-to-prod paths

### 7.3 prod profile

Recommended `.env.prod`:

```env
TRUTHOS_ENV=prod
TRUTHOS_LOG_LEVEL=info

TRUTHOS_DB_PATH=/srv/inspirit-truthos/data/truthos.db
LANCEDB_PATH=/srv/inspirit-truthos/data/lancedb

OPENAI_BASE_URL=https://openclaw.example.com/v1
OPENAI_API_KEY=${PROD_OPENCLAW_KEY}
OPENAI_FALLBACK_BASE_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small

LOCAL_LLM_BASE_URL=http://127.0.0.1:8080/v1
LOCAL_LLM_MODEL=qwen2.5-3b-instruct

CLOUD_PROXY_BASE_URL=https://proxy.example.com/v1beta
CLOUD_PROXY_TOKEN=${PROD_PROXY_TOKEN}
```

prod goals

- stable service
- graceful degradation
- clean observability
- no ad hoc config edits
- no secret leakage

## 8. Gateway Endpoint Strategy

### 8.1 Primary endpoint

TruthOS should first try:

`OPENAI_BASE_URL`

In local development this is often:

`http://localhost:11435/v1`

In routed or hosted environments this may be:

- a Tailscale URL
- OpenClaw-hosted endpoint
- internal proxy gateway

Your environment docs already show gateway and external URL planning through Tailnet / domain routing. 

9️⃣999-管理網域：架構檢測與藍圖規劃

### 8.2 Fallback endpoint

TruthOS should maintain an official fallback:

`https://api.openai.com/v1`

This ensures that:

- gateway failure does not kill index rebuild
- gateway failure does not kill semantic retrieval
- API can remain usable when primary routing is broken

### 8.3 Model discovery requirement

Gateway health is not just “endpoint responds”.
It must also confirm:

- `/v1/models` returns `200`
- `EMBEDDING_MODEL` is present or supported

If model discovery fails, the system should treat the gateway as unavailable.

## 9. Embedding Provider Policy

### 9.1 Default policy

TruthOS embedding policy:

- try gateway
- if gateway fails, try official OpenAI
- if embeddings unavailable, use SQLite fallback retrieval

This policy is consistent with the self-healing architecture you’ve already implemented and verified.

### 9.2 Embedding model default

Recommended default:

`text-embedding-3-small`

Reason:

- lightweight
- stable
- suitable for semantic indexing of truth puzzles
- widely supported in OpenAI-compatible patterns

### 9.3 Do not couple embedding provider to local OpenClaw only

The system must not assume that a locally installed OpenClaw binary implies the repo is embedding-ready.

This distinction matters operationally:

- OpenClaw = gateway
- `openai` Python client = application client
- LanceDB = vector storage layer

## 10. LanceDB Path Policy

### 10.1 Repository-local default

Default:

`./data/lancedb`

This is preferred in local dev because:

- it keeps semantic artifacts visible
- easy to back up
- easy to inspect
- easy to rebuild

### 10.2 Production path guidance

Use a stable mounted path such as:

`/srv/inspirit-truthos/data/lancedb`

or equivalent persistent volume.

### 10.3 LanceDB path rules

- do not point LanceDB to temporary directories in prod
- do not mix environments into the same LanceDB path
- do not share a single index path between dev and prod

### 10.4 Separate environment storage

Recommended:

```text
data/
  dev/
    truthos.db
    lancedb/
  staging/
    truthos.db
    lancedb/
  prod/
    truthos.db
    lancedb/
```

Or equivalent if managed externally.

## 11. SQLite Path Policy

### 11.1 Local default

Default:

`./data/truthos.db`

### 11.2 Production recommendation

Use persistent mounted storage, for example:

`/srv/inspirit-truthos/data/truthos.db`

### 11.3 SQLite path rules

- never store prod DB in a temp folder
- never silently overwrite prod DB during dev operations
- always back up SQLite before destructive migrations

SQLite is the structured source of truth.
If LanceDB disappears but SQLite survives, the system can recover.

## 12. Environment Selection Rules

### 12.1 Explicit selection required

TruthOS should not rely on “whatever `.env` happens to exist”.

Preferred startup pattern:

```bash
TRUTHOS_ENV=dev uvicorn app.main:app --reload
```

Or a wrapper script that loads:

- `.env.dev`
- `.env.staging`
- `.env.prod`

depending on the selected mode.

### 12.2 Recommended file layout

```text
env/
  truthos.dev.env
  truthos.staging.env
  truthos.prod.env
```

This mirrors your prior multi-environment planning approach. 

003-心靈拓樸圖：Bridge 架構藍圖

### 12.3 Startup wrapper guidance

Recommended commands:

```bash
source env/truthos.dev.env && uvicorn app.main:app --reload
```

or via Docker compose:

```bash
docker compose --env-file env/truthos.dev.env up
```

## 13. Persona and Environment Separation

TruthOS may later serve multiple personas or agents in the wider in spirit ecosystem.

Your earlier multi-persona planning already established:

- per-agent directories
- persona-specific `SOUL.md`
- environment-specific activation lists. 

003-心靈拓樸圖：Bridge 架構藍圖

TruthOS rule

Keep persona config and environment config separate.

Do not mix:

which persona is active
with

which embedding provider is active

These are different concerns.

Recommended split:

- persona config = agent / UI / orchestration layer
- environment config = endpoint / storage / provider layer

## 14. Secrets Handling

### 14.1 Never commit real secrets

Do not commit:

- real OpenAI keys
- proxy tokens
- gateway auth tokens
- internal infrastructure URLs that should remain private

### 14.2 Use .env.example as documentation, not real config

Repository should contain:

- `.env.example`
- `env/*.example` or templates

Repository should not contain:

- actual production secrets

### 14.3 Safe defaults

For local primary gateway paths, `OPENAI_API_KEY=dummy` is acceptable if the local gateway ignores the key.

Do not use real prod secrets in dev config.

## 15. Validation Checklist Per Environment

### 15.1 dev checklist

- `.env.dev` loaded
- SQLite path exists
- LanceDB path writable
- gateway health checked
- OpenAI fallback available if desired
- `/healthz` okay
- `/system/status` visible
- `/api/truth/query` returns structured response

### 15.2 staging checklist

- staging secrets loaded
- staging gateway reachable
- fallback tested
- vector rebuild tested
- degraded mode tested intentionally
- runtime observability verified

### 15.3 prod checklist

- prod secrets injected safely
- health probes monitored
- backups configured
- vector rebuild procedure documented
- fallback mode tested recently
- no dev paths present in runtime config

## 16. Common Misconfiguration Patterns

### 16.1 Wrong OPENAI_BASE_URL

Symptom:

- gateway check fails
- `/v1/models` returns `404` or `502`

Fix:

- confirm actual gateway path
- confirm `/v1` suffix
- confirm service is running

### 16.2 Missing EMBEDDING_MODEL

Symptom:

- gateway reachable but embeddings unavailable

Fix:

- verify model exists in provider
- verify gateway exposes it
- verify `.env` matches supported model name

### 16.3 Wrong LanceDB path

Symptom:

- `vector_index=false`
- index rebuild seems to run but nothing persists

Fix:

- confirm `LANCEDB_PATH`
- confirm process write permissions
- confirm environment is not writing to temp path

### 16.4 Wrong SQLite path

Symptom:

- system appears empty
- build process reads zero puzzles
- API loses semantic core

Fix:

- confirm `TRUTHOS_DB_PATH`
- verify actual file exists
- confirm current environment is pointing to intended DB

### 16.5 Dev/prod path bleed

Symptom:

- dev rebuild affects prod
- unexpected index state
- mismatched data counts

Fix:

- separate storage paths
- separate env files
- never share DB/index directories across environments

## 17. Recommended File Layout

```text
inspirit-truthos/
  .env.example
  env/
    truthos.dev.env
    truthos.staging.env
    truthos.prod.env

  data/
    dev/
      truthos.db
      lancedb/
    staging/
      truthos.db
      lancedb/
    prod/
      truthos.db
      lancedb/
```

This is the cleanest form if you want explicit environment separation in one host.

## 18. Final Rule

Environment design is not a side issue.
It is what determines whether TruthOS is:

- reproducible
- observable
- recoverable
- safe to evolve

If config is vague, the system becomes haunted.

If config is explicit, the system becomes operable.

That is the real purpose of this file.

---

## 你現在已經有五塊正式檔案

放在 repo 根目錄就是：

```text
/Users/tongwei/.openclaw/inspirit-truthos/
  AGENTS.md
  PROJECT_RULES.md
  ARCHITECTURE.md
  OPERATIONS.md
  ENVIRONMENT.md
```

給 Codex 的固定前置句

之後你可以固定在任務前加這句：

Before making changes, read AGENTS.md, PROJECT_RULES.md, ARCHITECTURE.md, OPERATIONS.md, and ENVIRONMENT.md and follow them as the repository constitution, blueprint, runbook, and configuration contract.

這樣 Codex 看到的不是零散要求，而是一套完整工程憲法。
