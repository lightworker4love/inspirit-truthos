# TruthOS Deployment Runbook

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

## Auto Deploy

After the `RAILWAY_TOKEN` GitHub Actions secret is configured, every push to
`master` triggers the deployment workflow:

```bash
git push origin master
```

The workflow runs the existing CI suite first. Railway deploy starts only after
the tests and container checks pass.

Production smoke check:

```bash
curl -s -w "\nHTTP %{http_code}" https://truth-api-production-0046.up.railway.app/health
curl -s -w "\nHTTP %{http_code}" https://hermes-agent-production-848a.up.railway.app/health
curl -s -w "\nHTTP %{http_code}" -X POST https://hermes-agent-production-848a.up.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "smoke-user-001", "message": "smoke test ping"}'
```

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

GitHub Actions requires:

| Secret | Purpose |
| --- | --- |
| `RAILWAY_TOKEN` | Railway account token from Account Settings -> Tokens. The workflow maps this secret to `RAILWAY_API_TOKEN` for Railway CLI authentication. |

## Known Issues / Lessons Learned

- 2026-05-18: Railway CLI env var is `RAILWAY_API_TOKEN` (not `RAILWAY_TOKEN`). Run 25998090297 failed for this reason and was intentionally abandoned.

- 2026-05-18: `hermes-agent` `POST /chat` requires `user_id` as a required field. Smoke test payload must include `{"user_id": "...", "message": "..."}`. Minimal valid smoke test command:

```bash
curl -s -X POST https://hermes-agent-production-848a.up.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "smoke-user-001", "message": "smoke test ping"}'
```
