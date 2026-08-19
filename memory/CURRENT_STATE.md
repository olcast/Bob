# CURRENT STATE — frozen source of truth

Frozen: 2026-08-19 13:05 UTC (by Charly, to stop the do-and-undo loop)

## Why this file exists
Context compaction has wiped the chat 2+ times today. Every wipe forces a
re-derivation, and re-derivation drifts → corrections → feels like reverting.
This file is the durable snapshot. If context is lost again, READ THIS FIRST and
treat it as authoritative over any fresh reconstruction.

## Project
"Charly/Bob" — Olivier Castagne's manual Hyperliquid crypto-perp desk
(BTC/ETH/SOL/HYPE). 3-model cross-check: DeepSeek v4-pro (producer) →
Qwen max (challenger) → Grok 4.6 (third). Read-only reporting desk;
execution is Olivier's layer. NEVER place/modify/cancel orders.

## Corrections locked in (do NOT re-revert)
- The crons **collection** was FREE and could keep running. It was NOT the cost
  source. Cost blowup ($200/day) came from API/model calls, not collection.
- Cron list is currently EMPTY (0 jobs) as of 13:03 UTC — collection crons are
  gone too. That is likely why OI-delta is null (no OI snapshot being written).
  Restoring the free collection cron is a candidate fix — but DO NOT touch crons
  without Olivier's explicit go.

## Live position (known)
- BTC SHORT: 0.78169 BTC @ 63,618 entry.

## Calls (today)
- 3 blind co-originator calls landed ~10:06–10:17 UTC (all fade/down-bias,
  p_up 0.37–0.45): deepseek_call.json, qwen_call.json, grok_call.json.
- Facilitator "evolve" reconciliation 11:20 UTC: Move1 up-poke 64,300–64,550
  (observe), Move2 down-flush (entry <63,930 → 63,650; branch C 62,500–62,700
  on OI cascade), death-price = 30m close >64,300 without OI expansion.

## Open items (the only remaining work)
1. Macro gate re-stamp (Fed minutes 18:00 UTC = key same-day catalyst).
2. Fix OI-delta (needs OI state snapshot; see cron note above).
3. Final reconcile of the 3 calls → one committed BTC call (2 next moves).

## Full conversation recovery (2026-08-19 13:15 UTC)
Olivier exported the full conversation history. The authoritative on-disk
copy is the trajectory JSONL files — if context is lost, READ THESE FIRST
(instead of re-deriving from scratch). Directory:
`/root/.openclaw/agents/co-deepseek/sessions/*.trajectory.jsonl`
Main history lives in the two biggest files:
- 87efeada-158f-42e7-8112-9fc6ca691095.trajectory.jsonl (current main session)
- 7cf9e0a7-e6c7-4133-835c-81081ce29bb2.trajectory.jsonl (morning main session)
Canonical identity: Olivier Ludovic Castagne, ol.castagne@gmail.com,
timezone Europe/Madrid. SSH host 62.238.58.152 (root@ubuntu-2gb-hel1-1).
Repo olcast/Bob. Desk architecture v2.6.4, frozen until 50 graded calls.
NOTE: a revoked Gmail app password appeared in the old history — it is
revoked, do not repeat or persist it.

## Data locations
- skills/hyperliquid-ops/data/crosscheck/{deepseek,qwen,grok}_call.json
- skills/hyperliquid-ops/data/facilitator_call_20260819_1120.md
- skills/hyperliquid-ops/data/three_model_reconciliation_2026-08-19.md
- skills/hyperliquid-ops/data/MORNING_PLAN_2026-08-19.md
- memory/2026-08-19.md (running log)
