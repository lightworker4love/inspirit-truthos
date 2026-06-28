# in spirit AI - Local Agentic OS v2 Deployment Plan

## Purpose
Specifies the rollout phases, governance checks, and criteria for deploying V2 Agentic OS capabilities within the local OpenClaw/TruthOS environment.

## Scope
Covers local host capabilities only. Valid for the `127.0.0.1:18789` OpenClaw mainline. Outlines how staging-to-canonical memory promotion is activated.

## Phased Approach
1. **Phase 0 (Scaffolding):** [CURRENT] Docs-first scaffolding of schemas, templates, and prompts. No runtime code changes.
2. **Phase 1 (Dry-Run API):** Implementing pure validation endpoints that accept V2 schemas but do NOT write to LanceDB/SQLite.
3. **Phase 2 (Staging Memory):** Activation of hypothesis-store [VERIFY: exact location of staging table/file in `/data/` or `MEMORY.md`].
4. **Phase 3 (Canonical Promotion):** Human-in-the-loop promotion gate activation.

## Governance & Review Rules
- **Kill-Switch:** `BLUEPRINT_WRITEBACK_ENABLED` remains FALSE until Phase 3 validates 100% cleanly.
- **Rollback:** See `cc-switch-layer0-rollback.md`.

## [VERIFY] Items
- **[VERIFY]** Ensure LanceDB can comfortably support draft/staging namespace isolation before Phase 2.
- **[VERIFY]** Verify `secondme-proxy` does not cache or prematurely flatten draft state.
