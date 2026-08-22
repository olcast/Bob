# IMPLEMENT-OR-NOT — asked THE READ stack
**Decider:** Grok 4.6 (think-high), recommend only
**AsOf:** 2026-08-22 ~11:30 UTC
**Not a price read.** No rails, no p, no desk map, no SCORE, no pin.
**Olivier has not answered** (i) no-pin / (ii) GATE-DEGRADED / (iii) pin-and-log.
This file does not pick it.

---

## SHORT

**NO** — parent implements nothing in this session.

Operator discipline until the next asked read. Pin-gate + wiring patches stay blocked until Olivier answers (i)/(ii)/(iii).

**Act:** Reply (i), (ii), or (iii) for a flash/unparseable Qwen — that is the only unlock; say “fix the wiring” if you also want C2/C4/C6 filed before the next asked read.

---

## Per-item verdict

| ID | Change | Verdict | Why |
|---|---|---|---|
| **C1** | Fail-closed identity gate (mismatch → Qwen-down) | **WAIT FOR OLIVIER** | Spawn hard-pin is already 0−−. Treating flash as Qwen-down **is** (i). Do not encode it. |
| **C2** | Split TOOLS.md spawn rule (flash vs 3.8-max) | **WAIT FOR OLIVIER** | Right fix, does not pick the gate — still a TOOLS.md patch. No asked read this session; parent can already ignore the flash line for the challenger. File it only after he says fix the wiring. |
| **C3** | `QWEN_COMMIT` fence; missing → Qwen-down; parent writes sidecar | **WAIT FOR OLIVIER** | Schema is good. Fail-closed parse **is** (i). No write tool on `co-qwen` this session. |
| **C4** | Pin is the only user-facing card; MOVE 1 / MOVE 2 | **WAIT FOR OLIVIER** | Olivier already named the second Telegram. File/SKILL edit waits. Operator: do not send a second card. He may still want an in-thread copy — do not freeze that in doctrine unasked. |
| **C5** | Weekend / stale-inbox VOID → cheap 0b | **WAIT FOR OLIVIER** | New RE-RUN trigger (6). Doctrine. Next asked read, not today. Do not slide back to full inbox re-ingest. |
| **C6** | Seal `read_packet.py`; fix TOOLS shrink copy | **WAIT FOR OLIVIER** | Real landmine (`prior_line()` opens `current_call.md`). Script edit. Did not fire this morning (RAW file used). Operator: do not open current_call until step 7; do not hand `read_packet.md` to Qwen while Continuity is in it. |
| **C7** | R5 sanitizer (strip pulse words / pattern tags) | **WAIT FOR OLIVIER** | Next asked read. New flag/script. Keep numbers, drop words — do not build it now. |
| **C8** | Pin-gate stays 0−− only; sign-flip is NOTE | **WAIT FOR OLIVIER** | Pin-gate already correct (do not implement a change). Script hygiene on `contested_check.py` can wait for Sunday. **Never** promote sign-flip to the pin-gate. |
| **C9** | PACKET MARK stamp | **WAIT FOR OLIVIER** | Cheap, next asked read. Not this session. |
| **A** | Pinned spawn spec + scoped write + optional `challenger_spawn.py` | **WAIT FOR OLIVIER** | Spec overlaps C1/C2. Scoped write = `openclaw.json` / tool policy — no config without him. Do not add `challenger_spawn.py` today. |
| **B** | Identity header; mismatch → respawn once → Qwen-down | **WAIT FOR OLIVIER** | Identity print is operator discipline. Respawn-then-Qwen-down picks (i). |
| **C** | Both `grok.md` + `qwen.md` or no pin; parent-scribe hatch | **WAIT FOR OLIVIER** | This **is** the pin-gate. Qwen leans (i). Do not install it. |
| **D** | Canonical COMMIT line + `compare_commits.py` | **WAIT FOR OLIVIER** | 0−− is already \|ΔP\| > 20pp. New comparator script is Sunday/next-read. Do not build it now. |
| **E** | One desk-map + MOVE labels; **ΔP + models on the pin** | **WAIT** on template / **NEVER** on ΔP+models on the pin | Single artifact + `MOVE 1`/`MOVE 2` = C4. Putting ΔP / verified models on the user-facing card violates SKILL step 6 + TOOLS standing-call card (desk map = 2 moves + 40x stops; no SCORE/process metadata). |
| **F** | Re-run `entry.py` at pin; refresh if quote >25m | **WAIT FOR OLIVIER** | 0f already kills >~30m. New 25m number is a doctrine tweak. Next asked read. |
| **G** | `full_read_log.jsonl` | **WAIT FOR OLIVIER** | Sunday retro nicety. Do not create a standing write path this session. |

