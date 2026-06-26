# ARCHITECTURE.md
# TruthOS System Architecture Blueprint

## 1. Purpose

This document defines the system architecture of `inspirit-truthos`.

TruthOS is the semantic reasoning core of the in spirit AI system.

It is designed to support:

- AI Mentor
- Second Me
- Life Knowledge Platform

TruthOS is not a general-purpose chatbot backend.
It is a structured reasoning system built to help users move from confusion, emotional entanglement, and limiting beliefs toward reflection, discernment, and grounded action.

At the platform level, this architecture supports the broader in spirit AI direction:
- long-term memory
- guided reflection
- semantic truth retrieval
- resilient fallback behavior
- observable runtime state

This aligns with the wider system goal of building a human-centered AI consciousness support infrastructure rather than a one-shot chat product. :contentReference[oaicite:3]{index=3} :contentReference[oaicite:4]{index=4}

---

## 2. System Context

TruthOS sits inside the broader in spirit AI stack.

### 2.1 Platform relationship

At the platform level:

- **AI Mentor**  
  Handles guided conversation and reflection

- **Second Me**  
  Maintains long-term personal continuity and memory

- **Life Knowledge Platform**  
  Provides the high-trust knowledge and principle layer

TruthOS is the reasoning core that connects user questions to:
- principles
- truth puzzles
- reflective responses
- retrieval modes
- fallback logic

This product framing is consistent with your existing proposal and fundraising materials. :contentReference[oaicite:5]{index=5} :contentReference[oaicite:6]{index=6}

### 2.2 Technical relationship

TruthOS integrates with the wider in spirit infrastructure:

- **OpenClaw**  
  model routing / tool / agent gateway

- **FastAPI**  
  application and API layer

- **SQLite**  
  structured source of truth

- **LanceDB**  
  high-precision semantic retrieval layer

- **Mem0 / Qdrant**  
  broader memory infrastructure in the overall platform

The role of LanceDB is especially important: in the wider system it is intended to function as a precision method / experience / principle memory layer, not as generic chat history. :contentReference[oaicite:7]{index=7}

---

## 3. Architectural Principles

### 3.1 Truth before fluency
The system prioritizes:
- grounded output
- interpretable structure
- resilience under failure
- clear retrieval path

over:
- impressive but unstable answers
- hidden dependency failure
- hallucinated certainty

This aligns with the project’s discernment principle that “plausible” is not the same as “true.” :contentReference[oaicite:8]{index=8}

### 3.2 Graceful degradation
TruthOS must continue to provide meaning even when parts of the system fail.

The architecture is explicitly designed so that:
- gateway failure does not kill the API
- embedding failure does not kill reasoning
- missing vector index does not kill retrieval
- degraded mode still returns usable output

### 3.3 Clear responsibility boundaries
Each layer should have a clear responsibility:
- storage is not routing
- routing is not reasoning
- vector retrieval is not chat memory
- API is not data modeling

---

## 4. High-Level Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                         │
│  - Second Me UI                                             │
│  - AI Mentor UI                                             │
│  - Internal tools / Coach review / admin console            │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI Layer                        │
│  - /healthz                                                  │
│  - /system/status                                            │
│  - /api/truth/query                                          │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     TruthOS Reasoning Layer                 │
│  - Dimension Classifier                                     │
│  - Retriever                                                │
│  - Reasoning Composer                                       │
│  - Fallback Controller                                      │
└───────────────┬────────────────────┬────────────────────────┘
                │                    │
                ▼                    ▼
┌────────────────────────┐   ┌───────────────────────────────┐
│   Embedding / Routing  │   │     Structured Truth Store    │
│  - OpenClaw Gateway    │   │  - SQLite                     │
│  - OpenAI fallback     │   │  - dimensions                │
│  - Gateway health      │   │  - principles                │
└──────────────┬─────────┘   │  - puzzles                   │
               │             │  - belief logs               │
               ▼             │  - blind spot archives       │
