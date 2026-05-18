# inspirit-truthos

TruthOS engine bootstrap for the in spirit AI system.

## Stack
- Python 3.11
- FastAPI
- SQLite
- Docker Compose

## Run locally
```bash
cp .env.example .env
python -m pip install -r apps/truth-api/requirements.txt
python scripts/seed_import.py
python scripts/build_vector_index.py
docker compose up
```

## Service URL
- API: `http://localhost:18000`

## Frontend (apps/truthos-web)

`apps/truthos-web` is the TruthOS v1 frontend for guided reflection, Hermes chat,
and Soul Map viewing. It is a Next.js App Router app with TypeScript, Tailwind
CSS, and shadcn/ui base components.

Local frontend development intentionally connects to Railway production backends:

```bash
NEXT_PUBLIC_HERMES_AGENT_URL=https://hermes-agent-production-848a.up.railway.app
NEXT_PUBLIC_TRUTH_API_URL=https://truth-api-production-0046.up.railway.app
```

Run locally:

```bash
cd apps/truthos-web
cp .env.local.example .env.local
npm install
npm run dev
```

## Production Status

| Service | URL | Health |
| --- | --- | --- |
| Truth API | https://truth-api-production-0046.up.railway.app | `/health` |
| Hermes Agent | https://hermes-agent-production-848a.up.railway.app | `/health` |

**Deployment**: Railway (Dockerfile-based, monorepo)

**CI/CD**: GitHub Actions -> Railway CLI auto-deploy on push to master

**Last verified**: 2026-05-18

## Seed import
```bash
python scripts/seed_import.py
```

## Build vector index
```bash
python scripts/build_vector_index.py
```

If the local embedding gateway is unavailable, the API will still serve requests via SQLite fallback retrieval.

## Run API directly
```bash
cd apps/truth-api
uvicorn app.main:app --reload
```
