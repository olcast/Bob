#!/usr/bin/env bash
# state_proximity_run.sh — single unambiguous entrypoint for the state-snapshot cron.
# Runs the canonical state serializer, commits it (SOP §0 single source of truth),
# then runs the entry-proximity check. One command, no agent-side chaining.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"    # .../skills/hyperliquid-ops/scripts
ROOT="$(cd "$HERE/../../.." && pwd)"                      # .../workspace

# 1) serialize state
python3 "$HERE/state_snapshot.py" || { echo "state_snapshot FAILED"; exit 1; }

# 2) commit state.json (durable single source of truth)
cd "$ROOT" || exit 1
git add skills/hyperliquid-ops/data/state.json
if ! git diff --cached --quiet; then
  git commit -m "state snapshot tick (auto)" --no-verify >/dev/null 2>&1 || true
fi

# 3) proximity check (prints hot/warm/cold to stdout for the agent to read)
python3 "$HERE/entry_proximity.py"

exit 0
