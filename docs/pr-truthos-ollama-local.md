# PR: TruthOS temporary Ollama local embeddings mode

## Summary

This change adds a temporary `ollama-local` embeddings mode for local TruthOS development.
It moves primary local embeddings off official OpenAI fallback while keeping health reporting honest:

- `embedding_gateway=false`
- `embedding_mode="ollama-local"`

This is a working local acceleration path, not real OpenClaw gateway mode.

## What changed

- Added explicit embedding provider detection with a dedicated `ollama-local` mode
- Kept `/healthz` truthful for non-gateway local embeddings
- Updated local Docker defaults to reach host Ollama from the container
- Added `scripts/check_embedding_mode.sh`
- Updated README and handoff docs to distinguish temporary local mode from real gateway mode
- Added tests covering `ollama-local` detection and health reporting

## Why it changed

TruthOS needed a stable local primary embeddings path without incorrectly labeling Ollama as OpenClaw gateway support.
This change improves local retrieval quality and cost control while preserving an explicit architectural boundary between:

- real OpenClaw gateway mode
- temporary local Ollama mode
- official OpenAI fallback
- SQLite fallback

## What was intentionally not changed

- No core reasoning behavior was changed
- No claim of real OpenClaw gateway support was added
- `check_gateway_mode.sh` was not removed; it should still fail in `ollama-local`
- Local `.env` was not included
- Unrelated worktree changes such as `reasoning.py` and `retriever.py` were not included

## Verification performed

```bash
python3 -m py_compile \
  apps/truth-api/app/config.py \
  apps/truth-api/app/gateway_check.py \
  apps/truth-api/app/embedding_pipeline.py \
  apps/truth-api/app/main.py \
  apps/truth-api/tests/test_truthos_integration_phase_2.py

./.venv311/bin/python -m pytest apps/truth-api/tests/test_truthos_integration_phase_2.py -q
./.venv311/bin/python -m pytest apps/truth-api/tests/test_case_identity_phase_1_5.py -q

docker compose up --build -d
./scripts/check_embedding_mode.sh
./scripts/smoke_test.sh

curl -s http://localhost:18000/healthz | python3 -m json.tool
curl -s -X POST http://localhost:18000/api/truth/query \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"mode-check-user","session_id":"mode-check-001","message":"我一直在關係裡討好對方，卻感到很委屈，不知道為什麼","mode":"mentor","language":"zh"}' \
  | python3 -m json.tool
```

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

## Why this is not real OpenClaw gateway mode

- The active embeddings endpoint is Ollama on `11434`
- OpenClaw still does not expose a usable `/v1/embeddings` HTTP endpoint for TruthOS
- `embedding_gateway` correctly remains `false`
- `check_gateway_mode.sh` should still fail in this setup

## Follow-up path to real gateway mode

- OpenClaw must expose `POST /v1/embeddings`
- The same gateway surface should expose a matching embedding model through `/v1/models`
- TruthOS can then switch from `EMBEDDING_PROVIDER=ollama-local` to `EMBEDDING_PROVIDER=gateway`

## Risks / notes for reviewers

- Local `.env` was intentionally excluded because it contains machine-specific values
- `env/truthos.dev.env` was also intentionally excluded from this deliverable
- If the embedding model changes again, the LanceDB index should be rebuilt so vector dimensions stay aligned
