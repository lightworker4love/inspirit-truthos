# Sprint 010 - Real Integration - COMPLETE

Date: 2026-05-17
Base: 8a58b5b

## Delivered

- Added runnable Hermes FastAPI service under `apps/hermes_agent/` with `/health`, `/chat`, and `/session/start/{user_id}`.
- Added `apps/hermes-agent/Dockerfile` and wired `hermes-agent` into `docker-compose.yml` on port `8001`.
- Added live session APIs for the Truth Console:
  - `GET /api/sessions/recent`
  - `GET /api/sessions/{session_id}/truth-scores`
  - `GET /api/sessions/stats/summary`
- Registered the session router in the TruthOS FastAPI app and added `/health` as an alias of `/healthz`.
- Added a `Live Monitor` tab to `/console` with summary metrics, recent sessions, truth-score timeline inspection, and 10-second refresh with Pause/Resume controls.
- Added skipped-by-default Docker E2E tests in `tests/test_integration_e2e.py`.
- Updated CI to validate Hermes health/chat and the Live Monitor APIs in the full-stack job.

## Validation

- `python3 -m py_compile` passed locally for the new Hermes service, session API, TruthOS app wiring, and bridge modules.
- `.venv/bin/python -m pytest tests/test_integration_e2e.py -q` passed locally with 2 skipped, as intended unless `RUN_E2E=true`.
- Full Docker validation is performed by GitHub Actions because this local folder is a scaffold and local Docker/git credentials are unavailable.

---

# Sprint 009 - Hermes x TruthOS Integration - COMPLETE

Date: 2026-05-17
Base: 7001a71

## Delivered

- `packages/hermes_truthos_bridge/` with `TruthOSClient`, `TruthOSHook`, and fire-and-forget helper.
- `packages/hermes-truthos-bridge/` compatibility/doc directory from the Sprint 009 brief.
- Fire-and-enrich async pattern: Hermes never blocks on TruthOS.
- Soul context pre-loading at session start through `TruthOSHook.get_soul_context()`.
- Docker Compose network `inspirit-net` attached to `truth-api`; ready for a future Hermes service.
- `TRUTHOS_BASE_URL` environment support in `TruthOSClient`.
- `tests/test_hermes_bridge.py` with timeout, connection error, enrichment, guidance, and soul context coverage.
- CI bridge reachability check added.

First sprint where real conversations can flow into TruthOS.
Soul Map can now accumulate from live Hermes traffic.

---

# Sprint 008 - Coach Review UI + Truth Console MVP - COMPLETE

Date: 2026-05-17
Base: 98510fe0a4a553756df134c1639209a813ba5437

## Delivered

- `GET /console` serves `truth-console.html`.
- 5-tab Truth Console: Soul Map, Blind Spots, Hard Cases, Designer Reviews, Knowledge Evolution.
- Added `PATCH /api/soul-map/{user_id}/pattern`.
- Added `PATCH /api/soul-map/{user_id}/blind-spot/{id}`.
- Added Designer console API reads for hard cases, reviews, and knowledge evolution.
- Added human coach review writeback: `POST /api/designer/coach-review/{hardcase_id}`.
- Added `tests/test_truth_console.py` with console route, Soul Map, Blind Spots, PATCH, and hard-case filter coverage.
- Updated CI with live console check and Soul Map API check.

First sprint where a human can sit in front of TruthOS and use it.

---

# Sprint 007 - Designer Agent + Knowledge Evolution Loop - COMPLETE

Date: 2026-05-16

## Summary

Sprint 007 closes the hard-case loop:

- Added migration 006 for hard-case status, Designer Agent summaries, prompt variants, AB tests, designer reviews, and knowledge evolution records.
- Added `DesignerAgent` with a truth-first weighted rubric, hard-case diagnosis, prompt A/B generation, deterministic AB evaluation, knowledge-layer writeback, and coach escalation when inconclusive.
- Added Designer Agent API endpoints for reviewing a single hard case and processing pending hard cases.
- Wired `/api/truth/query` so detected hard cases are written as pending, immediately reviewed when migration 006 columns are present, and returned with `designer_review` plus `knowledge_evolution_written`.
- Updated seed import so fresh databases run migrations 004, 005, and 006.
- Added tests for migration 006 idempotency/preservation and Designer Agent resolution/escalation behavior.

## Validation

- `.venv/bin/python -m pytest tests/test_migration_006.py tests/test_designer_agent.py -q` passed: 6 tests.
- `.venv/bin/python -m py_compile` passed for changed Python files.
- Full local `pytest tests/` is blocked in this scaffold by missing full-repo modules such as `app.dimension_classifier`; GitHub Actions must validate against the real repo checkout.

## Operational Notes

- Local shell git push is still blocked by missing credentials.
- Remote publishing should use the GitHub connector and target `master`.
- CI should run migrations 004, 005, and 006 before pytest and validate the Designer Agent endpoint in full-stack.

---

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
