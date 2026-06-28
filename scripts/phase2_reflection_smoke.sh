#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_URL="${1:-http://127.0.0.1:18000}"
PAYLOAD_PATH="${2:-$ROOT/docs/daily-reflection/examples/phase2_smoke_payload.json}"

echo "[1/4] POST /api/reflection/writeback"
curl -sS -X POST "$BASE_URL/api/reflection/writeback" \
  -H "Content-Type: application/json" \
  --data @"$PAYLOAD_PATH"
echo
echo

echo "[2/4] GET /api/reflection/runs/2026-03-13?user_id=smoke-user"
curl -sS "$BASE_URL/api/reflection/runs/2026-03-13?user_id=smoke-user"
echo
echo

echo "[3/4] POST /api/reflection/materialize"
curl -sS -X POST "$BASE_URL/api/reflection/materialize" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"smoke-user","run_date":"2026-03-13","rebuild_all":false}'
echo
echo

echo "[4/4] GET /api/reflection/dashboard/overview?user_id=smoke-user"
curl -sS "$BASE_URL/api/reflection/dashboard/overview?user_id=smoke-user"
echo
