#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8010}"
USERNAME="${USERNAME:-hank}"
PASSWORD="${PASSWORD:-secret}"
MODE="${MODE:-spiritual_reflection}"

echo "== 1. Health check =="
curl -fsS "${BASE_URL}/health" | python3 -m json.tool

echo
echo "== 2. Login =="
LOGIN_JSON=$(curl -fsS -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"${USERNAME}\",
    \"password\": \"${PASSWORD}\"
  }")

echo "${LOGIN_JSON}" | python3 -m json.tool
SESSION_TOKEN=$(echo "${LOGIN_JSON}" | python3 -c 'import sys, json; print(json.load(sys.stdin)["session"]["token"])')

echo
echo "== 3. Allowed modes =="
curl -fsS "${BASE_URL}/models/allowed" \
  -H "Authorization: Bearer ${SESSION_TOKEN}" | python3 -m json.tool

echo
echo "== 4. Create thread =="
THREAD_JSON=$(curl -fsS -X POST "${BASE_URL}/threads" \
  -H "Authorization: Bearer ${SESSION_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"mode\": \"${MODE}\",
    \"title\": \"Smoke Test Thread\"
  }")

echo "${THREAD_JSON}" | python3 -m json.tool
THREAD_ID=$(echo "${THREAD_JSON}" | python3 -c 'import sys, json; print(json.load(sys.stdin)["threadId"])')

echo
echo "== 5. Chat =="
curl -fsS -X POST "${BASE_URL}/chat" \
  -H "Authorization: Bearer ${SESSION_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"threadId\": \"${THREAD_ID}\",
    \"message\": \"這是一則 smoke test，請溫和回應我一句話。\",
    \"mode\": \"${MODE}\"
  }" | python3 -m json.tool

echo
echo "Smoke test complete."
