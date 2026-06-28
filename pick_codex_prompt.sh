#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

usage() {
  cat <<'EOF'
Usage:
  ./pick_codex_prompt.sh tiny
  ./pick_codex_prompt.sh normal
  ./pick_codex_prompt.sh arch

Modes:
  tiny    -> CODEX_PROMPT_ULTRA_SHORT.md
  normal  -> CODEX_PROMPT_SHORT.md
  arch    -> CODEX_PROMPT_FULL.md
EOF
}

mode="${1:-}"

case "$mode" in
  tiny)
    target="$ROOT_DIR/CODEX_PROMPT_ULTRA_SHORT.md"
    ;;
  normal)
    target="$ROOT_DIR/CODEX_PROMPT_SHORT.md"
    ;;
  arch)
    target="$ROOT_DIR/CODEX_PROMPT_FULL.md"
    ;;
  -h|--help|help|"")
    usage
    exit 0
    ;;
  *)
    echo "Unknown mode: $mode" >&2
    echo >&2
    usage >&2
    exit 1
    ;;
esac

if [[ ! -f "$target" ]]; then
  echo "Prompt file not found: $target" >&2
  exit 1
fi

cat "$target"
