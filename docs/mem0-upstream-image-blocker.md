# Mem0 Upstream Image Blocker

## Status
Status: blocked pending upstream publishable non-latest tag. citeturn0view0  
External dependency wait state; first local activation is not ready while this blocker persists. citeturn0view0

## Summary
- The truth-api scaffolding and governance design are not the cause of this delay; local Python packaging, virtual environment (Python 3.12), and targeted memory test suites are verified and pass locally.
- The Qdrant vector store is healthy and reachable on the local compose network.
- The verified official Mem0 REST API image identity is `mem0/mem0-api-server`, but currently only `latest` is verifiable.
- We have introduced a minimal, explicit Qdrant config contract via `mem0-config.yaml` (`MEM0_CONFIG_PATH`), but the upstream `mem0-api-server:latest` image eagerly instantiates a hardcoded `pgvector` DEFAULT_CONFIG during import/startup. This causes the application to crash immediately before it can read or honor the external Qdrant config.

## Why activation is blocked
> **EXCEPTION NOTE**: Local-only bring-up exception approved. The `mem0/mem0-api-server:latest` image is temporarily allowed for this first local validation only. This does not satisfy final pinned-tag policy. No shared rollout is allowed under this exception.

1. First local activation remains blocked by upstream image behavior. The `mem0-api-server:latest` image crashes upon import because it fundamentally requires PostgreSQL dependencies (`psycopg2`) to evaluate its own hardcoded defaults, even when explicitly configured to use `qdrant`.
2. Do not attempt to bypass this by injecting PostgreSQL dependencies into the container. The correct fix is an upstream release that defers config evaluation or packages dependencies correctly.
3. `docker-compose.yml` remains in a local-only exception state and must not be treated as activation-ready until a verified non-latest tag is proven to honor external configs properly.

## Verified facts
- **Local Packaging:** truth-api editable packaging is fixed and targeted memory pytest files pass.
- **Qdrant:** Healthy and active in compose validation.
- **Mem0 Local Setup:** The mem0 container successfully receives `OPENAI_API_KEY` and the explicit Qdrant config contract (`mem0-config.yaml`).
- **Activation impact:** Blocked by upstream image/config behavior (eager pgvector DEFAULT_CONFIG evaluation failure).

## Local-only exception
- Operator-approved local-only bring-up exception: for this validation, the compose image may temporarily point to `mem0/mem0-api-server:latest`.
- This exception still does not satisfy the final pinned-tag policy, does not authorize any shared rollout, and requires reverting to a verified non-latest tag once one is published.

## Not blocked by
- truth-api memory policy design, editable packaging, or local test suite.
- local scaffolding layout, runbooks, or deployment checklist.
- any OpenClaw runtime configuration change.
- plugin routing or legacy plugin configuration revival.

## Reactivation conditions
1. Wait for an official upstream publishable non-latest tag to be released for `mem0/mem0-api-server`.
2. Update `docker-compose.yml` to pin that exact tag.
3. Re-run local compose validation.
4. Confirm `mem0` no longer falls back to `pgvector` at import/startup and correctly honors `MEM0_CONFIG_PATH`.
5. Confirm the `/health` endpoint responds successfully.
6. The first local activation checklist is re-opened only after steps 1–5 succeed.

## Guardrails
- Do not change the OpenClaw runtime configuration while this blocker remains unresolved.
- Do not revive any legacy plugin configuration in `openclaw.json`.
- Do not activate services or uncomment compose blocks for a shared rollout until the blocker is cleared.
- Do not workaround the upstream crash by adding pgvector dependencies (`psycopg2`) locally.

## Proposed status line
Status: Mem0 blocked by upstream image/config behavior.
