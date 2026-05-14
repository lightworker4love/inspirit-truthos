# Sprint 005 - Full-Stack Validation - PARTIAL COMPLETE

Date: 2026-05-14

## Completed

- Added GitHub Actions CI at `.github/workflows/ci.yml`.
- Added a GitHub-hosted `full-stack` job that:
  - builds and starts `docker compose`,
  - waits for `http://localhost:18000/healthz`,
  - sends a live `/api/truth/query` request,
  - validates all four `truth_map` layers,
  - validates `verification_track`,
  - validates legacy additive fields `dimensions`, `principles`, `puzzles`, `response`,
  - checks `truthevals` writeback from inside the running `truth-api` container.
- Preserved legacy query response fields in `apps/truth-api/app/main.py`.
- Added `truthevals` compatibility view over `truth_evals` for Sprint005 validation queries.
- Added `tests/test_api_backward_compatibility.py`.
- Added fallback `truth_map.truth_claim.axiom` for fresh databases with no puzzle rows.

## Local Validation

Completed in the Codex workspace:

- `python3 -m py_compile` passed for changed Python files.
- `.venv/bin/python -m pytest tests/test_migration_004.py tests/test_seed_validator.py tests/test_truth_map_response.py tests/test_truth_verification.py tests/test_verification_writeback.py -q` passed: 15 tests.

The local workspace is still a scaffold, not a full real checkout, so the API import test that requires the full repo dependency set is intended to run in GitHub Actions.

## Remaining Blockers

- Local Docker validation is blocked because this shell has no `docker` command.
- Local Git clone/push is still blocked:
  - HTTPS: no non-interactive username/token.
  - SSH: `Permission denied (publickey)`.
  - `gh`: not installed.
- GitHub Actions status could not be confirmed through the available connector: commit status returned no statuses and workflow-run lookup returned no runs. The workflow file is present on `master`; if Actions are disabled for the repo, enable Actions in repository settings and rerun.

## Required Operator Action

1. Enable or confirm GitHub Actions for `lightworker4love/inspirit-truthos`.
2. Install/start Docker Desktop locally if local `docker compose` validation is required.
3. Resolve one local Git credential path:
   - install/login `gh`, or
   - configure HTTPS PAT, or
   - register the local SSH public key in GitHub.

---

# Sprint 004 - Truth Properties Integration - COMPLETE

Sprint 004 integrated TruthOS' five truth properties into the real repo structure:

- Consistency
- Plurality
- Objectivity
- Discoverability
- Verifiability

The implementation is adapted to the current lightweight FastAPI pipeline:

`classify_dimensions -> retrieve_puzzles -> compose_response`

`TruthVerificationLayer` now runs during `POST /api/truth/query`, before the final response is returned, and each query writes a `truth_evals` audit row.
