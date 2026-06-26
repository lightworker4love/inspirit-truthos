# API_CONTRACTS.md
# TruthOS API Contracts Manual

## 1. Purpose

This document defines the canonical API contracts for `inspirit-truthos`.

It formalizes:

- endpoint responsibilities
- request / response contracts
- required fields
- optional fields
- degraded-mode behavior
- error handling rules
- forward compatibility expectations

This document exists so that:
- human engineers know what each endpoint promises
- Codex / agents can modify implementation without breaking behavior
- clients can safely integrate against stable response shapes
- runtime fallback behavior remains observable and intentional

TruthOS is not just a text-generation endpoint.
Its APIs are part of a structured reflection and reasoning system.

---

## 2. Contract Design Philosophy

## 2.1 Stable structure over ad hoc output
Responses should remain structurally stable even when:
- providers change
- retrieval mode changes
- gateway fails
- vector retrieval is unavailable

The system should change **mode**, not shape.

## 2.2 Degraded mode is still a valid mode
If the system falls back from:
- gateway -> OpenAI
- LanceDB -> SQLite

the response should still preserve the same outer contract whenever possible.

## 2.3 APIs should expose meaningful runtime metadata
TruthOS is a self-healing system.
Therefore the contract should reveal enough state to let operators understand:
- what path was used
- whether the result came from semantic retrieval or fallback
- whether the system is healthy or merely degraded

## 2.4 Reflection APIs are not generic CRUD
These APIs are meant to support:
- guided reflection
- case-level interpretation
- belief shift tracking
- blind spot pattern capture

This matches the broader in spirit system design around long-term memory, reflection, and coach-guided refinement.

---

## 3. API Versioning Principles

## 3.1 Current baseline
TruthOS currently assumes a single internal version line.

Recommended future header strategy:

- `X-TruthOS-Version: 1`

or URL versioning if needed later:

- `/v1/healthz`
- `/v1/api/truth/query`

Until versioning is introduced, all changes should remain backward-compatible whenever possible.

## 3.2 Breaking-change rule
A change is breaking if it:
- removes an existing required field
- changes the meaning of an existing field
- changes a field type
- removes degraded-mode behavior without replacement

Breaking changes require:
- contract update
- migration note
- coordination with clients

---

## 4. Common Response Rules

## 4.1 JSON only
All endpoints return JSON.

## 4.2 Required response shape discipline
Even if internal logic changes, outer response shapes should remain stable.

## 4.3 Error structure
Recommended canonical error shape:

```json
{
  "error": {
    "code": "BAD_REQUEST",
    "message": "message is required",
    "details": {}
  }
}
```

## 4.4 Runtime metadata

Where useful, responses should include:

`embedding_mode`

`retrieval_mode`

`dimension`

`principles`

This is especially important for `/api/truth/query`.

---

## 5. Endpoint: `GET /healthz`

## 5.1 Purpose

Provides a lightweight service health probe.

It must answer:

is the API process alive?

is the embedding gateway reachable?

does the vector index exist?

which embedding mode is active?

This endpoint is part of the operational contract, not optional decoration.

## 5.2 Request

No body.

## 5.3 Response

```json
{
  "status": "ok",
  "embedding_gateway": true,
  "vector_index": true,
  "embedding_mode": "gateway"
}
```

## 5.4 Field semantics

`status`

process health indicator

expected value: `"ok"`

`embedding_gateway`

whether primary gateway is currently reachable and usable

`vector_index`

whether LanceDB index exists and is readable

`embedding_mode`

active embedding mode

allowed values:

`gateway`

`openai`

`sqlite`

## 5.5 Behavioral rules

must return 200 if API service is alive, even in degraded mode

should not fail just because gateway is down

degraded mode should be represented in fields, not by crashing

## 5.6 Example degraded response

```json
{
  "status": "ok",
  "embedding_gateway": false,
  "vector_index": true,
  "embedding_mode": "openai"
}
```

---

## 6. Endpoint: `GET /system/status`

