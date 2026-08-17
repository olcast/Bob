# HL-OPS CALLS LEDGER — live Gmail primary, as pasted by Olivier 2026-08-17 08:33 UTC

Version at paste time: **v3.2.20**, entries **#000–#084**, next ID presumably #085.
This SUPERSEDES the Drive backup (v3.1.1, #000-#059) previously read — that backup is now
2 major versions and 25 entries behind the real primary.

Confirmed structural facts from this paste:
- Primary source of truth = Gmail draft "HL-OPS CALLS LEDGER — machine-updated, do not send".
  Drive is fallback-only. Local reconstruction (skills-archive) is a third-tier snapshot —
  now confirmed stale on every version axis.
- Lineage since the v3.1.1 backup: #071 TRIAL LOG T-002/T-003 → #072 LATENT-FUEL doctrine →
  #073 INTERACTIVE + COVERAGE-GAP → #074 TRIAL LOG T-004/T-004b → #075 D7-LOG →
  #076 GROUND-TRUTH LIQ DATA + FORWARD COLLECTOR + T-004c line-excursion →
  #077 COMBINER (VCP-COMBINER-001 sealed) + DISCOVERY SWEEP (30 BTC-only trials, NULL) +
  PER-ASSET no-pooling rule + shallow-reclaim admission gate →
  #078 WASHING-MACHINE model confirmed + NO-RULES discovery + 2 robust decorrelated
  reversal edges (E2 resTL-reject, E4 poke-reclaim; N_eff 3) + MM/PATH lens →
  #079/#080/#081 SWING-DESK FIRING sequence (weekend BTC coil, "next 2 moves") →
  #082 D7-LOG (collector) mark 63,088 →
  #083 SWING-DESK FIRING (Sunday) — coil held ~13h, up-tilted (analog leg-1 60%) →
  #084 SWING-DESK FIRING + SUNDAY RETRO — coil held ~16h, hold/up sharpened
  (analog 60%, breadth 5/5 aligned), dn moved BELOW the 62k pool per candidate L1;
  retro 0/4 resolved (accumulating); skills v3.13-v3.20.

Full #077 entry text (COMBINER LAYER SEALED, DISCOVERY SWEEP null, per-asset rule, admission
gate) captured verbatim below for reference — this is the last full entry Olivier pasted:

