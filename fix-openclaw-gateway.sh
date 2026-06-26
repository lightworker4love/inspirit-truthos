#!/bin/bash
set -euo pipefail

# Terminal color escapes for status output
GREEN=$'\033[1;32m'
YELLOW=$'\033[1;33m'
RED=$'\033[1;31m'
RESET=$'\033[0m'

PLIST="$HOME/Library/LaunchAgents/ai.openclaw.gateway.plist"
LABEL="ai.openclaw.gateway"
UID_VALUE="$(id -u)"
STEP1_STATUS="pending"
STEP2_STATUS="pending"
STEP3_STATUS="pending"
STEP4_STATUS="pending"
STEP5_STATUS="pending"
STEP6_STATUS="pending"
FALLBACK_REQUIRED=false
OVERALL_FAILED=false

print_header() {
  echo ""
  echo "=== $1 ==="
}

set_status() {
  case "$1" in
    "Step 1") STEP1_STATUS="$2" ;;
    "Step 2") STEP2_STATUS="$2" ;;
    "Step 3") STEP3_STATUS="$2" ;;
    "Step 4") STEP4_STATUS="$2" ;;
    "Step 5") STEP5_STATUS="$2" ;;
    "Step 6") STEP6_STATUS="$2" ;;
  esac
}

print_status() {
  echo -e "$1"
}

print_summary() {
  print_header "Summary"
  printf "%-10s %s\n" "Step 1" "${STEP1_STATUS}"
  printf "%-10s %s\n" "Step 2" "${STEP2_STATUS}"
  printf "%-10s %s\n" "Step 3" "${STEP3_STATUS}"
  printf "%-10s %s\n" "Step 4" "${STEP4_STATUS}"
  printf "%-10s %s\n" "Step 5" "${STEP5_STATUS}"
  printf "%-10s %s\n" "Step 6" "${STEP6_STATUS}"
}

print_header "Preflight"
for BIN in lsof launchctl python3 openclaw curl; do
  if ! command -v "$BIN" >/dev/null 2>&1; then
    print_status "${RED}❌ Required binary missing: $BIN${RESET}"
    OVERALL_FAILED=true
    print_summary
    exit 1
  fi
done
print_status "${GREEN}✅ All required binaries present${RESET}"

print_header "Step 1 — Clearing port 11435"
PIDS=$(lsof -ti :11435 || true)
if [[ -n "$PIDS" ]]; then
  for PID in $PIDS; do
    kill -9 "$PID" >/dev/null 2>&1 || true
  done
  sleep 1
fi
if [[ -z $(lsof -ti :11435 || true) ]]; then
  print_status "${GREEN}✅ Port 11435 cleared${RESET}"
  set_status "Step 1" "success"
else
  print_status "${YELLOW}⚠️ Port 11435 still occupied — proceeding anyway${RESET}"
  set_status "Step 1" "warning"
fi

print_header "Step 2 — launchctl bootout"
if [[ -f "$PLIST" ]]; then
  if launchctl bootout "gui/${UID_VALUE}" "$PLIST" >/dev/null 2>&1; then
    print_status "${GREEN}✅ launchctl bootout completed using plist${RESET}"
    set_status "Step 2" "success"
  else
    print_status "${YELLOW}⚠️ launchctl bootout (plist) reported an issue — continuing${RESET}"
    set_status "Step 2" "warning"
  fi
else
  if launchctl bootout "gui/${UID_VALUE}/${LABEL}" >/dev/null 2>&1; then
    print_status "${GREEN}✅ launchctl bootout completed using service label${RESET}"
    set_status "Step 2" "success"
  else
    print_status "${YELLOW}⚠️ launchctl bootout reported an issue (plist missing or service unloaded) — continuing${RESET}"
    set_status "Step 2" "warning"
  fi
fi
sleep 2

print_header "Step 3 — Patch LaunchAgent plist"
if [[ ! -f "$PLIST" ]]; then
  print_status "${YELLOW}⚠️ Plist not found at $PLIST — skipping patch${RESET}"
  set_status "Step 3" "skipped"
