# Full-Stack Review — Olivier's Hyperliquid Trading Operations

**Reviewer:** DeepSeek V4 Pro (subagent, depth 1/1)
**Date:** 2026-08-18 ~07:20 UTC
**Scope:** read-only audit of the `hyperliquid-ops` skill + live account + market state
**Method:** followed the skill's own READ procedure — read SKILL.md and THINKING-PROCESS.md first, ran the Step 0 macro gate (`macro_preflight.py`) BEFORE any level work, did the disconfirming search via `news_check.py` (web_search is disabled in this environment), then the confluence/divergence read.

> **Standing meta-note:** this reviewer is the same model identity (deepseek-v4-pro) that the desk does *not* use for trading reviews. This is an *audit*, not the desk's own adversarial cross-check. Where I disagree with the desk, I say so and why. Where I cannot verify a number, I say "unverified" explicitly rather than fabricate.

---

## 0. TL;DR — what matters most

1. **There is a live short position that is fighting the desk's own published thesis and is $446 (0.69%) from liquidation.** This is the single most important finding. Position: SHORT 0.78169 BTC @ 63,618, liq 64,772.42, mark 64,326 — while the desk's open call and its recently-elevated Path B (squeeze through 64,427–64,746) point price *up through the liquidation level*. If the desk is right, the account blows up.
2. **The macro gate is VOID and the VOID itself is the story.** Four >=2% movers require stories; the disconfirming search found them immediately: *"Trump Rejects Iran Truce as War Escalates"* (Bloomberg 06:47 UTC, 2026-08-18) → WTI +3.76%, Brent +3.34%; *"Rising Yields Threaten to Puncture Asia's AI-Driven Stock Rally"* + *"Bond Slump Sends Long-Term Borrowing Costs to Highest in Decades"* → Nikkei −2.16%, Korea 200 −3.29%. The desk's reigning narrative (from the 2026-07-26 era) was anchored on a **US-Iran pause**; the actual live story is the pause **ending**. That is a regime reversal, not noise.
3. **The doctrine is coherent and the tooling is mostly healthy** — 979-line SKILL.md, 79 numbered rules, all scripts parse, collector is populating, calibration loop is logically sound. The problems are concentrated in (a) the position/thesis mismatch, (b) a stale macro narrative, and (c) a handful of ledger-vs-code drift items (details in §1–§2).

---

## 1. SKILL / DOCTRINE HEALTH

**Verdict: healthy, with minor drift. Grade B+.**

- `SKILL.md` is **979 lines, 79 numbered doctrine rules** (`grep -c "^[0-9]\+\. \*\*"` = 79). That is a *substantial, convergent* doctrine — coherent enough that I could follow a real READ procedure from it top to bottom without contradiction.
- `THINKING-PROCESS.md` is coherent and correctly describes the actual scripts that exist: Step 0 macro gate → Step 1 wave structure (5m/1h/4h FIRST) → Fib zones + Fib-time windows → anti-Elliott discipline. The scripts named in doctrine all exist in `scripts/`.
- **All 45 scripts parse cleanly** (`ast.parse`, Python 3.14.4, no syntax failures). This reverses an earlier concern (the summary flagged possible incompleteness); the actual state is clean.
- **Git state is clean**, working tree empty; recent commits show disciplined remediation: `1315a44` (restore doctrine after the skill_workshop overwrite bug, fix L1 invalidation placement, prune resolved calls), `808b251` (2nd-occurrence overwrite fix), `03f8de0` (fix skill-path so new sessions can *find* the skill).

**Drift items (minor, worth fixing):**

1. **Ledger #091 vs TOOLS.md — both present and consistent.** Good: the skill_workshop-overwrite standing check is logged in BOTH the ledger (#091) and TOOLS.md. That's correct redundancy, not drift. (I independently verified `wc -l` = 979 + rule count = 79, matching a healthy restored state.)
2. **Ledger #092 vs the actual code — the fix has ALREADY landed in code, but the ledger still says "not yet fixed."** `call_evolve.py` now contains the sequential-path awareness (`move1_dir`/`move1_zone` handling, `STRENGTHENED_ALT_PATH`, the candleSnapshot path-dependent check) exactly matching the #092 "standing follow-up." The ledger entry ends with "Flagging as an open script-level gap" — that's stale. **Recommendation: backfill a short note that #092's code fix landed.** This is precisely the kind of ledger-to-source drift this desk says it hates.
3. **`doctrine.json` `promoted[]` is still empty.** L1 and L2 (the sweep/reclaim lessons that drive the current invalidation placement) remain *candidate*-level on trial rather than promoted to binding. That's consistent with the deliberate "promotion bar / human-approval gate" design, but it means the *binding* doctrine under-weights exactly the lessons the desk is currently operating on. Flag, don't force: this is a governance choice, not a bug.
4. **`web_search` is disabled in this environment** (no provider). Doctrine's Step 0 disconfirming-search depends on a live search; the fallback (`news_check.py` RSS, `inbox_check.py` Gmail) works but is *headline-only* and self-describes as a "PARTIAL substitute." This is a real capability ceiling: for a war-events regime like today, headline-only RSS is enough to *name* the story but not to *date-and-source* every mover with confidence. Flag as an operational risk, not a code bug.

