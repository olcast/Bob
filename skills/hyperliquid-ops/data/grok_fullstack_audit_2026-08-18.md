**Round-1 was a caricature of a caricature.** Several “missing pictures” are already named, scripted, or half-wired. The real holes are narrower, meaner, and mostly *seams*: sensors that exist in the human read never reach the originator packet; the judge grades a different object than doctrine claims is the edge; the hypothesis generator searches a different market than the desk trades.

No price. No direction. No new religion.

---

## 1. Inventory — what I wrongly called missing

Credit the stack. Do not re-list these as gaps.

| Round-1 claim | What is actually wired | How far it really goes |
|---|---|---|
| Premium–oracle | `oi_flow.py`: premium in bp, 3-day hourly, **±4bp = fair**. Funding demoted to a *price*; crowding is premium. Excess APR vs **universe-median** baseline (~10.95% / 5.475%), not raw funding. | **Level, not residual.** Printed funding, not `predictedFundings`. No \(d(\text{premium})/dt\), no carry identity, no HL−CEX. |
| OI vs price as path | Explicit rules: OI↑+price↓ = new shorts; OI↓+price↓ = long liq. Snapshot in `~/.hyperliquid-ops/oi_state.json`; says when Δ is unavailable. | One hand-written copula cell. Not a library, not a residual. |
| Absorption / sequence | `orderflow.py`: heavy one-sided vol + **below-median range** = absorption; price extreme *after* CVD extreme = exhaustion; \(\lvert\Delta\%\rvert\gtrsim 30\%\) = control; print-count honesty mandatory. | Qualitative cousins of markout/λ. No horizon curve, no Kyle λ, no VPIN. |
| Bandwidth | `assemble_brief._four_dims`: 5bp bid/ask **size + order count + bid_weight%**. | **Stock at one radius.** No slope, convexity, multi-band, refill τ. |
| HLP / whale | `oi_flow.py` pulls HLP inventory and whale net. Books \(<\$10\text{M}\) OI suppressed (one-participant filter). | **Stocks.** No quote-response, no refill~HLP, no uPnL-path. Whale net is at best a *single* size bucket. |
| Joint state | `state_view.py` relationship matrix (“don’t double-count”). `analog.py` = empirical analogue / base rate. Pulse: vol/CVD → hold; **accelerating efficiency** → break/fake. | Principle + one analogue search + one efficiency adjective. No vector residual, no path lexicon, no tail-dependence. |
| Cross-asset factor | `cross_asset_snapshot.md`: 24h breadth, 1h β, 1h corr, named decoupling. Routing by **turnover** \(V/\text{OI}\) (tape vs positioning). | Daily/hourly, crypto-vs-xyz. **Not** same-contract cross-*venue*. Not 30s–5m residual. Not info-share. |
| Liq-fuel | Liq-map magnet; doctrine asks “does it sit on a Fib?” Stops-beyond-magnets = cascade (finding #4). | Stop *locations*. Not cost-basis, not underwater mass, not pain gradient. |
| Learning / rates | `state.json` is SoT for live call + `base_rates`. SCORE → `calibration.py` (Brier, sweep-then-right, kill n≥30). `discovery_loop.py` proposes. Human SAVE is the gate. | Loop *exists*. What it can *see* is one metric. See §3. |
| Efficiency / vol geometry | Named in `pulse.py` (“accelerating efficiency”). | An adjective on a 2s adjudicator. No RV, BV, jump-share, vol-of-vol, volume-time ER. |
| Macro / session | VOID/CLEAR gate, inbox+disconfirming search, session-gap catch-up, US-open awareness. | Clock as *calendar*, not as a residual. |

**Also already present, which round-1’s 6-bullet summary hid:** wave/Fib *enumeration* (not assertion); close-only entries/tripwires; nested-vs-exclusive scale rule; entry-as-clock (falsifiability); two-family producer/challenger + degraded-independence flag; R-fiction on xyz; narrative-vector collapse; sample-size speech; “mechanism > fit”; trial-count as denominator.

Round-1’s #3, #6, #8, #9, #10 were **over-claimed**. The desk is not a four-number dashboard. It is a two-tier system: a *rich human read* (`oi_flow`, `orderflow`, `pulse`, `analog`, `state_view`) and a *thin fire packet* (`assemble_brief` §0/§0b). That split is the first real finding.

---

## 2. Real gaps — what the current files still cannot see

These remain genuine. Cheap column = HL public already in the scope note.

### Still blind (sensors)

**A. Tape *mix*, not tape *sum*.** `orderflow` nets signed volume and flags absorption via range. It cannot see 400 clips vs eight whales, HHI of the last N prints, or print-to-tick *by bucket*. Whale net is one threshold, not a mix. CVD-up + price-up is still tautological once you leave the 90s window.

**B. Liquidity-as-process.** 5bp size is in §0b. Missing: 1/2/5/10/25bp vector, log-slope, convexity, bid−ask slope gap, **sweep-refill half-life**, cancel/replace flicker, microprice−mark−oracle triad. Finding #4 (stops beyond magnets cascade) is a *static* venue fact. You do not measure whether *this* book will cascade in the next 800ms.

**C. Impact / markout / toxicity.** No \(\lambda\), no +1s/+5s/+30s/+5m size-weighted markout, no VPIN-on-volume-clock, no \(\lambda_{5s}/\lambda_{60s}\). Pulse’s hold-vs-break is exactly this decision, made with CVD + “efficiency.” Absorption (vol vs range) is the right *family* and the wrong *estimator*: it cannot tell “eaten and will revert” from “informed and will keep the tick.”

**D. Cost-basis / uPnL surface.** Liq map ≠ inventory opened-at. Same OI at the same mark is inert or nuclear depending on distance-to-pain × size × time-held. HL can proxy this from tape + OI-Δ attribution. You do not.

**E. Arrival / clock residual.** Volume and vol-ROC are aggregates. No inter-arrival, no Hawkes \(\alpha/\beta\), no run-length CDF, no volume-time resample, no TOD-seasonal residual. Session opens are watched; seasonality is still constantly promoted to signal. `assemble_brief` velocity is a 90-minute % change on six 15m closes. That *is* the diffusion mental model.

**F. Predicted-vs-printed funding and basis identity.** You watch premium *level* and funding *excess*. Unused: `predictedFundings`, \(d(\text{premium})/dt\) vs printed vs predicted, HL mark − CEX-index \(z\), carry residual \(\text{funding} - \text{basis}/\text{horizon} - r_f\). Doctrine already says funding is the slow tax and premium is the crowd. When they disagree, you cannot see it.

**G. Jump geometry.** No RV, no bipower, no \(J = 1-\text{BV}/\text{RV}\), no vol-of-vol, no term structure. Pulse “efficiency” is not this. Perps die in jumps (liq, oracle, venue). Velocity/accel will keep under-reading the next 60–180s on every discrete event. Calibration’s sweep diagnostic is a *cousin* (wick-through) scored *after the fact* on 5m candles — not a live jump detector.

**H. Micro residual vs BTC / info-share.** Snapshot β is 1h on 3672 bars. Missing: 30s–5m residual on volume-time, 100–500ms lead-lag, \(\lvert d\beta/dt\rvert\). 24h breadth already shows BTC+SOL vs ETH/SPX/NDX decoupling; you then read name-local OI/CVD as if the factor question were settled.

**I. HLP as a *process*.** Inventory is pulled. Missing: conditional response of mid over 30–90m to HLP Δ, spread/skew as a function of HLP *path* (not level), refill \(\tau\) regressed on HLP. When the house is the 5bp, their inventory cycle *is* bandwidth. You own the data; §0b emits bid_weight and never mentions HLP.

**J. Systematic path-objects.** You have one cell (OI vs price), a relationship matrix, and `analog.py`. Missing: vector residual of \(\{\Delta p, \Delta\text{OI}, \text{funding}, \Delta\text{CVD}\}\), a path lexicon with successor *distributions*, copula tail \(P(\Delta\text{OI ext}\mid\Delta p\text{ ext})\). “OI fell on 6× volume” was a one-off insight, not a library.

**K. Concentration / cross-margin graph.** Still absent. \(<\$10\text{M}\) OI suppression is market-level, not within-BTC top-N / isolated-vs-cross / collateral overlap. Semi-costly; still the highest-Sharpe *positioning* layer HL uniquely offers. Not first.

**L. Same-contract cross-venue.** Cross-*asset* ≠ cross-*venue*. No \(z(\text{HL}-\text{BIN mid/funding/OI-}\Delta)\), no depth-share, no first-to-move on jumps. HL-only tape can describe an island. Cheap-external. Not wired.

**Costly, still correctly deprioritized:** Deribit GEX, ETF creations, CEX on-chain, social, TradFi flow.

### Still blind (architecture — these are not sensors, they are why sensors don’t matter)

**M. Originator starvation.** `assemble_brief._four_dims` participation is “last 15m vol ≷ mean of the previous five.” That is not `oi_flow`. Live venue block is mark / OI / funding. HLP, whale, premium path, CVD, absorption, liq-map, turnover, analog base rates — **absent from the fire packet**. Doctrine tells originators to read `state.json` for rates; `_current_call_facts` extracts zones/dirs/kills and **explicitly drops** `base_rates` and every verdict. If the wrapper only points at `brief_context.md`, the SoT is a rumor.

**N. Zone injection is an independence leak.** “Past-as-prior, never past-as-anchor” + “facts not conclusions” — then the packet ships `move1/2/3_zone` and `move*_dir` from the *previous* live call. Zones are last round’s conclusions about structure. Fresh mid + stale geometry is an anchor with a timestamp.

**O. Mechanism is not graded.** SCORE is \(\{ts, h, up, dn, p_{up}\}\). `resolve()` is first-touch on BTC 5m highs/lows. Doctrine’s falsifiable bar is “continuation on expanding OI” (etc.). A target hit on *falling* OI is Brier-right and doctrine-wrong. The only proof of edge cannot see the thing you say is the edge.

**P. `discovery_sweep.py` is a competing epistemology.** It searches z>2 fade, 4-consec, NR7, Donchian-20, large-range follow/fade, vol-spike, inside-bar — candle patterns, BTC only, +0.5/−0.3/5bp, vs random, OOS. It does **not** test OI↑price↓, premium-outside-4bp, absorption-at-level, 5bp bid_weight extremes, HLP lean, breadth divergence. Doctrine #46 is mechanism > fit. This script is pure fit. If a Donchian cell ever lands in `lessons.json`, the desk will have promoted a theory it claims not to hold.

---

## 3. Loops and graphs — well-formed on paper, broken at three seams

### What is well-formed

- Forward-only auto-resolve. No self-grading.
- Brier vs a written baseline. Kill-switch pre-committed at n≥30.
- Sweep-then-right as a *named* failure mode, feeding a candidate (L1: draw invalidation below the pool). That is the only place the loop’s object matches a real desk wound.
- Propose ≠ promote. Human SAVE is the anti-overfit gate. Honest null is an allowed output.
- Shared `resolve()` between calibration and discovery. One outcome definition.
- Stateless originators + fire-time assemble: right instinct for “amnesiac originator.”
- Contribution scoreboard is governance, not an agent reward. Correct #56 instinct.
- BTC-only in sweep (no pooled fake edges). Trial-count printed.

### Seam 1 — the judge’s object ≠ the doctrine’s object

`calibration.resolve`:
- Hardcoded `coin: BTC`. xyz / ETH / SOL calls are ungraded or mis-graded.
- Neither target touched → `first='dn'`, \(o=0\). “Nothing happened” is scored as down-won. Patient/range/stand-down calls are structurally punished. Move-1 “observe only” cannot even enter this judge cleanly.
- Same-bar both-touch uses a close-vs-midpoint heuristic. Fine for a v1; not a microstructure clock.
- Sweep depth is in *dollars*, useful — and unused anywhere except a print line.
- **No field for the mechanism bar.** OI, funding, premium, CVD, HLP never enter \(o\).

`discovery_loop.evaluate` auto-handles **one** metric: `swept_then_right_rate`. Every other lesson returns `INSUFFICIENT` / “track by hand at the retro.” The promotion bar of “5 forward supporting calls” is **not implemented per lesson**; the one auto-path uses a *global* swept-rate. So the loop cannot do what SOP §3b says it does (grade disagreements, grade reasoning-improvements, retire stale rules by forward evidence). It can do L1. Everything else is theater with a JSON schema.

### Seam 2 — discoveries do not reach the brief

SOP path (claimed):

`calibration` → `discovery_loop` → Olivier SAVE → `doctrine.json` / `SKILL.md` → next assemble.

Actual fire-path inputs (`assemble_brief.py`): SOP prose, `state.json` **zones**, `brief_facts.md`, `macro_gate_resolved.md`, `cross_asset_snapshot.md`, live mid/OI/funding, skinny four-dims.

**Not in the packet:** `lessons.json`, KG, `backtest_rates.json` (except a warning to cap at one line), `oi_flow` snapshot, `orderflow` snapshot, analog rates, HLP, premium history, SCORE calibration state, sweep-rate, discovery survivors.

KG (`17e 21r`): VCP, providers, Olivier, desk, four-dims *as a concept* related to “immutability ≠ correctness.” It does not hold promoted lessons, analog rates, venue findings as live objects, or any sweep/Brier number. SOP still says “the store is currently EMPTY” in one place and the summary shows 17 nodes in another — even the graph’s self-description is stale. **Read-KG-every-session is not in the assembler.** The graph cannot capture what the loops discover because nothing writes discoveries *into* it, and nothing reads it at fire time.

Three rate stores: `state.json:base_rates`, `backtest_rates.json`, `analog.py` output. Provenance rule (`{rate, n, source}` or reject) is correct and is not mechanically enforced on the originator packet.

### Seam 3 — circular / untested doctrine (flag, don’t soften)

1. **Immutability ≠ correctness, applied at home.** The fire packet is a receipt. §0b’s four-dims are a caricature of the four-dims the KG treats as canonical. You will stamp a wrong read with a perfect timestamp. That is the VCP gap you already filed on Knight/Citigroup, aimed at yourselves.

2. **Zones-as-facts.** Injecting `move*_zone` / `move*_dir` while forbidding “prior verdicts” is a word game. Structure *is* the last verdict.

3. **Elliott mandatory + “admissible only as falsifiable scenarios” + mechanism > fit.** Three constraints. In a 2-move brief they collapse to a count that cannot be graded by `calibration.py`. Untested ceremonial section.

4. **Macro VOID (≥2% any flagged mover, no named story) can freeze the desk.** Frozen desks produce no SCORE tags. The kill-switch never sees the regime where the gate is most active. Selection bias on the only judge.

5. **p_base = 0.5.** Session drift, liq-magnet geometry, and “neither = down” mean the naive baseline is not naive. Skill vs a wrong null is not skill.

6. **Bounded independence** is filed as critical knowledge, then fallback *explicitly* allows same-model self-challenge. The flag is honest; the graded sample will mix independent and degraded runs unless `fallback:` is a first-class split in calibration. It is not.

7. **Move-3 protocol is empty checkboxes** next to a live path_b_terminus. The desk named the “decide at the level under adrenaline” failure and has not closed it. Process theater.

8. **R-fiction and cascade-stop physics** live in `brief_facts.md` (good) and do not live in `resolve()`, sizing code, or a live bandwidth process. Known, not measured, not graded.

9. **“Positions, not funding”** then §0b emits `funding_pct_h` as “velocity of carry” and does not emit premium or ΔOI. The assembler disagrees with the skill.

10. **Discovery survivors have no pipe into `lessons.json`.** Sweep cannot pollute doctrine today only because nothing connects them. That is a missing wire, not a virtue. The moment someone pastes a SURVIVES line into the lab notebook, #46 is dead.

**Net:** the learning loop is well-formed as a *sweep-rate machine for invalidation geometry*. It is not well-formed as a general recursive desk. The graph is a staff chart plus a philosophy footnote. Hard-won lessons leak at SAVE→assemble (rates, HLP, premium, CVD, analog) and at evaluate() (every non-L1 lesson).

---

## 4. Confluence / combination / contradiction

Doctrine already says a single series forecasts nothing. Keep that. Re-state against **named** variables only: OI / ΔOI, funding excess, printed funding, premium (mark−oracle), CVD/Δ%, liq-map magnet, 5bp size + bid_weight + n, mark/oracle, HLP inventory, whale net, 24h breadth, 1h β/corr, turnover \(V/\text{OI}\), velocity / accel on 15m, pulse efficiency, absorption (vol vs range), sequence (CVD ext vs price ext), analog base rate, SCORE sweep.

### (a) Confluent pairs — raise conviction in a *state*, not a side

- **Absorption + sequence + 5bp holding + turnover routing.** Heavy one-sided CVD, range below median, price extreme *after* CVD extreme, 5bp size not evaporating, and \(V/\text{OI}\) tells you whether this window is even legal evidence. That is pulse CONFIRM-hold with its sample-size speech attached. Existing pieces; not one emit.

- **ΔOI sign vs price + premium outside ±4bp + funding *excess* same sign.** New inventory + a real crowd + a tax that has actually left the IR baseline. Crowding as *fuel*, which is already doctrine — only when all three agree is the fuel live. Premium inside ±4bp nullifies the funding read (you already teach this; originators may not see premium).

- **Liq-map magnet sitting on an enumerated Fib/wave level + turnover \(<~0.4\).** Positioning magnet, tape is noise. Your own routing rule. The confluence is “this level is a stock of people, not a flow event.”

- **HLP inventory lean + 5bp bid_weight extreme + n small.** House *is* the bandwidth. 5bp “OK” is a single desk’s quote. Finding #4 becomes conditional: cascade is what happens if *that* inventory flinches.

- **24h breadth divergent (BTC/SOL vs ETH/SPX/NDX) + 1h β(SPX,NDX) weak.** Local OI/CVD/premium describe *crypto-idiosyncratic* positioning. Macro-named story in `macro_gate_resolved.md` is context, not confirmation. This pair is already in the snapshot; it is not wired to suppress name-local reads.

- **Velocity decelerating (accel_pct < 0) + vol_trend contracting + sequence exhaustion.** Diffusion read of “move dying.” Valid only if jump-share is low (you cannot yet know) and 5bp did not just refill after a sweep (you cannot yet know).

- **Sweep-then-right elevated + invalidation sitting on the liq-map magnet.** The loop’s one real result plus finding #4. State = “our death-price is on the wrong side of physics.” Direction-free. Highest-conviction confluence you can already compute.

- **Analog coin-flip + OI-vs-price and wave enumeration *agree*.** Your written tie-break. If they *disagree*, the confluent object is “stand down” — not currently a first-class state.

### (b) Composite signals no single dimension contains

- **Hold-vs-break object (pulse, completed).** \(\mathrm{CVD}\) direction × absorption (vol/range) × sequence (timing) × 5bp persistence × turnover-legality × (missing) markout curve. Today pulse approximates this with CVD + “efficiency.” The composite is the desk’s actual 2-second product.

- **Fuel-vs-crowd object.** Premium (crowd *now*) × ΔOI-vs-price (whether inventory is being *added*) × funding *excess* (whether the tax has moved) × liq-map distance