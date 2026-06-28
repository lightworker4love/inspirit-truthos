#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f ".env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source ".env"
  set +a
fi

TRUTHOS_BASE_URL="${TRUTHOS_BASE_URL:-http://localhost:18000}"
OPENAI_BASE_URL="${OPENAI_BASE_URL:-}"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"
EMBEDDING_MODEL="${EMBEDDING_MODEL:-}"
SERVICE_NAME="${TRUTHOS_SERVICE_NAME:-truth-api}"

fail() {
  echo "❌ $1" >&2
  exit 1
}

info() {
  echo "==> $1"
}

models_url() {
  local base_url="$1"
  if [[ -z "$base_url" ]]; then
    echo ""
    return
  fi

  local trimmed="${base_url%/}"
  if [[ "$trimmed" == */v1 ]]; then
    echo "${trimmed}/models"
  else
    echo "${trimmed}/v1/models"
  fi
}

tmp_body() {
  mktemp "${TMPDIR:-/tmp}/truthos-gateway-check.XXXXXX"
}

request_status() {
  local url="$1"
  local body_file="$2"
  shift 2
  curl -sS -o "$body_file" -w "%{http_code}" "$@" "$url" || true
}

json_dump() {
  local body_file="$1"
  if python3 -m json.tool "$body_file" >/dev/null 2>&1; then
    python3 -m json.tool "$body_file"
  else
    cat "$body_file"
  fi
}

if [[ -z "$OPENAI_BASE_URL" ]]; then
  fail "OPENAI_BASE_URL is not set. TruthOS cannot validate gateway mode."
fi

if [[ -z "$EMBEDDING_MODEL" ]]; then
  fail "EMBEDDING_MODEL is not set. TruthOS cannot validate gateway mode."
fi

MODELS_URL="$(models_url "$OPENAI_BASE_URL")"
AUTH_ARGS=()
if [[ -n "$OPENAI_API_KEY" ]]; then
  AUTH_ARGS=(-H "Authorization: Bearer ${OPENAI_API_KEY}")
fi

info "docker compose ps"
docker compose ps || fail "docker compose ps failed"

HOST_BODY="$(tmp_body)"
CONTAINER_BODY="$(tmp_body)"
HEALTH_BODY="$(tmp_body)"
trap 'rm -f "$HOST_BODY" "$CONTAINER_BODY" "$HEALTH_BODY"' EXIT

info "Host models endpoint"
echo "Configured OPENAI_BASE_URL=${OPENAI_BASE_URL}"
echo "Resolved host models URL=${MODELS_URL}"
HOST_STATUS="$(request_status "$MODELS_URL" "$HOST_BODY" "${AUTH_ARGS[@]}")"
if [[ "$HOST_STATUS" != "200" ]]; then
  echo "Host endpoint response:"
  json_dump "$HOST_BODY"
  fail "Host cannot reach the configured models endpoint (${HOST_STATUS})."
fi
json_dump "$HOST_BODY"

info "Container models endpoint"
CONTAINER_STATUS="$(
  docker compose exec -T "$SERVICE_NAME" sh -lc '
    set -eu
    if [ -f /app/.env ]; then
      set -a
      . /app/.env
      set +a
    fi
    python - <<'"'"'PY'"'"'
import os
from urllib.parse import urljoin

import httpx

base_url = os.getenv("OPENAI_BASE_URL", "").strip()
api_key = os.getenv("OPENAI_API_KEY", "").strip()

def models_url(raw: str) -> str:
    normalized = raw.rstrip("/") + "/"
    if normalized.endswith("/v1/"):
        return urljoin(normalized, "models")
    return urljoin(normalized, "v1/models")

headers = {}
if api_key:
    headers["Authorization"] = f"Bearer {api_key}"

url = models_url(base_url)
print(f"models_url={url}")
try:
    response = httpx.get(url, headers=headers, timeout=5.0)
    print(f"status={response.status_code}")
    print(response.text)
except Exception as exc:
    print("status=000")
    print(f"error={exc}")
PY
  ' | tee "$CONTAINER_BODY" | awk -F= '/^status=/{print $2}' | tail -n1
)"
if [[ "$CONTAINER_STATUS" != "200" ]]; then
  cat "$CONTAINER_BODY"
  if [[ "$OPENAI_BASE_URL" == http://localhost* || "$OPENAI_BASE_URL" == https://localhost* || "$OPENAI_BASE_URL" == http://127.0.0.1* || "$OPENAI_BASE_URL" == https://127.0.0.1* ]]; then
    echo "Hint: Docker containers cannot use host localhost directly. Use a host-reachable address such as host.docker.internal when the gateway runs on the host."
  fi
  fail "Container cannot reach the configured models endpoint (${CONTAINER_STATUS})."
fi
cat "$CONTAINER_BODY"

info "TruthOS /healthz"
HEALTH_STATUS="$(request_status "${TRUTHOS_BASE_URL}/healthz" "$HEALTH_BODY")"
if [[ "$HEALTH_STATUS" != "200" ]]; then
  json_dump "$HEALTH_BODY"
  fail "/healthz did not return HTTP 200 (${HEALTH_STATUS})."
fi
json_dump "$HEALTH_BODY"

python3 - "$HEALTH_BODY" <<'PY'
import json
import sys

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as handle:
    payload = json.load(handle)

if payload.get("embedding_gateway") is True and payload.get("embedding_mode") == "gateway":
    print("✅ TruthOS is running in gateway mode")
    raise SystemExit(0)

raise SystemExit(
    "Health check did not report gateway mode. "
    f"embedding_gateway={payload.get('embedding_gateway')} "
    f"embedding_mode={payload.get('embedding_mode')}"
)
PY
