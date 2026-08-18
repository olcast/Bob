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

## 4. Cross-check (two independent eyes) — final architecture

- **DeepSeek `deepseek-v4-pro` = producer** (carries the heavy full-stack work).
- **Qwen `qwen3.8-max` = challenger** (1M ctx, cheap, direct-pay — can actually fit the full review).
- Run them **sequentially** (lesson: Kimi's concurrency=1 taught us overlapping calls collide; also DashScope/other providers may serialize). For important outputs: produce with one, independently challenge/verify with the other, reconcile.
- **Kimi `kimi-k3`** is a distant third — do not put it in the critical path (128k ctx overflows on full reviews; concurrency ceiling).

## 5. Anti-burn guardrail

Direct-pay only, no OpenRouter markup. Flagship spend (GPT/Opus) is reserved for a single high-stakes decision, never the daily driver. This guardrail traces to the ~$250 OpenRouter burn (2026-08-17).

## 6. Freshness / verification discipline

- Every price/level quoted carries its pull timestamp. Nothing older than ~30min presented as current — re-run instead.
- When in doubt, hit the live endpoint, don't recall a number from memory.
- Cross-check a single model's output against a second (rule #4) — the 2026-07-26 confirmation-bias miss is the standing cautionary tale.
