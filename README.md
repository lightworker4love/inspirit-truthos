# inspirit-truthos

TruthOS is the semantic reasoning core of the in spirit AI system.

It supports:

- AI Mentor
- Second Me
- Life Knowledge Platform

This repository is not a generic chatbot backend.
It is a truth-oriented reasoning system designed for:

- grounded reflective output
- semantic truth retrieval
- graceful degradation
- observable runtime behavior

## Core Idea

TruthOS helps users move from:

- confusion
- emotional entanglement
- limiting beliefs
- repeated life patterns

toward:

- reflection
- discernment
- clearer responsibility
- grounded action

## System Role

At a high level:

- SQLite is the canonical structured truth source
- LanceDB is the high-precision semantic retrieval layer
- OpenClaw is the routing / gateway layer
- OpenAI fallback preserves embedding resilience
- FastAPI exposes the runtime API

TruthOS is designed to preserve meaning under imperfect conditions.
If one layer fails, the system should degrade gracefully rather than hard-crash.

## Repository Constitution

This repository is governed by the following core documents:

- [AGENTS.md](/Users/tongwei/.openclaw/inspirit-truthos/AGENTS.md)
- [PROJECT_RULES.md](/Users/tongwei/.openclaw/inspirit-truthos/PROJECT_RULES.md)
- [ARCHITECTURE.md](/Users/tongwei/.openclaw/inspirit-truthos/ARCHITECTURE.md)
- [OPERATIONS.md](/Users/tongwei/.openclaw/inspirit-truthos/OPERATIONS.md)
- [ENVIRONMENT.md](/Users/tongwei/.openclaw/inspirit-truthos/ENVIRONMENT.md)
- [DATA_MODEL.md](/Users/tongwei/.openclaw/inspirit-truthos/DATA_MODEL.md)
- [API_CONTRACTS.md](/Users/tongwei/.openclaw/inspirit-truthos/API_CONTRACTS.md)
- [SEED_AUTHORING_GUIDE.md](/Users/tongwei/.openclaw/inspirit-truthos/SEED_AUTHORING_GUIDE.md)
- [README_CONSTITUTION.md](/Users/tongwei/.openclaw/inspirit-truthos/README_CONSTITUTION.md)

Recommended opener for Codex:

```text
Before making changes, read AGENTS.md, PROJECT_RULES.md, ARCHITECTURE.md, OPERATIONS.md, ENVIRONMENT.md, DATA_MODEL.md, API_CONTRACTS.md, and SEED_AUTHORING_GUIDE.md and follow them as the repository constitution, blueprint, runbook, configuration contract, data model authority, API contract authority, and seed-authoring baseline.
```

Additional baseline:

- use [.env.example](/Users/tongwei/.openclaw/inspirit-truthos/.env.example) and [`env/`](/Users/tongwei/.openclaw/inspirit-truthos/env) as the canonical environment templates
- use [`seeds/`](/Users/tongwei/.openclaw/inspirit-truthos/seeds) as the canonical seed baseline

## Prompt Helpers

Prompt presets for Codex:

- [CODEX_PROMPT_ULTRA_SHORT.md](/Users/tongwei/.openclaw/inspirit-truthos/CODEX_PROMPT_ULTRA_SHORT.md)
- [CODEX_PROMPT_SHORT.md](/Users/tongwei/.openclaw/inspirit-truthos/CODEX_PROMPT_SHORT.md)
- [CODEX_PROMPT_FULL.md](/Users/tongwei/.openclaw/inspirit-truthos/CODEX_PROMPT_FULL.md)
- [README_PROMPTS.md](/Users/tongwei/.openclaw/inspirit-truthos/README_PROMPTS.md)
- [pick_codex_prompt.sh](/Users/tongwei/.openclaw/inspirit-truthos/pick_codex_prompt.sh)

## Seed And Env Baseline