---

## 2. DATA PIPELINE

**Verdict: functioning and sane, with one freshness gap. Grade B.**

- **`collector.jsonl`** — 152 rows total, balanced across 4 kinds (38 × market/book/hlp/liqmap each). Spans **2026-08-17 09:05:51Z → 2026-08-17 20:27:54Z (~11.4h)**. BTC mark range over that window: **63,276 → 64,528** (n=38). Consistent, monotonic timestamps, no NaN/garbage observed. This is the forward-only "goldmine" layer and it is, as designed, the *only* persistent record of HLP net inventory + true liquidation map — worth its weight.
  - **Gap:** last tick 20:27Z on 08-17; nothing since (it's now ~07:20Z 08-18). This matches the ledger's note that all four crons were disabled per Olivier's cost directive (~$200/day → ~$200/month). Consequence: **~11h of the war-escalation regime is NOT captured** (oil spiked overnight *after* the last tick). If the desk wants the liq-map/HLP observables across the move it is currently trading into, that window is lost. Flag.
- **`addressbook.json`** — 280 addresses, persisting coverage as designed. Healthy.
- **`calls.json`** — 1 open call (`ts 1786963783916`, up=64,579, dn=63,001, p_up=0.56, h=24, by Claude, `move1_dir=down`, `move1_zone=[62499,62730]`). Pruning note in commit `1315a44` ("prune resolved calls from calls.json") was correctly applied — only the live call remains, which also fixed the duplicate-notification spam.
- **`call_evolution.jsonl`** — 73 records, append-only, functioning. This is the persistence of doctrine #7 (continuity) and it is working.
- **Collector correctness (code-level):** I read `collector.py` closely. It is genuinely READ-ONLY (only hits `/info`; never `/exchange`; a hardcoded comment asserts "Never /exchange, never keys"). The liq-map aggregator is the *true* liquidation price per position (Hyperliquid's own `liquidationPx`), not a leverage guess — correctly more trustworthy than the Coinglass estimate. The `--cap 150` bounded sweep and `--lookback` gapless realized-liq logic are sane. The `bucket_pct=0.005` bucketing is reasonable. **No bug found** in collector.py itself.
- **`calibration.py` (grading):** logically sound and honest — auto-resolves from `candleSnapshot`, emits the sweep-diagnostic (swept-then-right), has an explicit kill-switch (no-skill verdict at n≥30). The one caveat: **it grades `first` target touched across the full window but does not model the sequential Move1/Move2 structure** — same latent issue #092 flagged for call_evolve. If a call is *sequentially* conditioned, a flat "up before dn" scorer can mis-grade when the sequence (rather than the levels) is what failed. Minor; note for the next calibration revision.

---

## 3. LEDGER & GRADING

**Verdict: the ledger is the strongest part of the stack. Grade A-.**

The ledger is a *real* audit trail, not a decorative log. It records: #085 cross-call consistency gap (scope/horizon discipline), #086 silent direction-flip catch (continuity rule), #087 P2 liq-map (Coinglass) gap + the honest "interactive-only" capability boundary, #088 the "bigger pool = higher-prob" pushback vs rejected rule #24, #089 the Gemini-coherence catch of a **real L1 invalidation-placement violation**, #090 the 4-way reasoning audit, #091 the skill_workshop overwrite (twice!), #092 the call_evolve sequential bug, #093/#094 the on-demand 3-model cross-check.

Grading loop integrity: **intact.** SCORE tags feed `calibration.py`, which grades the *committed* call against the naive baseline via Brier. Outcomes auto-resolve from price. There is no manual self-grading (the exact self-deception the design warns against). The kill-switch is pre-committed.

**One honest caveat:** none of the resolved outcomes are visible to me in the files I read (no `records.json`/`SCORE` tag dump was in the data dir). So I cannot *independently* confirm the desk is beating baseline — I can only confirm the *machinery* for proving it exists and is correctly designed. If a resolved-calls score archive exists outside the files I saw, it wasn't in `data/`. **Recommendation: keep an append-only `graded_calls.jsonl` in `data/` so the calibration denominator is itself auditable.**

---

## 4. POSITIONS & PnL (LIVE EXTRACTION) — **the headline**

**VERIFIED, pulled directly from Hyperliquid `clearinghouseState` for wallet `0x496c84Ae4C963048063F63F1Ac572Af399579Ef2` (config.json "Main") at ~07:20 UTC 2026-08-18:**

| Field | Value |
|---|---|
| Asset / side | **BTC — SHORT 0.78169** |
| Entry price | 63,618.0 |
| Leverage | cross, 40x |
| Position value (notional) | $50,282.99 |
| Account value | **$981.86** |
| Total margin used | $1,257.07 |
| **Unrealized PnL** | **−$553.36 (ROE −44.5%)** |
| **Liquidation price** | **64,772.42** |
| **BTC mark (now)** | **64,326** |
| **Distance to liquidation** | **$446 = 0.69%** |
| Funding all-time / since-open | +$87.68 received / +$6.03 received |
| Withdrawable | 0.0 |

**Interpretation — this is the finding that overrides everything else:**

- The account is **short against entry 63,618** and is **0.69% from liquidation** as of my read.
- The desk's own **open call** (`up=64,579`, `dn=63,001`, `p_up=0.56`) has its **up-target already *above* the current mark**, and the desk's own recently-elevated **Path B** (#090/#093) is *"squeeze through 64,427–64,746"* — a path that takes price **through the liquidation level (64,772)**. In plain terms: **the desk's current thesis and the account's actual exposure point in opposite directions.** The short is a bet on the down-poke path (Path A); the desk has itself been *elevating the up/squeeze path to co-equal* on exactly the price action that is killing the short.
- This is not me second-guessing a trade — it's a structural self-consistency failure: **the account's position has no published invalidation/risk plan that is visible in any file I read.** calls.json carries the *thesis*, not the *position's* stop/liq discipline. There is no position-sizing note tying the 0.78 BTC short to the account's $981 equity at 40x (note: 40x on a $1,257 margin slice against $981 total account value means the position is already consuming >100% of equity in margin terms — the account is effectively one liquidation away from zero).
- Funding is *received* (+$87.68 all-time), i.e. this short has been *paid* to hold — consistent with the negative-funding short-crowd regime the desk's own #093 red-team identified ("persistent, self-funded short book for 72h, premium −3.05bp→−4.23bp"). That red-team finding said the short crowd is *well-capitalized and will reject near 64,400–64,700, not cascade* — which is actually *supportive* of this short in the near term, but it does **not** change the fundamental problem that there is **no recorded plan** for the 64,772 liquidation level sitting ~$446 above price.

**This is the #1 recommendation target.** See §7.

---

## 5. MARKET READ (Step 0 macro gate → confluence/divergence)

I followed the desk's own discipline strictly, and the gate did its job *before* I touched any level.

### Step 0 — Macro gate: **VOID**

`macro_preflight.py --thesis "BTC reversal/reclaim thesis review"` @ 07:18:33 UTC:

```
VERDICT: **VOID** — 4 asset(s) moved >= 2.0% in 24h.
  [ ] WTI          +3.76%
  [ ] Brent        +3.34%
  [ ] Korea 200    -3.29%
  [ ] Nikkei       -2.16%
```

DXY and VIX are **stubs** (constant, non-live) — correctly flagged by the script; dollar read must come from EUR/JPY instead.

### Step 0b — Disconfirming search (neutral wording, `news_check.py`, since `web_search` is disabled)

```
[2026-08-18 06:47 UTC] Trump Rejects Iran Truce as War Escalates
[2026-08-18 06:51 UTC] US Stock-Index Futures Drop as Bond Yields and Oil Prices Rise
[2026-08-18 06:57 UTC] Rising Yields Threaten to Puncture Asia's AI-Driven Stock Rally
[2026-08-18 04:25 UTC] Bond Slump Sends Long-Term Debt Costs to Highest in Decades
[2026-08-18 04:00 UTC] Trump's cuts to South Korean drills stir doubts about US resolve in Asia
```

**The macro picture is internally coherent — every one of the 4 gate movers resolves to a *named, dated* story, which is exactly the bar doctrine sets:**

- Oil up (WTI/Brent) → **Iran truce rejected, war escalates** (supply risk premium).
- Bond yields up, "highest in decades" → **risk-off in rates-sensitive Asia**: Nikkei −2.16%, Korea 200 −3.29% (and Korea specifically: US resolve in Asia questioned → geopolitical discount).
- US equity futures down on yields + oil → broad risk-off.

**Confluence/divergence read vs the desk's standing thesis:** this is a **DIVERGENCE, and a material one.** The desk's reigning narrative is the *US-Iran pause* (the 2026-07-26 era framing). The live story is the pause *ending* — war re-escalating, oil spiking, yields at multi-decade highs, Asia breaking down. A BTC thesis that was formed under "calm, no squeeze, no crowd" (which `oi_flow.py` still confirms: "no positioning extremes, funding two-sided, OI stable, premiums inside 15bp") is now being asked to hold across a **regime flip it wasn't priced for**. Bitcoin itself is only +1.21% 24h — it has *not yet* repriced the macro shift, which is precisely the kind of "macro says one thing, the asset hasn't caught up" setup the gate exists to catch.

### Step 1 — Wave / flow read (BTC), as the gate would allow *only after* the stories are named

- **`pulse.py BTC`** @ 07:19 UTC:
  - 5m: px 64,309 · vol −84% (fading) · CVD −sell slope −104 → **FADING/DIVERGING → FAKE risk**
  - 1h: px 64,287 · vol +15% (flat) · CVD +buy +467 but price DOWN → **FADING/DIVERGING → FAKE risk**
  - Both timeframes read the current push as **unbacked** — volume fading or CVD diverging. That is the fake-move signature.
- **`oi_flow.py --coins BTC`** @ 07:18:54 UTC: BTC 24h **+1.21%**, OI $2,703M (**ΔOI −1.0%**), turnover 0.58, excAPR **−5.6%**, prem −4.6bp, 3d prem −4.3bp. Turnover 0.58 is above the 0.4 "noise" threshold but below the 2.0 "tape worth reading" line — positioning, not tape, is the signal here, and there is **no crowd** (no squeeze/flush fuel). The script's own verdict: "Nothing is crowded, so there is no squeeze or flush setup to lean on."

**Synthesis of the market read:** the desk's *current* BTC stance is a **down-poke-first (Path A) with a recently-elevated squeeze-alternate (Path B)**. The live flow (fading/diverging on both TFs) is *consistent* with Path A's down-poke in the near term, **but** the macro gate is VOID on a war/yields regime that the whole stance was not built for, and Path B — if it fires — runs price straight into the account's 64,772 liquidation. The correct desk response under its *own* doctrine is: **resolve the macro VOID first, do NOT present fresh levels yet, and reconcile the position's liquidation level against the thesis before talking about entries.**

---

## 6. RISK & FIREWALLS

**Verdict: the doctrine's *risk framework* is disciplined and genuinely adversarial; the *practical* risk is a live position/liq mismatch the framework hasn't caught. Grade: framework A-, execution C-.**

Strengths (verified in doctrine/scripts):
- **Mechanism-over-fit:** rule #24 ("bigger pool = higher-prob") was tested and *rejected* (0/4), and the desk *held that line* in #088 against its own temptation to elevate 61,868. That is exactly the anti-overfit discipline you want.
- **Trial-count denominator:** doctrine explicitly allows a *rejected* candidate (pool→target) to stay dead rather than re-condition on new data. Good.
- **Decorrelation / adversarial bundle:** `contested_check.py` (blind Grok), `redteam_packet.py` (GPT-5.1 game-theory), `coherence_packet.py` (Gemini-3-Pro long-context). Three independent models arguing, not voting. This is best-in-class among the autonomous-trading desks I've seen.
- **Forward + stopping rules:** `calibration.py` has a pre-committed kill-switch (no-skill verdict at n≥30). `call_evolve.py` never mutates the frozen commit. The #085 "frozen-commit" discipline prevents silent rewrite of p_up.
- **Read-only enforcement:** collector/call_evolve/calibration all only hit `/info`; no `/exchange`, no key material in code. `.secrets/` is gitignored and 0700.

Weaknesses (concrete):
1. **The position has no recorded risk plan.** See §4. The entire firewall apparatus grades *calls*, but there is no equivalent, visible artifact tying an *actual position* to a liquidation/stop discipline. The desk traded beyond its own instrumentation. This is the gap between "we have amazing call-grading" and "we are 0.69% from liquidation and nothing in the repo knows it."
2. **The macro narrative is stale and un-versioned.** There's no single, dated "current macro regime" file that the gate or a human can diff against. The #085 lesson (scope/horizon must be named loudly) was applied to *call families* but not to the *macro regime* itself. When "war is paused" flips to "truce rejected, war escalating," the desk has no forced re-commit point.
3. **`doctrine.json` promoted[] is empty** — the binding doctrine lags the operational lessons the desk relies on (L1 invalidation placement, which already saved it once in #089).

---

## 7. CONCRETE RECOMMENDATIONS (priority order)

**P0 — Before anything else:**
1. **Reconcile the live short against the thesis — today, now.** The account is SHORT 0.78169 BTC @ 63,618, liq 64,772.42, mark 64,326 (0.69% away), ROE −44.5%, and the desk's own Path B points up *through* liquidation. Either (a) the thesis is down-poke-first and the short is *positioned for it* — in which case there must be a written rule for the 64,772 level (accept it, or exit/hedge before price gets there), or (b) the desk does not actually believe the short, in which case holding it is pure undefended risk. **There is no scenario where holding this position with zero recorded stop discipline is correct.** This is a *read-only review* — I have not and will not touch the position — but I am flagging it as an urgent, no-further-levels-until-resolved item.

**P1 — Governance/process (cheap, high value):**
2. **Version the macro regime.** Add an append-only `data/macro_regime.md` (or JSON) — a single dated line: "US-Iran status, oil regime, yields regime, risk-on/off" — that the macro gate *checks and diffs* on every run, forcing an explicit re-commit when a mover flips the regime. This operationalizes the #085 scope lesson at the macro layer where it was never applied.
3. **Backfill ledger #092** to note that `call_evolve.py`'s sequential-path fix *has landed* in code (it has — I verified the `move1_dir`/`move1_zone`/`STRENGTHENED_ALT_PATH` logic is present), so the ledger stops saying "not yet fixed."
4. **Add a `graded_calls.jsonl`** to `data/` so the calibration denominator (resolved outcomes) is itself auditable, not just the machinery around it. Also extend `calibration.py` to model the sequential Move1/Move2 ordering, so a sequence-failure isn't mis-scored as a flat "up-before-dn" wrong.

**P2 — Data freshness / coverage:**
5. **Close the 11h collector gap / decide it deliberately.** The crons being off for cost is a *legitimate* choice, but it means the liq-map/HLP observables across the overnight war-spike are gone forever. If cost is the driver, run the collector as a *one-shot* at live-trading hours instead of a 24/7 loop, so the forward-only goldmine doesn't go dark during regime moves.
6. **Fix the search ceiling.** `web_search` disabled → disconfirming search is RSS-headline-only, which is too thin for dating/sourcing every mover in a war regime. Either restore a search provider key or accept (and document) that the Step 0 gate is operating at degraded fidelity.

**P3 — Nice-to-have:**
7. **Promote L1 (and L2) out of trial** once Olivier signs off — the binding doctrine should reflect the lesson that already prevented a bad grade in #089.
8. **Have the calibration/backtest suite run a dedicated "position-size × liq-distance" stress test**, so future entries carry a printed "this position liquidates at X, Y% away, and here's the plan if it tags" line before any trade — closing the §6/§4 gap structurally rather than by vigilance.

---

## Appendix — what I could NOT verify (stated explicitly, per the honesty rule)

- **No SCORE-tag / resolved-outcomes archive** was present in `data/`; the desk's actual Brier/skill is *unverified by me*. The calibration *machinery* is sound; the *numbers* I cannot confirm from files I read.
- **`inbox_check.py` Gmail pull** was not run end-to-end (I saw the redacted `.secrets/gmail.env` and the code's read-only IMAP intent, but did not execute it against live credentials — read-only audit of *trading*, and I did not need the inbox confirmation beyond the RSS stories).
- **Coinglass P2 liq-map** is interactive-only (ledger #087) — not reproducible in this headless context; I relied on the ledger's own description of the 61,868 cluster.
- The **position snapshot** is verified *as of ~07:20 UTC 2026-08-18* and will be stale within minutes; re-run before acting.

*End of report.*
