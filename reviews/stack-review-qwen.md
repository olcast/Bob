# FULL-STACK REVIEW — Olivier's Hyperliquid Trading Ops
**Reviewer:** Qwen 3.8 Max (qwen/qwen3.8-max), subagent, read-only audit
**Date:** 2026-08-18, work performed 08:14–08:35 UTC
**Scope:** skills/hyperliquid-ops (SKILL.md, references/, scripts/, data/), ledger, cron, live HL API. No orders placed or modified. No files in the skill modified.
**Method:** SKILL.md + references/THINKING-PROCESS.md read top to bottom first; THE READ executed for the market section (Step 0 macro gate FIRST, per task and doctrine); scripts run live; data files inspected line-by-line.

---

## EXECUTIVE SUMMARY (blunt)

1. **The doctrine is genuinely good and internally coherent** — the best anti-overfitting governance I've seen attached to a retail-scale trading desk (mechanism>fit, trial-count denominator, forward-only validation, kill-switches, read⊥holdability). Its #53 self-audit ("discipline framework, alpha FROZEN") is honest and still the correct self-description.
2. **The grading loop is currently broken — and it is the single most important thing on the desk.** `calibration.py` runs against `data/calls.json`, which holds **exactly 1 call** (committed 2026-08-17 10:49 UTC) because resolved calls were pruned (git commit 1315a44) to stop notification spam. Matured SCORE tags exist in the ledger text (I resolved two live: one swept-then-right, one hit) but **nothing is feeding them to the judge**. The desk's "only proof of edge" is presently grading a sample of n=1.
3. **The data pipeline is stopped.** All hlops crons were disabled 2026-08-17 (cost directive, ledger #094). Last collector tick: **2026-08-17 20:27:54 UTC** (~12h stale at review time). Only one cron exists (`HL BTC price-level watch`, every 30m), and it has **never run** (`Last: -`). Forward-only data (liq-map, HLP, addressbook) only accrues if something runs — right now nothing does.
4. **The account section (extracted because the task explicitly required it) contains a red flag the desk's own research predicts:** a **40x cross BTC SHORT**, entry 63,618, liq 64,772.30 (**0.90% from mark at review time**), uPnL −$451 on a **$1,084 account**, liquidation sitting almost exactly on the 4h .786 break (64,778) that the desk's own scenario tree names as the squeeze-path tripwire. Per doctrine #22 I do not issue the flip and the market read below was written blind-first; but the hand-off rule (#9) requires saying it plainly: **the live book and the desk's own alternate path are adversarially coupled.**
5. **Market read (gate resolved, tape-first per Olivier's standing instruction):** BTC 64,178 (08:16 UTC) is resilient (+1.2% 24h) *through* a risk-off Asia/oil session; shorts are paying (excess funding −14.5% APR, premium −5.0bp, OI flat). That is denied-exit-liquidity setup, but it only becomes a squeeze on an **impulsive acceptance >64,778**; the pulse at 08:18 UTC is split (1h CONFIRMING, 5m FADING) = AMBIGUOUS on the line. Committed path: Move 1 push into 64,350–64,780 (~55%), Move 2 conditional rejection back toward 63,500 (~55% conditional) vs impulsive break to 65,475 (~45% conditional). Details + tripwires in §5.

---

## 1. SKILL / DOCTRINE HEALTH

**Size & structure.** SKILL.md = 979 lines / 142 KB, doctrine versions v2.3 → v3.35 + two August-17 amendments ("2 moves = PATH not FORK", "ON THE LINE discipline"). references/THINKING-PROCESS.md = 105 lines, coherent, matches the SKILL's THE READ summary.

**Verdict: coherent, but rotting at the edges.**

What checks out:
- THINKING-PROCESS.md steps 0–8 map 1:1 onto the SKILL's THE READ 0–7 + step 8 capture duty. The ordering (macro gate → wave frame → positioning → joint state → RoC adjudication → analog repro → commit → continuity → capture) is internally consistent and each step names its script and its doctrine number. I executed it end-to-end this morning and every step had a live tool that produced sensible output.
- Cross-references resolve: L1 lesson ↔ #089 ledger fix ↔ current_call.json invalidation text (61,800 below the 61,821–61,976 pool) are all mutually consistent. The #092 call_evolve bug (Move-2-progress-as-primary) **has been fixed in code** — `call_evolve.py` lines 146–162 now read `move1_dir`/`move1_zone` and emit `STRENGTHENED_ALT_PATH` (visible in the last call_evolution.jsonl row). Ledger said "STANDING FOLLOW-UP (not yet fixed)" — it is fixed; the ledger line is stale.
- All **40 scripts compile clean** (`python3 -m py_compile` sweep, zero errors) and every script I ran (macro_preflight, oi_flow, wave_scenarios, structure, pulse, analog, state_view, cross_asset, calibration, discovery_loop, leaderboard, hl_ops) executed without crash against live data. HL API reachable (0.3s, 232 universe entries).

Real problems:
- **Stale entry:** ledger #092's "not yet fixed" follow-up (see above).
- **Document sprawl is a liability, not an asset.** 979 lines of append-only doctrine with 59+ numbered rules, 35 version deltas, and no index. A fresh agent (every firing is stateless) must load ~142 KB before doing anything; token cost and comprehension risk both grow monotonically. Nothing is ever retired — even REJECTED findings stay in full prose. Recommend a tiered split: ≤150-line OPERATING CORE (THE READ + house rules + self-check + frozen-thesis scope guard) + archive for the trial history. The trial history is valuable *as evidence*, but it should not be in the hot path of every firing.
- **Step-numbering drift:** THE READ in SKILL.md lists steps 0–7 (with "8 capture" implied), THINKING-PROCESS.md lists 0–8. The "Amendment — 2 next most probable moves" references "THE READ step 6" and "#085 horizon-scope discipline" — #085 is a *ledger entry*, not a numbered doctrine rule, and nothing says so. Minor, but in a system this rule-dense, ambiguous citations cause real drift (the #089 incident was exactly a level that got re-pinned without re-applying a cited rule).
- **The skill_workshop overwrite bug (#091, twice on 2026-08-17)** is correctly documented as a standing check (in ledger AND TOOLS.md). The mitigation is procedural, not fixed upstream. Fine as-is, but every future apply carries a real clobber risk — the 2026-08-17 config-clobber trail in ~/.openclaw (`openclaw.json.clobbered.*`, 6 files across two days) shows this environment has a broader clobber pattern, not just this skill.
- **No contradictions found** between numbered rules, with one soft tension: #25b DEATH-PRICE GUARD (every multi-path thesis must name its down) vs the standing call's current state where both Path A (down-poke→reclaim) and Path B (squeeze) are up-eventual theses. The call does carry a death price (hourly acceptance <61,800), so it passes — barely. Worth re-checking every time paths get re-weighted.

---

## 2. DATA PIPELINE

Files: `scripts/collector.py`, `scripts/call_evolve.py`, `data/calls.json`, `data/call_evolution.jsonl`, `data/addressbook.json`, `data/collector.jsonl`.

**collector.jsonl** — 152 rows / **38 ticks**, 2026-08-17 09:05:51 → 20:27:54 UTC. Kinds: market 38, book 38, hlp 38, liqmap 38, **liqevent 0**. BTC-only (per doctrine #52 compaction-aware rewrite). All rows parse; no corruption. Tick spacing min 0.02h / max 1.38h — this is not a 20-min schedule, it's ~3–4 runs across the day (consistent with manual/interactive collection after crons died).

Anomalies & flags:
- **Pipeline is stopped**: last tick 20:27:54 UTC Aug 17 = ~12h before this review. doctrine #34(d) is explicit: the liq-map/HLP/addressbook are **forward-collect-only** — "the sample only exists if we record it." Every hour nothing runs is data permanently gone. The VCP-ABLATION P2 layer (#28) and blow-ratio/trick-EV calibration (#13) are accruing at ~zero.
- **liqevent = 0 rows.** Addressbook grew 150 → 280 addresses in the window, but no liquidation events were captured. Either the window was quiet or the event-harvest path never fired; at 280 addresses coverage is still thin (doctrine #49 itself flagged "46 addresses missed the 63,500 pool"). Not corruption — but the "ground-truth liq events" capability (#34b) is still theoretical.
- **liqmap sanity**: last tick (20:27 UTC) shows downFuel $76.6M vs upFuel $13.2M, fuelSkew −0.707 (long-liq dominated), biggest long cluster **61,761.6 ($38.3M)** — consistent with ledger #087's Coinglass 61,868 cluster. Note it also carries far-strike junk (12,223/$14.5M, 25,734/$11.4M) = ancient tiny positions; the ranked-top read is still correct but a consumer that doesn't sort-by-notional could misread it.
- `hlp` rows carry **no `coin` field** (the 38 coin-less rows are all `hlp`). By design (vault-level), but undocumented in collector-README — flagged.
- **No durable sink.** #34(d) warned "wire the sink before relying on accumulation" — collector writes local JSONL; the seed/ folder shows Drive-style exports were done manually (tick-*.jsonl, call-*.json seeds dated 08-15/08-16). Since crons died, no export has happened. If this host dies, the P2 sample dies with it.

**call_evolution.jsonl** — 73 rows, 2026-08-17 10:21:34 → 17:47:45 UTC, tracking 3 original calls (1786866352316 = 08-16 07:45; 1786871688457 = 08-16 09:14; 1786963783916 = 08-17 10:49). Status distribution: RESOLVED 39 / OPEN 34; conviction deltas: STRENGTHENED 7, CONTESTED_INTERNAL 3, WEAKENED 1, STRENGTHENED_ALT_PATH 1, UNCHANGED 22. Internally consistent with the ledger narrative (the 16:00 "72% toward up target" misreport → #092 → the final ALT_PATH row). **The tracker worked well; it is also now stopped** (last run 17:47 UTC; the open call matures today ~10:49 UTC with no tracker watching).

**calls.json** — 1 entry, matching `current_call.json` (ts 1786963783916, up 64,579, dn 63,001, p_up 0.56, h 24, by Claude, move1_dir down / move1_zone [62,499, 62,730]). Consistent. **But:** the pruning that left 1 entry destroyed the calibration input (see §3) — the fix for call-evolve spam created a grading-loop outage.

**addressbook.json** — 280 addresses with first-seen timestamps, all within 08-17. Sane, growing, persistent. Good.

**Verdict:** files are clean and mutually consistent; the pipeline is *designed correctly but not running*. This is an operational failure, not a data-quality failure.

---

## 3. LEDGER & GRADING

**Ledger.** references/ledger-live/LEDGER.md (git-tracked primary since 2026-08-17) holds entries #085–#094; full history #000–#084 in the two paste files. Append-only discipline visible in git log (commits 1315a44, 808b251 with explicit restore messages). Entry quality is high: #086 (silent direction flip, self-logged), #089 (Gemini coherence catching the L1 invalidation drift — verified against lessons.json before acting), #091 (skill_workshop clobber, twice), #092 (script bug caught by the user) — this is a desk that logs its own failures with timestamps, which is rare and real.

Problems found:
- **Duplicate entry: #093 and #094 are the same event** (same cross-check, same three model results nearly verbatim, timestamps 16:49–16:52 vs "16:52"), one labeled "post-cron-disable" and one "post-call, not blocking". Append-only means no deletion, but this should get a reconciliation line so a future reader (or the Gemini coherence audit) doesn't treat them as two independent cross-checks.
- **SCORE-tag custody is split and broken.** Step 6 says tags go "silently to the ledger"; the machine-readable home is calls.json; the actual matured tags live in HL-OPS_CALLS_LEDGER_...through-084.txt (2 tags: L215 `{"ts":1786859373553,"h":36,"up":63474,"dn":62800,"p_up":0.54}`, L262 `{"ts":1786871688457,"h":30,"up":63474,"dn":61900,"p_up":0.55}`). `calibration.py data/calls.json` reports **"0 resolved of 1 logged calls"**. I resolved the two ledger tags manually against live 5m candles:
  - L215 tag → **o=0, first=dn, swept_then_right=TRUE, sweep_depth $122** (dn tagged first, up reached anyway — exactly the L1 signature the SWEEP DIAGNOSTIC exists to catch).
  - L262 tag (#084) → **o=1, first=up** (clean hit).
  Two datapoints is nothing — but they are *graded, matured, sitting in a text file the judge never reads*. **This is the single highest-priority fix on the desk.**
- **The Sunday retro machinery has never produced a verdict.** `leaderboard.py data/calls.json` → "0 resolved of 1"; `discovery_loop.py` likewise has nothing resolved to mine. doctrine.json `promoted: []` (correct — nothing has earned it). The governance loop (calibration → discovery_loop → leaderboard → Olivier's save) is fully built, correctly firewalled, and **starved of inputs**.
- No grading drift detected in what exists (frozen commits stayed frozen — #085 respected through #089/#093/#094, current_call.json carries the corrected invalidation without touching up/dn/p_up). The discipline is being kept; it just has no scoreboard.

---

## 4. POSITIONS & PnL

Fetched 2026-08-18 ~08:19 UTC via `hl_ops.py` (read-only /info). House rules normally bar this section; the review task explicitly required it, and the market read in §5 was produced **before** weighting anything against the book (read⊥holdability, #22).

**Account "Main" (0x496c…9Ef2):** account value **$1,084.01** · notional **$50,180.75** · margin used $1,254.52 · withdrawable $0.00.

| Coin | Side | Size | Entry | Mark (08:19) | Liq px | Lev | uPnL | Funding |
|---|---|---|---|---|---|---|---|---|
| BTC | **SHORT** | 0.78169 | 63,618 | 64,194 | **64,772.30** | **40x cross** | **−$451.12** (ROE −36.3%) | −$6.13 since open (−2.8% APR, i.e. currently receiving) |

**Distance to liquidation: 0.90%.** Bold-flagged per the report format's own rule (within 15%).

**PnL** (exchange-reported, includes realized+unrealized): day **−$672.34** · week **−$1,660.59** · month **−$6,869.25** · all-time **−$28,570.79** on $14.84M lifetime volume.
**Funding (3d):** net −$2.15 (paid $14.17 / received $12.03, 70 events, BTC only) — funding is noise next to the P&L swings; the bleed is directional, not carry.

Observations (facts, not a flip):
- The short's liquidation (64,772) sits within $6 of the 4h **.786 break level 64,778** (wave_scenarios, 08:18 UTC) and inside the desk's own Path-B tripwire zone (64,427–64,746 cluster, ledger #090). An impulsive squeeze acceptance there = liquidation. The desk's own red-team (#093) argued the squeeze fuel is insufficient — that argument is the only thing standing between this book and its liq price, and it is a *thesis*, not a fact.
- The desk's admitted research family is explicit: **poke-high→reject SHORT has NO content anywhere** (#40: "the SHORT mirror does NOT (null/negative everywhere clean). Buy the down-poke; don't reflexively short the up-poke"). A short entered at 63,618 into a coiling range with negative funding (shorts paying) is on the wrong side of every edge the desk itself has measured. I state this as a post-mortem observation about the *entry*, per house rules the disposition is Olivier's alone.
- PnL trajectory: −$28.6k all-time with current equity $1,084 and 40x leverage is an account in its endgame phase. Nothing about the desk's *analysis* quality says it should be trading this size; everything about the *sizing* says the book is doing the dying.

---

## 5. MARKET READ — BTC (deliverable per THE READ, Step 0 gate run first)

**0a — Macro gate.** `macro_preflight.py --thesis "BTC chop 62.5k–64.7k, down-poke-first primary, squeeze alternate"` at **08:16:56 UTC** → **VOID**, 4 movers ≥2%: Korea 200 −4.16% (HL), WTI +3.72%, Brent +3.16% (HL basis, ≈ real Brent ~$90.9–91.5), Nikkei −2.49%. Stubs correctly flagged (xyz:VIX 20.000, xyz:DXY 97.150 — not quoted).

**0b — Disconfirming search (neutral wording, searched to break the risk-off reading).** All four movers matched to named, dated stories:
- **Oil:** *"Brent settled at $90.87, up 2.65%; WTI at $84.50, up 2.55%"* (Business Recorder/Reuters, print 2026-08-18); driver: *"The 60-day deadline for the U.S. and Iran to negotiate a peace deal and reopen the Strait of Hormuz expired, with no agreement in sight"* + *"Trump threatens to bomb Oman"* (CBS News, 2026-08-18); *"Trump won't extend Iran ceasefire"* (CNBC, 2026-08-17); Tehran gives Washington *"a few weeks"* (India Today, 2026-08-18). De-escalation search found **no active off-ramp** — the ceasefire has *expired*, talks stalled. This is the exact story family that gapped the desk on 2026-07-26, inverted: then it was an unpriced pause; now it is an unpriced *resumption risk*.
- **Asia equities:** *"Asia shares decline as worries about rising oil prices outweigh boost from strong earnings"* (AP via KSAT, 2026-08-18); KOSPI *"slips below 7000… bond-yield jitters"* + Middle East tensions (Chosun Biz / IBTimes, 2026-08-18). Caveat per doctrine: HL Korea/Nikkei perps are thin off-hours venues; direction matches cash reports (Nikkei cash −1,150 pts/−1.66% per India TV), magnitude on the HL prints is venue-amplified.
- **Calendar (72h):** FOMC minutes Wed Aug 19 2:00pm ET (July 28–29 meeting; BofA: watching how many members "wanted a hike"); Jackson Hole Aug 27–29, Warsh's first keynote Aug 28; Sept 16 Fed decision 19 days out. No CPI inside 72h.

**Gate status: CLEAR** (every mover matched; stories pre-date or co-time the moves per doctrine rule 6). Named catalysts: Iran/Hormuz deadline expiry (live), FOMC minutes Wed.

**Tape-first per Olivier's standing instruction** — news is used only to check whether the wire contradicts the tape:

**0e/Step 2 — Positioning (oi_flow.py 08:18 UTC):** BTC 64,164, +1.20% 24h, OI $2,672M (ΔOI −0.3% vs 0.3h-old snapshot — flat), turnover 0.61 (tape marginally readable), **excess funding −14.5% APR** (raw −4.3% vs +10.95% dex baseline), **premium −5.0bp** (just outside the ±4bp fair band), 3d mean −4.4bp. Translation: **shorts have been paying for 3 days straight while price grinds up; OI is not capitulating.** Per #25 this is denied-exit-liquidity fuel — but latent fuel is unobservable; the doctrine TELL requires an **impulsive** break through resistance to claim it. ETH/HYPE: neutral (premium −4.7/−4.5bp, inside-ish, no crowd).

**Step 1 — Wave frame (wave_scenarios.py 08:18 UTC):** 4h leg A 65,475 → B 62,523; retrace **+56%**, zone .382 63,651 / .5 63,999 / .618 **64,347** / .786-break **64,778** — price is entering the decision zone *now*. Fib-time: 34-bar window 08-20 04:00 (next turn-due). 1h leg 63,650→62,523: **break confirmed** (>+.786 63,384) and Fib-time 89 bars = **turn DUE**. 5m: mixed/coiling (highs 64,226/64,418/64,326, lows rising 64,103/64,124/64,240) — reconcile rule: neither path may be called dead.

**Step 3/4 — Joint state + adjudication (state_view.py, pulse.py, structure.py, all 08:18 UTC):** trend +1.31% [mid], regime efficiency 0.28 pctile 0.74 [trending], basis +3.9bp [perp discount], funding pctile 0.08 (extreme low = shorts paying), no price-structure trigger armed on last closed bar. **ON THE LINE** (within 0.5% of the 64,418–64,635 structure cluster, score 154, 9 objects, 4 TFs): pulse split — **5m FADING/DIVERGING** (vol −88%, CVD sell-slope) vs **1h CONFIRMING/CONTINUATION** (vol +54% expanding, CVD +buy, accel +1,421). Verdict: **AMBIGUOUS** — stated plainly per the ON-THE-LINE amendment, not forced. Structure zones: below 62,498–62,711 (score 352 — the standing call's Move-1 shelf, intact); above 64,418–64,635 (154), 64,725–64,980 (102), 65,475–65,715 (142).

**Step 5 — Repro (analog.py 08:18 UTC):** state = efficiency 0.28, range-pos 81%, ATR-compress 0.46; n=390 analogs: **leg-1 UP 56% / DOWN 44%** (median 3h); **leg-2 REVERSE 67%** (70% reverse after up-leg1). The washing-machine base rate: the first $300 mildly favors up from here; the second $300 favors giving it back.

**0e — Confluence / divergence:**
- *Agree:* tape (+1.2%), positioning (shorts paying, no long crowd), and analog base rate all lean up-first; structure places the magnet cluster 64.4–64.8k directly above.
- *Disagree (the warning):* the macro wire is risk-off (oil +3%, Asia down, Hormuz deadline expired) and BTC is ignoring it. **When price contradicts the narrative, the price is right — until the narrative arrives as an event.** The asymmetric headline here is not more escalation (that's the consensus now) — it's either an actual Hormuz strike (gap down through everything) or a surprise extension/ceasefire renewal (oil unpairs, risk-on rip). BTC resilience through oil-up is strength; the same tape through a strike headline is the trap-door.
- *Tripwire:* **64,778** (4h .786 = liq cluster edge = the open short's liquidation). Below: 63,600, then 63,001.

**Continuity (#7):** vs the standing call (08-17 10:49 UTC, ledger #090→#093, 55/45 down-first/squeeze): elapsed 21.5h of the 24h horizon; Move 1's down-poke **never fired**; price migrated 63,579→64,178 into the squeeze zone. Path B has been gaining probability all session-by-session; as of this read it is the *de facto* live path. The frozen commit (up 64,579 before dn 63,001, matures ~10:49 UTC today) sits 0.62% below its up-target — it resolves HIT if the cluster breaks in ~2.5h, via the alternate path, while its primary leg never occurred. That is the path-vs-fork ambiguity in a live specimen.

### THE DELIVERABLE — 2 next most probable moves (sequential path)

```
Move 1 (near-term, ~55%): push continues into the 64,350–64,780 decision zone
  (4h .618 64,347 → structure cluster 64,418–64,635 → .786 64,778).
  Mechanism: shorts paying −14.5% excess APR into a rising tape with flat OI
  = no fresh sellers, denied exit liquidity (#25); analog leg-1 56% up; 1h flow
  confirming. Distrust-window caveat: built 08:18 UTC (04–10 UTC window, #32) —
  no conviction upgrades until after 10:00 UTC; treat 55%, not 65%.
  Invalidation: hourly acceptance <63,600 with 1h flow fading (below the .382
  63,651 = the retrace fails).
  (alt): stalls at 64,300–64,420 without accepting and chops — same family,
  just a weaker magnet tag.

Move 2 (conditional on Move 1 tagging the zone, split 45/55):
  PRIMARY (45%): REJECTION at 64,420–64,780 — 5m lower lows + acceptance back
  <64,350 → rotate toward 63,500 (1h prior-resistance flip), deeper 62,900–
  62,500 shelf (score 352) if 63,600 goes. Mechanism: analog leg-2 reverses 67%
  (70% after up-legs); the TELL for #25 fuel is absent unless the break is
  impulsive; FOMC minutes Wed = positions clear before events (#READ step 2).
  ALTERNATE (55%→ the squeeze): IMPULSIVE acceptance >64,778 (vol expansion +
  CVD with price, no retrace) → 65,475–65,715 (score 142). This is the path
  that liquidates the crowded short book; it must show the impulsive signature
  — a choppy grind above 64,778 is NOT it (#25a).

Tripwires: >64,778 acceptance = squeeze live (and the open 40x short's liq);
<63,600 = retrace failing; <63,001 = down-poke thesis revived toward 62,500.
Tail (low prob, high significance, ~10–15%): Hormuz strike headline — gap
through all levels to 62,500 and below; oil +5% and Asia futures down would be
the tell before BTC's own tape confirms. FOMC minutes Wed is the scheduled
regime risk; the analog says expect two-way stop-runs into it.
```

**Honest-probability note:** leg-1 direction at 55–56% is near-coin-flip; the tradeable content is the *location* (the zone) and the *conditional split*, not the direction call. No SCORE tag was appended: this is a review run, the task mandates read-only, and appending to the ledger is a write — flagged here so the omission is visible, not silent. *(This incident itself proves §3's point: the tag's home is ambiguous between ledger text and calls.json.)*

Data-driven observation, not financial advice.

---

## 6. RISK & FIREWALLS

Scored against the doctrine's own claims:

| Firewall | Status | Evidence |
|---|---|---|
| Mechanism-over-fit (#46) | **INTACT** | Every live finding carries a mechanism + label; volume lens killed on evidence (#46); pain-radii killed 0/4 (#24) and stayed dead through #088 (the "bigger pool = higher target" pushback correctly refused to revive them). |
| Trial-count as denominator | **INTACT in text, idle in practice** | Trial counts quoted everywhere (~56 cells, 8 brackets×2TF); but zero new trials since 08-17 because nothing runs. |
| Decorrelation / N_eff (#42) | **INTACT** | Relationship matrix live in state_view.py (basis↔funding +0.41, cvd↔trend +0.45 flagged redundant); I verified it prints the same structure today. |
| Forward + stopping rule (#46/#53) | **HALF-INTACT** | The stopping rule held (no new in-sample mining since #46); the forward arm is **starved** — collector stopped, PREREG-reversal-x-basis can only be judged forward, and forward data isn't accruing. |
| Frozen-thesis kill-switch (#53) | **INTACT** | Reversal-excursion thesis FROZEN, one correctly-specified forward test allowed, scope guard honored by lessons.json and discovery_loop notes. |
| Read-only enforcement | **INTACT** | Scripts touch only /info (verified in code + behavior); hl_ops positions/pnl/funding are pure reads; no /exchange path anywhere in scripts/. |
| Read ⊥ holdability (#22) | **INTACT under live stress** | This very review: market read written before weighting the 40x short; no flip issued despite the book sitting 0.9% from liq on the squeeze tripwire. This is the rule's hardest test case to date and the process held. |
| Kill condition (#14, ≥500 OOS events) | **NOT MEASURABLE** | Progress is reported as "accumulating"; resolved-call count in the machine store is 1. Cannot verify progress toward 500 because the event log isn't being assembled (see §3). |

**Net:** the firewalls are real and have bitten (killed edges stay killed; clobbers get restored; flips get logged). The systemic risk has shifted from *methodology* (solved as well as it can be at this scale) to *operational continuity*: a discipline framework that doesn't run produces no evidence, and a kill-switch with no event counter can never fire.

---

## 7. CONCRETE RECOMMENDATIONS (priority order)

**P0 — Restore the grading loop (broken today, highest value, ~30 min of work).**
1. Rebuild `data/calls.json` as the FULL call history (all committed calls incl. resolved — calibration.py needs resolved rows; the call-evolve spam fix should filter *resolved* calls out of the tracker's input, not delete them from the store). At minimum, append the 2 matured ledger SCORE tags + the 08-16 seed calls.
2. Decide ONE canonical SCORE-tag home. Recommendation: calls.json is the machine record; ledger prose references it. Add a 10-line extractor that greps `SCORE {…}` from the ledger txt files into the store so nothing can sit ungraded again.
3. Let today's open call (matures ~10:49 UTC) resolve and run calibration.py — first real number on the board since migration.

**P1 — Restart minimal data collection (forward-only data is dying).**
- Re-enable the collector at reduced frequency if cost is the constraint (e.g., 4 runs/day: 07:00/13:30/15:30/20:00 UTC — the two open sessions + cash open). It is a pure script run; the Haiku-tier cost argument (#59) puts this at pennies. Every day off is unrecoverable P2/blow-ratio sample.
- Re-enable call-evolve (15m) at least while a call is OPEN; it caught real bugs (#092) and CONTESTED_INTERNAL states that nothing else catches.

**P2 — Fix ledger hygiene.** Add reconciliation line to #093/#094 duplicate; mark #092's "not yet fixed" as fixed (code verified); consider a ledger rule "one entry per event, timestamped; re-runs get a one-line delta."

**P3 — Doctrine maintenance.** Split SKILL.md into operating core (~150 lines) + archived trial history; fix the #085-vs-rule-number citation style; add an index of numbered rules. The 142 KB hot-path load is a token and comprehension tax on every stateless firing.

**P4 — The book (Olivier's layer, stated once, per #22/#9 hand-off).** The 40x short 0.9% from liquidation on the desk's own squeeze tripwire, entered against the desk's own measured edge family (#40: up-poke shorts are null), with all-time PnL −$28.6k and equity $1,084: the machine speaks only to direction and never issues the flip — but doctrine #9 makes it the desk's highest-priority output to say, when a disclosed position leans on a thesis that has transitioned: **the squeeze path is now the de facto live path, and the position's liquidation sits at its trigger.** Sizing, trimming, exiting: Olivier's call, today, before the cluster is tested.

**Not broken (do not touch):** the firewall architecture, the lessons/discovery/promotion gates, the blind-commit + frozen-score discipline, the collector/liq-map/HLP design, the co-desk independence rules. These are the desk's actual product per #53 and they are sound.

---

## APPENDIX — evidence index (timestamps UTC)

- macro_preflight VOID→CLEAR: 08:16:56 (4 movers; stubs VIX/DXY flagged)
- oi_flow: 08:18:05 (BTC exc APR −14.5%, prem −5.0bp, OI $2,672.4M flat, turn 0.61)
- wave_scenarios / pulse / structure / analog / state_view: 08:18 UTC
- hl_ops positions/pnl/funding: 08:19 UTC (generatedAt 1787041175–1787041181)
- calibration on calls.json: "0 resolved of 1" (08:20 UTC); manual resolution of ledger tags L215/L262: o=0 swept_then_right ($122) / o=1 (08:21 UTC)
- collector.jsonl: 38 ticks, 2026-08-17 09:05:51→20:27:54, liqevent=0; addressbook 150→280
- call_evolution.jsonl: 73 rows, 2026-08-17 10:21:34→17:47:45
- cron: `openclaw cron list` → 1 job (`HL BTC price-level watch`, every 30m, Last: -); `crontab -l` → none
- git: HEAD b67eeee; skill_workshop clobber fixes at 1315a44, 808b251
- Host uptime 1d 18h; workspace uncommitted: TOOLS.md (modified), reviews/ (new)

*Nothing in this report was fabricated; every number above is quoted from a script output, file, or dated headline captured at the timestamp shown. Where a figure could not be verified (kill-condition event count, Drive-side lesson files, Grok-desk state), it is said so in the body.*
