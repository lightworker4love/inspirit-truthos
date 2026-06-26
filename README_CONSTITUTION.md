# README_CONSTITUTION.md

# TruthOS Constitution Overview

This file is the single-entry overview for the governance documents of `inspirit-truthos`.

Together, these documents define how the TruthOS repository should be understood, changed, operated, and recovered.

They are intended to be read as a coordinated set, not as isolated notes.

Alongside the core documents, the repository also carries canonical baseline artifacts for seed authoring and environment templates.

The repository homepage Quick Start already adopts that baseline through `.env.example`, `env/`, and `seeds/`.

---

## 1. The Seven Core Documents

The repository constitution currently has seven core documents:

- `AGENTS.md`
- `PROJECT_RULES.md`
- `ARCHITECTURE.md`
- `OPERATIONS.md`
- `ENVIRONMENT.md`
- `DATA_MODEL.md`
- `API_CONTRACTS.md`

Each serves a different role.

### `AGENTS.md`

Audience:

- Codex
- AI agents
- automated code modifiers

Purpose:

- constrain agent behavior
- define non-negotiable repository rules
- preserve TruthOS intent during automated changes

Think of it as:

- the agent constitution

### `PROJECT_RULES.md`

Audience:

- human engineers
- collaborators
- maintainers
- future contributors

Purpose:

- define the engineering worldview of the project
- explain design intent
- constrain human design and maintenance decisions

Think of it as:

- the human engineering constitution

### `ARCHITECTURE.md`

Audience:

- engineers
- architects
- maintainers
- agents that need system-level context

Purpose:

- describe the formal system blueprint
- clarify component boundaries
- explain retrieval, fallback, and memory-layer roles

Think of it as:

- the system blueprint

### `OPERATIONS.md`

Audience:

- operators
- maintainers
- engineers doing runtime validation or incident response

Purpose:

- define health checks
- document fallback operations
- provide rebuild and troubleshooting procedures
- make failure states observable and recoverable

Think of it as:

- the operations runbook

### `ENVIRONMENT.md`

Audience:

- engineers
- maintainers
- operators
- agents that need explicit config context

Purpose:

- define the environment model
- standardize `.env` expectations
- formalize gateway, embedding, and storage configuration
- separate dev / staging / prod assumptions

Think of it as:

- the configuration contract

### `DATA_MODEL.md`

Audience:

- engineers
- maintainers
- data stewards
- agents that generate or transform seed data

Purpose:

- define the canonical truth schema
- formalize dimensions, principles, puzzles, belief logs, and blind spot archives
- preserve `embedding_text` semantics
- keep seed data governable and retrievable

Think of it as:

- the data model authority

### `API_CONTRACTS.md`

Audience:

- engineers
- maintainers
- client integrators
- agents that change API behavior

Purpose:

- define canonical endpoint contracts
- preserve stable request / response shapes
- formalize degraded-mode behavior
- keep runtime metadata and API semantics observable

Think of it as:

- the API contract authority

---

## 2. How These Documents Relate

These seven files are not redundant.
They operate at different layers:

- `AGENTS.md` tells automated modifiers how to behave.
- `PROJECT_RULES.md` tells humans how to think about the project.
- `ARCHITECTURE.md` tells everyone how the system is structured.
- `OPERATIONS.md` tells maintainers how to keep the system alive and recover it.
- `ENVIRONMENT.md` tells maintainers and agents how runtime configuration must be expressed.
- `DATA_MODEL.md` tells maintainers and agents how truth data must be structured and governed.
- `API_CONTRACTS.md` tells implementers and clients what the runtime interface must promise.

In short:

- `AGENTS.md` = how to change
- `PROJECT_RULES.md` = why to change carefully
- `ARCHITECTURE.md` = what the system is
- `OPERATIONS.md` = how to run and recover it
- `ENVIRONMENT.md` = how to configure it correctly
- `DATA_MODEL.md` = how the truth data must be modeled
- `API_CONTRACTS.md` = how the API must behave at the boundary

Supporting baseline artifacts:

- `SEED_AUTHORING_GUIDE.md` = how seed data should be authored and expanded
- `.env.example` and `env/` = how environment templates are expressed in practice
- `seeds/` = the canonical starter seed corpus

---

## 3. Recommended Reading Order

If you are an AI agent:

