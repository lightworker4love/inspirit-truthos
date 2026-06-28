Repo root: /Users/tongwei/.openclaw/inspirit-truthos

Before making changes, read AGENTS.md, PROJECT_RULES.md, ARCHITECTURE.md, OPERATIONS.md, ENVIRONMENT.md, DATA_MODEL.md, API_CONTRACTS.md, and SEED_AUTHORING_GUIDE.md in /Users/tongwei/.openclaw/inspirit-truthos and follow them as the repository constitution.

This repo is inspirit-truthos, the TruthOS reasoning core for AI Mentor, Second Me, and the Life Knowledge Platform. It is not a generic chatbot backend.

Preserve:
- SQLite as canonical truth source
- LanceDB as high-precision retrieval
- OpenClaw as routing layer
- FastAPI as API surface

Preserve graceful degradation:
- embeddings: gateway -> OpenAI -> SQLite mode
- retrieval: LanceDB -> auto-build -> SQLite fallback

Do not hard-crash if degraded meaning can still be served. Keep /healthz, /system/status, and /api/truth/query truthful about runtime mode. Protect embedding_text, keep truth data semantics stable, keep API shapes stable across modes, keep responsibilities clear, keep environment selection explicit, do not leak secrets, and verify compile, vector build, and key endpoints after changes.
Use `seeds/` and `env/` as the canonical seed-authoring and environment configuration baseline.
