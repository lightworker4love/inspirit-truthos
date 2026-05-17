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
| `RAILWAY_TOKEN` | Allows the deploy workflow to call Railway CLI |
