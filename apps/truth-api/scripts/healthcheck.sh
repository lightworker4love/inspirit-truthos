#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api"
BASE_URL="${BASE_URL:-http://127.0.0.1:8010}"
OPENCLAW_URL="${OPENCLAW_URL:-http://127.0.0.1:18789}"
DB_PATH="/Users/tongwei/.openclaw/data/in-spirit-case-auth.db"
TRUTH_PLIST="${HOME}/Library/LaunchAgents/ai.inspirit.truth-api.plist"
OPENCLAW_PLIST="${HOME}/Library/LaunchAgents/ai.openclaw.gateway.plist"
STDOUT_LOG="/Users/tongwei/.openclaw/logs/truth-api.stdout.log"
STDERR_LOG="/Users/tongwei/.openclaw/logs/truth-api.stderr.log"

ok() { echo "[OK] $*"; }
warn() { echo "[WARN] $*"; }
fail() { echo "[FAIL] $*"; }

echo "== truth-api healthcheck =="

if curl -fsS "${BASE_URL}/health" >/dev/null; then
  ok "truth-api health endpoint reachable"
else
  fail "truth-api health endpoint failed"
fi

if curl -fsS "${OPENCLAW_URL}/v1/models" >/dev/null; then
  ok "OpenClaw models endpoint reachable"
else
  fail "OpenClaw models endpoint failed"
fi

if launchctl print "gui/$(id -u)/ai.inspirit.truth-api" >/dev/null 2>&1; then
  ok "truth-api LaunchAgent loaded"
else
  warn "truth-api LaunchAgent not loaded"
fi

if launchctl print "gui/$(id -u)/ai.openclaw.gateway" >/dev/null 2>&1; then
  ok "OpenClaw LaunchAgent loaded"
else
  warn "OpenClaw LaunchAgent not loaded"
fi

if [[ -f "${DB_PATH}" ]]; then
  ok "SQLite DB present: ${DB_PATH}"
else
  fail "SQLite DB missing: ${DB_PATH}"
fi

if [[ -f "${STDOUT_LOG}" ]]; then
  ok "stdout log present"
else
  warn "stdout log missing"
fi

if [[ -f "${STDERR_LOG}" ]]; then
  ok "stderr log present"
else
  warn "stderr log missing"
fi

if [[ -x "${APP_DIR}/scripts/smoke-test.sh" ]]; then
  ok "smoke-test.sh executable"
else
  warn "smoke-test.sh not executable"
fi

echo
echo "== recent stderr tail =="
if [[ -f "${STDERR_LOG}" ]]; then
  tail -n 20 "${STDERR_LOG}" || true
else
  echo "(no stderr log)"
fi

echo
echo "== recent stdout tail =="
if [[ -f "${STDOUT_LOG}" ]]; then
  tail -n 20 "${STDOUT_LOG}" || true
else
  echo "(no stdout log)"
fi

echo
echo "Healthcheck complete."