else
  PLIST_RESULT=$(
    PLIST_PATH="$PLIST" python3 <<'PY'
import os
import pathlib
import plistlib
import sys

path = pathlib.Path(os.environ["PLIST_PATH"]).expanduser()
data = plistlib.loads(path.read_bytes())
patched = False

if "SandboxProfile" in data:
    data.pop("SandboxProfile")
    patched = True

args = data.get("ProgramArguments")
if not isinstance(args, list):
    print("invalid")
    sys.exit(0)

def ensure_flag(flag, value):
    global patched
    if flag in args:
        idx = args.index(flag)
        if idx + 1 >= len(args):
            args.append(value)
            patched = True
        elif args[idx + 1] != value:
            args[idx + 1] = value
            patched = True
    else:
        try:
            run_index = args.index("run")
            insert_index = run_index + 1
        except ValueError:
            insert_index = len(args)
        args[insert_index:insert_index] = [flag, value]
        patched = True

ensure_flag("--bind", "0.0.0.0")
ensure_flag("--port", "11435")

data["ProgramArguments"] = args
path.write_bytes(plistlib.dumps(data))
print("patched" if patched else "unchanged")
PY
  )
  if [[ "$PLIST_RESULT" == "patched" ]]; then
    print_status "${GREEN}✅ plist patched — bind=0.0.0.0, port=11435, SandboxProfile removed${RESET}"
    set_status "Step 3" "success"
  elif [[ "$PLIST_RESULT" == "unchanged" ]]; then
    print_status "${YELLOW}⚠️ plist already correct — no modifications made${RESET}"
    set_status "Step 3" "unchanged"
  else
    print_status "${RED}❌ plist patch failed (invalid format)${RESET}"
    set_status "Step 3" "failed"
    OVERALL_FAILED=true
    print_summary
    exit 1
  fi
fi

print_header "Step 4 — launchctl bootstrap"
if [[ ! -f "$PLIST" ]]; then
  print_status "${YELLOW}⚠️ Plist missing — cannot bootstrap; enabling fallback${RESET}"
  set_status "Step 4" "skipped"
  FALLBACK_REQUIRED=true
else
  if launchctl bootstrap "gui/${UID_VALUE}" "$PLIST" >/dev/null 2>&1; then
    sleep 3
    if launchctl print "gui/${UID_VALUE}/${LABEL}" >/dev/null 2>&1; then
      print_status "${GREEN}✅ launchctl print succeeded — service visible${RESET}"
      set_status "Step 4" "success"
    else
      print_status "${YELLOW}⚠️ launchctl print failed after bootstrap — forcing fallback${RESET}"
      set_status "Step 4" "warning"
      FALLBACK_REQUIRED=true
    fi
  else
    print_status "${YELLOW}⚠️ Bootstrap failed — forcing background fallback${RESET}"
    set_status "Step 4" "failed"
    FALLBACK_REQUIRED=true
  fi
fi

print_header "Step 5 — Background fallback"
if [[ "$FALLBACK_REQUIRED" == "true" ]]; then
  nohup openclaw gateway run --bind 0.0.0.0 --port 11435 >/tmp/openclaw-gateway.log 2>&1 &
  GATEWAY_PID=$!
  echo "$GATEWAY_PID" >/tmp/openclaw-gateway.pid
  print_status "${GREEN}🚀 Gateway started in background mode — PID: ${GATEWAY_PID} — logs: /tmp/openclaw-gateway.log${RESET}"
  set_status "Step 5" "success"
else
  print_status "${GREEN}✅ Launchctl handled the service; background fallback not needed${RESET}"
  set_status "Step 5" "skipped"
fi

print_header "Step 6 — Health verification"
sleep 3
if lsof -iTCP:11435 -sTCP:LISTEN -n -P >/dev/null 2>&1; then
  HTTP_CODE="$(curl -s -o /dev/null -w "%{http_code}" http://localhost:11435/ || true)"
  print_status "${GREEN}✅ Gateway is UP and listening on 0.0.0.0:11435 — probe HTTP code: ${HTTP_CODE:-n/a}${RESET}"
  set_status "Step 6" "success"
else
  print_status "${RED}❌ Gateway failed to start — inspect /tmp/openclaw-gateway.log${RESET}"
  set_status "Step 6" "failed"
  OVERALL_FAILED=true
fi

print_summary

# Operator notes:
# - If launchctl lacks GUI-domain permissions, manual bootout/bootstrap may still be required.
# - After recovery, confirm port 11435 is bound before resuming higher-level activations.
# - Replace any temporary latest image/tag pin with a verified non-latest upstream tag once available.

if [[ "$OVERALL_FAILED" == "true" ]]; then
  exit 1
fi

exit 0
