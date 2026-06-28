#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_DATE="$(TZ=Asia/Taipei date +%F)"
STRICT_MODE=0
STRICT_MATERIALIZE=0
ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --strict)
      STRICT_MODE=1
      shift
      ;;
    --strict-materialize)
      STRICT_MATERIALIZE=1
      ARGS+=("$1")
      shift
      ;;
    *)
      ARGS+=("$1")
      shift
      ;;
  esac
done

if [[ " ${ARGS[*]} " != *" --date "* ]]; then
  ARGS+=(--date "$DEFAULT_DATE")
fi

PYTHON_BIN="${TRUTHOS_BRIDGE_PYTHON:-$ROOT/.venv311/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

"$PYTHON_BIN" "$ROOT/scripts/bridge_daily_reflection_to_api.py" "${ARGS[@]}"
STATUS=$?

if [[ $STATUS -ne 0 ]]; then
  if [[ "$STRICT_MODE" -eq 1 || "$STRICT_MATERIALIZE" -eq 1 || "${DAILY_REFLECTION_WRITEBACK_STRICT:-0}" = "1" ]]; then
    exit "$STATUS"
  fi
  echo "Bridge writeback failed but was suppressed (non-strict mode)." >&2
  exit 0
fi

exit 0
