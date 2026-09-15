# Contributing to TruthOS

Thank you for helping improve TruthOS. The project is early-stage, so focused
issues and small pull requests are the easiest to review and maintain.

## Prerequisites

- Git
- Python 3.11
- Docker with Docker Compose
- Node.js 20 and npm for frontend work

## Start the local stack with Docker

1. Create a local environment file:

   ```bash
   cp .env.example .env
   ```

2. Review `.env` and keep only local or test values in it. Never commit this
   file.

3. Build and start the API and Hermes services:

   ```bash
   docker compose up -d --build
   ```

4. Verify both services:

   ```bash
   curl http://localhost:18000/healthz
   curl http://localhost:8001/health
   ```

5. Stop the stack when finished:

   ```bash
   docker compose down
   ```

The Next.js frontend runs separately during local development:

```bash
cd apps/truthos-web
cp .env.local.example .env.local
npm ci
npm run dev
```

See [`DEPLOY.md`](DEPLOY.md) for deployment-specific information.

## Run the tests

Create and activate a virtual environment, then install the backend and test
dependencies:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r apps/truth-api/requirements.txt
python -m pip install pytest pytest-asyncio httpx
```

Use a disposable database so test setup does not modify repository data:

```bash
export TRUTHOS_DB_PATH=/tmp/truthos-contributor.db
python scripts/seed_import.py
SQLITE_DB_PATH="$TRUTHOS_DB_PATH" python scripts/run_migration_004.py
SQLITE_DB_PATH="$TRUTHOS_DB_PATH" python scripts/run_migration_005.py
SQLITE_DB_PATH="$TRUTHOS_DB_PATH" python scripts/run_migration_006.py
TESTING=true python -m pytest tests/ -v --tb=short
```

For frontend changes, run:

```bash
cd apps/truthos-web
npm ci
npm run lint
npm run build
```

## Open an issue

- Search existing issues before creating a new one.
- Use the bug or feature template and include a minimal reproduction when
  possible.
- Keep private data out of screenshots, fixtures, logs, and examples.
- Do not report an undisclosed security vulnerability in a public issue. Follow
  [`SECURITY.md`](SECURITY.md) instead.

## Submit a pull request

1. Create a focused branch from the current `master` branch.
2. Keep the change small and explain the problem it solves.
3. Add or update tests for changed behavior.
4. Update documentation when setup, APIs, or contributor workflows change.
5. Run the relevant checks locally and report the results in the pull request.
6. Link the issue the pull request addresses.

Pull requests should avoid unrelated refactors, generated artifacts, local
databases, and environment files.

## Protect secrets and personal data

Never commit API keys, access tokens, passwords, private keys, real personal
records, private knowledge-base content, or production database extracts. Use
documented environment variables and synthetic fixtures. If a secret is exposed,
revoke or rotate it immediately and report the incident privately as described
in [`SECURITY.md`](SECURITY.md).
