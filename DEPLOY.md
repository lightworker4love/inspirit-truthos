# TruthOS Deployment Runbook

## Railway Free Preview Boundary

The public deployment is configured as an early-stage preview on Railway Free.
The plan currently provides a small monthly resource credit and supports the
three services used by this repository, but its CPU, memory, deployment-window,
and availability limits are not a production SLA.

To stay within that boundary:

- keep exactly the three deployed services: `truth-api`, `hermes-agent`, and
  `truthos-web`;
- keep Railway Serverless sleeping enabled for all three services;
- do not schedule keep-alive requests;
- expect a cold start, and occasionally an initial 502, after inactivity; and
- treat successful health checks as preview evidence, not a production-ready
  claim.

Free-tier deployments can be rejected during Railway regional peak hours. If a
reviewed deployment is blocked for that reason, retry it manually outside the
reported window instead of creating an empty commit.

## Local Development

1. Copy the local environment template:

```bash
cp .env.example .env
```

2. Start the local stack:

```bash
docker compose up -d --build
```

3. Check local services:

```bash
curl http://localhost:18000/health
curl http://localhost:8001/health
```

## Manual Railway Deploy

Log in to Railway before deploying:

```bash
railway login
```

Deploy the Truth API service:

```bash
railway up --service truth-api
```

Deploy the Hermes Agent service:

```bash
railway up --service hermes-agent
```

Deploy the TruthOS Web frontend:

```bash
railway up --service truthos-web
```

## Automated and Manual Deploy

After the `RAILWAY_TOKEN` GitHub Actions secret is configured, a runtime change
on `master` runs `TruthOS CI`. A successful push-triggered CI run then starts the
Railway deployment workflow. Documentation-only changes are ignored, and CI is
not duplicated inside the deployment workflow.

The workflow can also be started with **Actions -> Deploy to Railway -> Run
workflow** after reviewing the current `master` commit. This is the supported
way to retry after choosing the Railway Free plan or after a peak-hours block.

Only one Railway deployment runs at a time. A newer deployment cancels an older
in-progress run so the Free plan does not spend resources deploying superseded
commits.

Production smoke checks require the current Railway-generated service domains.
Copy them from the Railway dashboard rather than relying on historical hostnames:

```bash
export TRUTH_API_URL="https://<current-truth-api-domain>"
export HERMES_AGENT_URL="https://<current-hermes-agent-domain>"
export TRUTHOS_WEB_URL="https://<current-truthos-web-domain>"

curl -fsS -w "\nHTTP %{http_code}\n" "$TRUTH_API_URL/healthz"
curl -fsS -w "\nHTTP %{http_code}\n" "$HERMES_AGENT_URL/health"
curl -fsS -o /dev/null -w "HTTP %{http_code}\n" "$TRUTHOS_WEB_URL"
```

The following optional integration check writes synthetic smoke-test data. Run
it only in an environment where that write is intended:

```bash
curl -fsS -w "\nHTTP %{http_code}\n" -X POST "$HERMES_AGENT_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "smoke-user-001", "message": "smoke test ping"}'
```

## Serverless Strategy

The Railway service manifests set `sleepApplication: true`. Railway may put an
inactive service to sleep and wake it on the next request, reducing idle compute
usage at the cost of cold-start latency.

The current `scripts/keepalive.sh` contains historical service hostnames and
must not be scheduled on the Free plan. It is a legacy helper, not evidence that
the preview is available. Scheduling it would defeat Serverless sleeping and
consume the monthly resource credit.

For paid-plan diagnostics only, first change the helper to accept current
verified domains and then run it manually:

```bash
./scripts/keepalive.sh
```

## Production Readiness Checklist

- [x] Docker Compose stack is built and exercised by GitHub CI
- [x] Railway service manifests parse and define health checks
- [x] Railway Serverless sleeping is configured for all three preview services
- [x] Documentation-only changes do not trigger CI or Railway deployment
- [x] Railway deployment waits for the successful push-triggered CI result
- [ ] Current Railway service domains are recorded and return successful health checks
- [ ] The legacy keepalive helper accepts current domains instead of fixed historical URLs
- [ ] Current dependency alerts are triaged before a production-readiness claim
- [ ] A production deployment is followed by read-only health checks and an explicitly authorized write-path smoke test

This checklist describes requirements, not current production availability. The
historical public hostnames previously listed here returned HTTP 404 on
2026-09-16, so production availability is currently **not verified**.

## Auto-Deploy Verification Log

| Date | Trigger | Workflow Run | CI | CD | Smoke Tests |
| --- | --- | --- | --- | --- | --- |
| 2026-05-18 | git push master (commit 4e9a3d8) | 25998301986 | ✓ | ✓ | /health ✓ /chat ✓ Soul Map write ✓ |

## Railway Logs

Truth API logs:

```bash
railway logs --service truth-api
```

Hermes Agent logs:

```bash
railway logs --service hermes-agent
```

TruthOS Web logs:

```bash
railway logs --service truthos-web
```

## GitHub Actions Status

List recent runs:

```bash
gh run list
```

Watch a specific run:

```bash
gh run watch <run-id>
```

## Rollback

1. Open the Railway dashboard.
2. Select the `inspirit-truthos` project.
3. Select the affected service.
4. Open Deployments.
5. Select the previous healthy deploy.
6. Click Rollback.

## Environment Variables

Use `.env.example` as the source of truth for local development variables.

Production variables are managed in Railway service settings and GitHub Actions
secrets. Do not commit secrets to the repository.

Current Railway services:

| Service | Required variables |
| --- | --- |
| `truth-api` | `TRUTHOS_ENV`, `TRUTHOS_DB_PATH` |
| `hermes-agent` | `TRUTHOS_BASE_URL` |
| `truthos-web` | `NEXT_PUBLIC_HERMES_AGENT_URL`, `NEXT_PUBLIC_TRUTH_API_URL` |

Railway service domains are deployment-specific. Retrieve the current domains
from the Railway dashboard or CLI, then run the smoke checks above. Do not commit
tokens or private environment values while recording operational evidence.

GitHub Actions requires:

| Secret | Purpose |
| --- | --- |
| `RAILWAY_TOKEN` | Railway account token from Account Settings -> Tokens. The workflow maps this secret to `RAILWAY_API_TOKEN` for Railway CLI authentication. |

## Known Issues / Lessons Learned

- 2026-09-16: Railway rejected deployment run `35003057703` because the account
  trial had expired. Select the Railway Free plan before manually retrying the
  reviewed `master` commit. Changing GitHub Actions billing does not resolve a
  Railway subscription error.

- 2026-05-18: Railway CLI env var is `RAILWAY_API_TOKEN` (not `RAILWAY_TOKEN`). Run 25998090297 failed for this reason and was intentionally abandoned.

- 2026-05-18: `hermes-agent` `POST /chat` requires `user_id` as a required field. Smoke test payload must include `{"user_id": "...", "message": "..."}`. Minimal valid smoke test command:

```bash
curl -s -X POST "$HERMES_AGENT_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "smoke-user-001", "message": "smoke test ping"}'
```

- 2026-05-19: Railway cold starts can make the first health or chat request
  feel degraded. The frontend now waits longer, shows a warm-up state, and
  production Railway manifests explicitly keep applications awake.

- 2026-09-16: The three historical Railway hostnames documented in this file
  returned HTTP 404. They were removed from the runbook. Re-establish current
  domains and rerun the smoke checks before claiming production availability.