### NEVER (do not implement, even after he answers)

- Flip `agents.defaults.subagents.model` or `co-deepseek.subagents.model` to `qwen/qwen3.8-max`. Tape / compaction / heartbeat stay flash.
- Add unconstrained `write` to `co-qwen`, or any write that can touch `current_call.md` / `armed_triggers.json` / Telegram.
- Put ΔP, verified models, SCORE, Fib, or Elliott on the user-facing pin.
- Adopt `contested_check.py` sign-flip as the pin-gate.
- Pin Grok-only because Qwen was flash/slow/chat-only — unless Olivier picks (ii) or (iii).
- Inherit last rails / open `current_call.md` before step 7.
- Run the asked stack think-off. Invert facilitator onto Qwen. Add a third live brain / debate loop.
- Re-fetch the full inbox on every asked read. Let the challenger co-author the desk map. Arm 5m closes.

---

## The five answers

### 1. Implement anything this session, before (i)/(ii)/(iii)?

**NO.**

No asked THE READ is in flight. Nothing to spawn, pin, or seal. File patches (TOOLS.md / SKILL.md / THINKING-PROCESS.md / scripts / `openclaw.json`) before the pin-gate answer either (a) sneak-pick (i) via C1/C3/B/C or (b) spend workshop/script surface on hygiene the parent can already do by hand. Prefer prompt/behavior discipline over patches. No `openclaw.json` without Olivier. No `skill_workshop` apply without his “fix the wiring” and the standing `wc -l` check.

### 2. If YES: minimum set

*N/A — NO.*

### 3. If NO: operator discipline until the next asked read

Parent / facilitator, next time he asks THE READ — **do not edit files to do this:**

1. Spawn `agent: co-qwen`, `model: "qwen/qwen3.8-max"`, `thinking: "high"`. The TOOLS.md line “if spawn, flash” is for tape / news-gate / collector / compaction only. Flash is not a valid challenge.
2. Before compare: read the child’s actual model + thinking from session metadata. Print it. If it is not `qwen/qwen3.8-max` + high: **stop and ask Olivier**. Do not invent Qwen-down vs GATE-DEGRADED vs pin-and-log.
3. After a successful `delivery.pin=true`: at most one line (`desk map pinned.`). Do not restate the card. Do not flatten `MOVE 1` / `MOVE 2` into `1)` `2)`.
4. Continuity is step 7. Do not open `current_call.md` / `calls.json` / the last Telegram card before commit. Challenger gets the R5 RAW file only — never `read_packet.md` while it still has `## Continuity` / `prior_line()`.
5. If Qwen returns chat-only: scribe verbatim to the sidecar, mark `scribe=parent`. Do not paraphrase p / rails / mid-box into the commit object.
6. Pin-gate stays **0−− only**: \|ΔP\| > 20pp = CONTESTED. Sign-flip at 4pp is not CONTESTED. Do not blend a rejected mid-box.
7. 0a live. Do not re-ingest the full inbox unless a written RE-RUN trigger fires. Do not invent trigger (6) this session.
8. Do not patch `openclaw.json`. Do not leave thinking on after pin + seed.

### 4. Blocked until he answers (i)/(ii)/(iii)

- C1 fail-closed identity → Qwen-down
- C3 missing/malformed `QWEN_COMMIT` → Qwen-down
- Qwen B respawn-once-then-Qwen-down
- Qwen C file-existence pin gate (and whether a parent-scribe hatch counts)
- Any hardness change to “no Grok-only pin”
- Adding a write tool to `co-qwen`
- Relitigating this morning’s pin as valid vs incomplete — that **is** the question
- C2 / C4 / C6 file patches (safe relative to the gate, still wait for “fix the wiring”)
- C5 / C7 / C8-script / C9 / D / F / G (next asked read or Sunday)

### 5. One sentence Olivier can act on

Reply **(i) no-pin**, **(ii) GATE-DEGRADED**, or **(iii) pin-and-log** for a flash or unparseable Qwen — that unlocks C1/C3; add “fix the wiring” if you want C2/C4/C6 written before the next asked read.

---

*Recommend only. No skill/TOOLS/script/`openclaw.json` edits. No pin. No SCORE.*