┌────────────────────────┐   └───────────────────────────────┘
│     LanceDB Layer      │
│  - truth_puzzles index │
│  - vector search       │
│  - auto-build / verify │
└────────────────────────┘
```

## 5. Core Components

### 5.1 SQLite — Structured Source of Truth

SQLite is the canonical structured data layer for TruthOS.

It stores:

- truth dimensions
- core principles
- truth puzzles
- belief logs
- blind spot archives

Responsibilities

- durable structured storage
- source dataset for index creation
- fallback retrieval source
- metadata filter source

Why SQLite

SQLite provides:

- simplicity
- local-first portability
- easy inspection
- stable fallback behavior

Current semantic core

The current dataset includes:

- 12 truth dimensions
- 100 core principles
- 1200 truth puzzles

This is the minimum semantic core that powers TruthOS reasoning. That structure is already loaded into the project database.

### 5.2 LanceDB — High-Precision Semantic Retrieval Layer

LanceDB is the semantic retrieval engine for TruthOS.

Its job is not to store general chat history.
Its job is to store vectorized truth puzzle knowledge for high-precision retrieval.

Responsibilities

- vector indexing of truth puzzles
- semantic retrieval from embedding_text
- high-precision principle and method access
- index reuse and lazy rebuild support

Why LanceDB

Within the in spirit system, LanceDB is explicitly positioned as:

- a long-term, evolvable experience layer
- a method / principle memory subsystem
- a precision retrieval layer adjacent to the core reasoning system

This is consistent with your LanceDB design notes. 

LanceDB：「AI 的修行手冊」

Why not use statement-only embeddings

TruthOS should embed embedding_text, not only statement.

Reason:
embedding_text can carry:

- dimension
- principle
- contextual keywords
- reframed meaning

This improves semantic recall quality.

### 5.3 OpenClaw — Model Routing Layer

OpenClaw acts as the gateway / routing layer.

Responsibilities

- route embedding requests
- unify local / proxied model access
- provide OpenAI-compatible interface where applicable
- support fallback policy

Important distinction

OpenClaw is not:

- the Python client
- the vector database
- the structured truth store

It is the gateway.

This matches your existing local dual-track architecture, where cloud models are routed through proxy infrastructure while local systems may connect directly to local model services. 

9️⃣999-管理網域：架構檢測與藍圖規劃

002-N SPiRiT AI × Antigravity 技…

Operational caveat

Gateway instability must not collapse the whole system.
A failing gateway should degrade the architecture into:

- official OpenAI embedding fallback
- or SQLite fallback retrieval

### 5.4 FastAPI — Application and API Layer

FastAPI is the entry point for runtime usage.

Primary endpoints

- /healthz
- /system/status
- /api/truth/query

Responsibilities

- expose stable API contract
- orchestrate classifier + retrieval + reasoning
- report system health and runtime mode
- never crash due to single-point downstream failure

FastAPI should not absorb all business logic.
It should coordinate services, not become a giant mixed-responsibility file.

## 6. TruthOS Query Pipeline

The central runtime path of the system is the TruthOS query pipeline.

### 6.1 Standard pipeline

```text
User Question
   ↓
Dimension Classifier
   ↓
Retriever
   ↓
Truth Puzzles
   ↓
Reasoning Composer
   ↓
Structured Truth Response
```

### 6.2 Step-by-step detail

Step 1 — User Question

The input enters through /api/truth/query.

Typical input:

- confusion
- emotional conflict
- relationship issue
- repeating life pattern
- self-reflection question

Step 2 — Dimension Classifier

The system estimates the most relevant truth dimensions.

Examples:

- relationship
- emotion
- belief
- motive
- discernment

This narrows retrieval space and improves puzzle relevance.

Step 3 — Retriever

The retriever attempts:

- LanceDB semantic search
- auto-build LanceDB index if missing
- SQLite keyword fallback if vector retrieval unavailable

This is the system’s retrieval fault-tolerance core.

Step 4 — Truth Puzzles

The retriever returns relevant truth puzzle records:

- dimension
- principle
- statement
- misbelief
- truth_reframe
- coach_prompt

Step 5 — Reasoning Composer

The reasoning layer synthesizes retrieved items into a structured response.

Output fields:

- mirror
- truth_view
- coach_question
- action

Step 6 — API Response

The final response returns not only the reflective content, but also runtime metadata such as:

- dimension
- principles
- retrieval mode
- embedding mode

## 7. Retrieval Modes

TruthOS supports three major retrieval modes.

### 7.1 Mode A — Gateway + LanceDB

```text
Question
  ↓
