# Phase 2.5 Bridge

This phase closes the loop from daily reflection artifacts to TruthOS staging DB.

## Flow

1. The daily reflection pipeline writes file artifacts for one day.
2. The bridge reads the same-day artifacts from `data/daily_reflections/YYYY-MM-DD/`.
3. It assembles a `POST /api/reflection/writeback` payload.
4. On success it writes `writeback_receipt.json`.
5. On failure it writes `writeback_error.json`.
6. Original daily artifacts are never deleted by bridge failure.

## Default identity

- `user_id`: `tongwei`
- `tenant_id`: `inspirit-local`

Both can be overridden by CLI or env:

- `TRUTHOS_REFLECTION_WRITEBACK_USER_ID`
- `TRUTHOS_REFLECTION_WRITEBACK_TENANT_ID`
- `TRUTHOS_REFLECTION_API_BASE`

## Scripts

- Bridge: [bridge_daily_reflection_to_api.py](/Users/tongwei/.openclaw/inspirit-truthos/scripts/bridge_daily_reflection_to_api.py)
- Wrapper: [run_daily_reflection_writeback.sh](/Users/tongwei/.openclaw/inspirit-truthos/scripts/run_daily_reflection_writeback.sh)

## Parameters

Bridge CLI:

```bash
python scripts/bridge_daily_reflection_to_api.py \
  --date 2026-03-13 \
  --api-base http://127.0.0.1:18000 \
  --user-id tongwei \
  --tenant-id inspirit-local
```

Supported flags:

- `--date YYYY-MM-DD`
- `--api-base`
- `--user-id`
- `--tenant-id`
- `--force`
- `--dry-run`

Wrapper:

```bash
bash scripts/run_daily_reflection_writeback.sh --date 2026-03-13
```

Optional strict mode:

```bash
bash scripts/run_daily_reflection_writeback.sh --date 2026-03-13 --strict
```

Non-strict is the default because bridge failure should not destroy the daily reflection artifact pipeline.

## Receipt format

Success writes:

- `data/daily_reflections/YYYY-MM-DD/writeback_receipt.json`

Shape:

```json
{
  "status": "success",
  "posted_at": "...",
  "run_date": "2026-03-13",
  "user_id": "tongwei",
  "tenant_id": "inspirit-local",
  "api_base": "http://127.0.0.1:18000",
  "endpoint": "http://127.0.0.1:18000/api/reflection/writeback",
  "payload_fingerprint": "...",
  "source_file": ".../reflection.json",
  "response": {},
  "notes": [],
  "retry": {
    "recommended": false,
    "next_retry_command": null
  }
}
```

## Error format

Failure writes:

- `data/daily_reflections/YYYY-MM-DD/writeback_error.json`

Shape:

```json
{
  "status": "error",
  "attempted_at": "...",
  "run_date": "2026-03-13",
  "user_id": "tongwei",
  "tenant_id": "inspirit-local",
  "api_base": "http://127.0.0.1:18000",
  "endpoint": "http://127.0.0.1:18000/api/reflection/writeback",
  "payload_fingerprint": "...",
  "source_file": ".../reflection.json",
  "error_type": "URLError",
  "error_message": "...",
  "notes": [],
  "retry": {
    "recommended": true,
    "next_retry_command": "python ... --force"
  }
}
```

## Retry behavior

- If a success receipt already exists for the same `run_date + user_id`, the bridge skips resend by default.
- Use `--force` to bypass local receipt skip.
- The API duplicate guard still remains active as a second safety layer.

## Missing artifact behavior

If `reflection.json` is missing, bridge fails safely and writes `writeback_error.json`.

## Dry run

```bash
python scripts/bridge_daily_reflection_to_api.py --date 2026-03-13 --dry-run
```

Dry-run prints the assembled payload preview and does not write receipt/error files.

## Why canonical promotion stays manual

Phase 2.5 only closes the staging ingestion loop.
It does not change governance:

- all import drafts remain `status = draft`
- no staging candidate is auto-promoted into canonical truth tables
- promotion remains human-review-gated

This preserves TruthOS’s core rule: plausible interpretation must not be upgraded into truth just because it was generated consistently.
