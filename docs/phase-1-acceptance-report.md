# Phase 1 Acceptance Report

## What Phase 1 Completed

Phase 1.5 adds the missing identity and minimal case-memory behaviors needed for the platform's case continuity direction:

- `preferred_name` is now carried through wisdom session metadata, frontend wisdom state, chat request metadata, backend request parsing, case resolution, prompt building, and final response composition.
- `CaseProfile` now has explicit `schema_version = 1`.
- completed conversations can write back a minimal blueprint:
  - `last_session_insight`
  - `life_themes`
  - `blind_spots`
- guarded `infer_soul_age()` now returns an explainable advisory structure and stays silent when evidence is insufficient.

## File Changes

Core implementation:

- `apps/truth-api/app/case_models.py`
- `apps/truth-api/app/case_resolver.py`
- `apps/truth-api/app/case_insight_service.py`
- `apps/truth-api/app/prompt_builder.py`
- `apps/truth-api/app/main.py`

Frontend / gateway propagation:

- `../workspace/scripts/openclaw-wisdom-proxy.mjs`
- `../workspace/custom-control-ui/wisdom-bootstrap.js`
- `../workspace/custom-control-ui/index.html`
- `../upstream/openclaw/ui/src/ui/storage.ts`
- `../upstream/openclaw/ui/src/ui/app.ts`
- `../upstream/openclaw/ui/src/ui/app-view-state.ts`
- `../upstream/openclaw/ui/src/ui/app-lifecycle.ts`
- `../upstream/openclaw/ui/src/ui/controllers/chat.ts`
- `../upstream/openclaw/src/gateway/protocol/schema/logs-chat.ts`
- `../upstream/openclaw/src/gateway/server-methods/chat.ts`

Tests:

- `apps/truth-api/tests/test_case_identity_phase_1_5.py`
- `../upstream/openclaw/ui/src/ui/app-lifecycle.node.test.ts`
- `../upstream/openclaw/ui/src/ui/controllers/chat.test.ts`

## Naming Priority

The effective naming order is now:

1. request/session `preferred_name`
2. stored `preferred_name`
3. `login_username`
4. `display_name`
5. workspace default
6. `"你"`

## Why Hank Is Now Hank

When wisdom session metadata provides `preferredName = "Hank"`:

- the frontend wisdom state stores `preferredName`
- chat metadata sends `preferred_name = Hank`
- the backend request model receives it unchanged
- `CaseResolver` chooses `preferred_name` before login/display/default names
- `PromptBuilder` serialises `Address as: Hank`
- `compose_response()` uses `case_ctx.address_as`, so the mirror starts with `Hank，`

This prevents `USER.md` or workspace default naming from overriding Hank.

## Tests and Limits

Covered:

- Hank full path from session-derived state to backend response
- fallback behavior without `preferred_name`
- minimal blueprint writeback preserving identity fields
- soul-age guard on insufficient history
- schema version default

Current limits:

- soul-age inference is heuristic, experimental, and advisory only
- blueprint extraction is conservative keyword-based signal capture, not full semantic analysis
- mem0/Qdrant sync is intentionally untouched in this phase

## Deployment Checklist

- [ ] Python test dependencies installed (`requirements.txt` + `pytest`)
- [ ] Playwright Chromium installed for UI browser-mode tests (when required)
- [ ] backend tests run (`apps/truth-api/tests/test_case_identity_phase_1_5.py`)
- [ ] frontend build run (`pnpm -C ../upstream/openclaw/ui build`)
- [ ] gateway/runtime build run (`pnpm -C ../upstream/openclaw build`)
- [ ] Hank `preferred_name` full-path verified
- [ ] anonymous fallback verified
- [ ] blueprint writeback verified (`last_session_insight`, `life_themes`, `blind_spots`)
- [ ] `soul_age` guard verified (`eligible=False` when insufficient data)
- [ ] release artifact rebuild verified (`workspace/custom-control-ui/assets` refresh if UI changed)
- [ ] smoke tests passed (Hank + fallback + writeback + guard)
- [ ] observability logs verified (no raw transcript dump, includes case writeback decision fields)
- [ ] public response contract checked: no prominent `soul_age` exposure in `/api/truth/query`
