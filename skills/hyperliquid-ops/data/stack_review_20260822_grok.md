# PROCESS REVIEW — asked THE READ stack
**Reviewer:** Grok 4.6 (think-high), process only
**AsOf:** 2026-08-22 ~11:20 UTC
**Scope:** this morning’s ~10:30–10:50 UTC asked full-read. Not a BTC price read. No rails, no p, no desk map, no SCORE, no pin.
**Sources used:** `SKILL.md` 0− through 7, `references/THINKING-PROCESS.md`, `TOOLS.md`, `openclaw.json` agent wiring, `scripts/read_packet.py`, `scripts/entry.py`, `scripts/contested_check.py`, `scripts/preflight_freshness.py`, `data/full_read_20260822_raw_packet.md`, `data/macro_gate_last.md`. Forbidden files not opened.

---

## 1. What the stack already does well (KEEP)

These fired this morning and are the product. Do not “improve” them into the opposite.

1. **Asked-only, two-lane brains.** Parent stayed think-off. Facilitator Grok 4.6 think-high ran 0–6 independently (~11m). That is exactly 0−−. Chat default off is the cost/quality split; the stack is the only thing that pays for thinking.
2. **Independence order.** Collector `--once` before the stack. Analog + absorption refreshed live. Last 07:14 rails were not inherited. Continuity only after commit. This is the 2026-08-21 anchoring fix actually landing, not just written.
3. **R5 packet as a real object.** A dedicated RAW FACTS file was written (no thesis, no rails, no p). Qwen was R5-clean and did not open forbidden files. The challenger is an information firewall, not a second voter in a debate.
4. **Pin-gate held.** Parent waited for Qwen, compared, then pinned / seeded / silent-SCORE. No Grok-only pin. No `/exchange`.
5. **|ΔP| used as written.** 4pp → not CONTESTED. Parent rejected the challenger’s mid-box short and pinned FLAT. That is `entry.py` (“WAIT — MID-RANGE; do NOT chase”) plus doctrine #8 (no consensus theater). Agreement on “nothing to do here” is a valid commit.
6. **0a live every read.** VOID printed on the live preflight. Cache was cited with age (~3.3h, <8h), not used as a substitute for 0a. Skipping 0a because a cache exists is the 07-26-class miss; that did not happen.
7. **Watch follows the pin, not the previous card.** Seed after this card is the standing contract (`pref_watch_follows_pin`).
8. **Challenger tool jail is mostly right.** `co-qwen` cannot `message` / `gateway` / `cron` / spawn / memory. It cannot pin, cannot touch Olivier, cannot inherit the book. Keep that jail.

---

## 2. Top 5 process bugs / missing gates from this morning

Ranked by how much they can corrupt the next asked read.

### BUG 1 — Challenger model is not actually pinned (highest)
**What happened:** Qwen landed on `qwen/qwen3.6-flash`, not `qwen/qwen3.8-max`.
**Why (mechanical):** two config lines override the agent primary on spawn:

- `agents.defaults.subagents.model = qwen/qwen3.6-flash`
- `agents.list[co-deepseek].subagents.model = qwen/qwen3.6-flash`

`co-qwen.model.primary` is 3.8-max and `thinkingDefault` is high. That does not win if the parent spawn inherits `subagents.model`. `TOOLS.md` then blesses the miss: “If a spawn is unavoidable: `model: qwen/qwen3.6-flash`.” That line was written for tape/news collectors, not the asked challenger. This morning the cost-lane note ate the pin-gate.
**Missing gate:** parent never asserted the child’s *actual* model from session metadata before treating the return as a 3.8-max challenge. A flash challenge is not the second family Olivier paid for. It is a cheaper, same-vendor, lower-reasoning draw — bounded independence, already flagged in his own prior review.

### BUG 2 — Challenger has no commit sink
**What happened:** Qwen’s allowlist is `read` + `session_status`. No `write`. It returned the commit in chat. Parent wrote the file.
**Why it matters:** the pin-gate’s audit trail is “two committed objects, then compare.” A chat blob that the parent transcribes is one object plus a paraphrase. That is how mid-box shorts get softened, p-values drift by a few pp, and `|ΔP|` becomes the parent’s memory of Qwen rather than Qwen. R5 independence is information separation *and* commitment separation.
**Keep the jail.** Do not give Qwen `message`, `armed_triggers`, or `current_call.md`. Give it a sidecar or a parseable block.

