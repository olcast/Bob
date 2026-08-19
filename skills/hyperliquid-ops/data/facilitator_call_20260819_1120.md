# FACILITATOR CALL — committed 2026-08-19 11:20 UTC, BEFORE challenger verdicts (independence seal)

Mode: evolve (open call exists). Mark 64,479.5 (pulled 11:20:15 UTC). Proximity WARM (move2 0.243%).

## Reasoning (four dimensions)
- Velocity: +0.126%/15m, pointed UP (2× the 10:56 read).
- RoC: −0.033 first half → +0.158 second half; accel +0.191 — strong build.
- Participation: vol_trend CONTRACTING; OI 39,634→39,480 BTC (INFERRED −155 BTC vs 10:56 fire) while price +0.13% = covering/exit, NOT sponsored. The single most dispositive dimension reads EXHAUSTED.
- Bandwidth: book FLIPPED — bid weight 64.3%→33.4%; ask depth 160.9 vs bid 80.6 BTC/5bp. Upward path now slips into resting sells.
- Carry: HL 5.98% ann vs BN 4.46 / BY 3.90 — HL long-premium WIDENED (~1.5pp). premium_bp=0 → PREREG legs DARK.
- Base rates (whisper only): reclaim EARLY n=76 fwd −0.21 / STRICT n=97 fwd −0.41 — in-sample, walk-forward-unvalidated.

## Narrative (context only)
Bond slump / 30y 5.33%; Fed minutes TODAY ~18:00 UTC = binary inside horizon. BTC holding vs SPX −0.94 / NDX −1.72 = narrow decoupling (breadth 2/5, ETH flat = DIVERGENT). Distrust window 04–10 UTC has passed.

## The moves (NESTED, not exclusive)
- **Move 1 — UP poke (IN PROGRESS, inside zone).** Zone 64,300–64,550; mark inside it. Observe-only (no entry per venue facts). Target upper zone 64,550; extension to 64,636/64,861 ONLY with OI expansion. Dead on 15m close < 64,300. p ≈ 0.50. Horizon: minutes–1h.
- **Move 2 — DOWN flush (ON DEATH'S DOORSTEP).** Entry 15m close < 63,930. Target 63,650; Branch C 62,500–62,700 only on OI cascade. DEATH-PRICE: 30m close > 64,300 without OI expansion — mark already 64,479 and OI is FALLING (no expansion), so the next 30m close above 64,300 KILLS this move. Soft-kill 1h close > 64,050 (already pierced intraday); hard-kill 4h close > 64,580 (+0.15% above mark). p ≈ 0.33. Horizon: 1–4h post-entry.
- Residual (chop / minutes-shock): 0.17. p_up ≈ 0.50.

## Key delta vs 10:56 fire
The fade thesis is WEAKENING: acceleration on contracting volume + falling OI + ask-flipped book is probe-like, but the death-price (64,300, no-OI-expansion) is about to trigger. If the next 30m closes > 64,300 without OI expansion: flush is DEAD; regime flips to range/continuation risk toward 64,580–64,861. Make-or-break bar: OI expansion on any continuation — without it, strength is covering, not sponsorship.

## Falsifiable bar / tripwires
- 30m close > 64,300 without OI expansion → Move 2 dead (structural).
- 4h close > 64,580 → hard kill, continuation regime.
- 15m close < 63,930 → Move 2 armed (entry prints).
- 15m close < 64,300 → poke leg void.

## Reasoning-improvements (facilitator)
1. oi_delta still null in packet despite being computable from consecutive state snapshots — wire the delta into assemble_brief.py (the death-price is ungradeable without it).
2. Book-flip (64.3%→33.4% bid weight in 24 min) deserves its own delta field in §0b — bandwidth direction-change is information, not just level.
3. Macro gate file still stamped 2026-08-18 on the Fed-minutes day — needs same-day re-stamp before US session.
