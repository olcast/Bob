# HL-OPS CALLS LEDGER — git-tracked primary (replaces Gmail draft)

**Status as of 2026-08-17: this file is now the primary, append-only ledger of record.**

Why the switch from the Gmail draft ("machine-updated, do not send"):
- Gmail draft has no version history, no diff, no locking — a single accidental overwrite (see #058
  clobber incident) can silently destroy history with no recovery path except a stale Drive backup.
- This environment cannot write to Gmail directly at all — every update required Olivier to
  manually paste the whole ledger back and forth, which is slow and itself a source of drift
  (local mirrors going stale vs. the real primary, exactly what caused the v3.1.1 vs v3.2.20
  confusion this session).
- A git-tracked file gets: full diffable history for free (`git log -p`), append-only by convention
  AND by tooling (commits, not overwrites), and direct write access for the desk/automation without
  a human copy-paste round-trip.

**How this works now:**
- Every new ledger entry (#085+) gets appended to this file and committed with a message like
  `ledger: #085 <short description>`.
- `git log --oneline -- skills-archive/hyperliquid-ops/references/ledger-live/LEDGER.md` gives the
  full entry-by-entry history — better than any version-number header.
- Olivier can still paste raw Gmail/Drive content for cross-checking at any time; it gets appended
  to `GMAIL-LEDGER-LIVE-PASTE-2026-08-17.md` (kept as a raw-paste audit trail) and reconciled here.
- No remote configured yet (local commits only) — if Olivier wants remote access (phone, other
  machines), add a private GitHub repo and `git push`. Until then this is local-only, single-writer
  (the desk/assistant), reviewed by Olivier via chat/Telegram.
- Human-save/approval gate is UNCHANGED: automation (discovery_loop.py, calibration.py,
  leaderboard.py) still only PROPOSES; promotions to doctrine.json still require Olivier's explicit
  approval before being committed as a doctrine change. Git tracking changes *how* the ledger is
  stored and diffed — it does not change *who* can approve a doctrine promotion.

---

## Full entry history (#000–#084)

Full verbatim entries #000–#084 are preserved as received, in:
- `HL-OPS_CALLS_LEDGER_2026-08-17_0842UTC_through-084.txt` (raw paste, #077–#084, v3.2.20 — the
  authoritative live-primary content as of the Gmail→git migration)
- `GMAIL-LEDGER-LIVE-PASTE-2026-08-17.md` (annotated mirror, same content + notes)
- Drive backup `HL_OPS_LEDGER_BACKUP_v3_1_1...txt` (#000–#059, stale fallback, kept for history only)

This LEDGER.md file is where **new entries (#085 onward)** get appended going forward, so the
active tail of the ledger lives in one clean git-tracked place instead of being re-pasted each time.

---

## Entries (#085+)

_(none yet — next entry will be #085, appended below this line and committed)_