### BUG 3 — Second Telegram after the pin is an unpinned second source of truth
**What happened:** pin went out as the desk map; parent then sent a second Telegram that flattened `MOVE 1` / `MOVE 2` into `1)` `2)`. Olivier called it.
**Why it matters:** the pin is the standing object (`pref_pin_standing_call`, SKILL step 6, TOOLS “Telegram standing-call card”). A restatement is a second card. Labels are the UX contract: `MOVE 1` = first leg of a PATH, not “option 1 of a fork” (SKILL amendment 2026-08-17). `1)` `2)` re-introduces the fork reading the amendment killed. There is no checklist item that says “do not restate the pin.”

### BUG 4 — Weekend VOID + cache-cite with no cheap 0b refresh
**What happened:** live 0a VOID (HYPE ≥2%). 0b+0c cited from the 07:14 UTC weekend-catch-up cache (age ~3.3h, <8h). Inbox not re-fetched. Cache itself says “No 22 Aug wire in the allowlist beyond Merryn / myFT” and inbox headers stop on 21 Aug.
**Why it is a bug even though it is legal:** the written RE-RUN triggers are (1) VOID with unmatched mover, (2) cache >8h, (3) session gap >~6h uncovered, (4) catalyst <90m, (5) Olivier asks. HYPE *had* a named dated story in the cache. Clock had nothing inside 90m. Gap from 07:14 → 10:30 is ~3h. So the parent followed the letter.
The spirit of 0d / 07-26 is weekend inbox lag: the pause email arrived *after* the tape had already moved. A Saturday 10:30 VOID whose last allowlisted header is Friday is that class. Live 0a had also *shrunk* the VOID set (07:14: BTC/ETH/SOL/HYPE; 10:35: HYPE only) — the cache stories are a day-old debasement/ETF tape, not a check that nothing new hit HYPE in the last three hours.
**Missing gate:** “0a VOID on a weekend / with inbox headers older than ~6h → cheap 0b search even if cache <8h.” Not a full inbox re-ingest.

### BUG 5 — Standing shrink path still anchors; R5 packet still leaks derived labels
Two landmines that did not fully fire this morning (the dedicated RAW file was used) but will fire the next time someone is tired or cheap:

- `scripts/read_packet.py` `prior_line()` **opens `current_call.md`** and prints “New call is a DELTA of that, not a restart.” That is the exact 0− / step-7 inversion the 2026-08-21 rule retired. `TOOLS.md` still says a full read is `read_packet.py` then `current_call.md`. Those two sentences fight SKILL 0−.
- This morning’s RAW packet was thesis-free, but it still shipped **derived features**: contradiction script tags `short-add ; trapped-longs`, pulse words `FADING/DIVERGING`, analog `LEG 2 REVERSE 72%`. R5: “raw exchange facts only — no thesis, no trap-scores, no derived features, no narrative.” Numbers are facts. Pattern tags are the auditor’s job.

Honorable mention, not top-5: marks in the RAW packet drift 76,973 → 77,198 across ~15m with no single “packet mark.” Minor. Also `contested_check.py` will flag a sign-flip even at 4pp; 0−− is `|ΔP| > 20pp` only. Parent used the doctrine rule (correct). Do not silently promote the script’s extra trigger.

---

## 3. Concrete improvements

Each: problem → change → why → cost/risk. Ordered for a parent who can implement or reject.

### C1. Fail-closed identity gate on the challenger (script + prompt)
- **Problem:** spawn can return flash (or Grok fallback) and the parent still compares/pins.
- **Change:**
  1. Asked-challenger spawn **must** pass `agent: co-qwen`, `model: "qwen/qwen3.8-max"`, `thinking: "high"`. Do not rely on `co-qwen.primary`.
  2. Before compare: parent prints `child.model` + `child.thinking` from session metadata. If not `qwen/qwen3.8-max` + high → treat as **Qwen-down**. SKILL already says: if Qwen is down, say so, do not pin a Grok-only card.
  3. Do **not** flip `agents.defaults.subagents.model` or `co-deepseek.subagents.model` to 3.8-max. Those paths are protected and exist so tape/compaction stay cheap.
- **Why:** this morning’s second brain was the wrong brain. The gate is one `if` before pin.
- **Cost/risk:** one asked 3.8-max call burns Token Plan 3k/5h. That is the intended spend. Risk = parent “helpfully” changes the global subagent default and every heartbeat child becomes max. Reject that.

### C2. Split the TOOLS.md spawn rule (prompt)
- **Problem:** one line (“if spawn, flash”) collides with 0−−.
- **Change:** replace with two bullets, verbatim:
  - Tape / news-gate / collector / compaction children → `qwen/qwen3.6-flash`, last line `ANNOUNCE_SKIP`. Never THE READ judgment.
  - Asked challenger → `co-qwen` / `qwen/qwen3.8-max` / thinking high. Flash is not a valid challenge.
- **Why:** the contradiction is what caused BUG 1. Behavior files are the live control until Olivier applies config.
- **Cost/risk:** none if scoped. Risk is someone “simplifies” back to one spawn rule.

