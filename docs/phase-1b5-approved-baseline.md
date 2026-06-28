# Phase 1B.5 Approved Baseline

Date: 2026-03-14

This note freezes the current local deployment state as the approved Phase 1B.5 baseline. No runtime code changes are included in this freeze.

## 1. Build Result

- `docker compose --progress plain build truth-api` completed successfully
- image built: `inspirit-truthos-truth-api:latest`
- the earlier hanging `docker compose build truth-api` process was terminated and replaced by the successful plain-progress rebuild

## 2. Container Status

- container: `inspirit-truthos-truth-api-1`
- current state: `Up (healthy)`
- container was recreated from the successful rebuilt image and reached healthy status before final validation rerun

## 3. Validation Result

- `./scripts/validate_phase1b.sh` passed after the rebuilt container became healthy
- passed checks:
  - schema validation for minimal payloads
  - baseline V1 query
  - V2 dry-run stub query
- note:
  - the script logs `Schema file missing: /app/schemas/case_reflection.schema.json`
  - current validation still passes because the invalid `case_reflection` payload is correctly rejected

## 4. Confirmed Provider / Model Discovery Inputs

- confirmed `.env` keys inside the container:
  - `OPENAI_BASE_URL`
  - `OPENAI_API_KEY`
  - `OPENAI_FALLBACK_API_KEY`
  - `OPENAI_FALLBACK_BASE_URL`
- confirmed model discovery path from the container:
  - `http://host.docker.internal:8080/v1/models`
- confirmed model discovery result:
  - endpoint responded successfully
  - 25 models were returned
  - observed examples include:
    - `gpt-5`
    - `gpt-5.4`
    - `gpt-5.3-codex`
    - `gpt-5.3-codex-high`
    - `gpt-5.3-codex-mid`

## 5. Exact Gate Required Before Phase 1C Reactivation

Phase 1C must remain frozen until all of the following are true on a freshly rebuilt `truth-api` container:

1. `docker compose --progress plain build truth-api` completes successfully
2. `docker compose up -d truth-api` completes and `inspirit-truthos-truth-api-1` reaches `healthy`
3. `./scripts/validate_phase1b.sh` passes end-to-end without rerun timing races
4. container `.env` still exposes the confirmed OpenAI provider keys listed above
5. `curl http://host.docker.internal:8080/v1/models` from inside the container still returns the expected model list successfully

Until that gate is re-confirmed, this Phase 1B.5 state is the approved baseline and Phase 1C should not be reactivated.
