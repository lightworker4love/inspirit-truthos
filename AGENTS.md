# AGENTS.md
# TruthOS Project Rules for Codex and Contributors

## 1. Project Identity

This repository is `inspirit-truthos`.

TruthOS is the semantic reasoning core of the in spirit AI system.

It is **not** a generic chatbot backend.
It is a **truth-oriented reflective reasoning engine** that supports:

- AI Mentor
- Second Me
- Life Knowledge Platform

TruthOS must help users move from:
- confusion
- emotional entanglement
- limiting beliefs
- repeated life patterns

toward:
- reflection
- discernment
- clearer responsibility
- grounded action

The system should behave like a **Human Consciousness Operating System**, not merely a text generator.

---

## 2. Core System Philosophy

### 2.1 Truth before fluency
The system must prefer:
- grounded outputs
- structured reasoning
- safe fallback behavior

over:
- impressive wording
- hallucinated certainty
- brittle dependencies

### 2.2 Never crash when meaning can still be served
If one subsystem fails, degrade gracefully.

Priority order:
1. LanceDB semantic retrieval
2. Rebuild index if possible
3. SQLite keyword fallback
4. Return useful reasoning response anyway

### 2.3 Codex must preserve continuity
Do not rewrite the repository in a way that breaks the existing working flow unless explicitly asked.

---

## 3. Architecture Rules

TruthOS uses a layered architecture:

- SQLite = structured source of truth
- LanceDB = high-precision semantic retrieval layer
- OpenClaw / gateway = model routing layer
- OpenAI client = embedding / model client
- FastAPI = application and reasoning API

### Important:
LanceDB is **not** treated as a generic chat memory store.

LanceDB is the:
- high-precision truth puzzle index
- method / principle retrieval layer
- semantic access layer for the TruthOS reasoning engine

SQLite remains the fallback source of truth.

---

## 4. Non-Negotiable Reliability Rules

### 4.1 The API must never hard-fail because of gateway issues
If local OpenClaw gateway fails:
- automatically fall back to OpenAI official endpoint if configured

If embeddings fail entirely:
- fall back to SQLite keyword retrieval

### 4.2 The API must never hard-fail because of missing vector index
If LanceDB index is missing:
- auto-build it if possible
- otherwise use SQLite fallback

### 4.3 /api/truth/query must always return a usable response
Even in degraded mode, the endpoint should still produce:
- mirror
- truth_view
- coach_question
- action

### 4.4 Health checks must reflect actual runtime mode
The system must expose:
- gateway status
- vector index existence
- embedding mode
- retrieval mode

---

## 5. Required Runtime Modes

TruthOS must support these modes:

### Mode A — Full semantic mode
- OpenClaw gateway available
- embeddings available
- LanceDB available

Use:
- gateway embeddings
- LanceDB retrieval

### Mode B — Fallback semantic mode
- OpenClaw unavailable
- OpenAI official endpoint available
- LanceDB available

Use:
- OpenAI embeddings
- LanceDB retrieval

### Mode C — Degraded reasoning mode
- embeddings unavailable
- LanceDB unavailable or missing

Use:
- SQLite keyword retrieval
- reasoning composer still returns structured output

---

## 6. API Output Contract

### 6.1 /healthz
Must return at least:

```json
{
  "status": "ok",
  "embedding_gateway": true,
  "vector_index": true,
  "embedding_mode": "gateway"
}
```

Allowed values for `embedding_mode`:

- `gateway`
- `openai`
- `sqlite`

### 6.2 /system/status

Must expose current runtime path:

```json
{
  "gateway": "openclaw",
  "embedding": "gateway",
  "retrieval": "lancedb",
  "vector_index": true
}
```

### 6.3 /api/truth/query

Must return structured reasoning output:

```json
{
  "mirror": "...",
  "truth_view": "...",
  "coach_question": "...",
  "action": "...",
  "dimension": "...",
  "principles": ["..."],
  "retrieval_mode": "lancedb",
  "embedding_mode": "gateway"
}
```

This endpoint must never return raw crashes caused by:

- gateway outage
- embedding provider failure
- missing LanceDB index

---

## 7. Data Model Rules

TruthOS currently uses:

- 12 truth dimensions
- 100 core principles
- 1200 truth puzzles

These are part of the project’s semantic core.

Do not casually rename schema fields without migration planning.

Key tables include:

- `truth_dimensions`
- `core_principles`
- `truth_puzzles`
- `belief_logs`
- `blind_spot_archives`

Important:

`embedding_text` is the preferred semantic field for vectorization.
Do not replace it with `statement` only unless explicitly requested.

Reason:
`embedding_text` may include:

- dimension
- principle
- contextual keywords
- reframed meaning

This improves retrieval quality.

---

## 8. Retrieval Rules

### 8.1 Preferred retrieval pipeline

- dimension classifier
- semantic retrieval
- principle selection
- reasoning composer

### 8.2 Retrieval fallback order

- LanceDB vector search
- auto-build LanceDB index
- SQLite keyword fallback

### 8.3 top_k guidance

Default semantic retrieval:

- `top_k = 12`

Do not aggressively reduce this unless tested.

### 8.4 Future reranking

If adding reranking:

