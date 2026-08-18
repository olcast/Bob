# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup: camera names and locations, SSH hosts and aliases, preferred TTS voices, speaker/room names, device nicknames, anything environment-specific.

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

### skill_workshop — verify every apply, don't trust the success response

Confirmed TWICE on 2026-08-17 (hyperliquid-ops skill): `skill_workshop(action="apply")` on an
"update" proposal can overwrite the ENTIRE target SKILL.md with just the new proposal_content,
instead of merging/appending it into existing doctrine. The tool call itself returns success in
both cases — a clean return does NOT mean the merge was correct.

**Standing rule — before/after EVERY skill_workshop apply on any skill with substantial existing
content:**
1. Before: `wc -l <skill>/SKILL.md` (and any other rough size signal specific to that skill).
2. Apply.
3. After: re-run the same check. If size dropped sharply instead of growing by roughly the
   proposal's size, the apply overwrote instead of merging — treat as a live incident, not a maybe.
4. If overwritten: pull `/root/.openclaw/skill-workshop/proposals/<id>/rollback.json`'s
   `previousContent`, combine with the new proposal's body (strip its own frontmatter), write back,
   re-verify, commit to git with a clear message.

See hyperliquid-ops ledger entry #091 for the full incident record.

---

Add whatever helps you do your job. This is your cheat sheet.

## Model providers (key inventory + "best model" policy)

**Policy: always use the very best model on each provider.** Discovered + confirmed 2026-08-18.

**DeepSeek** (`api.deepseek.com`, OpenAI-compatible) — 2 models on key:
- `deepseek-v4-pro` ← **BEST / flagship** (use this; it's the primary + agent default)
- `deepseek-v4-flash` (cheap/fast, use only for low-stakes or bulk)

**Moonshot / Kimi** (`api.moonshot.ai/v1`, config baseUrl has `/v1`) — 4 models on key:
- `kimi-k3` ← **BEST / flagship** (but see reliability note below)
- `kimi-k2.6` — previous-gen general model
- `kimi-k2.7-code` — code-specialized
- `kimi-k2.7-code-highspeed` — code-specialized, fast

**Reliability note (Kimi/Moonshot):** on 2026-08-18 kimi-k3 failed a full-stack review twice, once with
`engine_overloaded` (429) and once with `request reached max organization concurrency: 1`. The Moonshot
org has a **concurrency limit of 1** — so DeepSeek + Kimi cannot run truly in parallel; overlapping Kimi
calls will serialize or collide-error. Don't assume a Kimi failure means the model is bad; check for the
concurrency/overload error string first before judging.

**Cross-check / recursive-verify rule:** for important outputs (market reads, reviews, decisions), produce
with one model and independently challenge/verify with a second — do not trust a single model's blind spot
(the 2026-07-26 confirmation-bias miss is the standing lesson).

## Operating & prompting discipline (from Olivier's Claude export, 2026-08-18)

Distilled from his "How to use Claude" guide. These map onto SOP-RECURSIVE.md; the durable ones
I should keep applying even without being asked:

- **Be clear & specific up front** — state the task, then give context, then break complex work into steps.
- **Prefer examples** — show the target output shape if a format/style matters.
- **Encourage explicit reasoning** — "think step-by-step / explain your reasoning" for complex reads (maps to the adversarial cross-check).
- **Iterate** — a first pass is rarely final; refine on "close, but adjust X."
- **Role-play for red-team** — adopt the counterparty/blind reviewer's perspective to stress-test a thesis.
- **Specify output structure** — headings, bullets, tables, exact metrics when it matters.
- **Admit uncertainty** — say "unverified / don't know" rather than fabricate (SOP §6).
- **Include full context each time** — no cross-session memory assumption (drives the KG/memory work).

These are *how to prompt me* AND *how I should operate* — the arrow points both ways.

## Related

- [Agent workspace](/concepts/agent-workspace)
