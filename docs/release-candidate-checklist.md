# Release Candidate Checklist (Phase 1.5 / 2)

This checklist is the formal RC gate for case identity propagation, minimal blueprint writeback, and guarded `soul_age` behavior.

## Prerequisites

- Python 3.11 virtualenv available (example: `.venv311`)
- Node 22+ and `pnpm` installed for `openclaw`
- dependency install:
  - `python -m pip install -r apps/truth-api/requirements.txt`
  - `python -m pip install pytest`
  - `pnpm -C ../upstream/openclaw install`
  - `pnpm -C ../upstream/openclaw/ui install`
- browser runtime for UI browser tests (if needed):
  - `pnpm -C ../upstream/openclaw/ui exec playwright install chromium`

## RC Validation Flow

### 1. Backend syntax + tests

- syntax check:
  - `.venv311/bin/python -m py_compile apps/truth-api/app/main.py apps/truth-api/app/case_models.py apps/truth-api/app/case_resolver.py apps/truth-api/app/case_insight_service.py apps/truth-api/app/prompt_builder.py`
- phase test suite:
  - `.venv311/bin/python -m pytest apps/truth-api/tests/test_case_identity_phase_1_5.py -q`

### 2. Frontend build

- control UI build:
  - `pnpm -C ../upstream/openclaw/ui build`

### 3. Gateway/runtime build

- gateway/runtime compile:
  - `pnpm -C ../upstream/openclaw build`

### 4. Hank full-path smoke test

- run:
  - `.venv311/bin/python -m pytest apps/truth-api/tests/test_case_identity_phase_1_5.py -q -k hank_preferred_name_full_path`
- expected:
  - request accepts `preferred_name=Hank`
  - `CaseResolver` resolves `address_as=Hank`
  - response mirror starts with `Hank，`

### 5. Anonymous fallback smoke test

- run:
  - `.venv311/bin/python -m pytest apps/truth-api/tests/test_case_identity_phase_1_5.py -q -k fallback_when_no_preferred_name`
- expected:
  - no `preferred_name` still returns valid response
  - fallback naming path remains stable

### 6. Blueprint writeback smoke test

- run:
  - `.venv311/bin/python -m pytest apps/truth-api/tests/test_case_identity_phase_1_5.py -q -k \"minimal_blueprint_writeback_preserves_identity or blueprint_writeback_observability_logs\"`
- expected:
  - updates only `last_session_insight`, `life_themes`, `blind_spots`
  - logs include `case_id`, `triggered`, `updated_fields`, `skip_reason`
  - identity fields remain intact

### 7. `soul_age` guard smoke test

- run:
  - `.venv311/bin/python -m pytest apps/truth-api/tests/test_case_identity_phase_1_5.py -q -k \"soul_age_not_emitted_when_history_is_insufficient or hank_preferred_name_full_path\"`
- expected:
  - insufficient rounds => `eligible=False`, `soul_age=None`
  - public `/api/truth/query` payload does not expose `soul_age`

## Optional One-Command Runner

- `bash scripts/rc_validate_phase_1_5.sh`

This script performs the same core checks and exits non-zero on failure.

## Missing Dependency Troubleshooting

- `pytest: command not found`
  - use `.venv311/bin/python -m pip install pytest`
- Playwright Chromium missing
  - run `pnpm -C ../upstream/openclaw/ui exec playwright install chromium`
- `pnpm` not found
  - install `pnpm` first, then re-run `pnpm -C ../upstream/openclaw install`