- do not remove base retrieval
- reranking must be additive, not destructive

Recommended future pipeline:

- retrieve top 40
- rerank to top 8–12
- compose response

---

## 9. Reasoning Rules

The reasoning composer should generate:

- mirror
- truth_view
- coach_question
- action

Definitions:

- `mirror`: reflect the user’s immediate lived state
- `truth_view`: name the deeper pattern or principle
- `coach_question`: open a meaningful reflective question
- `action`: provide one grounded next step

Important:

Do not over-mystify outputs.
Do not make unsupported metaphysical claims sound certain.
Do not present speculation as truth.

Use language that is:

- reflective
- clear
- grounded
- actionable

---

## 10. Gateway and Embedding Rules

### 10.1 OpenClaw is a routing layer

OpenClaw is not a substitute for:

- `openai` Python client
- `lancedb` Python package

Do not assume a machine-level OpenClaw install makes the repo reproducible.

### 10.2 Reproducibility is mandatory

All runtime dependencies required by the repo must be declared in:

- `apps/truth-api/requirements.txt`

At minimum include:

- `openai>=1.0`
- `lancedb`
- `pandas`
- `pyarrow`
- `numpy`
- `tqdm`
- `python-dotenv`

Do not rely on globally installed packages.

### 10.3 Embedding client behavior

Embedding pipeline should:

- try gateway first
- fall back to official OpenAI if configured
- fail gracefully into SQLite retrieval if both unavailable

---

## 11. Security and Safety Rules

### 11.1 Do not leak secrets

Never print raw:

- API keys
- tokens
- credentials
- local secret paths

### 11.2 Preserve existing guardrails

If changing config or scripts:

- do not weaken existing security posture
- do not bypass redaction or guardrails

### 11.3 Safe logging

Logs should be useful, but never dump full secrets or sensitive request payloads unnecessarily.

---

## 12. Change Management Rules

### 12.1 Prefer small, composable changes

When modifying the repo:

- avoid giant rewrites
- preserve current working behavior
- make isolated improvements

### 12.2 Explain before large refactors

If a major refactor is needed, first summarize:

- current behavior
- proposed behavior
- risk
- migration impact

### 12.3 Keep file intent clear

Important files and their roles:

- `gateway_check.py` = gateway health and routing detection
- `embedding_pipeline.py` = embedding provider orchestration
- `vector_index.py` = LanceDB creation and validation
- `retriever.py` = retrieval logic and fallback chain
- `reasoning.py` = structured response synthesis
- `main.py` = API surface
- `scripts/build_vector_index.py` = vector index build entrypoint

Do not blur responsibilities unnecessarily.

---

## 13. Testing Rules

At minimum, changes should be verified through:

- Python compile check
- vector build command
- health endpoint
- truth query endpoint

Expected commands:

```bash
python -m compileall apps/truth-api/app scripts/build_vector_index.py
python scripts/build_vector_index.py
```

Expected endpoints:

- `GET /healthz`
- `GET /system/status`
- `POST /api/truth/query`

Goal:

Every change should preserve at least degraded-mode operability.

---

## 14. Project Tone Rules

This repository is serious about:

- discernment
- reflective guidance
- system resilience

Avoid turning it into:

- a generic assistant demo
- a mystical word generator
- an over-engineered framework experiment

Build for:

- clarity
- durability
- graceful degradation
- future extensibility

---

## 15. Golden Rule

If you must choose between:

- elegant failure
- and total crash

choose elegant failure.

If you must choose between:

- impressive output
- and truthful, grounded output

choose truthful, grounded output.

TruthOS exists to preserve meaning under imperfect conditions.

---

## 16. Local Agentic OS v2 Rules 

### 16.1 Staging vs. Canonical Truth
The system must enforce a strict boundary between generated insight (Hypothesis/Staging) and verified wisdom (Canonical).
- **Hypothesis:** All new spiritual interpretations, case reflections, and blueprint updates generated by the reasoning composer start as drafts.
- **Canonical:** An insight only becomes Truth if it passes human-in-the-loop review or strict policy promotion.
- **Do not flatten** spiritual patterns or psychological reflections into unchecked truth claims.

### 16.2 Writeback and Mutation Governance
- The system must respect the `BLUEPRINT_WRITEBACK_ENABLED` kill switch at all times.
- Silent modifications to core memory or the user's Soul Blueprint are **strictly forbidden**.
- All memory mutations, additions to the truth puzzle registry, or blueprint changes must generate an Audit Event matching `audit_event.schema.json`.

### 16.3 Promotion and Agentic Review
Before a hypothesis integrates into `MEMORY.md` or LanceDB:
1. It must be evaluated against the V2 schemas in `/schemas`.
2. It must be documented using the `promotion_record.schema.json`.
3. If an agent loops, fails, or hallucinates standard truth constructs, it must trigger the `retrospection_template` and gracefully degrade to SQLite keyword fallback.

### 16.4 Accept No Ambiguity (The VERIFY Rule)
When interacting with the repository or proposing automated configuration changes:
- Do not invent repository facts. 
- Do not assume pipeline state. 
- If the state of a file, kill switch, or memory sync task is uncertain, explicitly mark it as `[VERIFY]` and pause for Operator confirmation.