> #077 — COMBINER LAYER SEALED + DISCOVERY SWEEP (30 BTC-ONLY TRIALS, NULL) + PER-ASSET RULE
> + ADMISSION GATE — 2026-08-15 ~13:20 UTC. Version v3.2.12 → v3.2.13. Interactive Opus
> session (OLIVIER-INPUT). Read-only; account untouched.
>
> COMBINER / ENSEMBLE LAYER (VCP-COMBINER-001 SEALED, sha256 14a75ca3...; doctrine #36).
> RenTec/Numerai METHOD not a magic signal: many weak decorrelated cost-surviving edges,
> blind-validated, regime-tested, ensembled; combined IR ~ IR_single x sqrt(N_independent).
> Frozen rules: admission gate (only ADMITTED, cost-surviving, continuous-calibrated signals
> weight); decorrelation is the point (|rho|>=0.7 = one bet; orthogonalise; report effective
> independent-bet count); weighting ladder equal -> risk-parity -> shrunk-IR -> meta-learner
> (promote only on OOS evidence); cost on AGGREGATE turnover; fractional-Kelly (<=1/4) under
> read-vs-holdability; scheduled re-fit + decay. STATE: 0 admitted -> equal-weight-of-one
> until a 2nd decorrelated admitted edge.
>
> PER-ASSET / NO-POOLING RULE (OLIVIER-INPUT, binding; #37a): BTC trades differently -
> never pool coins; a BTC signal is a BTC signal. Pooling manufactures fake edges.
> RETRO-FLAG: T-002/T-003 (#071) pooled BTC/ETH/SOL - the pooled-positive
> (depth->reclaim) superseded by the BTC-only reconfirm; pooled-negatives stay null.
> Both collectors already per-asset.
>
> DISCOVERY SWEEP = 30 BTC-ONLY TRIALS, 0 SURVIVORS (T-005 price + T-006 positioning;
> scripts/discovery_sweep.py, funding_sweep.py; excursion-graded +0.5%/-0.3%/5bp vs matched
> random control, OOS split). T-005 (27 cells, 1h/2h/4h): mean-reversion, momentum
> (NR7/Donchian), large-range, vol-spike, inside-bar - all net-negative after cost, none
> beats random OOS. T-006 (3 cells, 180d fundingHistory): funding/premium-extreme fade +
> funding-follow - null on BTC (funding pinned). Median MFE fine but only 37-59% reach +0.5%
> before the -0.3% stop vs the reclaim's 85%. Harness lesson: cost 5bp=0.0005 not 0.05
> (factor-100 bug, caught; the random control cancels it).

## Gap vs skills-archive/hyperliquid-ops confirmed by this paste
1. `discovery_sweep.py` and `funding_sweep.py` DO exist in the reconstructed archive
   (confirmed on disk) — good, matches T-005/T-006 tooling referenced above.
2. VCP-COMBINER-001 reference file exists on disk too (references/VCP-COMBINER-001.md) —
   need to confirm its sealed hash matches `sha256 14a75ca3...` quoted here.
3. Entries #078-#084 (washing-machine model, SWING-DESK FIRING cadence, D7-LOG collector
   readings, Sunday retro mechanics) are NOT yet reflected anywhere in the local archive —
   this is genuinely new doctrine content past what was reconstructed from claude.ai export.
4. Local archive's `THINKING-PROCESS.md` needs a pass to check it already encodes the
   washing-machine model / MM-PATH lens described in #078, or needs updating.

## Additional entries pasted 2026-08-17 08:33-08:38 UTC (continuing #077 tail + #078 full)

#077 tail — SHALLOW-RECLAIM reconfirmed BTC-only + ADMISSION GATE written
(references/ADMISSION-shallow-reclaim.md): n=93, med MFE +1.09%, reach +0.5% 85%
(OOS-stable train=test=85%), med MAE -1.42%; +0.5/-0.3 bracket ~breakeven-neg - the -0.3%
stop is INSIDE the -1.42% noise. Edge=excursion not chase. Gate pre-registers a tradeable
spec + A7/A5/A4/A6/R5/A2/decorrelation.
OLIVIER-INPUT TALLY: prior 2 HIT (#072,#074) + 1 framing-HIT (#076) / 1 MISS (#071) /
1 MISS-as-edge (#074); +1 HIT (#37a no-pooling). Hunt executed: honest 30-trial null,
0 false admits.
ENFORCEMENT (this session): trials T-005 (27) + T-006 (3) = 30 DISCOVERY; rules ADOPTED
2 (#36 combiner, #37a no-pooling); sealed specs 1 (VCP-COMBINER-001) + admission gate;
CONTESTED 0; ADMITTED 0.

> #078 - WASHING-MACHINE MODEL + NO-RULES DISCOVERY + FIRST ROBUST EDGES +
> ENSEMBLE/DECORRELATION + MM/PATH LENS - 2026-08-15 ~13:55 UTC (15:55 CEST).
> Version v3.2.13 -> v3.2.14. Interactive Opus session (OLIVIER-INPUT deep research
> block). Read-only; account untouched. Skills v3.13-v3.20 delivered for save.
>
> ARC (trials T-007...T-011; doctrine #38-#43):
> - T-007 ADMISSION (shallow-reclaim, #38): NOT admitted. 1h reclaim FAILS the
>   microstructure null (just a bounce off a swept low; adds no calibrated info); 4h
>   dip-entry@level->+1.0% marginal (regime-concentrated, dies at 25bp, n=62). The -0.3%
>   stop is refuted (inside the -1.42% MAE noise).
> - OLIVIER METHOD CORRECTIONS (all adopted, binding): grade by MAX excursion not fixed
>   time; strip COST in discovery (trader's biz); and DISCOVERY MUST NOT BE
>   STOPPED/INVALIDATED BY TRADING RULES - a stop is exactly what invalidates a pattern
>   that would have worked.
> - T-008 NO-RULES DISCOVERY (#39, discovery_excursion.py): removing stop/cost/bracket
>   surfaced REAL predictive content the bracket had hidden. vol-spike-FADE (5m/15m/1h),
>   shallow-reclaim (15m/4h, NOT 1h) - all reversal-shaped; momentum/breakout null.
>   Patterns are TIMEFRAME-SPECIFIC (don't pool TFs, cf. #37a). Reconciles the earlier
>   '30 trials 0 survivors' (that was under trading rules).
> - T-009 THESIS (#40, thesis_test.py): OLIVIER thesis (no stops - reversals off pokes -
>   trendline reject-for-continuation) SUPPORTED, 2 refinements - reversal is
>   LONG-BIASED (buy the down-poke; up-poke short does NOT reverse, BTC up-drift);
>   continuation is the REJECT not the rebreak (breaks tend to FAIL = traps).
> - #41 WASHING-MACHINE MODEL (market_structure.py) CONFIRMED: BTC mean-reverts (VR<1
>   falling with horizon, 0.99->0.90); trend legs retrace 20-37% ('comes back for it');
>   funding bleeds the counter-trend crowd during trends (slow, small). EXPLAINS why
>   every edge is reversal-shaped.
> - T-010 ENSEMBLE (#42, edge_ensemble.py): bootstrap-CI + 4-fold walk-forward CULLED 2
>   of 4 candidates -> 2 ROBUST survivors: E2 resTL-REJECT short (1h, walk-forward 4/4
>   positive) + E4 poke-low->reclaim (15m, CI90 [+0.040,+0.218] EXCLUDES 0).
>   Decorrelation EXCELLENT (avg -0.12, N_eff 3.0). KEY: equal-weighting the nulls HURT
>   (ensemble Sharpe +0.04 < best-single +0.10) - WEIGHT ONLY ADMITTED EDGES; the
>   COMBINER Sec2 admission gate proven with data.
> - T-011 MM/WHALE LENS (#43, mm_regime.py): the market engineers PATH not DIRECTION;
>   reversals are liquidity-grab footprints (SFP = whale filling size). Empirically the
>   edges are STRONGER after a trailing move than in a dead range - the move BUILDS the
>   offside leverage/stops, the reversal HARVESTS it (corrects 'fade noise in quiet
>   range'). Forward edge = SFP x true liq-map = whale-fill detector (collector-accruing).
>
> STATE: 2 robust in-sample-OOS reversal edges (E2 + E4), decorrelated (N_eff 3); 0
> ADMITTED (owe a pre-registered FORWARD/blind run + E2xE4 cross-clock decorrelation
> before weight). Combiner idle until the pair blind-validates. OLIVIER-INPUT this block
> = 5 HITs (max-excursion - no-rules-discovery - thesis - washing-machine - MM/path); the
> reframing moved the desk 0 -> 2 robust candidate edges.

### Key cross-check vs local archive (updated)
- `discovery_excursion.py`, `thesis_test.py`, `market_structure.py`, `edge_ensemble.py`,
  `mm_regime.py` ALL exist on disk in `skills-archive/hyperliquid-ops/scripts/` already -
  confirms the reconstructed archive DOES contain the T-007..T-011 tooling, even though the
  doctrine narrative (#38-#43, washing-machine model, E2/E4 admitted-pending status) was not
  previously known on this side.
- `references/ADMISSION-shallow-reclaim.md` exists on disk too - need to diff its content
  against the n=93/MFE+1.09%/MAE-1.42% numbers quoted here to confirm it's the CURRENT
  version and not a stale earlier admission-gate draft.
- Real open item per #078: E2 (resTL-reject short, 1h) and E4 (poke-low->reclaim, 15m) are
  ROBUST but NOT YET ADMITTED - owe a forward/blind validation run. This is a concrete,
  checkable to-do against the live collector data already on hand.

## Continuation pasted 2026-08-17 08:35 UTC ("NEXT BLOCK" backlog item + #079 full)

**NEXT BLOCK (OLIVIER-scoped, NOT YET BUILT)** — explicit outstanding build item from the
primary itself: add **HL SPOT BTC + CVD** (`orderflow.py`) — spot<->perp lead/lag &
divergence; **trader-PROFILING by address/size** via HL's per-address transparency to
isolate the CONTRARIAN/loser cohort (buy-highs/sell-lows) to FADE. Framed by Olivier as
"the decorrelated positioning family; the deepest use of the mine Renaissance never had."
-> This is a concrete build target. `orderflow.py` already exists on disk in the local
archive - need to check whether it already covers spot<->perp lead/lag, or whether this is
genuinely unbuilt and the next thing to construct.

ENFORCEMENT (this block): trials T-007-T-011 (5); doctrine #38-#43 (6, all
DISCOVERY/method); process rules ADOPTED 3 (no-rules discovery - grade path-not-direction
- weight-only-admitted); candidates ADMITTED 0; robust survivors 2; blind audits 0
(mechanical).

> #079 - SWING-DESK FIRING (weekend, on-demand) - GRADE #29/#49 -> EVOLVE -> NEXT 2 MOVES
> - 2026-08-15 16:00 UTC (18:00 CEST, Sat; weekend thin-book decoupling binding). Version
> v3.2.14 -> v3.2.15. Scheduled Fable/Opus firing. Read-only; account untouched.
> CONTINUOUS read - evolves the 14:00 UTC read (#29/#49), does not restart.
>
> PRICE: BTC 63,074 @ 15:58 UTC (was ~63,015 @ 14:00 -> essentially FLAT over ~2h; the coil
> held).
>
> MACRO GATE: CLEAR-for-BTC. macro_preflight VOID on HYPE +2.02% ONLY - semi-independent
> alt (#51), no dated macro story (search = price-prediction spam), and an UP move does not
> contradict a BTC-flat/coil thesis -> logged as idiosyncratic ambiguity (#6), not
> thesis-breaking. BTC +0.17%, ETH +0.17%, SOL/majors flat; energy/gold/indices quiet.
> Catalyst calendar: NO tier-1 inside 72h; tripwires = FOMC minutes ~Wed Aug 19-20 +
> Jackson Hole Aug 27-29 (Warsh's first as Fed Chair). Weekend = scenario, not a sized call.
>
> GRADE (baseline = #29/#49 @ 14:00 UTC):
> - LEG-1 #29 up-leg-then-SFP-down ('push into 63.29-63.65k short-liq shelf -> SFP reversal
>   down 62.4k/62.0k'): NOT TRIGGERED, WEAKENED->near-dead. Price never reached the 63,290
>   shelf; it drifted DOWN toward the make-or-break instead. The required push-up first leg
>   is out of time (4h Fib-time now 34 bars = a turn is DUE). Unresolved; the up-leg premise
>   is fading.
> - MAKE-OR-BREAK ~63,000 (0.786 on BOTH 1h+4h): STILL LIVE, now being TESTED - px 63,075
>   sitting ON it; neither broken <62.8k nor accepted >63.65k.
> - #48 14:00 analog ('leg-1 coin flip, modal poke->rotate, real move waits on catalyst'):
>   HOLDING / partial-HIT - ~2h in, no $300 leg fired, coil intact (analog median 3h to
>   leg-1). No fake conviction paid.
> RUNNING: last gradeable directional call (#29/#49) still OPEN; leg-1 untriggered; no new
> resolution to bank this firing.
>
> THE READ (16:00 UTC):
> - WAVE (wave_scenarios): 4h retrace DEEPENED to 74% - PAST the .618 magnet (63,474) and
>   now AT the .786 (63,001). 1h .786 = 63,013. Both TFs CONVERGE ~63,000 = make-or-break,
>   price ON it. 4h Fib-time 34 bars -> turn DUE. The 63,474/63,500 magnet (4h .618 + liq
>   pool) is now ABOVE price - a push there is now COUNTER-TREND, no longer the base case.
> - POSITIONS (oi_flow): NEUTRAL vs oracle (prem -4.1bp, excAPR 0.0%, turnover 0.21 = dead
>   weekend book; no prior snapshot on this box -> no dOI this run, said out loud). state_view
>   1h: basis +7bp / 75th pctile [PERP PREMIUM] + funding pctile 1.0 -> MILD perp-long lean =
>   an offside crowd to HARVEST on a break (#45). 4h CVD-slope -441 (selling into the zone).
>   basis<->funding +0.41 (one bet - not double-counted).
> - ANALOG (n=166; fingerprint coil eff 0.07 / range-pos 19% / ATR-compress 0.24): LEG-1 UP
>   52% / DOWN 48% = coin flip (median 3h); LEG-2 REVERSE 57% (after a down-leg 59%
>   reverse). Range-pos LOW.
>
> EVOLUTION vs 14:00: up-path (push to shelf) WEAKENED->near-dead (driver: down-drift + 
> Fib-time due); down-path STRENGTHENED mildly (driver: 4h CVD-, mild perp-long lean to
> harvest, retrace deepened past .618); make-or-break LEVEL-SHIFTED from 'watch, price above
> it' to 'price testing ON it now.'

### Key cross-check vs local archive (continued)
- Confirms the **CONTINUOUS-read discipline**: SWING-DESK FIRINGs explicitly EVOLVE the
  prior read rather than restart from scratch each firing - grading the prior call's
  triggers/invalidations first, THEN re-running the pipeline, THEN stating what changed
  and why. `THINKING-PROCESS.md` on disk should be checked against this pattern (step 8,
  "continuity/delta vs last read", already partially covers this per prior session notes -
  needs verification it matches this exact grade-then-evolve structure).
- Weekend-thin-book decoupling is treated as a first-class regime flag, gating call sizing
  ("weekend = scenario, not a sized call") - not currently an explicit flag anywhere
  identified in the local archive; worth checking `macro_preflight.py` / `check.py`.
- Idiosyncratic-alt-move handling (HYPE +2.02%, no dated story, doesn't contradict BTC
  thesis -> logged as ambiguity not thesis-breaking, doctrine #6) matches the VOID outcome
  observed in this session's own live macro_preflight.py run on HYPE +3.71% - consistent
  behavior, good sign the local script is doctrine-faithful on that specific gate.

## Continuation pasted 2026-08-17 08:36 UTC (#079's NEXT-2-MOVES delta + #080 partial)

> NEXT 2 MOVES (DELTA, from #079):
> - MOVE 1 - make-or-break resolution (~coin flip; direction NOT faked). Discriminator
>   level = ~62,800 (.786 floor / direct-break trigger). HOLD 62,800-63,000 -> down-poke
>   bought (#40 long-bias) -> counter-trend bounce to the 63,474/63,500 magnet (4h .618 +
>   liq pool). BREAK / hourly-accept <62,800 -> mild perp-longs harvested + 4h CVD- ->
>   62,400 then 62,000 (long-liq pool). Marginal lean DOWN-resolve ~52% (4h CVD-, perp-long
>   lean, deepened retrace) vs ~48% hold - a thin, honest coin flip; the LEVEL, not the
>   direction, carries the conviction.
> - MOVE 2 - leg-2 (washing-machine 57% reverse, #41). If MOVE 1 breaks DOWN to
>   62,400/62,000 -> expect a BOUNCE (down-poke bought; 59% reverse) back toward
>   62,800-63,000, NOT a trend start, ABSENT a catalyst. If MOVE 1 holds & bounces UP to
>   63,474/63,500 -> first impulse is often a FAKE (#49) -> reject / perp-premium
>   reject-short fade (#44/#45) back down, UNLESS it reclaims + accepts >63,474 -> 4h wave
>   RESUMES toward 65,475.
> - MAKE-OR-BREAK (the ONE level): ~62,800. Hourly acceptance below = down leg confirmed
>   (62,400->62,000); holding it keeps the coil / up-bounce alive.
> - TAIL (low-prob / high-significance): weekend thin book (turnover 0.21) + extreme coil
>   (ATR-compress 0.24) + Fib-time turn DUE + FOMC-minutes / Jackson-Hole regime approaching
>   -> a fast, OUTSIZED impulse on little volume can overshoot either target (weekend
>   decoupling). The DOWN-death (names the down per #25): a real break that ACCEPTS
>   <62,000 with no washing-machine bounce kills the up-bias and opens a larger down leg.
>   Low prob this weekend, high significance.
>
> ENFORCEMENT (this firing): scripts run - macro_preflight, wave_scenarios, oi_flow,
> state_view, analog (all read-only /info; account/positions untouched per house rules).
> 0 new trials; 0 new doctrine; blind audit 0 (firing, not research); CONTESTED 0;
> ADMITTED 0.

> #080 - SWING-DESK FIRING (weekend, on-demand) - GRADE #079 -> EVOLVE -> NEXT 2 MOVES -
> 2026-08-15 16:22 UTC (18:22 CEST, Sat; weekend thin-book decoupling binding). Version
> v3.2.15 -> v3.2.16. Scheduled Fable/Opus firing. Read-only; account untouched.
> CONTINUOUS read - evolves the 16:00 UTC read (#079), ~22 min elapsed, does not restart.
>
> PRICE: BTC 63,055 @ 16:22 UTC (was 63,074 @ 15:58 -> FLAT, -19; the coil held another
> ~22 min).
>
> MACRO GATE: CLEAR. macro_preflight no VOID (HYPE +1.93%, back UNDER the 2% gate;
> semi-independent alt #51, an up-move does not contradict BTC-flat/coil). BTC -0.06%,
> ETH -0.01%, SOL -0.20%; energy/gold/indices quiet; DXY/VIX stubs. Catalyst: NO tier-1
> <72h; tripwires = FOMC minutes Wed Aug 19-20, Jackson Hole Aug 27-29 (Warsh). Weekend =
> scenario, not a sized call.
>
> GRADE (baseline = #079 @ 16:00 UTC):
> - #079 MOVE-1 marginal DOWN-resolve (~52%): NOT TRIGGERED, now WEAKENED / CONTRADICTED.
>   Price did NOT break <62,800; it HELD ~63,000 and the 5m turned to HIGHER HIGHS +
>   HIGHER LOWS above the make-or-break (highs 63034/63035/63112, lows 63002/62967/63006).
>   The #52 5m-reconcile rule fires: #079's down-lean was micro-blind and is fading.
> - MAKE-OR-BREAK ~63,000 (0.786 both TFs): STILL LIVE, HOLDING. px 63,055 just above it;
>   neither <62,800 nor >63,650 accepted.
> - ANALOG leg-1 FLIPPED to UP 55% (was DOWN 52% @ #079) - the coin flip tilted marginally
>   UP.
> RUNNING: #29/#49->#079 directional call still OPEN; nothing resolved to bank (~22 min,
> coil intact). No fake conviction paid.
> [continuation pending — THE READ / NEXT-2-MOVES / ENFORCEMENT for #080 not yet pasted]

### Note on discovered mechanism: #52 5m-reconcile rule
Entries #079->#080 show a concrete, valuable doctrine item in action: a HIGHER-timeframe
lean (4h CVD-, retrace depth) gets explicitly checked against the 5-MINUTE tape every
~20-30 min during a live firing, and if the 5m structure contradicts the HTF lean (higher
highs+higher lows here), the lean is flagged WEAKENED/CONTRADICTED rather than held
stubbornly. This is exactly the anti-narrative-capture behavior the hostile reviews said
was missing (Truth-Decay/co-narration risk) - worth confirming `pulse.py` on disk already
implements this 5m-vs-HTF reconcile check, and if not, that's a concrete gap to close.

## Action
Treat this file as a running append-only local mirror. Whenever Olivier pastes more of the
live Gmail draft (older entries #000-#070, or new ones past #084), append here with the
same version/entry-id bookkeeping, so the local side never silently drifts from primary again.
