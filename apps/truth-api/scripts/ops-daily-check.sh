#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api"
BASE_URL="${BASE_URL:-http://127.0.0.1:8010}"
OPENCLAW_URL="${OPENCLAW_URL:-http://127.0.0.1:18789}"
DB_PATH="/Users/tongwei/.openclaw/data/in-spirit-case-auth.db"
STDOUT_LOG="/Users/tongwei/.openclaw/logs/truth-api.stdout.log"
STDERR_LOG="/Users/tongwei/.openclaw/logs/truth-api.stderr.log"

ok() { echo "[OK] $*"; }
warn() { echo "[WARN] $*"; }
fail() { echo "[FAIL] $*"; }

echo "== ops daily check =="

echo
echo "-- service reachability --"
if curl -fsS "${BASE_URL}/health" >/dev/null; then
  ok "truth-api reachable"
else
  fail "truth-api unreachable"
fi

if curl -fsS "${OPENCLAW_URL}/v1/models" >/dev/null; then
  ok "OpenClaw reachable"
else
  fail "OpenClaw unreachable"
fi

echo
echo "-- launchd status --"
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

echo
echo "-- db file --"
if [[ -f "${DB_PATH}" ]]; then
  ok "DB present: ${DB_PATH}"
  sqlite3 "${DB_PATH}" "SELECT 'users', COUNT(*) FROM users;"
  sqlite3 "${DB_PATH}" "SELECT 'case_threads', COUNT(*) FROM case_threads;"
  sqlite3 "${DB_PATH}" "SELECT 'case_entries', COUNT(*) FROM case_entries;"
  sqlite3 "${DB_PATH}" "SELECT 'audit_logs', COUNT(*) FROM audit_logs;"
else
  fail "DB missing: ${DB_PATH}"
fi

echo
echo "-- smoke script --"
if [[ -x "${APP_DIR}/scripts/smoke-test.sh" ]]; then
  ok "smoke-test.sh executable"
else
  warn "smoke-test.sh not executable"
fi

echo
echo "-- log tail: stderr --"
if [[ -f "${STDERR_LOG}" ]]; then
  tail -n 15 "${STDERR_LOG}" || true
else
  warn "stderr log missing"
fi

echo
echo "-- log tail: stdout --"
if [[ -f "${STDOUT_LOG}" ]]; then
  tail -n 15 "${STDOUT_LOG}" || true
else
  warn "stdout log missing"
fi

echo
echo "Daily check complete."
