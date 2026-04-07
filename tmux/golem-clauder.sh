#!/usr/bin/env bash
set -euo pipefail

# golem-clauder.sh — run clauder with the golem boot phrase
#
# Launches claude via tmux, sends the golem boot phrase, then nudges
# it to continue until it reports no more work to do.
#
# Usage: golem-clauder.sh [clauder args...]
# Example: golem-clauder.sh --dir ~/work/style --idle 15 --claude-args="--dangerously-skip-permissions"

DIR="$(cd "$(dirname "$0")" && pwd)"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ] || [ $# -eq 0 ]; then
  echo "golem-clauder — run clauder with the golem boot phrase"
  echo ""
  echo "Usage: golem-clauder.sh [clauder args...]"
  echo "Example: golem-clauder.sh --dir test-workdir --idle 15 --claude-args=\"--dangerously-skip-permissions\""
  echo ""
  if command -v golem &> /dev/null; then
    echo "Requires: golem (found: $(which golem))"
  else
    echo "Requires: golem (NOT FOUND — install golem first)"
  fi
  echo ""
  echo "Options (passed to clauder):"
  "$DIR/clauder.py" --help 2>&1 | grep -A1 "^  --"
  exit 0
fi

if ! command -v golem &> /dev/null; then
  echo "ERROR: golem not found in PATH. Install golem first." >&2
  exit 1
fi

BOOT_MSG=$(golem boot)

exec "$DIR/clauder.py" "$BOOT_MSG" "$@"
