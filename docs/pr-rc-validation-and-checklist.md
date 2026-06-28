# PR Draft: rc-validation-and-checklist

## Branch

`chore/rc-validation-and-checklist`

## Commit Message

`chore(rc): add repeatable phase-1.5 validation script and checklist`

## PR Title

`chore: release-candidate validation checklist and runner for phase 1.5/2`

## Scope (staged files)

- `docs/release-candidate-checklist.md`
- `scripts/rc_validate_phase_1_5.sh`

## PR Body (draft)

### Summary

This PR introduces a repeatable RC validation workflow for Phase 1.5/2 closeout.

### Included

- actionable RC checklist covering backend, frontend, gateway/runtime, and smoke checks
- one-command validation runner script
- explicit dependency guidance for missing `pytest` / Playwright runtime

### Out of scope

- no runtime logic changes
- no API contract changes

### Validation

- `bash -n scripts/rc_validate_phase_1_5.sh`
- `bash scripts/rc_validate_phase_1_5.sh`

### Risk

- low; doc/script-only operational change
