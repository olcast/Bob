# BRIEF CONTEXT — assembled 2026-08-18 16:45:10 UTC (fire-time, fresh from source files)

This packet replaces the old hand-assembled spawn string. It is REBUILT every firing from the
CURRENT source files below. You are STATELESS: read THIS now, do NOT rely on any memory of a
prior run, and do NOT inherit anyone's prior conclusion. Facts + rules are below; the DIRECTION
and the VERDICT are yours to produce independently.

---

## 0. LIVE venue state (Hyperliquid API, pulled at fire time — not from disk)
{
  "mark": "64756.5",
  "oi_btc": "41659.94486",
  "funding": "-0.0000098284",
  "markPx": "64756.0"
}

## 1. CURRENT CALL LEVEL FACTS (state.json — zones/structure only, no prior verdicts)
{
  "moves": {
    "move1": {
      "zone": [
        64300,
        64550
      ],
      "dir": "up"
    },
    "move2": {
      "zone": [
        64000,
        63650
      ],
      "dir": "down"
    },
    "move3": {
      "zone": [
        62500,
        62700
      ],
      "dir": "STAND_ASIDE (Branch C)"
    }
  },
  "death_price": "30m close >64,300 after the poke, without OI expansion",
  "soft_kill": null,
  "hard_kill": null
}

## 2. DOCTRINE RULES (SOP-RECURSIVE.md — read the rule prose; obey it, don't quote it)
--- BEGIN SOP ---
# SOP — Recursive Learning, Model-Version Hygiene, Memory/KG

Standing operating procedure (Olivier, 2026-08-18). This file is **instruction, not notes** — Charly must follow it every session, unprompted.

## 0. Canonical state + event-driven orchestration (Olivier 2026-08-18, "are we optimal" → no → fixed)