1. `AGENTS.md`
2. `ARCHITECTURE.md`
3. `OPERATIONS.md`
4. `ENVIRONMENT.md`
5. `DATA_MODEL.md`
6. `API_CONTRACTS.md`
7. `SEED_AUTHORING_GUIDE.md`
8. `PROJECT_RULES.md`

If you are a human engineer new to the repo:

1. `PROJECT_RULES.md`
2. `ARCHITECTURE.md`
3. `OPERATIONS.md`
4. `ENVIRONMENT.md`
5. `DATA_MODEL.md`
6. `API_CONTRACTS.md`
7. `SEED_AUTHORING_GUIDE.md`
8. `AGENTS.md`

If you are debugging production or runtime behavior:

1. `OPERATIONS.md`
2. `ARCHITECTURE.md`
3. `ENVIRONMENT.md`
4. `DATA_MODEL.md`
5. `API_CONTRACTS.md`
6. `SEED_AUTHORING_GUIDE.md`
7. `PROJECT_RULES.md`

If you are planning a refactor:

1. `PROJECT_RULES.md`
2. `ARCHITECTURE.md`
3. `ENVIRONMENT.md`
4. `DATA_MODEL.md`
5. `API_CONTRACTS.md`
6. `SEED_AUTHORING_GUIDE.md`
7. `AGENTS.md`
8. `OPERATIONS.md`

---

## 4. Shared Non-Negotiable Themes

All seven documents share the same core principles:

- TruthOS is not a generic chatbot backend.
- TruthOS must optimize for truthful, grounded, structured reasoning.
- Graceful degradation is mandatory.
- Single-point failures must not hard-crash the whole system if degraded meaning can still be served.
- SQLite remains the canonical structured source of truth.
- LanceDB remains the high-precision semantic retrieval layer.
- OpenClaw remains the routing / gateway layer.
- Health and observability must reflect the actual runtime path.
- `embedding_text` must retain its semantic role.
- truth data must remain structured, governable, and semantically sharp.
- API shapes must stay stable even when runtime mode changes underneath.
- Security, redaction, and guardrails must not be weakened casually.

---

## 5. Practical Use

When giving Codex or another agent a task, the recommended opener is:

```text
Before making changes, read AGENTS.md, PROJECT_RULES.md, ARCHITECTURE.md, OPERATIONS.md, ENVIRONMENT.md, DATA_MODEL.md, API_CONTRACTS.md, and SEED_AUTHORING_GUIDE.md and follow them as the repository constitution, blueprint, runbook, configuration contract, data model authority, API contract authority, and seed-authoring baseline.
```

When onboarding a human engineer, the recommended path is:

- read `PROJECT_RULES.md` to understand the worldview
- read `ARCHITECTURE.md` to understand the system
- read `OPERATIONS.md` to understand runtime and recovery
- read `ENVIRONMENT.md` to understand environment and configuration boundaries
- read `DATA_MODEL.md` to understand truth data structure and seed semantics
- read `API_CONTRACTS.md` to understand endpoint shape and degraded-mode guarantees
- read `SEED_AUTHORING_GUIDE.md` to understand how seed rows should be authored, reviewed, and expanded
- read `AGENTS.md` to understand automation constraints

---

## 6. Repository Layout

These files are intended to live together at the repo root:

```text
/Users/tongwei/.openclaw/inspirit-truthos/
  AGENTS.md
  PROJECT_RULES.md
  ARCHITECTURE.md
  OPERATIONS.md
  ENVIRONMENT.md
  DATA_MODEL.md
  API_CONTRACTS.md
  README_CONSTITUTION.md
```

Optional prompt helpers may also live here:

- `CODEX_PROMPT_ULTRA_SHORT.md`
- `CODEX_PROMPT_SHORT.md`
- `CODEX_PROMPT_FULL.md`
- `README_PROMPTS.md`
- `pick_codex_prompt.sh`

Baseline artifacts may also live here:

- `SEED_AUTHORING_GUIDE.md`
- `.env.example`
- `env/`
- `seeds/`

---

## 7. Final Framing

These documents exist to prevent a common failure mode:

people keep changing the system locally,
but no one preserves the meaning of the system globally.

TruthOS is intended to be:

- reflective
- resilient
- explicit
- governable
- recoverable

The constitution set exists so the repository can evolve without losing its core identity.
