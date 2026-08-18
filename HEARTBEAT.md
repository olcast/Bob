# Heartbeat tasks

## Recursive discovery (daily)

When you next run a heartbeat, if it is the first heartbeat of the UTC day (or a discovery cycle is due):

1. `cd skills/hyperliquid-ops/scripts`
2. Run `python3 calibration.py` and `python3 discovery_loop.py data/calls.json data/lessons.json`
3. If there are PROPOSED promotions/retirements, surface them to Olivier as a short list (never auto-promote — the human SAVE is the gate).
4. If nothing earned promotion/retirement, log an honest null in the daily note and move on.

## Model-version hygiene (per session)

Re-resolve each provider's flagship model id via the live `/models` endpoint before any call-generation or review (see SOP-RECURSIVE.md §1). Fix stale config ids before use.

## Knowledge graph (per session)

Read `skills/knowledge-graph/data/kg-summary.md`; add entities/relations for anything significant this session; run `node skills/knowledge-graph/scripts/summarize.mjs` after changes.
