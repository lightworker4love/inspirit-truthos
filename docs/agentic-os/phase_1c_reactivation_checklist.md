# Phase 1C Reactivation Checklist

## Purpose
This checklist defines the mandatory gates required before Phase 1C may be reactivated on the local TruthOS runtime.
Phase 1C must remain disabled until all build, validation, and provider/model discovery conditions below are satisfied.

## Scope
Repository root: `/Users/tongwei/.openclaw/inspirit-truthos`. [cite:1]
Truth API entrypoint: `apps/truth-api/app/main.py`. [cite:1]
This checklist applies only to the local `truth-api` service and its `dry_run` path.
This checklist does **not** authorize writeback, canonical promotion, session memory write, or any mutation of legacy blueprint persistence flows.

## Baseline Requirement
Phase 1C may only begin from the approved **Phase 1B.5** baseline.
The runtime must currently preserve:
- V1 baseline request behavior.
- `dry_run=true` returning the non-mutating stub.
- `jsonschema`-based schema loading and validation helpers.
- No connection from runtime to legacy mutating blueprint flows for dry-run execution.

## Hard Safety Rules
- Do not modify `secondme-proxy`.
- Do not bypass `BLUEPRINT_WRITEBACK_ENABLED`. [cite:1]
- Do not enable canonical promotion.
- Do not enable session memory write in `dry_run` mode.
- Do not call legacy mutating blueprint persistence from the new dry-run path.
- Do not begin Phase 1C until all gates below are checked and operator-approved.

## Gate A — Build and Runtime Baseline
- [ ] Run `cd /Users/tongwei/.openclaw/inspirit-truthos`. [cite:1]
- [ ] Run `docker compose build truth-api`. This is required because Compose build is the formal rebuild step for service images from source.[web:81][web:80]
- [ ] Run `docker compose up -d truth-api`. This is required because Compose up recreates/starts the service using the built image.[web:111]
- [ ] Confirm the `truth-api` container is healthy.
- [ ] Do **not** treat `docker compose restart` as sufficient evidence of a correct rebuild.[web:90][web:81]

## Gate B — Phase 1B Validation
- [ ] Run `./scripts/validate_phase1b.sh`.
- [ ] Confirm schema validation passes for all minimal payloads.
- [ ] Confirm the invalid payload case is rejected cleanly.
- [ ] Confirm baseline V1 query still returns the standard `TruthQueryResponse`.
- [ ] Confirm `dry_run=true` still returns the approved Phase 1B.5 stub envelope.
- [ ] Confirm no writeback is executed during dry-run validation.

## Gate C — Provider and Model Discovery
- [ ] Confirm the provider base URL used by the container.
- [ ] Confirm the fast model alias to be used for Phase 1C.
- [ ] Record the exact values or mapping source used for:
  - `OPENAI_BASE_URL`
  - `OPENAI_API_KEY`
  - `OPENAI_FALLBACK_API_KEY`
  - `OPENAI_FALLBACK_BASE_URL`
- [ ] Confirm provider/model discovery is performed **without** modifying application code.
- [ ] Confirm model listing from inside the container succeeds.
- [ ] Save discovery evidence for operator review.

## Gate D — Allowed Phase 1C Scope
Phase 1C is only allowed to proceed under the following narrow scope:
- [ ] `dry_run=true` only.
- [ ] Generate **one** artifact only: `blueprint_instance`.
- [ ] Use the confirmed provider/model only.
- [ ] Strip markdown-wrapped JSON safely before parsing.
- [ ] Generate `Hypothesis ID / UUID` locally outside the LLM.
- [ ] Validate the result against `blueprint_instance.schema.json`.
- [ ] Return the result inside the dry-run envelope only.
- [ ] No writeback.
- [ ] No canonical promotion.
- [ ] No session memory write.

## Gate E — Runtime File Boundaries
- [ ] `apps/truth-api/app/main.py` remains on the approved Phase 1B.5 baseline before Phase 1C changes begin. [cite:1]
- [ ] `apps/truth-api/app/v2_schema_loader.py` remains read-only utility logic. [cite:1]
- [ ] `apps/truth-api/app/v2_validation.py` remains pure validation logic. [cite:1]
- [ ] `apps/truth-api/app/v2_dry_run_agent.py` may exist as a draft, but it must not be reconnected to runtime until this checklist is complete.
- [ ] No change is made to `case_insight_service.py` for initial Phase 1C reactivation.
- [ ] No change is made to `secondme-proxy`. [cite:1]

## Evidence to Attach
Attach the following before approval:
- [ ] Output of `docker compose build truth-api`.
- [ ] Output of `docker compose up -d truth-api`.
- [ ] Output of `./scripts/validate_phase1b.sh`.
- [ ] Container health confirmation.
- [ ] Provider/model discovery output.
- [ ] Model listing output from inside the container.
- [ ] Any remaining `[VERIFY]` items.

## Operator Approval
- [ ] Host operator confirms all gates above are complete.
- [ ] Host operator confirms no unresolved `[VERIFY]` item blocks Phase 1C.
- [ ] Host operator explicitly approves Phase 1C reactivation.
- [ ] AI implementation may only begin **after** this explicit approval.

## Blocked States
If any of the following is true, Phase 1C remains blocked:
- Build not completed.
- Validation script not fully passing.
- Provider base URL not confirmed.
- Fast model alias not confirmed.
- Dry-run stub no longer stable.
- Runtime still attempts mutating side effects.
- Any unresolved `[VERIFY]` item affects provider/model routing or writeback safety.
- Operator approval not given.

## Ready State
Phase 1C may be reactivated only when **all** boxes above are checked and the operator has explicitly approved the next step.

## Suggested Operator Commands
```bash
cd /Users/tongwei/.openclaw/inspirit-truthos
docker compose build truth-api
docker compose up -d truth-api
./scripts/validate_phase1b.sh
docker exec inspirit-truthos-truth-api-1 env | grep -E 'MODEL|OPENAI|API_KEY|API_BASE'
docker exec inspirit-truthos-truth-api-1 sh -lc "cat /app/.env | grep -E '^(MODEL|OPENAI)' | cut -d'=' -f1"
docker exec inspirit-truthos-truth-api-1 curl -s http://host.docker.internal:8080/v1/models
```
