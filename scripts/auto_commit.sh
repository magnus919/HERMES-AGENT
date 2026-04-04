#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

python3 scripts/sync_hermes_snapshot.py > /tmp/hermes-sync-result.json

git add -A
if git diff --cached --quiet; then
  echo "No backup changes detected."
  exit 0
fi

ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
git commit -m "chore: sync Hermes snapshot ${ts}"
git push origin main

echo "Backup synced, committed, and pushed at ${ts}."
