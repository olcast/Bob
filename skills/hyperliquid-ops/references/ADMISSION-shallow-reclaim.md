# ADMISSION CHECKLIST — shallow-sweep → reclaim (CANDIDATE → ADMITTED)
### The one signal that survived discovery. This is the exact gate it must pass to earn live weight.

**Status:** CANDIDATE. **Target ensemble:** VCP-COMBINER-001 (needs a 2nd decorrelated admitted edge to activate).
**Asset scope:** BTC only — never pooled with ETH/SOL/HYPE (they trade differently; a signal admitted on BTC is a BTC signal, others are separate questions).
**Doctrine:** R4 firewall + A4 proper scoring + A5 regime-spanning + A6 microstructure null + A7 cost model.

### What we actually have (BTC 1h, 208d, reconfirmed 2026-08-15, unpooled)
- n = 93 events. Median MFE **+1.09%**, reached **+0.5% in 85%** of cases — and **OOS-stable: train 85% / test 85%**. Median MAE **−1.42%**, median time-to-peak ~11h.
- BUT the mechanical +0.5%/−0.3% bracket is **≈breakeven-negative** (full −0.023%/tr; train +0.001 / test −0.042) because the −0.3% stop is *inside the noise* — only 12% of events never breach −0.3%, so 88% get stopped before the +1% run.
- **READ THIS CORRECTLY:** the edge is the **excursion** (price does travel), NOT the tight-stop trade. The signal predicts a move; capturing it needs the right bracket. Admission must validate the *tradeable* version, not the −0.3% chase.

### Step 0 — pre-register ONE tradeable spec (frozen before any more testing)
The −0.3% stop is refuted; pre-commit a single alternative and test only that (no spec-shopping):
- **Entry:** on the reclaim close of a shallow sweep (< ~0.24% beyond the swept level, per #23/T-001 depth rule), OR a dip-entry on first retrace back toward the reclaimed level.
- **Stop:** structural — below the sweep low, or ~1×ATR14 / ~−0.8 to −1.0% (must sit *outside* the −1.42% median MAE noise, not inside it).
- **Target:** partial at +0.5%, runner toward the +1.0% excursion / next structure. Report as R-multiple, not just hit/miss.
- One spec. Written down. Then run the tests below once.

### The gate — ALL must pass, out-of-sample, before ADMITTED
1. **A7 — costs first.** Tradeable-spec expectancy **> 0 after 5bp**, OOS; report also at 25bp (must not be fragile to the haircut). A pre-cost edge is not an edge.
2. **A5 — regime-spanning.** Validate on a held-out window crossing ≥1 SMA-state change (the 4h/833d history gives a bull→bear span). Report expectancy **per regime** — a signal that only works in one regime is down-weighted, not admitted as unconditional.
3. **A4 — proper scoring, not hit-rate.** Define the binary label (reaches +0.5% before the structural stop within H). Report **log-loss + Brier + a reliability curve by probability bin** (is a "0.7" a real 0.7?). Hit-rate anecdotes do not admit.
4. **A6 — beat the microstructure null.** The reclaim must beat the *boring* explanation: mean-reversion after any wick / any bounce off a swept level *without* the reclaim-confirmation. Build that control on identical swept-low geometry minus the confirmation; the reclaim must add measurable lift over it. (Adverse-selection / inventory-unwind is the null, not "vs do-nothing".)
5. **Blind audit (R5).** Structured packet (raw facts only, no thesis); auditor derives P independently; **|ΔP| > 20pp = CONTESTED**, cannot enter at full weight.
6. **Power / N (A2 realism).** n = 93 is short of the order-hundreds needed for an edge claim across regimes. Extend N honestly: pool *within BTC across time* (more history), NOT across assets; and let forward events accrue. Report the confidence interval; if the CI straddles zero after costs, it stays CANDIDATE.
7. **Decorrelation (COMBINER §4).** Before it ever shares an ensemble, measure its per-trade return correlation with the second edge; |ρ|≥0.7 = one bet, not two.

### If it passes
→ ADMITTED as a **BTC** signal, emitted as a calibrated probability (Step-3 calibration), sized by fractional Kelly (≤¼) / vol-target — **read-only: the desk emits the view, the trader sizes it** (#22). Enters VCP-COMBINER-001 at equal-weight once a second decorrelated admitted edge exists.

### If it fails a gate
→ Logged as a graded MISS with the failing gate named (not buried). The excursion observation still informs the P2 liq-map work (does an approaching liq-cluster explain *which* reclaims run?) — that's the forward-only frontier, tested separately.

### Frontier that could BECOME the second edge (forward-only, not yet gradeable)
The collector's P2 layer (HL ground-truth liq-map + HLP inventory, filling from 2026-08-15) — does an untapped liq-cluster ahead, or an HLP inventory tilt, add *independent* information to the reclaim? If yes and decorrelated, it's edge #2 and the combiner switches on. Until there's enough forward data, it is descriptive only.
