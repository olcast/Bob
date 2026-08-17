# THE READ — the desk's standing thinking process (converged 2026-08-15)

The default method for ANY market read / level call / trade idea. **Run it end-to-end, unprompted.** Ordered.
Each step names its tool and the doctrine it draws on. It exists so a read is never a narrative fit (the
Elliott trap, #46): it is macro-gated → **structure-framed** → position-grounded → signal-adjudicated →
empirically base-rated → committed with honest probability. **The method is the product; the level is the
footnote.**

## 0 — Macro gate first. Never a level before this. (SKILL Step 0)
`macro_preflight.py` → VOID / CLEAR. Disconfirming search in neutral wording (search to BREAK the thesis,
not confirm it). Inbox pass. 72h catalyst calendar — name the tripwire out loud. If VOID, stop and resolve
every flagged mover to a named, dated story. Cross-asset divergence outranks your thesis: if price
contradicts the narrative, the price is right.

## 1 — Wave structure across timeframes, FIRST. Enumerate the scenario SPACE + the levels. (#49)
`wave_scenarios.py` on 5m / 1h / 4h **before looking at any signal.** The swing structure gives the **Fib
retrace zones = WHERE** the next reversal or trendline-break can happen, and the two competing scenarios
(**R** = trend resumes vs **C** = break/reversal). It also gives **WHEN**, not just where — **Fib *time***:
bars elapsed since the last pivot vs Fibonacci counts (5/8/13/21/34/55/89) flag when the next turn is *due*
(wave_scenarios.py prints both the Fib price zone and the Fib-time windows). **Why first:** it converts an infinite chart into a few
concrete, falsifiable levels and a binary question — that frame is what makes everything downstream
*interpretable*, and it is what makes CONFLUENCE visible (on 2026-08-15 the 4h .618 at 63,474 was only
recognisable as the same thing as the 63,500 liquidity pool *because the wave frame was laid down first*).
**The discipline that keeps "structure first" from becoming the Elliott trap:** it ENUMERATES both
scenarios, it never asserts one — the picking is done in steps 2–5. Heuristics that earned their place:
first impulse is often a **fake** (grab then reverse); **down-pokes get bought** (long-bias #40); the
**0.786 is the make-or-break**.

## 2 — Positions, not funding. Map the fuel onto the frame, in RATE-OF-CHANGE. (#44, #49)
`oi_flow.py` + the collector (Drive). Open interest and **ΔOI** — is leverage BUILDING or CLEARING? The
**liq-map fuel-skew** — where is the fresh liquidity / the magnet, and does it sit ON one of step-1's levels
(that coincidence is the edge)? **HLP house inventory** — is the market-maker offside and forced to defend?
Whale / per-address net. Funding and premium are a *price of holding*, not a quantity — **secondary
confirmation only**; neutral funding is a baseline, not a crowd. Read velocity, not level. **Into a known
event, positions are often CLEARED first** — expect OI to bleed and two-way stop-runs before the catalyst;
the event itself can break either way.

**LIQUIDITY LENS (#55) — read like the market maker.** Price is liquidity-seeking: it moves TOWARD the pools
(stops / liq-clusters / round numbers), not away — the magnet is a magnet *because* liquidity rests there.
Name the pool at every armed level (wave pivots + the liq-map's `longLiqClusters`/`shortLiqClusters` + round
numbers). And the invalidation is a **scoring line, not a stop** (no stops in discovery): commit it *below* the
pool, so a stop-hunt that wicks the pool and reverses to target scores as the correct call it was, not a loss
(candidate L1). Anticipate the hunt, but don't hallucinate the hand — you read snapshots (OI, funding, HLP,
liq-map), not resting or spoofed size; the one tell that can't be faked is sustained **acceptance**, so weight
the hold over the touch.

## 3 — See ALL dimensions at once + their relationships. (#47)
`state_view.py`. Price-structure, positioning, funding, regime, flow — read **jointly**, one screen. Use the
**relationship matrix** to avoid double-counting correlated dimensions (basis ≈ funding, cvd ≈ trend). The
signal is a **REGION of the joint state**, never one lens in isolation.

## 4 — Signals + their RATE-OF-CHANGE adjudicate which scenario resolves. (#49)
At the step-1 level, which signals' **velocity** calls R vs C: volume-expansion + CVD turning up → the level
**HOLDS** (real); **accelerating efficiency (Δefficiency) without volume** → it **BREAKS** (or it's the
fake). The velocity of the signal beats its level (Δefficiency was the #1 backtested discriminator). **Fast
at-the-level call:** `pulse.py [level]` reads volume + CVD rate-of-change on 5m/1h and returns **CONFIRMING**
(continuation — let it run) vs **FADING/DIVERGING** (the fake — fade it) in ~2 seconds. Run it when price
reaches a magnet to decide continue-vs-fake.

## 5 — Repro the current state for the empirical base rate. (#48)
`analog.py`. Fingerprint now (regime, ATR-compression, range-position), pull the historical analogs, read the
forward path distribution. The honest base rate that stops narration — and tells you when a leg is a **coin
flip**, at which point steps 1–2 (structure + liquidity) are what break the tie, not a story.

## 6 — Commit to a best call. Honest probability, weight the significant tail.
Even a coin-flip leg gets a **committed lean** once structure + liquidity break the tie. Name the
**low-probability / high-significance tail** (vol expansion, catalyst break) — a low probability can dominate
on payoff, so it is not optional. State the **make-or-break level** and the invalidation. Put conviction on
what is actually reliable (the reclaim, the vol expansion), **never faked on direction**. **Cross-asset
breadth** (`cross_asset.py`) is a confluence/divergence check here: does the complex — ETH/SOL/HYPE + xyz
SPX/NDX — CONFIRM the BTC move? Divergence lowers conviction. There is **no tradeable cross-asset LEAD**
(#51) — breadth is the usable cross-asset signal, not a leading indicator.

## 7 — Continuity: assess how the scenarios EVOLVED since the last read.
When a prior read exists (the ledger, or earlier in the conversation), **don't start over** — read its
enumerated scenarios and state how each moved since: **strengthened / weakened / invalidated /
level-shifted**, and the DRIVER (wave shift, OI ΔOI, magnet moved, new catalyst, make-or-break tested), **plus the wall-clock TIME elapsed since the last read** — a call has a
time budget: if the expected leg didn't fire within its window it is weakening, and Fib-time (step 1) may now
put a turn *due*. The
new call is the **DELTA** of the prior one. This makes the desk a single *evolving* scenario tree, not a
series of disconnected snapshots — and it is what lets grading + expectancy accumulate across reads.

## 8 — Capture: log a testable improvement, or an honest null. (#54 CAPTURE DUTY)
Closing step, EVERY run — this is how one agent's learning becomes every agent's. Ask: *did this read reveal
a testable improvement to the METHOD?* — a better-calibrated way to set the probability, a break-line that
should have sat below the liquidity, a signal that keeps mis-firing, a relationship worth conditioning on. If
YES **and** it is (1) falsifiable — names a `metric` + forward test + promotion `bar`; (2) observation-backed —
tied to a specific call or miss *this run*; (3) not a duplicate; (4) METHOD / STANCE / bias-control scope —
**never** the frozen alpha thesis (#53): append ONE candidate `lesson-YYYYMMDD-HHMM.json` to the Drive folder
`12xPcwVMMXfk3mqCxGSN-hBBeLKI4NNoG`. If NO: nothing — **an honest null is the correct output; most runs add
nothing.** Candidates are INERT hypotheses: they change nothing until they survive the bar (Sunday retro,
`discovery_loop.py`) AND Olivier saves the skill. A flood of vibes is the overfitting trap; the bar + the
save-gate are what make looking-for-improvements safe.

## Firewall — throughout, always
Mechanism before fit (#46). Trial-count as the denominator. Decorrelation / N_eff — redundant confirmations
are not confirmations (#42). Forward / blind validation + a stopping rule. **Elliott is admissible ONLY as
enumerated, falsifiable scenarios with levels — never a wave-count narrative.** Read-only always: this is
analysis, not orders; execution and sizing are Olivier's separate layer.

---
*Provenance: converged live 2026-08-15 on the BTC read where multi-TF wave structure + a liquidity magnet on
the 4h .618 + rate-of-change signals beat a single-TF statistical lean (doctrine #40–#49). Promoted to the
standing process by OLIVIER ("updated the thinking process for everything… so next time you come with it
without me prompting").*
