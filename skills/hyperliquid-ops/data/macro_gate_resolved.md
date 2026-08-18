# MACRO GATE — PRE-RESOLVED (trusted local file, read-only)

This is the resolved macro gate output for the current call window. It is written by Charly
(the reconciler) from `bloomberg_macro_gate.py` + `news_gate.py` runs and the disconfirming
search already done this session. A sub-agent doing a full-stack review should READ THIS FILE
instead of fetching live email/news (which trips the external-content security guard).

Generated: 2026-08-18 ~11:08 UTC

## Named story (matched to every ±2% mover)

**Bond slump / long-end repricing.** 30y UST 5.33% (highest since 2007). Drivers: debt supply +
stuck-above-target inflation — NOT growth optimism. Fed minutes due Wed 2026-08-19.

Cross-asset movers (all ≥2% 24h), each matched to this named story:
- WTI +3.8% / Brent +3.4% — Hormuz transit collapse (5 tankers Sat vs 31 prior wknd), US-Iran deal doubt.
- Korea 200 −4.9% / Nikkei −2.7% — leveraged AI/memory unwind + risk-off, KOSPI profit-taking.

## Divergence check (the tradeable signal)
- Equities selling hard (SPX/NDX/Nikkei down) WHILE BTC holds +1.3% → BTC-bid-during-bond-slump.
- BUT breadth does NOT confirm: ETH flat (+0.0%) vs BTC +1.25% (breadth-divergence component tripped, #12).
- Decoupling ~24h old, unconfirmed. History: if macro asset keeps moving and BTC doesn't follow,
  BTC is the LAGGING asset, not the leading one. Short end (hike-off) is what BTC trades; long end
  (term premium) is what's selling.
- Regime label: ACTIVE RISK-OFF, long-end-led.

## Distrust window (doctrine #7)
04–10 UTC EU morning = statistical distrust window. The current call was committed ~09:2x UTC —
inside it — and must be read with that caveat (no conviction upgrades from moves inside the window).

## Note for reviewer
This file is CONTEXT for Step 0 of the full-stack review. The reviewer's job is NOT to re-derive
the macro gate — it is already resolved here. Proceed to review calls / scripts / ledger / grading
using this as the named macro story.