### C3. Challenger commit schema; parent writes the sidecar (script + prompt)
- **Problem:** no write tool → chat-only commit → parent paraphrase.
- **Change:** spawn prompt requires a single fenced block, last, nothing after:

```
QWEN_COMMIT
{"asof":"...Z","model":"qwen/qwen3.8-max","p_up":0.00,"horizon_h":12,
 "move1":{"name":"...","entry":0,"exit":0,"inv":0,"stop":0,"reentry":0,"reverse":0},
 "move2":{"...":"..."},
 "reasons_not":["...","...","..."],
 "alt_invalidation":"...",
 "flat": true}
```

  Parent parses that block and writes `data/full_read_YYYYMMDD_qwen.md`. If the block is missing/malformed → Qwen-down, no pin.
  Do **not** add unconstrained `write` to `co-qwen`. If a write tool is added later, path-allow only `data/full_read_*_qwen.md`.
- **Why:** commitment separation without letting the challenger touch the pin, the watch, or Telegram.
- **Cost/risk:** Qwen may still ramble; the parser must require the fence. Risk of giving write: one bad path clobbers `current_call.md`. Prefer parse-and-write.

### C4. Pin is the only user-facing card (pin format + prompt)
- **Problem:** second Telegram restated and flattened labels.
- **Change:**
  1. Pin body is the desk map. Exact labels, every time: `MOVE 1` then `MOVE 2` (bold). Never `1)` `2)`, never “first/second,” never “option A/B.”
  2. Each move prints the six prices on their own lines: `ENTRY` / `EXIT` / `INVALIDATION` / `ENGINE STOP` / `RE-ENTRY` / `REVERSE`. If FLAT, first line says `FLAT` and the six lines are still the *armed* rails, not a chase.
  3. After `delivery.pin=true` succeeds: chat reply is one line, e.g. `desk map pinned.` Forbidden: restating the card in the same turn.
  4. Add a self-check bullet: “Did I send a second user-facing card after the pin? If yes, that message is a defect.”
- **Why:** pin = standing object. `MOVE 1`/`MOVE 2` is PATH language. `1)` `2)` is FORK language. Olivier already named this.
- **Cost/risk:** he may still want a short unpinned copy in-thread. That is the question in §5. Until he answers: pin only.

### C5. Weekend / stale-inbox VOID → cheap 0b only (data freshness)
- **Problem:** letter of the cache rule vs 07-26 weekend miss.
- **Change:** add RE-RUN trigger (6), one sentence in SKILL 0 / THINKING-PROCESS 0 / `macro_gate_cache.py` header:
  **If live 0a is VOID AND (weekend OR newest inbox header in the cache is older than ~6h), run 0b search in neutral wording. Do not re-ingest the full inbox. Cite the cache for depth.**
  Still skip 0b when 0a is CLEAR, cache <8h, weekday, inbox headers cover the gap.
- **Why:** this morning was legal and still the 07-26 shape (weekend, VOID, last allowlisted header yesterday).
- **Cost/risk:** a few search calls on weekend VOID reads. Risk is sliding back to “re-fetch inbox every asked read” — reject that; 0c stays cached.

### C6. Seal `read_packet.py` and fix TOOLS shrink copy (script + prompt)
- **Problem:** shrink path opens `current_call.md` and tells the facilitator the new call is a delta.
- **Change:**
  - Delete the Continuity section from `read_packet.py` (or replace with `SEALED until step 7 — do not open current_call.md / calls.json / the last Telegram card`).
  - `TOOLS.md` shrink: “facilitator reads `read_packet.md` + live sensors. `current_call.md` is step 7 only.”
  - Asked challenger never receives `read_packet.md` if that file still has a prior-call line; it receives the R5 RAW file only.
- **Why:** otherwise the next cheap read re-imports the anchoring bug the 20:46 confirmation retired.
- **Cost/risk:** facilitator might forget continuity exists. Step 7 is the reminder. Do not put a “hint” of last rails in the packet.

### C7. R5 sanitizer (script)
- **Problem:** RAW packet still carries pulse words, contradiction pattern tags, analog reverse commentary.
- **Change:** `python3 scripts/raw_packet.py --r5` (or a flag on the assembler) that keeps: timestamps, marks, VOID list, OI/ΔOI/turnover/excess/prem, wave *levels and fib-time counts*, liqmap clusters + forced-path distances, occupancy closed-bar accepts, analog n + P(up first) as a frequency, clock, xyz hours. Strips: `FADING/CONFIRMING`, `trapped-longs` / `short-add`, “the move that hurts,” any p, any rails, any “WAIT/FLAT/chase.” Spawn first line: “If this packet contains a thesis, rails, p, or pattern tag, stop and ask for a clean packet.”
- **Why:** R5 is the only reason Qwen is not Grok-in-a-mirror.
- **Cost/risk:** over-strip and Qwen misses pulse/analog. Compromise: keep the *numbers* (vol %, CVD slope, analog 46/54) and drop the *words*. Pulse labels are the facilitator’s job in 0–6, not the challenger’s input.

