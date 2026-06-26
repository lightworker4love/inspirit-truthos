# PR Draft: core-identity-and-blueprint

## Branch

`feature/core-identity-and-blueprint`

## Commit Message

`feat(case): finalize identity continuity and minimal blueprint observability`

## PR Title

`feat: core identity continuity + minimal blueprint writeback observability`

## Scope (staged files)

- `apps/truth-api/app/case_models.py`
- `apps/truth-api/app/case_insight_service.py`
- `apps/truth-api/tests/test_case_identity_phase_1_5.py`

## PR Body (draft)

### Summary

This PR finalizes core Phase 1.5/2 behavior for case identity continuity and blueprint writeback observability without expanding feature scope.

### Included

- keeps `preferred_name`-centric identity handling aligned with current flow
- keeps `soul_age` guarded behavior and non-definitive positioning
- adds structured blueprint writeback observability fields (no raw transcript dump)
- expands test coverage for:
  - no public `soul_age` exposure in `/api/truth/query`
  - writeback observability logging fields

### Out of scope

- no new feature paths
- no blueprint inference expansion
- no change to guarded `soul_age` rules

### Validation

- `python -m py_compile` on truth-api changed modules
- `pytest apps/truth-api/tests/test_case_identity_phase_1_5.py -q`

### Risk

- low-to-medium; changes are scoped to case model wording, writeback logging, and tests only
