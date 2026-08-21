# Current Call — 2026-08-21 20:24 UTC (full stack, independent, grok-4.6)

## Liveness (fetched before this stack)
- `collector.py --once` 20:18:56Z — market/book/hlp/liqmap written. Liqmap age **20m** at 20:20. STATUS OK. nPos=122 nAddr=400.
- analog.py live 20:20 n=1 REFUSE. analog_markov live 20:20 n=161.
- Tape 90s live 20:22. Absorption sidecar STALE (19:31) — not used.
- Macro 0b/0c cache 15:00 CEST age ~7.3h <8h. 0a live VOID — named stories filled from cache + disconfirming search (trigger 1).

## Macro gate: VOID → CLEAR (cache 15:00 CEST; 0a live 20:18 UTC)
Named + dated for every ≥2% mover:
- **BTC +6.58% / ETH +4.76% / SOL +4.75% / HYPE +3.29%** mark BTC 77,445 @ 20:18. FT 21 Aug: “Bitcoin and gold surge as Bessent’s bond market intervention weighs on dollar.” CoinDesk 21 Aug: “Bitcoin slips back to $77,000 after challenging $80,000 overnight.” The Block 20 Aug: spot BTC ETFs +$517m. Inbox 10:08: “The debasement trade is back.” Multiple candidates — do not assert one cause.
- **Gold +2.03%** → Bloomberg 21 Aug “Gold Jumps as Treasury Buybacks Revive Debasement Concerns.” Same Bessent/debasement tape. Alts = BTC beta.
- **Disconfirming:** Euronews/CNBC 20–21 Aug — yields rebound after Bessent; buyback being faded in bonds while gold/BTC still bid.
- **Divergence:** SPX +0.39% / NDX +0.37% = crypto-native, not equity beta. Cross-asset 24h breadth 5/5 confirms direction, not magnitude.
- Oil not a ≥2% mover. xyz:VIX / xyz:DXY stubs — not quoted. EUR/JPY flat.
- Clock: CEX funding +3.7h. Deribit 22AUG26 0DTE +11.7h (OI 5001). No CPI/FOMC inside 72h / 90m.

## Structure (this stack — wave first)
- 4h last UP 73,001 → **79,584**; px ~77,441 @ 20:20. Decision: 77,069 · 76,292 · 75,516 · break 74,555. Retrace +33% = **in the zone, above 77,069**.
- 1h last DOWN 77,894 → **76,620**. Decision: 77,107 · 77,257 · 77,407 · break **77,593**. Retrace +64% = **ON 77,407**.
- Last closed 1h **77,018** (19:00) ABOVE 76,620 / BELOW 77,593. Forming 20:00 1h.
- Last closed 4h 77,018 (16:00) BELOW 79,584. No 4h accept of the high.
- 5m MICRO: HIGHER HIGHS + HIGHER LOWS = up micro. Do not call the up-path dead.
- Fib-time 1h: 2b since 18:00 → 5b=**23:00**. 4h 5b=08-22 04:00.
- Own-lines: nearest above 78,092 (1h TL-res) / 79,142 / 79,803. No live TL break+retest at mark.

## Pulse / fuel (this stack)
- 5m PULSE **CONFIRMING** up — vol +226%, CVD buy. Let a push run; do not fade mid-range.
- 1h PULSE FADING on last closed bar (19:00 dump). Stale vs the bounce. Re-run at 21:00 close.
- Live 90s tape 20:22: n=486, Δ **−75.0%** (sell 37.0 vs buy 5.3). Price 77,441 → 77,466 UP while sold into. Exhaustion shape (price high after CVD high). Sample OK. Prints contradict 5m pulse — contradiction is the signal.
- BTC dOI **+0.6%** (0.8h). Prem +0.2bp NEUTRAL. Turn 2.90. Excess APR 0.0%. No perp crowd; latent fuel not visible.
- Magnet UP (fresh 20:00): short-liq **78,803 +1.8% $1.4M** (Δ +1.44M). Stretch 79,956 $1.4M. 78,034 $5k spent.
- Downside: 76,497 $3k / **76,112 $75k** / **75,728 $171k**.
- Forced: tag 78,803 fires $1.4M shorts; tag 76,112 fires $75k longs.
- Analog.py n=1 REFUSE (unusual). Markov 52/48 n=161 — coin-flip cell; structure + tape break the tie, not the path %.
- Contradiction **SPLIT** (price×cvd, cvd×fuel). Do not average.
- Options PROXY: max-pain **74,000**, callShare 0.585 — NOT dealer GEX.
- Occupancy: coil 36.8%. No 4h accept of 79,584.
- Accel: mark accelerating+. xyz AFTER-CASH (crypto no-op).

## Book
FLAT. Mark ~77,454 is MID 76,620–78,803. Do NOT chase. 5m confirming is not an entry from mid-range.

## Two next-most-probable moves
**Move 1 — LONG flush-reclaim of 76,620 (R of 4h up-leg / 1h low holds).** p ≈ 0.52
- ENTRY: **76,620** 15m close reclaim after a poke (already above — do not chase; arm the poke-reclaim). Engine stop **76,160** (0.6%).
- EXIT: partial **77,593** · full **78,803** ONLY on 15m accept >77,593 · stretch **79,584**.
- FAST KILL: 15m close **<76,160**. CONFIRM KILL: 1h close **<76,160**.
- RE-ENTRY: after target-exit at 78,803, re-long only on a later 15m reclaim of **78,803**.
- REVERSE: 15m accept **<76,112** → short toward **75,728 / 75,516**.

**Move 2 — SHORT tag-reject of 78,803 (fresh $1.4M short-liq / 4h high still unaccepted).** p ≈ 0.48
- ENTRY: **78,803** 15m close fail after a tag. Engine stop **79,276** (0.6%).
- EXIT: partial **77,593** · full **76,620** · stretch **75,728**.
- FAST KILL: 15m close **>79,276**. CONFIRM KILL: 1h close **>79,276**.
- RE-ENTRY: after target-exit at 76,620, re-short only on a later 15m fail of **76,620**.
- REVERSE: 15m accept **>79,276** → long toward **79,584 / 79,956**.

Death-price: **15m accept < 76,160** (hold/R dead) XOR **15m accept > 79,276** (fade/C dead).
While waiting: **77,593** is the 1h break. 15m close >77,593 = bounce accepted — do not take a 77,407 short; wait for 78,803.
Tail: 5m confirming through 78,803 with volume → 79,584 / 79,956. 15m accept <76,112 → 75,728 / 75,516. Neither is an entry from 77,454.
SCORE silent: up 78803 / dn 76620 / p_up 0.52 / h 8.
