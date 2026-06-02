# TruthOS Architecture

TruthOS is the knowledge graph and semantic memory layer for the in spirit AI
platform. It is designed to give agents durable context across sessions while
keeping application surfaces, retrieval, storage, and deployment concerns
separate.

## System Role

TruthOS sits between agent workflows and persistence/retrieval infrastructure.
It is not a chat frontend by itself, and it is not a model provider. Its job is
to store, enrich, retrieve, and expose structured memory that other systems can
use.

```text
OpenClaw / Claude Code / local LLM workflows
        |
        v
Hermes Agent / bridge clients
        |
        v
TruthOS API
        |
        +--> SQLite persistence
        +--> vector index / semantic retrieval
        +--> seed knowledge and truth map data
        +--> frontend surfaces for review and exploration
```

## Main Components

### Truth API

Location: `apps/truth-api`

The FastAPI service owns the core API surface, including query handling, seed
loading, truth map response shaping, soul map behavior, and retrieval fallback
logic.

Responsibilities:

- expose API endpoints for downstream agents and frontend clients
- load seed knowledge and migration-backed state
- route queries through retrieval and reasoning layers
- provide health checks for CI/CD and deployment smoke tests

### TruthOS Web

Location: `apps/truthos-web`

The Next.js frontend gives users and maintainers a visual surface for guided
reflection, Hermes chat, and Soul Map inspection.

Responsibilities:

- present interactive user-facing views
- call configured API and Hermes endpoints
- keep local development configuration explicit through `.env.local`
- avoid storing secrets in frontend code

### Hermes Bridge

Locations:

- `packages/hermes_truthos_bridge`
- `packages/hermes-truthos-bridge`
- `apps/hermes_agent`

The Hermes bridge lets conversational agent flows send context into TruthOS
without making the chat runtime responsible for persistence details.

Responsibilities:

- translate agent events into TruthOS API calls
- avoid blocking agent responses when TruthOS is unavailable
- preserve a clean boundary between chat orchestration and memory persistence

### Seed Knowledge and Retrieval

Locations:

- `data/seeds`
- `scripts/seed_import.py`
- `scripts/build_vector_index.py`
- `packages/truth_schema`

Seed data and retrieval scripts provide the baseline knowledge graph and
semantic search substrate.

Responsibilities:

- define initial truth-map and reflection primitives
- validate seed schema before import
- build local retrieval indexes
- support fallback retrieval when an embedding gateway is unavailable

## Data Flow

1. A user or agent submits a message through Hermes, OpenClaw, Claude Code, or a
   local workflow.
2. The bridge calls the TruthOS API with the relevant user/session context.
3. The API loads persistent memory and seed knowledge.
4. Retrieval uses vector search when available and fallback retrieval when the
   embedding gateway is unavailable.
5. TruthOS returns structured context, truth-map data, or writeback results to
   the caller.
6. Frontend surfaces can inspect or present the resulting state.

## Boundaries

TruthOS should keep these boundaries explicit:

- Transport logic belongs in API routes and bridge clients.
- Persistence logic belongs in storage/repository modules and migrations.
- Prompt or reasoning logic belongs in reasoning and retrieval modules.
- Frontend presentation belongs in `apps/truthos-web`.
- Deployment and smoke checks belong in GitHub Actions, Railway config, and
  runbooks.

Avoid coupling prompt logic directly into transport, persistence, or deployment
files.

## Deployment Surface

TruthOS currently uses Railway-oriented service manifests and GitHub Actions
workflows. Deployment configuration should remain auditable and should not
contain secrets.

Public demo endpoints, when referenced, are for evaluation only. They may be
rate-limited, rotated, or removed without notice.

## Security Considerations

Important review areas:

- API endpoints should not expose private memory or internal state without an
  explicit access model.
- Frontend code must not contain server-side secrets.
- CI/CD should reference GitHub Actions secrets by name only, never by value.
- Seed data should be treated as public once committed.
- Public demo endpoints should be documented as non-production guarantees.
- Logs, fixtures, and examples should avoid personal data and credentials.

## Maintainer Workflow

For public maintenance, prefer small auditable changes:

- documentation PRs for positioning, architecture, and integration notes
- validation issues for smoke checks and CI/CD health
- integration issues for OpenClaw, Claude Code, local LLM, RAG, and retrieval
  workflows
- security notes for endpoint exposure, secret handling, and public demo safety

This keeps TruthOS understandable to contributors and credible as an actively
maintained open-source project.
