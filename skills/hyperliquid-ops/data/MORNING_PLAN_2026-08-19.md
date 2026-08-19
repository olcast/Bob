# Morning implementation plan — 2026-08-19

Source: Grok 4.6 full-stack audit (round 2, read real doctrine/skills/loops/graphs).
Olivier: "let's wait till the morning and implement everything. Closing these gaps will help us reach our goal."

## PRINCIPLE (Olivier, 2026-08-18 20:29): implement EVERYTHING, whatever it costs within reason.
No deferral. Every item below ships. The "candidates" tier also ships, gated only by the
"prove it flips a decision" bar — not skipped, just built with a falsifiability check attached.

## FIRST-CLASS ITEM — contract-aware lens (do NOT implement on a caricature)
The desk trades TWO venue types and Grok's audit (BTC-centric) mostly skipped the xyz book.
Every fix below must be applied PER-CONTRACT, not uniformly:
- BTC/ETH/SOL/HYPE = hard-stop, live mark, real 5bp, real R. Full sensor set applies.
- xyz (SP500/Brent/Gold) = oracle-priced, DARK when underlying closed, R FICTIONAL,
  $465M-OI thin book, re-open re-mark 3-4% gap. The live gap here is:
  oracle-dark-hour geometry + re-open-gap + R-fiction, NOT markout/tape-mix.
Consequence: seam #1/#3 fixes (wiring base_rates/HLP/premium/CVD into the fire packet) apply
on the hard-stop venues; xyz needs its own block (R-fiction flag + dark-hour state + re-open gap).
Do not let "four dimensions" become four uniform dials across five contracts.

## Do FIRST (seams, not new sensors — cheapest highest-value)

1. **Seam #1 + #3 — close originator starvation + judge's blind spot**
   - Wire into `assemble_brief.py` fire packet the variables the originators are currently
     STARVED of: `base_rates`, HLP inventory, whale net, premium path, CVD, absorption,
     analog base rates. (They read mark/OI/funding + four-dims only today.)
   - Add a mechanism-bar field to `calibration.py resolve()` so the score sees OI/funding/CVD/premium
     — doctrine claims the edge is the mechanism, but the judge only scores first-touch on BTC 5m.
   - Fix: "neither touched = down won" punishes patient/stand-down/move-1-observe-only calls. Give
     them a legitimate outcome state instead of mis-scoring as down-win.

2. **Seam #2 — discoveries don't reach the brief**
   - Pipe `lessons.json` + KG + `backtest_rates.json` into `assemble_brief.py`.
   - Hard-won lessons currently leak at SAVE→assemble. Close it.

3. **"Zones-as-facts" word game (past-as-prior honesty)**
   - Decide how to inject prior structure (move*_zone/dir) without re-anchoring originators.
   - "Structure is the last verdict" — need an honest past-as-prior convention, not a
     timestamp-on-an-anchor.

4. **Write audit into `lessons.json`** as a candidate lesson (seam findings + "mechanism > fit").

## Then (candidates, do NOT build until proven they flip a decision)

Missing sensors Grok flagged — list as candidates, test cheaply first, adopt only if they change a read:
- Tape *mix* (size-bucketed CVD, HHI of prints) — "8 whales vs 400 clips"
- Liquidity-as-process (refill half-life, book convexity)
- Impact/markout (Kyle λ, horizon curve)
- Cost-basis / underwater surface (liq-map ≠ where inventory opened)
- Predicted-vs-printed funding residual
- Jump geometry (realized-vol / jump-share) — "perps die in jumps, your lens is diffusion"

## Standing bar (do not regress)
- "Remove anything that does not improve" — every addition must prove it flips a decision.
- Confluence not consensus; produce w/ one model, challenge w/ second (bounded-independence caveat).

## Open position (carry over)
- SHORT 0.78169 BTC @ 63,618, ~$1,000+ underwater, death-price fired 14:26 — cover still UNCONFIRMED.
