#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OPENCLAW_DIR="$ROOT_DIR/../upstream/openclaw"
PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/.venv311/bin/python}"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "error: python binary not found at $PYTHON_BIN"
  echo "hint: set PYTHON_BIN=/path/to/python3.11"
  exit 1
fi

if ! "$PYTHON_BIN" -c "import pytest" >/dev/null 2>&1; then
  echo "error: pytest is not installed in this environment"
  echo "hint: $PYTHON_BIN -m pip install pytest"
  exit 1
fi

command -v pnpm >/dev/null 2>&1 || {
  echo "error: pnpm is required for openclaw build validation"
  exit 1
}

echo "[1/5] backend syntax check"
"$PYTHON_BIN" -m py_compile \
  "$ROOT_DIR/apps/truth-api/app/main.py" \
  "$ROOT_DIR/apps/truth-api/app/case_models.py" \
  "$ROOT_DIR/apps/truth-api/app/case_resolver.py" \
  "$ROOT_DIR/apps/truth-api/app/case_insight_service.py" \
  "$ROOT_DIR/apps/truth-api/app/prompt_builder.py"

echo "[2/5] truth-api phase test suite"
"$PYTHON_BIN" -m pytest "$ROOT_DIR/apps/truth-api/tests/test_case_identity_phase_1_5.py" -q

echo "[3/5] openclaw ui build"
pnpm -C "$OPENCLAW_DIR/ui" build

echo "[4/5] openclaw gateway/runtime build"
pnpm -C "$OPENCLAW_DIR" build

echo "[5/5] targeted smoke assertions"
"$PYTHON_BIN" -m pytest "$ROOT_DIR/apps/truth-api/tests/test_case_identity_phase_1_5.py" -q \
  -k "hank_preferred_name_full_path or fallback_when_no_preferred_name or minimal_blueprint_writeback_preserves_identity or soul_age_not_emitted_when_history_is_insufficient or blueprint_writeback_observability_logs"

echo "RC validation completed."
