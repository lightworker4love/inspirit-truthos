# Phase 2 Ollama Local Handoff

## What changed

- Added an explicit non-gateway embedding mode: `ollama-local`
- Kept `/healthz` truthful with `embedding_gateway=false`
- Switched local Docker development to use host Ollama embeddings at `http://host.docker.internal:11434/v1`
- Added `scripts/check_embedding_mode.sh` for mode verification
- Updated docs to distinguish temporary local mode from real OpenClaw gateway mode

## Why it changed

Local TruthOS needed a working primary embeddings path without pretending OpenClaw gateway support already existed.
Ollama now provides the primary local embeddings endpoint for development, while preserving the distinction between:

- `gateway`
- `ollama-local`
- `openai`
- `sqlite`

## Current health output

```json
{
  "status": "ok",
  "embedding_gateway": false,
  "vector_index": true,
  "embedding_mode": "ollama-local",
  "retrieval_mode": "vector"
}
```

## Why this is not real gateway mode

- The active embeddings endpoint is Ollama on `11434`
- OpenClaw still does not expose a usable `/v1/embeddings` HTTP endpoint
- `check_gateway_mode.sh` should continue to fail in this setup

## Required path to real OpenClaw gateway mode

- OpenClaw must expose `POST /v1/embeddings`
- The gateway surface should also expose a matching model id through `/v1/models`
- TruthOS can then switch to `EMBEDDING_PROVIDER=gateway` and a real OpenClaw base URL

## Verification commands

```bash
docker compose up --build -d
./scripts/check_embedding_mode.sh
./scripts/smoke_test.sh
curl -s http://localhost:18000/healthz | python3 -m json.tool
```

## Commit hash

`<fill-after-commit>`
