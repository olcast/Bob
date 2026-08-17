# VCP-COMBINER-001 — Pre-Registration (SEALED)
## The ensemble layer: turning cost-surviving, decorrelated edges into one weighted view

**Author:** Olivier Castagne · HL-OPS swing desk
**Status:** SEALED PRE-REGISTRATION — frozen decision rules, written BEFORE the signals exist.
**Seal:** UTC timestamp + SHA-256 in the companion `.seal.txt`. Any later edit changes the hash → tamper-evident. The point of sealing a *method* (not just an experiment): it pre-commits HOW a signal earns weight, so the combiner can never be reverse-fit to make a favoured signal look good after the fact.
**Doctrine lineage:** extends VCP-ABLATION-001 (feature layers P0–P5); R4 firewall (DISCOVERY→CANDIDATE→ADMITTED); A4 proper scoring; A5 regime-spanning; A6 microstructure null; A7 cost model; #22 read⊥holdability; the RenTec/Numerai method — *many weak decorrelated edges, costs first, blind-validated, regime-tested, ensembled* — taken as METHOD, never as a magic signal.

### 0. One-line thesis
The edge is not any single signal — it is the disciplined combination of several weak, decorrelated, cost-surviving signals. A combined information ratio scales roughly as `IR_single × √(N_independent)`, so the object worth maximising is **the number of genuinely independent, admitted, net-of-cost bets**, not the cleverness of any one. This is the statistical form of the VCP intuition ("confluence and correlations within many pictures"): confluence = decorrelated agreement, priced honestly.

### 1. Where this sits
- **VCP-ABLATION-001** asks: does each added *picture* (P0 price → … → P5 macro) lower out-of-sample log-loss? It grades **features**.
- **VCP-COMBINER-001** sits one level ABOVE: does each added *signal* — an ADMITTED forecast built from those pictures — add **ensemble value net of aggregate cost**? It grades **combinations**.
- Same firewall, one level up. The combiner is itself an instrument and is firewalled like any signal (§5, §10).

### 2. Admission gate — what may carry weight (FROZEN)
A signal `S_i` gets **zero weight** until ALL hold:
1. **ADMITTED** per R4 — blind-validated OOS, on a partition spanning ≥1 regime change (A5), proper-scored (log-loss/Brier + reliability by bin, A4), and it **beats the microstructure null** (A6: classical LOB mechanics — adverse selection, inventory unwind, quote-pull — not just "beats baseline").
2. **Net-positive after the standing cost model** (Olivier's real ~5bp round-trip, applied to the signal's OWN turnover; A7). A pre-cost edge is not an edge.
3. **Emits a CONTINUOUS, CALIBRATED output** — a probability of its declared target, or a z-scored expected excursion — **not a binary trigger**. Calibrated by isotonic/Platt on held-out data. (Binary throws away the confidence and the agreement-in-degree the combiner needs.)
4. Carries a documented **decorrelation profile** (§4).

DISCOVERY / CANDIDATE signals are logged and tracked but **never weighted**. No exceptions for a signal that "looks obviously right" — that instinct is exactly what the gate exists to check.

### 3. Signal contract (the interface every edge must implement)
At each decision time `t`, an admitted signal emits:
- `p_i,t ∈ (0,1)` — calibrated probability of its **pre-declared target**, OR `z_i,t` — standardised expected excursion;
- `c_i,t` — a confidence / inverse-variance weight (how sharp this estimate is now);
- `h_i` — target horizon; `null_i` — the null it must beat.
**One target family per ensemble.** The primary target is **T-A reclaim-vs-continue** (per the ablation). A signal that forecasts a different object (T-B liq-magnet, T-C cascade) enters a **separate** ensemble for that target — never mixed. Combining forecasts of different questions is a category error.

### 4. Decorrelation (the entire source of value)
Before any weighting, on held-out data, compute pairwise correlation of (a) signal **outputs** and (b) signal **realised PnL/residuals**. Rules, frozen:
- Two signals with `|ρ| ≥ 0.7` (either measure) are ONE **cluster** — the cluster receives a single signal's worth of weight, split inside it. Correlated signals are not two bets.
- Every NEW signal is **orthogonalised** against the span of existing ones (residualise; only its incremental, uncorrelated component earns weight). A noisier copy of an existing edge adds nothing and gets nothing.
- Report the **effective number of independent bets** (e.g. `1/Σwᵢ²`, or an eigenvalue count of the signal covariance). This number — not the raw signal count — is the headline metric of the ensemble.

