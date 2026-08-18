#!/usr/bin/env bash
# discovery_sweep_run.sh — durable runner for the discovery battery.
# Runs all sweep scripts, tees their stdout into data/prospecting.log
# (guaranteed at the shell layer — no reliance on the agent to redirect),
# and appends a timestamped header so the artifact is always written,
# even on a null result.
#
# The agent cron calls THIS script. It never has to remember the redirect.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"          # .../skills/hyperliquid-ops
LOG="$ROOT/data/prospecting.log"

mkdir -p "$ROOT/data"

{
  echo ""
  echo "===== discovery-sweep run $(date -u +%Y-%m-%dT%H:%M:%SZ) ====="
  echo ""
  python3 "$HERE/discovery_sweep.py"
  echo ""
  echo "----- discovery_excursion.py -----"
  python3 "$HERE/discovery_excursion.py"
  echo ""
  echo "----- cross_lens.py -----"
  python3 "$HERE/cross_lens.py"
  echo ""
  echo "----- funding_sweep.py -----"
  python3 "$HERE/funding_sweep.py"
  echo ""
  echo "----- edge_ensemble.py -----"
  python3 "$HERE/edge_ensemble.py"
  echo ""
  echo "===== end run $(date -u +%Y-%m-%dT%H:%M:%SZ) ====="
} 2>&1 | tee -a "$LOG"

exit 0
