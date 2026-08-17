# VCP-ABLATION-001 — Pre-Registration (SEALED)
## "Does adding pictures improve outcomes?" — a nested-ablation test, with liquidation maps

**Author:** Olivier Castagne · HL-OPS swing desk
**Status:** SEALED PRE-REGISTRATION — no results viewed at seal time.
**Seal:** UTC timestamp + SHA-256 of this file, recorded in the companion `.seal.txt`. Any later edit changes the hash → tamper-evident (VCP Layer-1/2 discipline applied to our own experiment).
**Doctrine:** extends desk #20 (state → transition → grade), #23 (depth→reclaim CANDIDATE), R4 firewall, A4–A7 (proper scoring / regime-spanning / microstructure null / cost model).

### 0. One-line hypothesis
Richer state predicts better **only conditionally**. This experiment measures whether each added feature layer — culminating in **liquidation-map data (P2)** — lowers **out-of-sample log-loss** on sealed labels *beyond the layer beneath it*, on regime-spanning held-out data, with trial count as the denominator. "More pictures help" is CONFIRMED for a layer iff it earns its degrees of freedom out-of-sample; otherwise REJECTED and logged.

### 1. Targets (all three; shared feature pipeline). Primary = T-A.
All labels computed strictly from information *after* event time. No look-ahead.

- **T-A — Reclaim vs continue (primary).** On a level-break (break of prior-24h high/low, desk spec): does price *reclaim* the level within horizon H (trap) or *continue* to the next liq cluster (real)? Directly extends #23 — the question is whether the liq-map beats sweep-depth alone.
- **T-B — Liq-cluster magnet.** From state at t: does price *touch the largest liq cluster* within 24–72h (binary) + regression variant (fraction of distance-to-cluster closed)? Tests the magnet hypothesis head-on.
- **T-C — Cascade vs fizzle.** On a break: does realized displacement exceed k·ATR14 (cascade) vs. mean-revert (fizzle)? Tail-weighted; rarer; always reported with n.

### 2. Feature layers (nested, additive — same for every target)
- **P0 — Price / structure.** OHLC features, ATR14, distance to structure.py zones, **sweep depth** (#23 feature), range-vs-median (quiet/loud), swing context.
- **P1 — + Positioning.** OI level & ΔOI, excess funding APR over dex baseline, premium bp (oi_flow).
- **P2 — + Liquidation maps.** Multi-exchange cluster sizes above/below, distance to nearest & largest cluster each side, up-fuel vs down-fuel asymmetry, total mapped liq within ±X%, at **1d / 7d / 30d / 1y** windows. Forward-collected (§5).
- **P3 — + Cross-venue / breadth.** BTC vs ETH/SOL/HYPE confirmation, cross-venue funding dispersion.
- **P4 — + Time.** Hour-class / pattern-of-life (04–10 UTC distrust window, etc.), lead-lag (spot-vs-perp, price-vs-news), scheduled-event proximity.
- **P5 — + Macro / news / sentiment.** Macro-gate state, Fear & Greed, SPY put/call.

### 3. Model & scoring
- **Model:** one low-variance classifier per (target, layer) — logistic regression / gradient-boosted stumps with hyperparameters fixed a priori. No per-run tuning.
- **Primary metric:** out-of-sample **log-loss**; secondary **Brier** + **reliability curve by bin** (A4). A layer improves outcomes iff ΔlogLoss(k vs k−1) < 0 on held-out data beyond the trial-adjusted threshold.
- **Marginal-information framing:** report *incremental* lift per layer, not total — each feature costs a degree of freedom; the test is whether it pays for itself OOS.
- **Cost model:** where lift is translated into a trade, the 25bp round-trip haircut (A7) applies.

### 4. Validation discipline (R4 firewall)
- **Split:** train older; validate on a held-out window that **spans ≥1 regime change** (A5). A same-regime later window is NOT independent.
- **Trial log:** every (target × layer) test = one trial. Trial count = denominator of any significance claim. No cherry-picking the best cell.
- **Maturity ladder:** DISCOVERY → CANDIDATE (this pre-registration freezes P0–P5 & targets) → ADMITTED (blind-validated OOS, regime-spanning, proper-scoring, beats the microstructure null A6). Nothing touches live conviction until ADMITTED.
- **Kill / degenerate:** if P2 shows no marginal OOS improvement across all three targets once N ≥ threshold spanning a regime, "liq maps add predictive information" is REJECTED for those targets — logged, not buried.

### 5. Data timeline (honest)
- **P0/P1** backtest on existing HL candle + oi_flow history **now** → the baseline the liq-map must beat.
- **P2 (liq maps)** are **forward-collection only** (historical heatmaps not retro-fetchable). Collection starts at seal time via the browser worker (Coinglass, free tier, multi-exchange, 1d/7d/30d/1y, BTC first). Interim P2 analysis is **descriptive only** until N and regime-span thresholds are met.
- Every snapshot carries its pull timestamp; the label window must strictly post-date the snapshot (no leakage).

### 6. Pre-registered thresholds (frozen at first-collection review)
- Admission N: order-hundreds of events / target / lane (A5).
- Regime-span: validation window must cross an SMA-state change.
- Significance: effect + bootstrap CI + trial count; no single-metric hard gate; proper-scoring evidence required (A6/A7 spirit).

---
**Nothing below the seal has been computed. If this file's hash does not match the companion seal, the pre-registration is void.**
