# TruthOS

[![TruthOS CI](https://github.com/lightworker4love/inspirit-truthos/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/lightworker4love/inspirit-truthos/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**An open-source knowledge graph and semantic memory layer for AI applications.**

TruthOS is the persistence and retrieval layer for the in spirit AI platform.
It integrates with OpenClaw, Claude Code, and local LLMs through RAG and vector
search.

> **Project status:** TruthOS is under active development. The v0.x line is
> suitable for evaluation and contributor testing; APIs and storage schemas may
> change before v1.0.

## What

TruthOS is the persistence and retrieval layer behind in spirit AI. It stores
structured knowledge, reflections, and agent-usable memory so downstream systems
can query and reuse context across sessions.

## Why

Most LLM workflows lose continuity between runs. TruthOS adds a semantic memory
layer with graph relationships and retrieval primitives so AI agents can work
with durable context instead of isolated prompts.

## How it fits

TruthOS sits between application agents and storage/retrieval infrastructure:

- Upstream: OpenClaw, Claude Code, local LLM workflows
- Core role: knowledge graph + semantic memory + retrieval
- Downstream: vector index, SQLite/storage layer, API services, frontend surfaces

## Stack

- Python 3.11
- FastAPI
- SQLite
- Docker Compose
- Next.js frontend in `apps/truthos-web`

## Run locally

```bash
cp .env.example .env
python -m pip install -r apps/truth-api/requirements.txt
python scripts/seed_import.py
python scripts/build_vector_index.py
docker compose up
```

## Service URL

- API: `http://localhost:18000`

## Frontend

`apps/truthos-web` is the TruthOS v1 frontend for guided reflection, Hermes
chat, and Soul Map viewing.

For local development, configure your own `.env.local`. Any public demo
endpoints referenced in this repository are for evaluation only, may be
rate-limited, and may be rotated without notice.

```bash
cd apps/truthos-web
cp .env.local.example .env.local
npm install
npm run dev
```

## Deployment

- Deployment target: Railway
- CI/CD: GitHub Actions with deployment workflow
- See `DEPLOY.md` for deployment details

## Contributing and security

- Read [`CONTRIBUTING.md`](CONTRIBUTING.md) for local setup, tests, and the pull
  request workflow.
- Report vulnerabilities privately according to [`SECURITY.md`](SECURITY.md).
- Follow current maintenance work in the repository's
  [issues](https://github.com/lightworker4love/inspirit-truthos/issues) and
  [`v0.1.0 — Foundation and Reliability`](https://github.com/lightworker4love/inspirit-truthos/milestone/1)
  milestone.
- TruthOS is available under the [MIT License](LICENSE).

## Seed import

```bash
python scripts/seed_import.py
```

## Build vector index

```bash
python scripts/build_vector_index.py
```

If the local embedding gateway is unavailable, the API can still serve requests
via fallback retrieval.

## Run API directly

```bash
cd apps/truth-api
uvicorn app.main:app --reload
```
