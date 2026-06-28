#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${APP_DIR}"

export PYTHONPATH="${APP_DIR}"

if [[ ! -f ".env" ]]; then
  echo "[ERROR] .env not found in ${APP_DIR}"
  echo "Copy .env.template to .env before running."
  exit 1
fi

if [[ ! -d ".venv" ]]; then
  echo "[INFO] Creating virtualenv..."
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "[INFO] Installing dependencies..."
pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null

if [[ ! -f "/Users/tongwei/.openclaw/data/in-spirit-case-auth.db" ]]; then
  echo "[INFO] Initializing database..."
  make init-db
fi

echo "[INFO] Seeding accounts..."
python scripts/seed-admin.py

echo "[INFO] Running tests..."
pytest

echo "[INFO] Starting truth-api on http://127.0.0.1:8010"
exec uvicorn app.main:app --reload --host 127.0.0.1 --port 8010
