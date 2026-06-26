Repo root: /Users/tongwei/.openclaw/inspirit-truthos

Before making changes, read AGENTS.md, PROJECT_RULES.md, ARCHITECTURE.md, OPERATIONS.md, ENVIRONMENT.md, DATA_MODEL.md, API_CONTRACTS.md, and SEED_AUTHORING_GUIDE.md in /Users/tongwei/.openclaw/inspirit-truthos and treat them as the repository constitution, system blueprint, runbook, configuration contract, data model authority, API contract authority, and seed-authoring baseline.

This repository is inspirit-truthos, the TruthOS semantic reasoning core for AI Mentor, Second Me, and the Life Knowledge Platform. It is not a generic chatbot backend, not a vector DB demo, and not a mystical text generator. Build for truthful, grounded, structured reasoning, resilience, observability, and graceful degradation.

Honor the architecture boundaries:
- SQLite = canonical structured truth source
- LanceDB = high-precision truth puzzle retrieval layer
- OpenClaw = routing / gateway layer
- OpenAI client = app-side embedding/model client
- FastAPI = API surface and orchestration layer

Honor the required runtime behavior:
- embedding path: gateway -> official OpenAI fallback -> SQLite degraded mode
- retrieval path: LanceDB -> auto-build index if possible -> SQLite keyword fallback
- /api/truth/query must still return usable structured output even in degraded mode
- /healthz and /system/status must report actual runtime mode, including gateway status, vector index status, embedding mode, and retrieval mode
- API contracts must preserve stable outer response shapes across gateway, OpenAI, and SQLite modes

Protect the semantic model:
- do not casually drift schema or rename core fields
- preserve embedding_text as the preferred semantic field
- keep LanceDB focused on truth puzzle / principle / method retrieval, not generic chat memory
- keep dimensions, principles, puzzles, belief logs, and blind spot archives structurally distinct
- keep `seeds/` and `env/` aligned with `SEED_AUTHORING_GUIDE.md` and `ENVIRONMENT.md`
- keep `/healthz`, `/system/status`, `/api/truth/query`, `/case/blueprint/summary`, `/case/belief-log`, and `/api/truth/blindspot/write` contract-safe
- keep file responsibilities clear and do not collapse logic into main.py

Preserve engineering discipline:
- prefer small, composable changes over large rewrites
- explain current behavior, proposed behavior, risk, and migration impact before major refactors
- keep configuration explicit across dev / staging / prod and do not rely on accidental machine state
- do not leak API keys, tokens, credentials, or local secret paths
- do not weaken guardrails, redaction, or logging safety

Minimum verification after behavior changes:
- python compile check
- vector build path
- /healthz
- /system/status
- /api/truth/query

If tradeoffs appear:
- prefer truthful output over impressive output
- prefer elegant degradation over total failure
- preserve meaning under imperfect conditions