### 5. Weighting ladder (promote ONLY on OOS evidence — the combiner is firewalled too)
Start at the simplest tier. A fancier tier is adopted **only if it beats the tier below** on held-out, regime-spanning, cost-adjusted proper score by more than the trial-count-adjusted threshold. Otherwise stay put.
- **T0 — EQUAL WEIGHT** across admitted, decorrelated clusters. The robust default; at small N it reliably beats "optimised" weights out-of-sample because estimation error dominates. Every fancier scheme must beat this.
- **T1 — RISK PARITY / inverse-variance:** `wᵢ ∝ 1/σᵢ` (OOS vol) so each cluster contributes equal risk. Earns its place when signal vols differ materially.
- **T2 — SHRUNK INFORMATION-RATIO:** `wᵢ ∝ IRᵢ`, shrunk hard toward equal (Ledoit–Wolf / James–Stein). Uses expectancy, but shrinkage stops it fitting noise.
- **T3 — META-LEARNER (Numerai-style stack):** regularised logistic / gradient-boosted stumps on the signals as features, fit on a SEPARATE meta-fold — **only** once N ≥ order-hundreds of events spanning ≥2 regimes. Below that it overfits; deferred by default.

### 6. Cost is charged on the AGGREGATE, never per-signal
The combiner nets the ~5bp (+ a turnover penalty) against the **combined** position's turnover, not each signal's in isolation. Pre-committed consequences:
- Co-directional signals do **not** pay double cost.
- A signal is scored on its **incremental** cost-adjusted contribution — the marginal IR it adds *after* the extra turnover it induces in the aggregate. This can differ from its standalone net edge: a signal that **smooths** aggregate turnover can be worth more than it looks; a **flippy** signal worth less (or negative) despite a positive standalone number.
- Costs-first, applied at the level where costs are actually paid.

### 7. Signal → conviction → (trader's) size
The combined output is a **single calibrated conviction** (probability or z). Mapping to exposure: **vol-targeting** or **fractional Kelly (≤ ¼, capped)** — never full Kelly (estimation error blows it up). Per-target and aggregate exposure caps are hard limits.
**Read⊥holdability / read-only constitution (#22):** the combiner emits a conviction-weighted **VIEW**; the trader sizes within risk limits and owns the book. The combiner never places orders, and never flips a view to rescue a position.

### 8. Decay & re-fit (edges die — Medallion is capacity/decay-bound, not permanent)
- A signal's weight **decays toward 0** when its live OOS performance stops beating its null. Benched, not deleted — kept for post-mortem.
- The combiner is re-fit on a **fixed schedule** (e.g. monthly/quarterly) under the full firewall — **never continuously** (continuous re-fit = chasing noise). Each re-fit is a logged trial; trial count is the denominator of any "it improved" claim.

### 9. Honest current inventory (what we can feed it TODAY)
- **ADMITTED signals: 0.**
- **Best CANDIDATE:** the **1h shallow-sweep → reclaim**, excursion-graded (median MFE ≈ +1.09%, ~85% reach +0.5%, OOS train ≈ test) — still needs blind + regime-span + proper-score + microstructure-null before it is ADMITTED.
- **Forward-only P2** (HL ground-truth liq-map, HLP inventory) is accruing from 2026-08-15 but is not yet gradeable.
- **Therefore the combiner is EQUAL-WEIGHT-OF-ONE** — i.e. it *is* the single signal — until a **second decorrelated admitted edge** exists. This is correct: building weights on one signal is banned; a one-signal "ensemble" is just that signal, sized fractionally. **Activation trigger: ≥ 2 admitted, decorrelated, cost-surviving signals on the same target.**

### 10. The combiner's OWN pre-registered success criteria
The ensemble EARNS its existence iff — out-of-sample, regime-spanning, after **aggregate** cost — its calibrated forecast beats ALL of:
(a) the single **best** signal; (b) **equal-weight** (required for any tier ≥ T1); (c) the **microstructure null** — on proper score (log-loss/Brier) AND realised cost-adjusted expectancy.
- If it does not beat equal-weight → it **is** equal-weight.
- If a single signal beats the ensemble OOS → the ensemble **stands down** to that signal.
- Nothing is adopted on in-sample improvement. Ever.

---
**Nothing above is active. This is a sealed method on the shelf, waiting for its second admitted edge. If this file's hash does not match the companion seal, the pre-registration is void.**
