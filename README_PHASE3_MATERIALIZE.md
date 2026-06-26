# Phase 3 Materialize Loop

This phase closes the same-run loop:

`daily artifacts -> writeback -> success receipt -> materialize -> materialize receipt/error -> dashboard cache updated`

## Default behavior

- writeback success triggers materialize by default
- writeback failure skips materialize
- materialize failure does not roll back a successful writeback
- default mode is non-strict

## Flags

Bridge script flags:

- `--materialize`
- `--skip-materialize`
- `--strict-materialize`

Wrapper examples:

```bash
bash scripts/run_daily_reflection_writeback.sh --date 2026-03-13
```

Skip materialize:

```bash
bash scripts/run_daily_reflection_writeback.sh --date 2026-03-13 --skip-materialize
```

Strict materialize:

```bash
bash scripts/run_daily_reflection_writeback.sh --date 2026-03-13 --strict-materialize
```

## Materialize request

The bridge calls:

```json
{
  "user_id": "tongwei",
  "tenant_id": "inspirit-local",
  "run_date": "2026-03-13",
  "mode": "incremental",
  "rebuild_all": false
}
```

Endpoint:

- `POST /api/reflection/materialize`

## Materialize receipt

Success writes:

- `data/daily_reflections/YYYY-MM-DD/materialize_receipt.json`

Key fields:

- `status`
- `posted_at`
- `run_date`
- `user_id`
- `tenant_id`
- `api_base`
- `endpoint`
- `mode`
- `payload_fingerprint`
- `response.materialized_views`

## Materialize error

Failure writes:

- `data/daily_reflections/YYYY-MM-DD/materialize_error.json`

Key fields:

- `status`
- `attempted_at`
- `run_date`
- `user_id`
- `tenant_id`
- `api_base`
- `endpoint`
- `mode`
- `payload_fingerprint`
- `error_type`
- `error_message`
- `retry.next_retry_command`

## Non-strict vs strict-materialize

Non-strict default:

- writeback receipt is preserved
- materialize error is written separately
- wrapper exits `0`
- daily artifacts remain untouched

Strict-materialize:

- writeback still stays committed
- materialize error is still written
- wrapper exits non-zero

## Governance boundary

Materialize is projection only.

It does:

- read staging data
- refresh cache tables
- refresh view-facing projection state

It does not:

- promote drafts
- mutate canonical truth tables
- bypass human review