- [SEED_AUTHORING_GUIDE.md](/Users/tongwei/.openclaw/inspirit-truthos/SEED_AUTHORING_GUIDE.md)
- [.env.example](/Users/tongwei/.openclaw/inspirit-truthos/.env.example)
- [`env/`](/Users/tongwei/.openclaw/inspirit-truthos/env)
- [`seeds/`](/Users/tongwei/.openclaw/inspirit-truthos/seeds)

## Stack

- Python 3.11
- FastAPI
- SQLite
- LanceDB
- OpenClaw / gateway routing
- Docker Compose

## Quick Start

Recommended local bootstrap order:

```bash
# review the canonical variable contract
sed -n '1,80p' .env.example

# use the dev baseline as your local starting point
cp env/truthos.dev.env .env

# inspect the canonical seed baseline
ls -la seeds

# install runtime dependencies
python -m pip install -r apps/truth-api/requirements.txt

# load seed data into SQLite
python scripts/seed_import.py

# build the LanceDB vector index from the seeded truth data
python scripts/build_vector_index.py

# start the local stack
docker compose up
```

## Service URL

- API: `http://localhost:18000`

## Core Commands

Seed import:

```bash
python scripts/seed_import.py
```

Build vector index:

```bash
python scripts/build_vector_index.py
```

Run API directly:

```bash
cd apps/truth-api
uvicorn app.main:app --reload
```

Compile check:

```bash
python -m compileall apps/truth-api/app scripts/build_vector_index.py
```

## Runtime Expectations

TruthOS should support three runtime modes:

- Full semantic mode: gateway + LanceDB
- Fallback semantic mode: OpenAI fallback + LanceDB
- Degraded reasoning mode: SQLite fallback

If the local embedding gateway is unavailable, the API should still remain serviceable through fallback behavior rather than failing closed.

## Recommended Reading Order

For human engineers:

1. [PROJECT_RULES.md](/Users/tongwei/.openclaw/inspirit-truthos/PROJECT_RULES.md)
2. [ARCHITECTURE.md](/Users/tongwei/.openclaw/inspirit-truthos/ARCHITECTURE.md)
3. [OPERATIONS.md](/Users/tongwei/.openclaw/inspirit-truthos/OPERATIONS.md)
4. [ENVIRONMENT.md](/Users/tongwei/.openclaw/inspirit-truthos/ENVIRONMENT.md)
5. [DATA_MODEL.md](/Users/tongwei/.openclaw/inspirit-truthos/DATA_MODEL.md)
6. [API_CONTRACTS.md](/Users/tongwei/.openclaw/inspirit-truthos/API_CONTRACTS.md)
7. [SEED_AUTHORING_GUIDE.md](/Users/tongwei/.openclaw/inspirit-truthos/SEED_AUTHORING_GUIDE.md)
8. [AGENTS.md](/Users/tongwei/.openclaw/inspirit-truthos/AGENTS.md)

For AI agents:

1. [AGENTS.md](/Users/tongwei/.openclaw/inspirit-truthos/AGENTS.md)
2. [ARCHITECTURE.md](/Users/tongwei/.openclaw/inspirit-truthos/ARCHITECTURE.md)
3. [OPERATIONS.md](/Users/tongwei/.openclaw/inspirit-truthos/OPERATIONS.md)
4. [ENVIRONMENT.md](/Users/tongwei/.openclaw/inspirit-truthos/ENVIRONMENT.md)
5. [DATA_MODEL.md](/Users/tongwei/.openclaw/inspirit-truthos/DATA_MODEL.md)
6. [API_CONTRACTS.md](/Users/tongwei/.openclaw/inspirit-truthos/API_CONTRACTS.md)
7. [SEED_AUTHORING_GUIDE.md](/Users/tongwei/.openclaw/inspirit-truthos/SEED_AUTHORING_GUIDE.md)
8. [PROJECT_RULES.md](/Users/tongwei/.openclaw/inspirit-truthos/PROJECT_RULES.md)

## in spirit AI Platform Integration

### English

TruthOS can be mounted behind OpenClaw as a structured reasoning layer. OpenClaw remains the main routing surface, while TruthOS provides:

- semantic dimension classification
- puzzle/principle retrieval
- structured reflective response blocks
- session-level dimension memory