### C8. Scoring / contested hygiene (scoring — silent, not user-facing)
- **Problem:** three comparators exist and they disagree: 0−− (`|ΔP| > 20pp`), `contested_check.py` (`|ΔP| ≥ 20pp` **or** sign-flip), doctrine #57 (~15pp + opposite direction).
- **Change:** pin-gate stays **0−− only**: `|ΔP| > 20pp` = CONTESTED, lowest conviction. `contested_check.py` may log a sign-flip as `NOTE` for the Sunday retro; it must not block or force a pin. Silent SCORE still grades the *pinned* card, not Qwen’s discarded mid-box, not a blend.
- **Why:** this morning 4pp + rejected mid-box was correct. Promoting sign-flip to a pin-gate would have labelled a FLAT-vs-slight-lean as CONTESTED and invited blending.
- **Cost/risk:** none. Risk is “make the threshold tighter so we use Qwen more.” That is consensus theater.

### C9. Packet mark stamp (data freshness, small)
- **Problem:** RAW file quotes four BTC marks over 15m.
- **Change:** one line at the top: `PACKET MARK <px> @ <ts>` and every later mark is labelled `stale-vs-packet` if older. Do not present 76,973 and 77,198 as the same now.
- **Why:** 0f freshness. Cheap.
- **Cost/risk:** none.

---

## 4. What NOT to change

These look like improvements. They re-import the bugs the stack was built to kill.

1. **Do not start from `current_call.md` / last Telegram / 07:14 rails.** Continuity is step 7 after commit. “Don’t start over” as a starting instruction is retired.
2. **Do not run the asked stack think-off** to save tokens. Parent think-off + child think-high is the split. A think-off 0–6 is a different (worse) product.
3. **Do not pin Grok-only** because Qwen was flash, slow, or chat-only. That is the failure mode 0−− names. Either get a real 3.8-max commit or do not pin (unless Olivier answers §5 the other way).
4. **Do not blend Qwen’s mid-box short into the pin when `|ΔP|` is 4pp and `entry.py` says WAIT.** Challenger reasons-not and alt-invalidation can be *cited* in continuity; they do not become MOVE 1. Mid-box chasing is how 40x dies.
5. **Do not flip `subagents.model` globally to 3.8-max** and do not invert facilitator onto Qwen. Tape/compaction/heartbeat stay flash. Token Plan 3k/5h is a seat cliff.
6. **Do not add a third live brain or a debate loop.** Doctrine #8 / #59: distinct capability, never another vote. This morning needed wiring, not another model.
7. **Do not re-fetch the full inbox on every asked read** when 0a is CLEAR and the cache is fresh. Token discipline is quality-preserving. The new trigger is weekend/VOID/stale-headers only.
8. **Do not overlay the book** on the pin. Desk map only.
9. **Do not put SCORE, Fib labels, or Elliott jargon on the user-facing card.** Silent ledger only. Plain language, exact prices.
10. **Do not arm 5m closes.** 15m entry / 15m fast kill / 1h confirm stays.
11. **Do not adopt `contested_check.py`’s sign-flip as the pin-gate.**
12. **Do not leave thinking on after pin + seed.**

---

## 5. One question before changing doctrine

**If the asked challenger lands on the wrong model (flash, not 3.8-max) or returns no parseable `QWEN_COMMIT` block: fail-closed (no pin, same as Qwen-down), or pin Grok’s card labelled DEGRADED / lowest conviction?**

This decides whether this morning’s pin was valid process with a degraded audit, or an incomplete card that should not have replaced the previous pin. Everything in C1/C3 hangs on the answer. Do not pick it in a review.

---

## Implementation order if Olivier says “fix the wiring, don’t wait”

1. C2 (TOOLS.md two spawn rules) — behavior file, no config patch.
2. C4 (pin template + no second card) — prompt/self-check.
3. C1 (spawn hard-pin + identity print) — prompt; config stays protected.
4. C3 (commit fence + parent write) — spawn prompt + five lines of parse.
5. C6 (seal `read_packet.py`) — one function delete.
6. C5 / C7 / C8 / C9 — next asked read, not today.

Do not apply via `skill_workshop` without the before/after `wc -l` check (TOOLS standing rule). Do not patch `openclaw.json` `subagents.model` without Olivier.

---

*Process only. No price, no rails, no p, no pin, no SCORE.*
