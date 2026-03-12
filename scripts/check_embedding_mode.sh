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

resolve_expected_mode() {
  if [[ -n "${EXPECTED_EMBEDDING_MODE:-}" ]]; then
    printf '%s' "$EXPECTED_EMBEDDING_MODE"
    return
  fi

  case "${EMBEDDING_PROVIDER:-auto}" in
    gateway|openclaw)
      printf 'gateway'
      return
      ;;
    ollama|ollama-local)
      printf 'ollama-local'
      return
      ;;
    openai)
      printf 'openai'
      return
      ;;
  esac

  if [[ -z "${OPENAI_BASE_URL:-}" ]]; then
    printf 'sqlite'
    return
  fi

  if [[ "${OPENAI_BASE_URL:-}" == *"11434"* ]]; then
    printf 'ollama-local'
    return
  fi

  if [[ "${OPENAI_BASE_URL:-}" == *"api.openai.com"* ]]; then
    printf 'openai'
    return
  fi

  printf 'gateway'
}

BODY_FILE="$(mktemp "${TMPDIR:-/tmp}/truthos-embedding-mode.XXXXXX")"
trap 'rm -f "$BODY_FILE"' EXIT

STATUS="$(curl -sS -o "$BODY_FILE" -w "%{http_code}" "${TRUTHOS_BASE_URL}/healthz" || true)"
if [[ "$STATUS" != "200" ]]; then
  echo "❌ /healthz returned HTTP ${STATUS}" >&2
  cat "$BODY_FILE" >&2
  exit 1
fi

ACTUAL_MODE="$(python3 - "$BODY_FILE" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as handle:
    payload = json.load(handle)
print(payload.get("embedding_mode", ""))
PY
)"
EXPECTED_MODE="$(resolve_expected_mode)"

echo "expected_embedding_mode=${EXPECTED_MODE}"
echo "actual_embedding_mode=${ACTUAL_MODE}"
python3 -m json.tool "$BODY_FILE"

if [[ "$ACTUAL_MODE" != "$EXPECTED_MODE" ]]; then
  echo "❌ Embedding mode mismatch: expected ${EXPECTED_MODE}, got ${ACTUAL_MODE}" >&2
  exit 1
fi

echo "✅ TruthOS embedding mode verified: ${ACTUAL_MODE}"
