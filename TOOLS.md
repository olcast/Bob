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

## Related

- [Agent workspace](/concepts/agent-workspace)
