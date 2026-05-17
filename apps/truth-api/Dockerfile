FROM python:3.11-slim

WORKDIR /app

COPY apps/truth-api/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --default-timeout=300 -r /tmp/requirements.txt

COPY . /app

CMD ["sh", "-lc", "python scripts/seed_import.py && cd apps/truth-api && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-${TRUTHOS_API_PORT:-8000}}"]
