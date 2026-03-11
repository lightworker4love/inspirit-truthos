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