## 6.1 Purpose

Provides runtime observability for the current execution path.

This endpoint should help answer:

what gateway path is active?

what embedding path is active?

what retrieval path is active?

is semantic mode available?

## 6.2 Request

No body.

## 6.3 Response

```json
{
  "gateway": "openclaw",
  "embedding": "gateway",
  "retrieval": "lancedb",
  "vector_index": true
}
```

## 6.4 Field semantics

`gateway`

current gateway state

expected values:

`openclaw`

`unavailable`

`embedding`

active embedding source

expected values:

`gateway`

`openai`

`sqlite`

`retrieval`

active retrieval path

expected values:

`lancedb`

`sqlite`

`vector_index`

whether the LanceDB index is currently available

## 6.5 Behavioral rules

must remain lightweight

should not trigger rebuild operations

should report current mode, not mutate the system

---

## 7. Endpoint: `POST /api/truth/query`

## 7.1 Purpose

This is the core TruthOS reasoning endpoint.

It accepts a user reflection / conflict / life-pattern question and returns a structured reasoning response based on:

dimension classification

truth puzzle retrieval

principle synthesis

fallback-aware runtime behavior

This endpoint should embody the TruthOS query pipeline:
user question -> dimension classifier -> retrieval -> reasoning composer -> structured response.

## 7.2 Request

Minimal request

```json
{
  "user_id": "u_001",
  "session_id": "s_001",
  "message": "我明明想幫家人，最後卻變成爭吵。"
}
```

Extended request

```json
{
  "user_id": "u_001",
  "session_id": "s_001",
  "message": "我明明想幫家人，最後卻變成爭吵。",
  "mode": "mentor",
  "depth": "deep",
  "language": "zh-TW"
}
```

## 7.3 Request fields

`user_id` (required)

user identifier

`session_id` (required)

session identifier

`message` (required)

user question / reflection input

`mode` (optional)

reasoning interaction mode

recommended values:

`mentor`

`coach`

`reflective`

`depth` (optional)

reasoning depth hint

recommended values:

`light`

`standard`

`deep`

`language` (optional)

output language hint

example:

`zh-TW`

## 7.4 Response

Recommended canonical response:

```json
{
  "mirror": "你想幫家人，背後其實有很深的愛，也有很強的責任感。",
  "truth_view": "當幫助變成接管，關係就會從支援轉為壓力。",
  "coach_question": "你是在陪伴他，還是在替他承擔人生？",
  "action": "先把你的責任和他的責任分開寫下來。",
  "dimension": "relationship",
  "principles": ["REL_001", "COM_001"],
  "retrieval_mode": "lancedb",
  "embedding_mode": "gateway"
}
```

## 7.5 Field semantics

`mirror`

reflects the user’s lived state in a grounded, non-judgmental way

`truth_view`

names the deeper pattern, principle, or distortion

`coach_question`

opens reflective inquiry rather than over-solving

`action`

gives one grounded next step

`dimension`

primary inferred dimension for the question

`principles`

list of principle codes selected or associated

`retrieval_mode`

retrieval path used

allowed values:

`lancedb`

`sqlite`

`embedding_mode`

embedding path used

allowed values:

`gateway`

`openai`

`sqlite`

## 7.6 Behavioral rules

must return 200 when possible, even in degraded mode

must never hard-fail solely because gateway is unavailable

if LanceDB unavailable, should return `retrieval_mode=sqlite`

if embeddings unavailable, should return `embedding_mode=sqlite`

response structure should remain stable across modes

## 7.7 Example degraded response

```json
{
  "mirror": "你很努力想讓事情變好，也因此背了過多責任。",
  "truth_view": "你把愛和責任綁得太緊，所以一有失控就容易轉成衝突。",
  "coach_question": "如果你不再替對方扛全部，你最害怕的是什麼？",
  "action": "先辨識：哪些是你的責任，哪些不是。",
  "dimension": "relationship",
  "principles": ["REL_001"],
  "retrieval_mode": "sqlite",
  "embedding_mode": "sqlite"
}
```

