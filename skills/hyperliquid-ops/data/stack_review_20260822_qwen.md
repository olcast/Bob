# STACK REVIEW — asked full-read run, 2026-08-22 ~10:30–10:50 UTC (blind process review, co-qwen)

Model: qwen/qwen3.8-max · thinking high · R5 CLEAN (no current_call / calls / armed / brain cards).
No write tool on challenger — parent scribed this file from the returned text.

## 1. What the stack already does well (KEEP)

1. **R5 firewall held end-to-end.** Packet is genuinely raw-facts-only. Challenger stayed R5-clean.
2. **Liveness-then-independence ordering was respected.** collector --once before stack; analog/absorption live; sidecars labeled and not used as live fingerprints.
3. **The seal held.** 07:14 rails not inherited; prior card only at step 7.
4. **Macro-gate split applied correctly.** 0a live VOID; 0b+0c from 07:14 cache (~3.3h, <8h); inbox not re-fetched; VOID mover had a named dated story.
5. **Lane separation held.** Think-off parent; Grok think-high 0–6; challenger before pin; ΔP then pin → seed → SCORE.
6. **Honest sensor labeling.** D11 reset, absorption stale-then-replaced, options PROXY, tod not-Hawkes, xyz DARK.
7. **FLAT was a legitimate output.** Mid-box short considered and rejected.

## 2. Top 5 process bugs / missing gates (ranked)

1. **Challenger ran on the wrong model — silently.** defaults.subagents.model = qwen3.6-flash overrode agent primary. Binding spec violated with zero gate friction.
2. **Challenger's commit was never persisted.** No write tool; commit lived in chat; qwen.md missing. Pin-gate evidence is scrollback.
3. **Second Telegram after the pin flattened MOVE 1 / MOVE 2 into "1) 2)".** PATH-not-FORK broken. Two divergent artifacts (pin vs follow-up).
4. **Challenger wiring lives in prose, not mechanics.** No spawn template pinning model/thinking/tools/packet/output schema. Config-precedence is invisible.
5. **ΔP/CONTESTED protocol is undefined at the data level.** |ΔP| by eye from prose. No canonical commit schema, no comparator, no run log.

## 3. Concrete improvements

**A. Pinned challenger-spawn spec** — explicit model=qwen/qwen3.8-max, thinking high, scoped write to full_read_<date>_qwen.md. Optional challenger_spawn.py that prints the payload.

**B. Identity header + parent verification** — every commit opens with brain/model/thinking/asOf/packet. Parent verifies runtime model before ΔP. Mismatch = respawn once, then Qwen-down path.

**C. File-existence pin gate** — both grok.md and qwen.md must exist or no pin. Parent-scribe escape hatch marked scribe=parent, verbatim=true.

**D. Canonical commit line + compare_commits.py** — COMMIT {brain, model, thinking, stance, p_up, h, up, dn, tripwire}. Mechanical ΔP + CONTESTED.

**E. Single-artifact pin rule + fixed template** — exactly ONE desk-map message; corrections replace the pin. MOVE 1 / MOVE 2 labels mandatory. Put ΔP + verified models on the pin.

**F. Freshness-at-pin** — re-run entry.py before pin; if quoted price >25m old, refresh.

**G. Run log** — append one JSON line per asked read to full_read_log.jsonl for Sunday retro.

## 4. What NOT to change

1. Do not let think-off parent co-run the stack.
2. Do not give challenger Grok's thesis/rails/p.
3. Do not inherit last rails "for continuity."
4. Do not relax no-Grok-only-pin when challenger is slow or "ΔP would be small."
5. Do not add a third voter.
6. Do not let trigger_watch auto-re-pin mid-box.
7. Do not re-run 0b+0c when cache <8h and no RE-RUN trigger.
8. Do not make the challenger co-author of the desk map.

## 5. One question for Olivier

How hard is the pin gate when the challenger's spec is only partially met?
(i) any spec violation ⇒ no pin (same as Qwen-down)
(ii) pin with visible GATE-DEGRADED flag
(iii) pin and log the miss for Sunday

Lean: (i) with a documented parent-scribe escape hatch.
