# SOP — Recursive Learning, Model-Version Hygiene, Memory/KG

Standing operating procedure (Olivier, 2026-08-18). This file is **instruction, not notes** — Charly must follow it every session, unprompted.

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

**Availability fallback (Olivier, 2026-08-18):** if either model in the pair errors/429s/times-out, fall back to the OTHER model to cover its role — DeepSeek fails → Qwen produces AND challenges (single-model self-challenge, flag as degraded independence); Qwen fails → DeepSeek produces AND challenges (same degraded flag). Never let one provider's outage stall a call-generation. If BOTH fail, fall back to Kimi `kimi-k3` (RPM=3 cap — expect slow/serialized, but it keeps the desk live). Record any fallback in the ledger so the bounded-independence caveat stays honest.

**When the cross-check fires (automatic, no human signal):**
- **Full firings (2/day) + any ad-hoc full read** → ALWAYS DeepSeek produces + Qwen challenges.
- **Light delta-briefs (2/day)** → DeepSeek only (deltas don't warrant the token spend).
- **High-stakes single decision** → manually escalate: full cross-check + optionally the flagship-spend spike (§5).

**Kimi `kimi-k3`** = distant third, NEVER in the critical path (128k ctx overflow + concurrency=1).

## 4b. Cost-effective specialist roster (Olivier 2026-08-18 — "no Grok/GPT unless a cheap red team is possible")

The desk runs a specialist set built ENTIRELY from direct-pay models we already use — NO Grok, NO GPT, no premium spend. Roles:

1. **Producer — DeepSeek `deepseek-v4-pro`** — generates the call/full-stack read.
2. **Challenger — Qwen `qwen3.8-max`** — adversarial-against-the-call (incentive red-team: argues why the call is wrong).
3. **Blind-audit (cost-effective Grok-substitute)** — DeepSeek OR Qwen fed the SAME data set but with NO direction verdict (numbers + neutral framing: OI *trend*, funding *history*, session context, liq-map *delta* — never a bare column). Anti-anchoring WITHOUT starving it into noise. NOTE (Olivier 2026-08-18): raw numbers ALONE are under-determined — a bare "OI 41,752" with no baseline produces noise, not insight, and the selection of WHICH numbers to show still leaks the thesis. The useful blind-audit withholds the CONCLUSION, not the CONTEXT.
4. **Coherence checker (cost-effective Gemini-substitute)** — ME (Charly), inline, zero token cost — checks the call against doctrine/ledger for self-contradiction (no silent direction flips, no #085 violations, L1 invalidation placement).
5. **Vision chart-reader — `qwen3-vl-max`** — standing third eye on FULL firings: reads 1h/4h candle structure, volume profile, liq-map heatmap, catches wick-rejections / printed lower-highs / whether the poke already fired. Text-reads can't see this; a chart-read can.
6. **Reasoning auditor — recurse (§3c)** — each model returns its call/challenge PLUS a reasoning-improvements list.
7. **Econ-timing — folded into the brief (§3c), NOT a separate agent** — the Producer's brief REQUIRES scheduled-catalyst + US-open timing.

**Red-team mapping (cheap)** — the old premium trio reduces to: blind-audit (DeepSeek/Qwen raw-numbers) + incentive-against (Qwen) + coherence (Charly). That IS the cost-effective red team. Bounded-independence caveat stands (both are Chinese frontier families).

**Firing policy:** full firings (2/day) + ad-hoc full reads → Producer + Challenger + Vision (3 eyes) + reasoning-audit. Light deltas → DeepSeek only. High-stakes → full set + optional flagship spike ONLY if Olivier approves.

## 5. Anti-burn guardrail

Direct-pay only, no OpenRouter markup. Flagship spend (GPT/Opus) is reserved for a single high-stakes decision, never the daily driver. This guardrail traces to the ~$250 OpenRouter burn (2026-08-17).

## 5b. Terminology — "frozen" vs "evolving" (Olivier, 2026-08-18)

Two words that must NEVER blur:

- **"Evolving"** = the LIVE read (what to do next). Levels, direction, p_up shift with fresh tape. This is the desk's working view and it is *supposed* to change — calls are dynamic and evolve by design.
- **"Frozen"** = ONLY the grading snapshot, immutable *at issuance*. The `(up, dn, p_up, ts, h)` recorded the moment a call is issued is fixed so calibration.py can grade it without hindsight bias. You cannot edit a graded snapshot to match where price went — that would let the desk "win" every call retroactively.

**Rule:** never call the *live read* "frozen"; it evolves. The only thing frozen is the scored snapshot of each issued call (append-only `calls.json` + resolved SCORE tags). When a new read supersedes an old one, the old snapshot is RETAINED for grading and the new read becomes the ACTIVE view — both coexist, neither is overwritten.

## 6. Freshness / verification discipline

- Every price/level quoted carries its pull timestamp. Nothing older than ~30min presented as current — re-run instead.
- When in doubt, hit the live endpoint, don't recall a number from memory.
- Cross-check a single model's output against a second (rule #4) — the 2026-07-26 confirmation-bias miss is the standing cautionary tale.