---

## 8. Endpoint: `POST /case/blueprint/summary`

## 8.1 Purpose

This endpoint summarizes a case / life story into a structured life blueprint.

It extends the earlier “case research and summary” design:

from life story

to core theme

to recurring patterns

to limiting beliefs

to soul lessons

to action suggestions

This is already consistent with your earlier case summary API design.

6️⃣666-靈性導向的研究與摘要 API

## 8.2 Request

```json
{
  "case_id": "case-2026-0001",
  "user_id": "u_001",
  "client_profile": {
    "age": 32,
    "background": "科技業 PM"
  },
  "life_story": "（長文字，個案自述、引導紀錄、你整理的片段）",
  "context": {
    "stage": "initial_assessment",
    "coach_perspective": "容易過度承擔他人情緒"
  },
  "options": {
    "language": "zh-TW",
    "depth": "standard"
  }
}
```

## 8.3 Request fields

`case_id` (required)

`user_id` (optional but recommended)

`client_profile` (optional)

`life_story` (required)

`context` (optional)

`options` (optional)

## 8.4 Response

```json
{
  "case_id": "case-2026-0001",
  "summary": {
    "core_theme": "過度責任與自我價值綁定",
    "life_patterns": [
      "習慣把別人的穩定視為自己的責任"
    ],
    "limiting_beliefs": [
      "若我不幫到底，我就不夠有愛"
    ],
    "soul_lessons": [
      "學習界線中的慈悲"
    ],
    "action_suggestions": [
      "練習區分支援與控制"
    ]
  },
  "truth_mapping": {
    "dimensions": ["relationship", "belief", "compassion"],
    "principles": ["REL_001", "BEL_001", "COM_001"]
  }
}
```

## 8.5 Field semantics

`summary.core_theme`

The main life lesson / developmental tension at this stage.

`summary.life_patterns`

Recurring emotional or relationship patterns.

`summary.limiting_beliefs`

Key restrictive beliefs or protective mechanisms.

`summary.soul_lessons`

Truth-oriented developmental lessons appropriate to this case.

`summary.action_suggestions`

Small, grounded, next-step practices.

`truth_mapping`

Maps the summary to TruthOS structures:

`dimensions`

`principles`

## 8.6 Behavioral rules

should not return vague “spiritual fluff” without structure

should remain case-specific

should allow coach guidance to later refine outputs

should support future coach notes integration, consistent with your existing review layer design.

8️⃣888-佟位 operating system：技術骨架…

---

## 9. Endpoint: `POST /case/belief-log`

## 9.1 Purpose

Creates a belief transformation event record.

This endpoint should write into the belief log layer and support:

before/after belief tracking

topic tagging

link to dimension / principle

future longitudinal growth analysis

## 9.2 Request

```json
{
  "user_id": "u_001",
  "case_id": "case-2026-0001",
  "belief_before": "如果我不幫到底，我就不夠有愛。",
  "belief_after": "我的愛不需要透過接管別人的人生來證明。",
  "tag": "relationship"
}
```

## 9.3 Request fields

`user_id` (required)

`case_id` (optional)

`belief_before` (required)

`belief_after` (optional but strongly recommended)

`tag` (optional)

`related_dimension_code` (optional future extension)

`related_principle_code` (optional future extension)

`evidence` (optional future extension)

## 9.4 Response

```json
{
  "status": "logged",
  "user_id": "u_001",
  "case_id": "case-2026-0001",
  "tag": "relationship"
}
```

## 9.5 Behavioral rules

must store at least the original belief

should support partial write even if `belief_after` is not yet available

should remain lightweight and log-oriented

should not attempt to generate a full case summary

This endpoint aligns with your belief-log and coach-review operating model.

8️⃣888-佟位 operating system：技術骨架…

---

## 10. Endpoint: `POST /api/truth/blindspot/write`

## 10.1 Purpose

Creates or updates a blind spot archive entry.