OpenClaw Gateway Embedding
  ↓
LanceDB Search
  ↓
Reasoning
```

Used when:

- OpenClaw is healthy
- embedding endpoint is available
- LanceDB index exists

### 7.2 Mode B — OpenAI Fallback + LanceDB

```text
Question
  ↓
OpenAI Embedding Fallback
  ↓
LanceDB Search
  ↓
Reasoning
```

Used when:

- OpenClaw is down or unstable
- official OpenAI embedding endpoint is available
- LanceDB index exists

### 7.3 Mode C — SQLite Fallback

```text
Question
  ↓
Dimension Classifier
  ↓
SQLite Keyword Search
  ↓
Reasoning
```

Used when:

- embeddings unavailable
- vector index unavailable
- gateway and fallback embedding both fail

This mode is degraded, but still meaningful.

## 8. Self-Healing Strategy

The system is explicitly designed as a self-healing retrieval architecture.

### 8.1 Failure classes

A. Gateway failure

Symptoms:

- 502
- 404
- model list unavailable
- embedding model missing

Response:

- mark gateway unavailable
- switch to OpenAI fallback if configured

B. Vector index missing

Symptoms:

- LanceDB table absent
- missing path
- uninitialized index

Response:

- auto-build index from SQLite source
- continue retrieval after successful build

C. Embedding failure

Symptoms:

- both primary and fallback embedding unavailable

Response:

- skip vector path
- use SQLite keyword retrieval

### 8.2 Golden rule

The system should never fail closed if a meaningful degraded path still exists.

## 9. Health and Observability

### 9.1 /healthz

Purpose:
basic health probe and runtime availability summary

Expected response:

```json
{
  "status": "ok",
  "embedding_gateway": true,
  "vector_index": true,
  "embedding_mode": "gateway"
}
```

Meaning of fields

- status: API process health
- embedding_gateway: whether primary gateway is reachable and usable
- vector_index: whether LanceDB index exists and is readable
- embedding_mode: current runtime path

Allowed values:

- gateway
- openai
- sqlite

### 9.2 /system/status

Purpose:
runtime observability endpoint

Expected response:

```json
{
  "gateway": "openclaw",
  "embedding": "gateway",
  "retrieval": "lancedb",
  "vector_index": true
}
```

This endpoint should answer:

- which path is active
- which fallback is currently in effect
- whether semantic mode is available

Why observability matters

A fallback system without observability becomes a haunted house:
something is working, but no one knows how.

## 10. Data Flow

### 10.1 Index build flow

```text
SQLite truth_puzzles
   ↓
Read embedding_text
   ↓
Embedding Provider
   ↓
Vector records
   ↓
LanceDB truth_puzzles table
```

### 10.2 Query flow

```text
User question
   ↓
Dimension classifier
   ↓
Embedding provider OR SQLite fallback
   ↓
LanceDB search OR SQLite search
   ↓
Relevant truth puzzles
   ↓
Reasoning composer
   ↓
Structured response
```

### 10.3 Fallback flow

```text
Gateway unavailable
   ↓
OpenAI fallback
   ↓
If also unavailable
   ↓
