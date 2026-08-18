# MOVE-3 PROTOCOL (DRAFT — pending ensemble answer + Olivier approval)

## Why this exists
The move chain currently ends at `path_b_terminus` (62,500–62,700). There is no defined
behavior for *what happens when the move-2 deep target is actually reached*. This is a live
gap: deciding at the level (under P&L + adrenaline) is exactly how the desk loses the edge
it spent the last week building. Pre-register the answer.

## The trigger (falsifiable, not vibes)
Move-3 activates ONLY when **move-2's deep target is tagged** — operationally:

- **Trigger:** a 15m close inside [62,500 – 62,700] (the R-044 pool / path_b_terminus zone).
- Until that prints, Move-3 is dormant. It does NOT fire on proximity, "warm," or a wick.

## The decision (to be filled from the ensemble re-derivation of R-044)
The correct Move-3 action is a function of ONE unknown: **the base-rate on a reclaim/bounce
at R-044, second approach.** Three candidate branches, chosen by the number, not by feel:

- **BRANCH A — reclaim-high (R-044 bounces):** reload/keep flat-to-long, target the snap
  back toward 63,130–63,380. Size only if the reclaim base-rate clears the desk minimum.
- **BRANCH B — reclaim-low (R-044 decays):** stand aside / let the short keep working toward
  the *next* liquidity pool below, do NOT catch the knife, do NOT flip long on a whisper.
- **BRANCH C — indeterminate (no clean edge):** explicit stand-down; no position change; the
  honest answer is "no trade" rather than a forced reload.

> The ensemble answer to "what's the reclaim base-rate at R-044 (second approach)?" selects
> the branch. Re-derive it, do not inherit the stale "decayed pool" label — same rule as
> `brief_facts.md` §3.

## Invalidation of Move-3 itself
Whatever branch is selected, it dies if:
- A 4h close back ABOVE 63,130 (up-side invalidation — the flush didn't continue), or
- A 15m close BELOW 62,000 (down-side — the flush blew straight through R-044 with no
  reaction, i.e. the pool is gone and the branch's premise failed).

## Grading
Any Move-3 action is graded forward like every other call (direction, reached, context, Brier).
Move-3 is NOT given a free pass for being "the deep one."

## Status
- [ ] R-044 reclaim base-rate re-derived by ensemble (DeepSeek + Qwen + Grok, blind)
- [ ] Branch selected (A / B / C) with the number cited
- [ ] Olivier approves the branch + the trigger definition above
- [ ] Written into `state.json` as `move3_*` fields, replacing this draft
