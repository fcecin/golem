#!/usr/bin/env bash
set -euo pipefail

# golem-claude.sh — launch claude in a work directory
# Usage: golem-claude.sh [claude args...]
# Run from a work directory (not the golem directory).

# Refuse to run inside the golem directory
if [ -f "kernel.md" ] || [ -f "boot.sh" ]; then
  echo "ERROR: You are inside the golem directory. Run this from a work directory." >&2
  exit 1
fi

mkdir -p workspace

GOLEM_DIR="$(cd "$(dirname "$0")" && pwd)"
BOOT_MSG="Read ${GOLEM_DIR}/kernel.md — it will explain everything."

echo "Paste this into chat:"
echo "  $BOOT_MSG"
echo ""

claude "$@"