This endpoint is meant to turn repeated hidden distortions into explicit records.

This is directly aligned with your consciousness blind spot mechanism.

✡️核心機制：in spirit AI 神經系統

## 10.2 Request

```json
{
  "user_id": "u_001",
  "title": "把責任感誤認成愛",
  "trigger_pattern": "家人一失序就立刻想接手全部",
  "known_theory": "知道要有界線，也知道不能替別人活",
  "practical_failure_mode": "一有危機就重新接手，之後又累又怨"
}
```

## 10.3 Request fields

`user_id` (required)

`title` (required)

`trigger_pattern` (required)

`known_theory` (optional)

`practical_failure_mode` (optional)

`suggested_anchors` (optional future extension)

`related_puzzles` (optional future extension)

## 10.4 Response

```json
{
  "status": "written",
  "title": "把責任感誤認成愛"
}
```

## 10.5 Behavioral rules

should create a usable archive entry even if some optional fields are omitted

should be idempotent-friendly in future

should support later enrichment with anchors, recurrence counts, and related puzzle IDs

---

## 11. Error Contracts

## 11.1 Standard format

Use:

```json
{
  "error": {
    "code": "BAD_REQUEST",
    "message": "message is required",
    "details": {}
  }
}
```

## 11.2 Recommended error codes

`BAD_REQUEST`

`VALIDATION_ERROR`

`NOT_FOUND`

`DEPENDENCY_UNAVAILABLE`

`INTERNAL_ERROR`

## 11.3 Degraded-mode rule

Wherever possible:

prefer degraded response over dependency error

do not return 500 just because gateway is down

do not return 500 just because LanceDB is missing if SQLite fallback exists

Example:
If `/api/truth/query` can still answer via SQLite, it should return 200 and report fallback mode.

---

## 12. Client Integration Rules

## 12.1 Clients should not assume full semantic mode

Consumers of the API should read:

`retrieval_mode`

`embedding_mode`

rather than assume every answer came from the same path.

## 12.2 Clients should treat missing optional fields safely

Future fields may be added.
Clients should ignore unknown fields instead of failing.

## 12.3 Stable meaning over rigid internal coupling

Clients should depend on:

contract fields

not internal implementation files

---

## 13. Future Extensions

The following future endpoints are consistent with the current contract family:

`POST /case/reflection`

For event-level reflective analysis.

`POST /api/truth/puzzles/upsert`

For seed dataset and truth puzzle ingestion.

`GET /api/truth/search`

For coach/admin search interface over dimensions / principles / puzzles.

`POST /api/truth/reindex`

For controlled vector index rebuild operations.

These are natural extensions of the current TruthOS design and fit the surrounding architecture of case summary, coach review, and long-term memory.

---

## 14. Final Rule

An API contract is not just a wire format.

In TruthOS, it is the boundary between:

system truth

runtime resilience

reflective usability

client trust

If the contract is stable:

clients stay sane

operators stay informed

degraded mode stays useful

the system can evolve

If the contract drifts:

fallback becomes confusing

integrations break

reasoning becomes harder to trust

Keep the shape stable.
Let the mode change beneath it.


---

## 你現在已經有七塊正式檔案

放在 repo 根目錄就是：

```text
/Users/tongwei/.openclaw/inspirit-truthos/
  AGENTS.md
  PROJECT_RULES.md
  ARCHITECTURE.md
  OPERATIONS.md
  ENVIRONMENT.md
  DATA_MODEL.md
  API_CONTRACTS.md
```

給 Codex 的完整前置句再升級

現在可以固定用這句：

```text
Before making changes, read AGENTS.md, PROJECT_RULES.md, ARCHITECTURE.md, OPERATIONS.md, ENVIRONMENT.md, DATA_MODEL.md, and API_CONTRACTS.md and follow them as the repository constitution, blueprint, runbook, configuration contract, data model authority, and API contract authority.
```

這樣它拿到的已經不是 prompt，而是一整套工程文明。
