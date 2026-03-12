FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY apps/truth-api/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --default-timeout=300 -r /tmp/requirements.txt

COPY . /app

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/healthz || exit 1

CMD ["sh", "-lc", "python scripts/seed_import.py && python scripts/build_vector_index.py && cd apps/truth-api && uvicorn app.main:app --host ${TRUTHOS_API_HOST:-0.0.0.0} --port ${TRUTHOS_API_PORT:-8000}"]
