# Sprint 006 - Soul Map Engine - COMPLETE

Date: 2026-05-15

## Summary

Sprint 006 brings the Soul Map tables to life:

- Added migration 005 for Soul Map depth fields, blind-spot depth fields, and `hardcasebuffer`.
- Added `SoulMapEngine` for pattern accumulation, decay-weighted significance, active lessons, stage transitions, blind-spot upsert, and hard-case detection.
- Wired `/api/truth/query` to update Soul Map state after truth-eval writeback.
- Injected Soul Map summary, primary recurring pattern, and evolution stage into the query writeback context.
- Added `GET /api/soul-map/{user_id}` and `GET /api/soul-map/{user_id}/blind-spots`.
- Added unit coverage for Soul Map weighting, evolution stages, blind-spot severity, hard-case detection, primary pattern selection, and migration 005 idempotency.

## Validation

- `.venv/bin/python -m pytest tests/test_soul_map_engine.py tests/test_migration_005.py -q` passed: 9 tests.
- `.venv/bin/python -m py_compile` passed for changed Python files.
- GitHub Actions `TruthOS CI #23` passed on `master`:
  - `test`: success
  - `full-stack`: success
  - `py-compile`: success
  - full-stack validated live Soul Map writeback and `GET /api/soul-map/{user_id}`.
- Full `pytest tests/` in this local scaffold is blocked because this folder is not a full repo checkout and is missing app modules that exist on `master`; GitHub Actions passed against the real repo.

## Operational Notes

- Local `git clone` and `git push` remain blocked by missing GitHub credentials.
- Remote publishing is done with the GitHub app connector.
- CI runs migration 004 and migration 005 on the test DB before pytest.

---

# Sprint 005 - Full-Stack Validation - COMPLETE

Date: 2026-05-14

## Sprint 005 Status

Completed remotely:

- Added `.github/workflows/ci.yml` on `master`.
- Preserved legacy query response fields: `dimensions`, `puzzles`, and `response`.
- Added `truthevals` compatibility view over `truth_evals`.
- Added API backward-compatibility test coverage.
- Added fallback `truth_map.truth_claim.axiom` so fresh databases with no puzzle rows still return a complete four-layer truth map.
- GitHub Actions `TruthOS CI #6` passed on `master`:
  - `test`: success
  - `full-stack`: success
  - `py-compile`: success

Local constraints remain:

- `docker compose up -d --build` cannot run here because Docker is not installed in this shell.
- Real local `git clone` / `git push origin master` is still blocked:
  - HTTPS: no non-interactive username/token.
  - SSH: `Permission denied (publickey)`.
  - `gh`: not installed/authenticated.

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
