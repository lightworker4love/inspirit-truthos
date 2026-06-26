#!/usr/bin/env bash
set -euo pipefail

ACTION="${1:-}"
TARGET="${2:-latest}"

APP_DIR="/Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api"
BACKUP_ROOT="/Users/tongwei/.openclaw/backups/truth-api"
DB_PATH="/Users/tongwei/.openclaw/data/in-spirit-case-auth.db"
ENV_PATH="${APP_DIR}/.env"
PLIST_PATH="${HOME}/Library/LaunchAgents/ai.inspirit.truth-api.plist"
OPENCLAW_JSON="/Users/tongwei/.openclaw/openclaw.json"

mkdir -p "${BACKUP_ROOT}"

timestamp() {
  date +"%Y%m%d-%H%M%S"
}

latest_snapshot() {
  ls -1dt "${BACKUP_ROOT}"/snapshot-* 2>/dev/null | head -n 1
}

stop_truth_api() {
  launchctl bootout "gui/$(id -u)" "${PLIST_PATH}" 2>/dev/null || true
}

start_truth_api() {
  launchctl bootstrap "gui/$(id -u)" "${PLIST_PATH}"
}

do_backup() {
  SNAPSHOT_DIR="${BACKUP_ROOT}/snapshot-$(timestamp)"
  mkdir -p "${SNAPSHOT_DIR}"

  [[ -f "${ENV_PATH}" ]] && cp "${ENV_PATH}" "${SNAPSHOT_DIR}/.env"
  [[ -f "${DB_PATH}" ]] && cp "${DB_PATH}" "${SNAPSHOT_DIR}/in-spirit-case-auth.db"
  [[ -f "${PLIST_PATH}" ]] && cp "${PLIST_PATH}" "${SNAPSHOT_DIR}/ai.inspirit.truth-api.plist"
  [[ -f "${OPENCLAW_JSON}" ]] && cp "${OPENCLAW_JSON}" "${SNAPSHOT_DIR}/openclaw.json"

  cat > "${SNAPSHOT_DIR}/MANIFEST.txt" <<EOF
created_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
host=$(hostname)
app_dir=${APP_DIR}
db_path=${DB_PATH}
env_present=$([[ -f "${ENV_PATH}" ]] && echo yes || echo no)
plist_present=$([[ -f "${PLIST_PATH}" ]] && echo yes || echo no)
openclaw_json_present=$([[ -f "${OPENCLAW_JSON}" ]] && echo yes || echo no)
EOF

  tar -czf "${SNAPSHOT_DIR}.tar.gz" -C "${BACKUP_ROOT}" "$(basename "${SNAPSHOT_DIR}")"
  echo "Backup created:"
  echo "  dir: ${SNAPSHOT_DIR}"
  echo "  tar: ${SNAPSHOT_DIR}.tar.gz"
}

do_list() {
  ls -1dt "${BACKUP_ROOT}"/snapshot-* 2>/dev/null || echo "No snapshots found."
}

do_restore() {
  if [[ "${TARGET}" == "latest" ]]; then
    SNAPSHOT_DIR="$(latest_snapshot)"
  else
    SNAPSHOT_DIR="${BACKUP_ROOT}/${TARGET}"
  fi

  if [[ -z "${SNAPSHOT_DIR:-}" || ! -d "${SNAPSHOT_DIR}" ]]; then
    echo "Snapshot not found: ${TARGET}"
    exit 1
  fi

  echo "Restoring from: ${SNAPSHOT_DIR}"
  stop_truth_api

  [[ -f "${SNAPSHOT_DIR}/.env" ]] && cp "${SNAPSHOT_DIR}/.env" "${ENV_PATH}"
  [[ -f "${SNAPSHOT_DIR}/in-spirit-case-auth.db" ]] && cp "${SNAPSHOT_DIR}/in-spirit-case-auth.db" "${DB_PATH}"
  [[ -f "${SNAPSHOT_DIR}/ai.inspirit.truth-api.plist" ]] && cp "${SNAPSHOT_DIR}/ai.inspirit.truth-api.plist" "${PLIST_PATH}"
  [[ -f "${SNAPSHOT_DIR}/openclaw.json" ]] && cp "${SNAPSHOT_DIR}/openclaw.json" "${OPENCLAW_JSON}"

  start_truth_api

  echo "Restore complete."
  echo "Run:"
  echo "  curl -s http://127.0.0.1:8010/health"
  echo "  ${APP_DIR}/scripts/smoke-test.sh"
}

case "${ACTION}" in
  backup)
    do_backup
    ;;
  list)
    do_list
    ;;
  restore)
    do_restore
    ;;
  *)
    echo "Usage:"
    echo "  $0 backup"
    echo "  $0 list"
    echo "  $0 restore latest"
    echo "  $0 restore snapshot-YYYYMMDD-HHMMSS"
    exit 1
    ;;
esac
