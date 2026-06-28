#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${TRUTHOS_BASE_URL:-http://localhost:18000}"

request_with_retry() {
  local method="$1"
  local url="$2"
  local payload="${3:-}"
  local body_file="$4"
  local status=""
  local attempt

  for attempt in 1 2 3 4 5 6 7 8 9 10; do
    if [[ "$method" == "GET" ]]; then
      status="$(curl -s -o "$body_file" -w "%{http_code}" "$url" || true)"
    else
      status="$(curl -s -o "$body_file" -w "%{http_code}" -X POST "$url" -H "Content-Type: application/json" -d "$payload" || true)"
    fi
    if [[ "$status" == "200" ]]; then
      printf '%s' "$status"
      return 0
    fi
    sleep 1
  done

  printf '%s' "$status"
  return 0
}

run_get() {
  local name="$1"
  local url="$2"
  local body_file
  local status

  body_file="$(mktemp)"
  echo "==> ${name}"
  status="$(request_with_retry "GET" "$url" "" "$body_file")"
  if [[ "$status" != "200" ]]; then
    echo "❌ FAILED"
    cat "$body_file"
    rm -f "$body_file"
    exit 1
  fi
  python3 -m json.tool "$body_file"
  rm -f "$body_file"
}

run_post() {
  local name="$1"
  local url="$2"
  local payload="$3"
  local body_file
  local status

  body_file="$(mktemp)"
  echo "==> ${name}"
  status="$(request_with_retry "POST" "$url" "$payload" "$body_file")"
  if [[ "$status" != "200" ]]; then
    echo "❌ FAILED"
    cat "$body_file"
    rm -f "$body_file"
    exit 1
  fi
  python3 -m json.tool "$body_file"
  rm -f "$body_file"
}

run_get "Health Check" "${BASE_URL}/healthz"
run_get "Dimensions 清單" "${BASE_URL}/api/truth/dimensions"
run_get "Principles（relationship）" "${BASE_URL}/api/truth/principles?dimension=relationship"
run_post "Truth Query（核心查詢）" "${BASE_URL}/api/truth/query" '{
  "user_id": "smoke-test-user",
  "session_id": "smoke-001",
  "message": "我一直在關係裡討好對方，卻感到很委屈，不知道為什麼",
  "mode": "mentor",
  "language": "zh"
}'
run_get "Session 記憶（驗證寫入）" "${BASE_URL}/api/truth/session/smoke-test-user"

echo "✅ All smoke tests passed"
