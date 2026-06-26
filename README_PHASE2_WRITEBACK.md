# Phase 2 Writeback Integration

This document covers the minimum viable Phase 2 integration for the TruthOS Daily Reflection Pipeline.

## What Phase 2 Adds

- FastAPI writeback contract
- SQLite staging tables
- dashboard materializer job
- smoke payload and smoke command
- duplicate guard and draft-only governance checks

## New API Endpoints

- `POST /api/reflection/writeback`
- `POST /api/reflection/materialize`
- `GET /api/reflection/runs/{run_date}?user_id=...`
- `GET /api/reflection/dashboard/overview?user_id=...`

## Staging Tables

- `reflection_runs`
- `reflection_discernment_layers`
- `reflection_truth_mappings`
- `dashboard_snapshots`
- `dashboard_daily_metrics`
- `dashboard_pattern_snapshots`
- `soul_map_candidate_events`
- `blind_spot_candidate_events`
- `belief_log_candidate_events`
- `case_summary_candidate_events`
- `core_principle_draft_events`
- `truth_puzzle_draft_events`
- `writeback_audit_log`

Materialized cache tables:

- `dashboard_overview_cache`
- `dimension_trends_cache`
- `recurring_patterns_cache`
- `belief_shift_cache`
- `blind_spot_heatmap_cache`

Views exposed to SQLite readers:

- `dashboard_overview_view`
- `dimension_trends_view`
- `recurring_patterns_view`
- `belief_shift_view`
- `blind_spot_heatmap_view`

## Governance Rules Enforced

- staging writes never touch canonical truth tables
- import drafts must keep `status = draft`
- duplicate payloads are skipped by fingerprint
- append-style candidate streams use duplicate guards
- same-day primary snapshots overwrite only the same `user_id + run_date`

## First-Run Smoke Command

If the API is already running on the default docker port:

```bash
bash scripts/phase2_reflection_smoke.sh
```

If the API is running locally on `8000` instead of `18000`:

```bash
bash scripts/phase2_reflection_smoke.sh http://127.0.0.1:8000
```

The smoke script will:

1. POST the sample writeback payload
2. read back the same day run
3. trigger the materializer
4. read the dashboard overview

## Manual Copy-Paste Smoke Commands

```bash
curl -X POST http://127.0.0.1:18000/api/reflection/writeback \
  -H "Content-Type: application/json" \
  --data @docs/daily-reflection/examples/phase2_smoke_payload.json
```

```bash
curl "http://127.0.0.1:18000/api/reflection/runs/2026-03-13?user_id=smoke-user"
```

```bash
curl -X POST http://127.0.0.1:18000/api/reflection/materialize \
  -H "Content-Type: application/json" \
  -d '{"user_id":"smoke-user","run_date":"2026-03-13","rebuild_all":false}'
```

```bash
curl "http://127.0.0.1:18000/api/reflection/dashboard/overview?user_id=smoke-user"
```

## CLI Materializer

```bash
python scripts/materialize_reflection_dashboard.py --user-id smoke-user --run-date 2026-03-13
```

## Current TODO

- canonical promotion policy is still intentionally out of scope
- multi-tenant partition rules still need a final `tenant_id` policy
- Mem0 integration remains disabled-compatible and null-safe, but not wired
- dashboard frontend still needs a consumer for the new projections