**Single source of truth:** `skills/hyperliquid-ops/data/state.json`, written by `scripts/state_snapshot.py`. It holds everything: `live_call` (scenario + entries + provenance + probabilities), `base_rates` (flattened from `backtest_rates.json`), `entries` (active entry triggers), and source mtimes for staleness detection. **EVERY agent — producer, challenger, provenance gate, falsifiability, level-watch, d7-depth, retro — reads `state.json` FIRST and never recalls a base rate from memory.** This is the structural fix for the 66%/85% misattribution class (ledger #097).

**Event-driven wake:** `scripts/entry_proximity.py` pulls the live mark and returns `hot`/`warm`/`cold` vs every active entry trigger. The level-watch cron runs it and wakes tighter when an entry is near — so the machines wake WHEN the trigger is near, not on a blind timer. Reconciled cadence: entry timeframe (15m close) → watch at ≤15m (10m), plus a 5m snapshot+proximity pulse on top.

**Orchestration roster (12 jobs):** state-snapshot 5m · price/entry-watch 10m · crosscheck-open 60m · d7-depth 2×/day · call-evolve 15m · collector 20m · discovery-sweep 2×/day · news-gate 3×/day · bberg ×3 (05:30/11:30/20:30 UTC) · sunday-retro weekly.

## 1. Model-version hygiene (ALWAYS use the highest/current version of each model)

Never trust a hard-coded model id. Proactively re-resolve the **best available model** per provider before any call-generation or review.

**Procedure — every session, and before any "generate the call" or "review the stack" task:**
1. Hit each provider's live `/models` endpoint (or `openclaw models list --provider <p>`).
2. Pin the **flagship** id currently returned, not the one from last session.
3. If the config's stored id ≠ current flagship, fix the config BEFORE using it.

**Known model ids (as of 2026-08-18) — re-verify, don't assume these stay current:**
| Provider | Endpoint | Current flagship | Versioning gotcha |
|---|---|---|---|
| DeepSeek | `api.deepseek.com` | `deepseek-v4-pro` | Was `deepseek-chat`; versioned ids (`-0813`, `-0731`) appear on the DashScope key too |
| Qwen / DashScope | `dashscope-intl.aliyuncs.com/compatible-mode/v1` | `qwen3.8-max` | Also exposes `deepseek-v4-pro-0813`, `ZHIPU/GLM-5.3`, `qwen3-vl-max` (vision) |
| Kimi / Moonshot | `api.moonshot.ai/v1` | `kimi-k3` | concurrency=1 org limit; 128k ctx (too small for full review); unreliable under load |
| xAI / Grok | `api.x.ai/v1` | `grok-4.6` | bundled `xai` plugin; flagship is the `grok-4.20-beta-*` branch (raw `/models` also returns `grok-4.6`/`4.5` but those don't map to a selectable plugin model) |

**Hard lessons already paid for:**
- 2026-08-18: assumed `kimi-k2` (didn't exist) → fixed to `kimi-k3` only after a 404/empty test.
- 2026-08-18: config still said `deepseek-chat` (stale) → real flagship was `deepseek-v4-pro`.

## 2. Recursive learning / self-improvement loop

The Hyperliquid desk already has the machinery. **Run it, don't just know it exists:**

- **Grading (proof of edge):** `calibration.py` grades committed `SCORE` tags → Brier vs naive baseline. Forward-only, kill-switch at n≥30.
- **Discovery (what to promote/retire):** `discovery_loop.py` over collected calls + `lessons.json` → proposes candidate lessons for promotion to doctrine and rules to retire.
- **Doctrine promotion bar:** candidates sit in `lessons.json` (trial) until promoted to `doctrine.json` (binding). Promotion is a *human-approved* gate — Charly proposes, Olivier signs off via the normal SAVE/apply path.

**Standing rule:** after any material market event or call resolution, run the discovery loop and surface *proposed* doctrine changes to Olivier (never auto-promote). This is the self-improvement engine; it only works if it actually runs.

## 3. Memory + context graph

Two layers, both mandatory:

- **Memory (ME) — `MEMORY.md` + `memory/YYYY-MM-DD.md`:**
  - Daily notes = raw log each session. Curate durable lessons/decisions into `MEMORY.md`.
  - Standing lessons (model-version gotchas, skill_workshop overwrite bug, the 2026-07-26 confirmation-bias miss) live in `MEMORY.md` and `TOOLS.md` — keep them current.
- **Knowledge graph (KG) — `skills/knowledge-graph/`:**
  - The store is currently EMPTY (`0e 0r`, depth 0). Populate it proactively: people, projects, decisions, providers, lessons, relationships.
  - Every session: read `skills/knowledge-graph/data/kg-summary.md`; add entities/relations for anything significant; always run `node skills/knowledge-graph/scripts/summarize.mjs` after changes.

## 3b. Recursive discovery — the self-improvement engine (RUN IT, don't just know it exists)

The loop is concrete and already built. The trigger is **cadence**, not luck:

```
calibration.py   → grades committed SCORE tags (Brier vs baseline, kill-switch n≥30)
discovery_loop.py calls.json lessons.json   → PROMOTE / RETIRE / WATCH verdicts
        ↓
OLIVIER's SAVE (skill_workshop apply / manual edit)   → promotes the lesson to doctrine
doctrine.json / SKILL.md updated   → NEXT call-generation reads the improved rules
        ↓ (loop — the definition of recursive)
```

**Cadence (standing):** run `calibration.py` + `discovery_loop.py` **after every resolved call**, and at minimum on a daily/heartbeat basis. Surface PROPOSED promotions/retirements to Olivier as a short list — **never auto-promote** (the human SAVE is the anti-overfit gate, audit #53).

**The recursion invariant:** the deliverable stays "the 2 next probable moves," but the *rules that generate them* are versioned by outcomes. A lesson earns promotion only after it holds FORWARD across N supporting calls (default bar = 5). This is what makes learning accumulate across sessions instead of resetting each morning.

**Cross-check feeds the loop (recursive everything):** a Producer/Challenger DISAGREEMENT is itself evidence. Capture each disagreement as a candidate lesson in `lessons.json` (with the specific divergence). The discovery loop grades *those* forward — so a disagreement that keeps predicting wrong outcomes gets retired, and one that keeps predicting right outcomes gets promoted to doctrine and changes how BOTH models are briefed next firing. The two-model pair is not a static check; it is an input to the same recursive loop.

## 3c. The next-2-moves brief — REQUIRED sections (Olivier, 2026-08-18)

Every next-2-moves call MUST include all of these, in this order. Levels alone are insufficient.

1. **Reasoning** — the *why* behind direction: tape mechanics (funding, OI, liq-fuel skew, premium), not just "up or down".
2. **Narrative** — the named macro story (bond slump, ETF flows, macro-bid), as CONTEXT only, with a divergence-check against the desk tape.
3. **Context** — scheduled Econ data / events (CPI, FOMC, payrolls) + US-open session state, each with timing.
4. **Timing** — which leg fires FIRST, then what, in clock/sequence order (not just a level list).
5. **Elliott Wave scenario** — the impulse-vs-corrective count, and which branch each count implies (countertrend corrective = fade; impulse-5 = continuation).
6. **The moves** — Move 1 (primary) + branch 1A→1B, Move 2 (alternative) + branch 2A→2B, tripwires close-only, p_up, and the falsifiable bar (e.g. continuation on expanding OI).

7. **Move relationship — scale decides invalidation (Olivier 2026-08-18, corrected).** Two moves are ONLY mutually exclusive when they are ALTERNATIVES at the SAME scale on the SAME leg (either you go up first, or down first — one path). But when one move is SMALL (a local poke) and the other is LARGE (a structural flush), they are NESTED, not exclusive: the small move sits INSIDE the large move's footprint, and the small move completing is COMPATIBLE with the large move still being live (the small poke is often the SETUP for the big flush — e.g. "poke-then-fade"). Invalidation is driven by STRUCTURAL breaks (a close through the larger thesis's invalidation level, e.g. the flush is dead only if price CLOSES above 64,550 on expanding OI), NEVER by the smaller move simply finishing. **Rule: reaching a move's target doesn't auto-invalidate a LARGER-scale scenario; only a structural close beyond the larger invalidation does.**

8. **Entry price (Olivier 2026-08-18) — a TRIGGER, not a limit.** Each move carries an `entry` = the close-confirmation level that DECLARES the leg started (e.g. "5m close above 64,347"). It is CONDITIONAL: you only act *if* the trigger prints, else the scenario stays dormant. Rules: (a) entry is ALWAYS close-confirmed (no wicks — consistent with the tripwire rule); (b) entry ≠ target — entry is where the leg STARTS, target is where it ENDS; (c) entries do NOT cancel across scales — a small Move-1 entry printing does not void a larger Move-2 (see #7); (d) derived by the SAME producer→challenger→reconciler→provenance-gate→falsifiability pipeline as the levels themselves — no new machinery, just an added field. **(e) The entry is what pins a scenario to a CLOCK.** Without an entry, a target is timeless/floating — it can never expired, so it can never be graded false. WITH an entry, the scenario gains a start-flag (when it becomes actionable) and an implied lifespan anchored to the entry's timeframe (1h entry ⇒ 1h-scale scenario; 15m ⇒ faster). `entry` + `invalidation` + `horizon` together = a full life-cycle (start / void / deadline), which is exactly what makes a scenario FALSIFIABLE and therefore GRADEABLE for Brier/expectancy. A trigger that never prints = clean resolved-false at expiry, not "unresolved forever."

This template is the brief the Producer is given AND the structure the Reconciler outputs. It is binding.

### Reasoning audit (Olivier, 2026-08-18) — inspect the REASONING itself, not just the verdict

Each model, in addition to producing/challenging the call, MUST inspect **how the reasoning was built** and **suggest improvements to the reasoning process**. This is a third required output per model, not optional polish:

- **What it audits:** input quality (right data, fresh tape, correct base rates), prior quality (were the assumptions tested against base rates or asserted?), inference steps (where the logic jumped, over-fit, or confused magnet-with-destination), missing context (Econ timing, session state, EW count, divergence-check), and the falsifiable bar (is it actually falsifiable, or unfalsifiable narrative?).
- **Output shape:** each model returns BOTH (a) its call/challenge AND (b) a short "reasoning-improvements" list — concrete changes that would make the reasoning stronger next time (better input, better prior, a step that should be re-ordered, a gap to close).
- **Feeds the loop:** reasoning-improvement suggestions are ALSO candidate lessons for `lessons.json` / `discovery_loop.py`. A suggestion that keeps improving forward outcomes gets promoted; a change that keeps adding noise gets retired. The cross-check is now grading two things: the call's correctness AND the reasoning that produced it.
- **Reconciler duty:** I (Charly) merge the reasoning-improvements lists across the pair, strip contradictions, and fold the surviving suggestions into the NEXT brief — so the brief itself gets better over time, not just the levels.

## 4. Cross-check (two independent eyes) — AUTOMATIC, not optional

**The wiring (how we actually USE the two agents):** spawn-on-demand subagents pinned per model via `sessions_spawn(model=...)` — NO named persistent agents (less config surface, already proven).

- **Producer — DeepSeek `deepseek-v4-pro`** (`sessions_spawn(model="deepseek/deepseek-v4-pro", task=...)`): generates the call / runs the full-stack read. Also the default agent model.
- **Challenger — Qwen `qwen3.8-max`** (`sessions_spawn(model="qwen/qwen3.8-max", task=...)`): same brief, independent run, then compared.
- **Reconciler — me (Charly):** judges where they GENUINELY diverge vs echo. Divergence = signal → captured as a candidate lesson (§3b). Agreement = lower info (bounded-independence caveat).
- Run the pair **in parallel for independent generation, reconcile after both land** (not sequential — that was only a Kimi-concurrency workaround; DeepSeek+Qwen on different accounts can run concurrently).

**Availability fallback (Olivier, 2026-08-18 — expanded for any-one-missing resilience):** the desk must keep working when ANY single model is absent/429s/times-out. Fallback order: **DeepSeek → Qwen → Grok → Kimi**, applying the highest-available model to whichever role is unstaffed.
- Producer (DeepSeek `deepseek-v4-pro`) down → next-highest (Qwen) produces AND its own challenger role degrades to a same-model self-challenge (flag `DEGRADED-INDEPENDENCE`).
- Challenger (Qwen `qwen3.8-max`) down → DeepSeek produces AND self-challenges (same degraded flag), or Grok steps in as challenger (preferred — preserves two-family independence).
- DeepSeek + Qwen BOTH down → **Grok `grok-4.6`** produces AND challenges (it is a different family, so independence is preserved even at this rung — better than the old Kimi-only tail).
- Grok also down / only Kimi left → Kimi `kimi-k3` (RPM=3 cap — expect slow/serialized, but it keeps the desk live).
- **Never stall a call-generation on a single provider outage.** Record every fallback in the ledger (`fallback:` field) so the bounded-independence caveat stays honest. A run that degraded is still logged and graded — degradation is a state, not a reason to skip the loop.

**When the cross-check fires (automatic, no human signal):**
- **Full firings (2/day) + any ad-hoc full read** → ALWAYS DeepSeek produces + Qwen challenges.
- **Light delta-briefs (2/day)** → DeepSeek only (deltas don't warrant the token spend).
- **High-stakes single decision** → manually escalate: full cross-check + optionally the flagship-spend spike (§5).

**Kimi `kimi-k3`** = distant third, OPTIONAL adversarial spot-checker, NEVER in the critical path (128k ctx overflow + concurrency=1 + RPM=3 + org rate-limit). **(Olivier 2026-08-18 — optional and measured, not a blocker: "use the verdicts to see if he's worth it.")** Kimi's output is `SUGGESTED` only — never overrides or blocks the Producer/Challenger verdict. The desk must run fine if Kimi is disabled, absent, or 429s.

**Design rule — do NOT hand Kimi the concluded verdict.** Feeding it the conclusion re-anchors it: it rubber-stamps or re-nitpicks what Qwen already said, which is an echo-check, not a third eye. Instead give it a **single narrow adversarial question it is uniquely positioned on**, sourced from the same neutral data set Qwen gets. Default question = the **stop-integrity / R-fiction check** (standing finding #1: is R real on this venue at this clock time — i.e. will the stop actually hold, or is the underlying dark and the close re-mark going to slip 1.33R → 3R+ in a wick). Swappable per-firing to whichever single hazard the desk wants stress-tested.

**Operating constraints:**
1. **Optional flag first.** Only invoke Kimi when explicitly enabled; by default the pair (DeepSeek + Qwen) runs without it. It is a measurement experiment, not a standing requirement.
2. **Never spawn two Kimi jobs in parallel** — concurrency=1 org limit → one dies instantly (`max organization concurrency: 1`). Serialize all Kimi work.
3. **Space Kimi calls ≥60s apart** — RPM=3 + rate-limit backoff stack on top of concurrency=1.
4. **Pre-supply the macro gate, don't let it fetch** — write the RESOLVED macro gate to `data/macro_gate_resolved.md` and brief Kimi to READ THAT FILE (Kimi correctly aborts on untrusted email/news ingest; the security guard zeroes the turn).
5. **Log every Kimi read as `KIMI-SUGGESTED` + grade it forward.** Record the read in the ledger tag alongside Producer/Challenger, then score it against the resolved outcome.

**Kimi is worth it iff** the graded `KIMI-SUGGESTED` delta (its flag vs the pair, scored against outcome) is positive and non-trivial over a meaningful N. Until that shows up, treat it as an optional dash of independence, not a core reviewer — and promote/retire it only by human gate (§3b), never auto.

## 4b. Symmetric originator round-robin — CONFLUENCE not CONSENSUS (Olivier 2026-08-18 — "sum of intelligences")

The desk runs a direct-pay **symmetric ensemble**. Every text model is a FULL co-originator AND a full cross-reviewer — nobody is assigned a permanent "challenger-only" seat. The governing idea is **confluence, not consensus**: the desk wants to read *where independent reasoning streams point the same way* (independent agreement = real conviction) and *where they split* (divergence = the high-information moment), NOT to average the three into one number.

**The three co-originators (identical neutral brief, blind to each other):**
1. **DeepSeek `deepseek-v4-pro`** — producer family A (Chinese).
2. **Qwen `qwen3.8-max`** — producer family B (Chinese).
3. **Grok `grok-4.6`** — producer family C (US/xAI). **KEEP him in
reasoning mode** (Olivier 2026-08-18: "keep him in reasoning"). The reasoning variant is the whole
point of the third family — depth over speed. Firing protocol for Grok is TWO-STAGE: first let him
reason out loud freely, THEN instruct "now commit the JSON call". Do NOT clamp him to a bare
one-shot JSON (that turns him into a faster, dumber echo of the other two and defeats the
ensemble). Accept the 4-5 min latency; full firings are 2/day.

Each lays down its OWN full call **first** (levels, direction, p_up, named death-price) on the SAME neutral data set, BEFORE seeing any other read. Three independent theses. Then each cross-reviews the other two (adversarial pass) — DeepSeek reviews Qwen+Grok, Qwen reviews DeepSeek+Grok, Grok reviews DeepSeek+Qwen. Every output is tagged `by:"<family>"` and `SUGGESTED` (advisory, never auto-trusted) — graded forward through the same `calibration.py`/`leaderboard.py` machinery (the `by:` field already maps each family name). Promote/retire/weight is **human-gated**, never auto.

**Reconcile (ME, Charly — inline, zero token cost, not a script):** I do NOT average the three numbers. I classify the triple as:
- **CONFLUENT** — 2+ independent families land within a tight band on direction + level ⇒ conviction (independent agreement, NOT an echo — `leaderboard.py` independence check discounts near-identical pairs).
- **DIVERGENT / CONTESTED** — the families materially split (≥ ~20pp p_up delta or a direction flip) ⇒ the high-information moment, surfaced to Olivier + captured as a candidate lesson (`contested_check.py`).
- **ECHO** — two families near-duplicate ⇒ discounted to one vote (same-family blind spot, especially DeepSeek-Qwen).

The full ensemble is the **sum of intelligences**: three distinct reasoning engines, independent enough that their correlated errors are the exception not the rule, graded against the only objective arbiter — the price tape.

**Supporting (non-originator) roles:**
5. **Vision chart-reader — `qwen3-vl-max`** — standing third eye on FULL firings: reads 1h/4h candle structure, volume profile, liq-map heatmap, catches wick-rejections / printed lower-highs / whether the poke already fired. Text-reads can't see this; a chart-read can.
6. **Reasoning auditor — recurse (§3c)** — each model returns its call/challenge PLUS a reasoning-improvements list.
7. **Econ-timing — folded into the brief (§3c), NOT a separate agent** — the Producer's brief REQUIRES scheduled-catalyst + US-open timing.

**Red-team mapping (direct-pay, three families, symmetric)** — every model both originates AND red-teams the others: DeepSeek reviews Qwen+Grok, Qwen reviews DeepSeek+Grok, Grok reviews DeepSeek+Qwen. Coherence (Charly) + Vision (`qwen3-vl-max`) ride on top. Bounded-independence caveat WEAKENS now that DeepSeek (Chinese), Qwen (Chinese), and Grok (US/xAI) are in the room — the remaining shared blind spot is only DeepSeek-Qwen, which Grok is positioned to catch as the odd family.

**Firing policy (symmetric round-robin):** full firings (2/day) + ad-hoc full reads → all three co-originators (DeepSeek + Qwen + Grok) each produce blind, then cross-review the other two, then Charly reconciles confluence/divergence + Vision chart-read (up to 4 independent eyes) + reasoning-audit. Light deltas → DeepSeek only. High-stakes → full ensemble + optional flagship spike ONLY if Olivier approves. **Resilience: any one of the text models may be absent — degrade via the §4 fallback chain (DeepSeek → Qwen → Grok → Kimi), the remaining two still origin + cross-review, and log the degradation; the loop and graphs still grade whatever landed.**

## 5. Anti-burn guardrail

Direct-pay only, no OpenRouter markup. Flagship spend (GPT/Opus) is reserved for a single high-stakes decision, never the daily driver. This guardrail traces to the ~$250 OpenRouter burn (2026-08-17).

## 5d. Backtesting measurement rules (Olivier 2026-08-18)

Two standing rules for how the desk measures edge — both fix a real flaw found while wiring the backtesters back in:

1. **COST IS REMOVED from edge measurement.** Transaction friction (maker/taker, 25bp/5bp round-trip) is an EXECUTION parameter, not a signal property. Folding it into the edge number masks whether the pattern itself has any juice (reclaim went from "-0.23% negative" to "+0.02% raw" once 25bp was stripped). Measure the RAW signal; reason about cost as a SEPARATE overlay afterward. All `backtest_*.py` now use `COST=0.0`/`cost=0.0`.
2. **TIMING = "did price reach higher/lower within X time", NOT first-touch.** The old `trade()` scored "stop-hit-then-recovered-to-target" as a LOSS, understating any slow-grind edge. The correct question is max forward excursion within the horizon: does price run to +0.8% (or higher) within H bars regardless of path. `backtest_lineexc.py` already did this correctly (peak-above/below); the others now report a `reached+X%` + `medReach` metric alongside (not replacing) first-touch. A pattern that "reaches" 64% but "hits on first-touch" 42% is a real slow-grind edge that first-touch was hiding.

**The backtester battery lives in `scripts/backtest_*.py`** (reclaim/sweep/magnet/confluence/sfp/lineexc/excursion) — walk-forward, own-lines (pivot known only at p+k, no look-ahead), vs random-entry control + unconditional drift baseline. `scripts/backtest_rates.py` runs the battery and persists machine-readable n/rate to `data/backtest_rates.json`. **The producer MUST read `backtest_rates.json` for any base rate instead of recalling from memory** — this is the fix for the 66%/85% misattribution (ledger #097).

3. **BACKTESTS WHISPER, THEY DON'T SHOUT (Olivier 2026-08-18 — anti-overfit, #53).** A backtest is CONSISTENCY evidence, not CONVICTION. In any call, backtest reference is capped to ONE line: "consistent with the X% reach rate (n=Y, TF) — in-sample, walk-forward-unvalidated." Never let a backtest number drive direction by itself. The only time a backtest earns foreground is when it surfaces something NEW — a divergence from the live tape, or a base rate that corrects what memory recalled. Then (and only then) flag it as an explicit improvement suggestion, with the caveat that it is still in-sample/regime-dependent. The whole point of walk-forward + OOS is humility: a backtest tells us what USED to happen, and the regime may have flipped.

## 5c. Incentive design — provenance gate + falsifiability score (Olivier 2026-08-18, "do we have an incentive design?")

The desk had a POLICING layer (audits + doctrine catch errors after the fact) but no INCENTIVE layer (making the generator prefer sound reasoning because sound reasoning pays). Built two tools — and WIRED them into the Sunday retro so they fire automatically:

- **`scripts/provenance_gate.py`** — hard precondition on any empirical base rate: must carry `{rate, n, source}`; demoted/retired figures carry `status:"DEMOTED"` + `use:false`. Probabilities must sum ~1.0 with a named residual. Flags BEFORE a call ships, not after. The exact R7 failure class (misattributed 66%/85%) now trips automatically.
- **`scripts/falsifiability_score.py`** — a second scored dimension BEYOND call-hit: reasoning integrity (death-price named, tripwire/target exclusive, probabilities derive, provenance present, no splice). 0.0–1.0, complements calibration.py (outcome judge), does NOT replace it. Below 0.60 = "reasoning not honestly gradeable."

**Wiring:** Sunday-retro cron (`2a1b9d2f`) runs calibration → discovery → leaderboard → provenance gate → falsifiability score, and surfaces a below-bar/gate-FLAGGED live call as an explicit "needs rebuild" flag. First live case = ledger #097 (the 09:2x call rebuilt 0.35→1.00).

## 5b. Terminology — "frozen" vs "evolving" (Olivier, 2026-08-18)

Two words that must NEVER blur:

- **"Evolving"** = the LIVE read (what to do next). Levels, direction, p_up shift with fresh tape. This is the desk's working view and it is *supposed* to change — calls are dynamic and evolve by design.
- **"Frozen"** = ONLY the grading snapshot, immutable *at issuance*. The `(up, dn, p_up, ts, h)` recorded the moment a call is issued is fixed so calibration.py can grade it without hindsight bias. You cannot edit a graded snapshot to match where price went — that would let the desk "win" every call retroactively.

**Rule:** never call the *live read* "frozen"; it evolves. The only thing frozen is the scored snapshot of each issued call (append-only `calls.json` + resolved SCORE tags). When a new read supersedes an old one, the old snapshot is RETAINED for grading and the new read becomes the ACTIVE view — both coexist, neither is overwritten.

## 5e. Past-as-prior, NOT past-as-anchor (Olivier 2026-08-18 — "evolution with more information")

A later ensemble run that produces a DIFFERENT read must REPLACE the old read, not be pulled toward it.
The old conclusion is a PRIOR, never an ANCHOR. Evolution means the newest read — conditioned on MORE
information (new tape, new funding, new OI, new catalyst) — wins; the old one is historical record only.

Three structural rules, so this is enforced by process and not by the reconciler's good intentions:

1. **Every level read is timestamped + input-stamped.** A new run carries a fresh timestamp and the
   inputs it saw (funding, OI, catalyst list). The old verdict stays in the append-only ledger as
   history, but is NEVER the starting point for the next read.
2. **Compare new-input → new-read, NOT new-read → old-read.** The question a fresh run answers is
   "given TODAY's tape, what's the edge?" — not "how far should I adjust LAST time's answer?".
   Anchoring to the past INPUT SET (stale catalyst, old OI) is the actual failure mode.
3. **Divergence from a prior read is INFORMATION, not a conflict to smooth.** If run #2 says
   "reclaim long" where run #1 said "stand aside", do NOT average them (that is anchoring with extra
   steps). Ask WHY the input changed (funding? catalyst? OI flush?) and let the CHANGED INPUT drive
   the new call. Old-vs-new divergence is a signal that something moved — grade the "something",
   not the two opinions.

Relationship to §5b: the graded snapshot (`up,dn,p_up,ts,h`) stays FROZEN for calibration; the LIVE
read (including move1/move2/move3 zones + direction) EVOLVES and is freely superseded. Both coexist;
neither is overwritten; the old live read gets no vote in the new one.

## 6. Freshness / verification discipline

- Every price/level quoted carries its pull timestamp. Nothing older than ~30min presented as current — re-run instead.
- When in doubt, hit the live endpoint, don't recall a number from memory.
- Cross-check a single model's output against a second (rule #4) — the 2026-07-26 confirmation-bias miss is the standing cautionary tale.

--- END SOP ---

## 3. VENUE-RISK FACTS (brief_facts.md — R-fiction, liq-magnet physics, narrative caps)
--- BEGIN VENUE-RISK FACTS ---
# BRIEF FACTS — shared venue-risk context (every originator reads BEFORE producing a call)

This file is the objective, non-directional fact sheet injected into EVERY originator's brief
(DeepSeek, Qwen, Grok) at the start of a round-robin firing. It is written by Charly (the
reconciler), not re-derived by the models.

**Read this first. It is CONTEXT, not a conclusion — it must not bias your direction.**
It exists so you calibrate correctly against the venue's real mechanics. Where a finding has
a *directional* implication, that is Charly's job (the reconcile layer), NOT yours — your job is
to produce your own independent read WITH these facts known.

---

## 1. Venue mechanics (facts about HOW the market works, not WHAT will happen)

- **Hyperliquid perps**: BTC / ETH / SOL / HYPE are hard-stop venues. SP500 / Brent / Gold are
  **oracle-priced synthetic ("xyz") markets** whose underlying trades only during US hours.

- **R is FICTIONAL on xyz oracle markets during closed-underlying hours** (finding #1).
  The risk envelope (0.33R sizing, 80%-of-liquidation stop, 3-stops/5-days breaker) assumes a hard
  engine stop that works on BTC/ETH/SOL/HYPE — it BREAKS when SP500/Brent/Gold underlying is dark
  (nightly + weekends). Friday 22:00 CET card → weekend headline → Sunday re-open re-marks 3–4% →
  the stop fires into a ~$465M-OI thin book = 3–6× planned R on a call priced as "conservative."
  The breaker counts STOPS, not realized R.

- **Stops placed "beyond liquidity magnets"** (finding #4): the price paths that reach them are
  disproportionately CASCADE paths, so conditional-on-stop slippage runs well above average.
  A `1.33R` plan can realize `3R+` in a single wick. (This is a fact about stop placement physics,
  independent of direction.)

- **Narrative-vector caps are semantic, not statistical** (finding #3): "AI infra bid" / "ETF flows"
  / "macro liquidity easing" read as three distinct vectors but collapse to ONE correlated position
  (long crypto beta) in a liquidation cascade.

## 2. Base rates — read from disk, never from memory

- **`data/state.json`** = single source of truth for the LIVE call, entries, and base rates
  (`{rate, n, source}`). QUOTE every base rate from this file with its n/source. Do NOT recall
  rates from memory. (Provenance gate: any empirical rate without `{rate, n, source}` is rejected.)
- **`data/backtest_rates.json`** = the walk-forward backtester rates. Cap backtest reference to
  ONE line and treat it as in-sample, walk-forward-unvalidated — NEVER let a backtest number drive
  direction by itself.

## 3. Macro gate + cross-asset — already gathered, RE-DERIVE don't inherit

- **`data/macro_gate_resolved.md`** = the pre-resolved macro NAMED STORY (bond slump, Fed minutes,
  distrust window). READ THIS FILE for the story; do NOT fetch live email/news (trips the
  external-content security guard and zeroes the turn).
- **`data/cross_asset_snapshot.md`** = the RAW 24h breadth + lead-lag + correlation numbers.
  You must RE-DERIVE breadth/divergence from these raw numbers YOURSELF — do NOT inherit the
  reconciler's "risk-off short" label. The raw tape (BTC+SOL up, ETH/SPX/NDX down) can pull the
  OPPOSITE direction from the macro story; your job is to reconcile them independently, not to
  rubber-stamp a conclusion.

## 4. Live entry levels (fact, current window — update per state.json)

- MOVE 2 FLUSH entry = 15m close BELOW 63,930 (below prior low 63,938 + 64,000 magnet).
- soft-kill = 1h close > 64,050. hard-kill = 4h close > 64,580 (acceptance alone kills).
- MOVE 1 poke = NO ENTRY (observe only).

---

**Reminder:** these are facts. Produce your own independent read (levels, direction, p_up, named
death-price) knowing them — do not treat any fact as a directional conclusion. Independence is the
whole point; your value is your *uncorrelated* read, not agreement with the other desks.

--- END VENUE-RISK FACTS ---

## 4. RESOLVED MACRO GATE (macro_gate_resolved.md — the NAMED story, pre-dating any move)
--- BEGIN MACRO ---
# MACRO GATE — PRE-RESOLVED (trusted local file, read-only)

This is the resolved macro gate output for the current call window. It is written by Charly
(the reconciler) from `bloomberg_macro_gate.py` + `news_gate.py` runs and the disconfirming
search already done this session. A sub-agent doing a full-stack review should READ THIS FILE
instead of fetching live email/news (which trips the external-content security guard).

Generated: 2026-08-18 ~11:08 UTC

## Named story (matched to every ±2% mover)

**Bond slump / long-end repricing.** 30y UST 5.33% (highest since 2007). Drivers: debt supply +
stuck-above-target inflation — NOT growth optimism. Fed minutes due Wed 2026-08-19.

Cross-asset movers (all ≥2% 24h), each matched to this named story:
- WTI +3.8% / Brent +3.4% — Hormuz transit collapse (5 tankers Sat vs 31 prior wknd), US-Iran deal doubt.
- Korea 200 −4.9% / Nikkei −2.7% — leveraged AI/memory unwind + risk-off, KOSPI profit-taking.

## Divergence check (the tradeable signal)
- Equities selling hard (SPX/NDX/Nikkei down) WHILE BTC holds +1.3% → BTC-bid-during-bond-slump.
- BUT breadth does NOT confirm: ETH flat (+0.0%) vs BTC +1.25% (breadth-divergence component tripped, #12).
- Decoupling ~24h old, unconfirmed. History: if macro asset keeps moving and BTC doesn't follow,
  BTC is the LAGGING asset, not the leading one. Short end (hike-off) is what BTC trades; long end
  (term premium) is what's selling.
- Regime label: ACTIVE RISK-OFF, long-end-led.

## Distrust window (doctrine #7)
04–10 UTC EU morning = statistical distrust window. The current call was committed ~09:2x UTC —
inside it — and must be read with that caveat (no conviction upgrades from moves inside the window).

## Note for reviewer
This file is CONTEXT for Step 0 of the full-stack review. The reviewer's job is NOT to re-derive
the macro gate — it is already resolved here. Proceed to review calls / scripts / ledger / grading
using this as the named macro story.

--- END MACRO ---

## 5. RAW CROSS-ASSET TAPE (cross_asset_snapshot.md — re-derive breadth/divergence yourself)
--- BEGIN CROSS-ASSET ---
CROSS-ASSET SNAPSHOT — raw 24h breadth + correlation (auto-refreshed per firing)

This is the RAW cross-asset tape for the current window. Originators must RE-DERIVE breadth
and divergence from these numbers, NOT inherit a pre-resolved "risk-off" conclusion.

## Live 24h returns (vs BTC direction)
    BTC   +1.09%   (reference)
    SOL   +1.09%   CONFIRMS
    HYPE  +0.32%   CONFIRMS
    ETH   -0.02%   DIVERGES
    SPX   -0.94%   DIVERGES
    NDX   -1.72%   DIVERGES
  breadth = 2/5 confirm BTC's 24h direction -> DIVERGENT (warning)

## Lead-lag vs BTC (1h, 3672 bars)
    ETH   beta~1.18
    SOL   beta~1.22   (SOL tends to lead/mirror BTC the tightest)
    HYPE  beta~1.27
    SPX   beta~0.20   (weak coupling — xyz macro)
    NDX   beta~0.30   (weak coupling)

## Correlation to BTC (1h returns)
    ETH 0.89   SOL 0.85   HYPE 0.59   SPX 0.49   NDX 0.50

## What this means (derive, don't inherit)
- BTC is +1.09% while SPX −0.94% / NDX −1.72% = a genuine crypto-vs-equity decoupling.
- BUT ETH is flat/divergent, so the crypto bid is NOT broad — it is BTC/SOL/HYPE-specific, not alt-wide.
- Read the breadth divergence yourself: a lift led by BTC+SOL with ETH lagging is NOT a
  high-conviction risk-on lift; it is narrow. Whether that resolves as a fade or a squeeze is
  a JUDGMENT — make it from these numbers, not from a label.

## Macro context (the named story, for calibration only)
- 30y UST 5.33% (highest since 2007) = long-end bond slump / risk-off regime pressure.
- Fed minutes Wed 2026-08-19 = binary repricing event inside the horizon.
- You must RECONCILE these against the raw breadth above — they can pull opposite directions.

--- END CROSS-ASSET ---

---

REMINDER: these are facts + rules. Produce your OWN independent read (levels, direction, p_up,
named death-price) knowing them. Independence is the whole point — your value is your UNCORRELATED
judgment, not agreement with any other desk or any prior run.
