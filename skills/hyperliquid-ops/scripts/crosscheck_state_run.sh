#!/usr/bin/env bash
# crosscheck_state_run.sh — single unambiguous entrypoint for hlops-crosscheck-open STEP 1.
# Runs the canonical state serializer + entry-proximity check in one command,
# so the isolated agent never has to chain two python invocations on one line
# (the "chained python -> Exec failed" bug class).
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"    # .../skills/hyperliquid-ops/scripts

# 0) "always keep comms": pre-firing whole-chain liveness gate.
#    Dead providers are excluded from the round-robin so the ensemble degrades
#    cleanly (2-model vote) instead of erroring mid-call. Never fatal to firing:
#    we proceed with whoever ANSWERED, and the liveness cron reports the death separately.
HEALTH="$(python3 "$HERE/model_health.py" --json 2>/dev/null)"
if [ -n "$HEALTH" ]; then
    echo "$HEALTH" > "$HERE/.model_health_last.json"
    DEAD_COUNT="$(echo "$HEALTH" | python3 -c 'import sys,json;print(len(json.load(sys.stdin).get("dead",[])))' 2>/dev/null || echo 0)"
    echo "[health] dead providers: $DEAD_COUNT"
else
    echo "[health] probe returned nothing — proceeding (degraded, no gate)"
fi

# 1.5) STALE-DATA GATE (Olivier 2026-08-19): if the forward tape is stale, backfill via
#      desk_collect BEFORE any model touches the state. No model reasons against a stale tape.
python3 "$HERE/preflight_freshness.py" --max-age-min 65 || { echo "preflight_freshness FAILED — tape not fresh"; exit 1; }

# 1) serialize state (single source of truth)
python3 "$HERE/state_snapshot.py" || { echo "state_snapshot FAILED"; exit 1; }

# 2) proximity check (pass-through to the round-robin originators)
python3 "$HERE/entry_proximity.py" || { echo "entry_proximity FAILED"; exit 1; }

exit 0