#### Environment variables

- `OPENAI_BASE_URL`: OpenClaw-compatible embedding/chat gateway URL
- `OPENAI_API_KEY`: API key for gateway or fallback OpenAI
- `EMBEDDING_MODEL`: embedding model for LanceDB indexing and retrieval
- `CHAT_MODEL`: model used by dimension-classifier LLM fallback
- `DIMENSION_CLASSIFIER_LLM_FALLBACK`: enable/disable classifier LLM fallback
- `TRUTHOS_INTERNAL_URL`: internal URL used by `scripts/openclaw_bridge.py`

#### API examples

Query TruthOS:

```bash
curl -X POST http://localhost:18000/api/truth/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "session_id": "sess-001",
    "message": "我一直在關係裡過度解釋自己，越來越焦慮",
    "mode": "mentor"
  }'
```

List all dimensions:

```bash
curl http://localhost:18000/api/truth/dimensions
```

List principles for one dimension:

```bash
curl "http://localhost:18000/api/truth/principles?dimension=relationship"
```

Read session memory:

```bash
curl http://localhost:18000/api/truth/session/user-123
```

#### 12 dimensions

| code | name_zh | name_en | description |
|---|---|---|---|
| motive | 動機 | Motive | Intent and hidden exchange. |
| cognition | 認知 | Cognition | Interpretation and mental framing. |
| emotion | 情緒 | Emotion | Emotional patterns and charge. |
| relationship | 關係 | Relationship | Boundaries, roles, and attachment. |
| belief | 信念 | Belief | Limiting beliefs and inner narratives. |
| evolution | 進化 | Evolution | Growth and repeated lessons. |
| causality | 因果 | Causality | Action and consequence loops. |
| manifestation | 顯化 | Manifestation | Value, money, and exchange. |
| suffering | 痛苦 | Suffering | Pain, collapse, and transformation. |
| freedom | 自由 | Freedom | Release and autonomy. |
| compassion | 慈悲 | Compassion | Care, support, and warmth. |
| discernment | 辨識 | Discernment | Truth, interpretation, and judgment. |

#### Session memory API

`GET /api/truth/session/{user_id}` returns the latest 20 dimension-memory records for a user. This is designed for continuity tracking rather than full transcript storage.

### 中文

TruthOS 可以作為 OpenClaw 後方的結構化推理層。OpenClaw 負責主路由，TruthOS 提供：

- 維度分類與語義補強
- principle / puzzle 結構化檢索
- 結構化回應欄位
- 同一用戶的 session 維度記憶追蹤

#### 環境變數說明

- `OPENAI_BASE_URL`：OpenClaw 相容的 embedding / chat gateway URL
- `OPENAI_API_KEY`：gateway 或 OpenAI fallback 使用的 API key
- `EMBEDDING_MODEL`：LanceDB 建索引與檢索使用的 embedding model
- `CHAT_MODEL`：dimension classifier 啟用 LLM fallback 時使用的 chat model
- `DIMENSION_CLASSIFIER_LLM_FALLBACK`：是否啟用 classifier 的 LLM fallback
- `TRUTHOS_INTERNAL_URL`：`scripts/openclaw_bridge.py` 轉發 TruthOS 時使用的內部 URL

#### API 呼叫範例

查詢 TruthOS：

```bash
curl -X POST http://localhost:18000/api/truth/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "session_id": "sess-001",
    "message": "我一直在關係裡過度解釋自己，越來越焦慮",
    "mode": "mentor"
  }'
```

查詢全部 12 維度：

```bash
curl http://localhost:18000/api/truth/dimensions
```

查詢指定維度 principles：

```bash
curl "http://localhost:18000/api/truth/principles?dimension=relationship"
```

查詢用戶 session 記憶：

```bash
curl http://localhost:18000/api/truth/session/user-123
```

#### Session 記憶 API

`GET /api/truth/session/{user_id}` 會回傳該用戶最近 20 筆維度記憶，用於追蹤演進脈絡，而不是保存完整對話逐字稿。
