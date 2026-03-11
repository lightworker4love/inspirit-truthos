# TruthOS PRD

## Background
TruthOS is the truth operating system layer for the in spirit AI system. The first goal is to turn truth dimensions, principles, and puzzles into a deployable local service.

## Problem Definition
Spiritual or reflective content becomes hard to reuse when it stays as loose text. Without schema, seed import, and API contracts, future retrieval and reasoning will drift.

## Product Goals
- Store truth dimensions, principles, and puzzles in SQLite.
- Provide a local API for health checks and truth query stubs.
- Create a stable seed import path for future dataset expansion.

## User Roles
- seeker
- coach
- designer
- agent

## MVP Scope
- SQLite schema
- seed import script
- FastAPI server
- `/healthz`
- `/api/truth/query`
- Docker Compose local startup

## Functional Modules
- dimension storage
- principle storage
- puzzle storage
- belief logging
- blind spot archive
- truth query stub

## Non-Functional Requirements
- local-first
- deterministic bootstrap
- simple structure
- easy future extension

## Acceptance Criteria
- repo can be created and started locally
- `docker compose up` starts the API
- `/healthz` returns ok
- `/api/truth/query` returns the documented stub payload
- seeds can be imported with `python scripts/seed_import.py`