SQLite fallback
```

## 11. File-Level Architecture

Below is the intended responsibility map of key files.

`apps/truth-api/app/gateway_check.py`

Purpose:

- detect gateway health
- verify embedding model availability
- report provider path

`apps/truth-api/app/embedding_pipeline.py`

Purpose:

- manage embedding provider selection
- primary and fallback embedding calls
- normalize embedding output

`apps/truth-api/app/vector_index.py`

Purpose:

- LanceDB existence check
- index build / validation / reuse
- shared logic for scripts and runtime

`apps/truth-api/app/retriever.py`

Purpose:

- execute 3-layer retrieval chain
- LanceDB search
- auto-build if missing
- SQLite fallback

`apps/truth-api/app/reasoning.py`

Purpose:

- synthesize retrieved knowledge into structured reflective output

`apps/truth-api/app/main.py`

Purpose:

- expose API endpoints
- orchestrate runtime flow
- provide stable response contract

`scripts/build_vector_index.py`

Purpose:

- manual / scripted index build entrypoint
- dev and operational bootstrap tool

## 12. External Integration Context

TruthOS does not live alone.

It is designed to integrate into the larger in spirit ecosystem, including:

- Second Me
- OpenClaw
- broader memory infrastructure
- orchestration layers built around Antigravity / OpenClaw patterns

Your earlier architecture documents already describe a system where:

- OpenClaw is the rational / action layer
- Second Me is the personal / inner layer
- memory flows through shared and layered infrastructure
- bridge / orchestration patterns connect constrained environments to the inner system stack

TruthOS is the reasoning organ inside that larger body. 

003-心靈拓樸圖：Bridge 架構藍圖

001-建立「多宇宙版」 Second Me 部署範本與版本命…

002-N SPiRiT AI × Antigravity 技…

## 13. Future Evolution Path

This document defines the current baseline architecture.
It also anticipates several future upgrades.

### 13.1 Reranking Layer

Future pipeline:

```text
Query
  ↓
Retrieve top 40
  ↓
Rerank top 8–12
  ↓
Reasoning composer
```

Goal:
improve semantic precision without removing retrieval resilience.

### 13.2 Principle Graph

Add structured relations between:

- dimensions
- principles
- puzzles
- blind spot patterns

This would allow:

- principle expansion
- contrast retrieval
- progression-aware reasoning

### 13.3 Blind Spot Feedback Loop

Integrate runtime cases into:

- belief logs
- blind spot archives
- principle reinforcement
- coach review loop

This aligns with your existing design around consciousness blind spot profiles and coach review layers. 

✡️核心機制：in spirit AI 神經系統

8️⃣888-佟位 operating system：技術骨架…

### 13.4 Multi-agent integration

TruthOS can later act as the reasoning core shared by:

- AI Mentor persona
- multiple Second Me personas
- other orchestrated agents in the in spirit ecosystem

That direction is already consistent with your multi-persona and multi-environment deployment planning. 

001-建立「多宇宙版」 Second Me 部署範本與版本命…

## 14. Engineering Boundaries

TruthOS should not drift into these anti-patterns:

### 14.1 Generic chat memory confusion

Do not treat LanceDB as a dump for arbitrary chat logs.

### 14.2 Monolithic API file

Do not let main.py absorb all logic.

### 14.3 Hidden fallback behavior

Do not fallback silently without health visibility.

### 14.4 Mystical overreach

Do not let output style replace actual reasoning structure.

The system may speak with warmth and symbolic depth, but architecture must remain explicit, testable, and accountable.

## 15. Summary

TruthOS is a local-first, structured, self-healing semantic reasoning engine.

Its architecture combines:

- SQLite for canonical structured truth data
- LanceDB for semantic retrieval precision
- OpenClaw for gateway routing
- OpenAI fallback for resilience
- FastAPI for stable API delivery
- Reasoning pipeline for reflective, structured outputs

The system is designed to preserve meaning under imperfect conditions.

That is its true architectural signature.

It is not merely:

- a chat backend
- a vector search demo
- a spiritual content wrapper

It is an attempt to build a reasoning layer for human reflection, continuity, and discernment in the age of AI. 

回應：OpenAI Codex 企劃書

proposal-longform-zh-tw

---

## 你現在可以怎麼放

建議三份一起放在 repo 根目錄：

```text
/Users/tongwei/.openclaw/inspirit-truthos/
  AGENTS.md
  PROJECT_RULES.md
  ARCHITECTURE.md
```

然後給 Codex 的開場句補這句

Before making changes, read AGENTS.md, PROJECT_RULES.md, and ARCHITECTURE.md and follow them as the repository constitution and system blueprint.

這樣 agent 不只知道「要做什麼」，還知道「這台機器為什麼這樣長」。
