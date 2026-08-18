#!/usr/bin/env bash
# crosscheck_state_run.sh — single unambiguous entrypoint for hlops-crosscheck-open STEP 1.
# Runs the canonical state serializer + entry-proximity check in one command,
# so the isolated agent never has to chain two python invocations on one line
# (the "chained python -> Exec failed" bug class).
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"    # .../skills/hyperliquid-ops/scripts

# 1) serialize state (single source of truth)
python3 "$HERE/state_snapshot.py" || { echo "state_snapshot FAILED"; exit 1; }

# 2) proximity check (pass-through to the round-robin originators)
python3 "$HERE/entry_proximity.py" || { echo "entry_proximity FAILED"; exit 1; }

exit 0
