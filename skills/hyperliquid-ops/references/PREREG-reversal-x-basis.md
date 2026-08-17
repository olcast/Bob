# PRE-REGISTRATION — "price-reversal × perp-spot-basis-extreme" (BTC, HL perp × HL spot)

**Status: FROZEN 2026-08-15. This is a commitment device, not a backtest.** It exists to answer OLIVIER's
governing law (doctrine #46): *infinite signal combinations across both venues, and all of them fit an
Elliott-wave-style narrative in-sample.* The only escape is to specify ONE mechanism-backed signal in
advance and let forward data it has never seen be the judge. Nothing here may be re-optimized. Changing any
line below voids this pre-registration and starts a NEW one with a fresh trial count.

## The one hypothesis (with its mechanism)

A price REVERSAL setup is a weak directional signal on its own. It becomes a real signal ONLY when the
perp↔spot basis says the offside crowd is trapped. **Mechanism:** the reversal harvests offside leverage
(#41/#43); a basis extreme is the independent read that the crowd is on the wrong side and about to be
squeezed. The basis LEADS the reversal (lead-lag validated, #46), so it is usable, not coincident.

Venues: perp = HL `BTC`; spot = HL `@142` (UBTC/USDC). BTC ONLY — never pooled with other coins (#37a).

## The frozen signal (exact, no free parameters left)

Timeframe 1h. Two legs, each graded independently:

- **LEG S (short):** E2 resTL-REJECT — price tags a confirmed descending-resistance trendline
  (`desc_res`, pivots k=3) within tol=0.0015 and closes back below it (< line·0.9995) — **AND** the
  contemporaneous basis is in its **top-30% PREMIUM** band. Direction d = −1.
- **LEG L (long):** E4 POKE-LOW→RECLAIM — price trades below a prior swing low (pivots k=3) within a
  0.0024 band and closes back above it — **AND** the contemporaneous basis is in its **bottom-30%
  DISCOUNT** band. Direction d = +1.
- Event de-dup: REF = 6 bars minimum between same-leg events.
- (LEG V, secondary/lower-confidence: E1 vol-spike-FADE aligned with the perp dislocation. Logged but not
  required for the primary verdict.)

**Basis-band rule — the one anti-look-ahead refinement vs discovery.** In discovery the 30/70 percentile
was computed on the FULL sample (look-ahead). Forward, the band is the 30th/70th percentile of the
**trailing 60-day** basis distribution, recomputed as each 1h bar arrives — past data only. This is frozen.

Grading: pure directional forward return d·(C[i+h]/C[i]−1), h = 12 bars, plus MFE/MAE excursion.
**NO stop, NO cost, NO bracket** (OLIVIER owns execution at ~0 cost; a stop would invalidate the pattern —
#35/#39). This matches how the edge was discovered; changing it would test a different thing.

## Forward protocol (the collector logs it; we do not touch it while it runs)

At each 1h close the forward log records: both leg triggers (bool), the trailing-basis percentile, and —
h bars later — the realized d·return and the MFE/MAE. A matched RANDOM control (same count, random
entry/direction) is logged alongside to cancel any systematic harness bias (#33).

**Pre-committed decision rule (evaluated ONCE, at the target sample, not before):**
- Target: **N ≥ 40 confirmed-confluence events per leg** (expect months; conditioned cells are rare — be
  patient, do not peek-and-stop).
- **CONFIRM (candidate → ADMITTED-forward)** iff, for a leg: mean conditioned content > mean of the SAME
  edge UNCONDITIONED, **and** > the random control, **and** the bootstrap 90% CI on the forward
  conditioned cell EXCLUDES 0, **and** the sign matches the in-sample sign.
- **REJECT** otherwise. A rejection is a SUCCESS of the method: it means the in-sample confluence was an
  Elliott count, and we learned it cheaply. Log it and move on — do NOT re-fit.

## The stopping rule (the point of the whole document)

While this runs: no new conditioners, no threshold changes, no timeframe changes, no "just one more
combination." The infinite-combination space is closed for this signal. Any modification = a new
pre-registration with its own trial count added to the denominator (#46). Trial-count context at freeze:
~14 discovery trials + dozens of conditioning cells this session — so a single lucky forward cell is not
enough; the pre-committed rule above is the whole bar.

## Provenance
- Derives from: doctrine #40 (reversals), #41 (washing-machine), #43 (MM path/liquidity-harvest),
  #44 (perp-premium fade), #45 (cross-lens capstone), #46 (Elliott-wave law + lead-lag + volume-null).
- Source scripts (in-sample, for audit only — NOT to be re-run for the verdict): scripts/cross_lens.py,
  scripts/spot_perp.py, scripts/edge_ensemble.py.
- Read-only discipline unchanged: this pre-registration observes forward data; it never places or sizes a
  trade. Execution is OLIVIER's separate layer.
