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

---
#085 — CROSS-CALL CONSISTENCY GAP + HORIZON-SCOPE DISCIPLINE (interactive Telegram session, Olivier correction) — 2026-08-17 11:37 UTC. Read-only; account untouched.

TRIGGER: the 10:49 UTC live BTC chat read (dn=63,001, ~24h horizon, tied to the 4h/1h wave-structure fib break) looked like it contradicted #084's standing swing-desk invalidation refinement (dn moved BELOW the 62k long-liq pool, per candidate lesson L1, on the #29→...→#084 continuous multi-day call). Olivier's correction, verbatim in spirit: two reads can BOTH be right when they are not on the same timeframe/schedule — a contradiction only exists when scope is shared and unstated, not whenever two price levels differ.

FINDING: these are not actually the same claim. #084's dn-below-62k-pool is the standing multi-day swing-desk invalidation. The 10:49 UTC call is a narrower, fresh read scoped to the CURRENT 4h/1h leg's own .786 fib break — a different horizon/call-family, not a restatement of the swing invalidation. Both were live simultaneously and both could be correct; the actual miss was that neither the chat reply nor the SCORE tag stated its own horizon/scope loudly enough for that to be obvious on read.

FIX (logged, PENDING Olivier sign-off before it becomes binding doctrine — human-approval gate unchanged): any BTC read carrying an invalidation level should (a) name which call-family/horizon it belongs to (intraday wave-structure vs standing swing-desk), and (b) be checked against calls.json's currently-OPEN calls on the same coin before being presented — flag explicitly if two OPEN invalidations disagree on the SAME horizon (a real contradiction) vs merely sit at different levels for different horizons (not one).

STANDING INFRA CONFIRMED LIVE (not new, just re-verified this session): automated disagreement detection already runs — contested_check.py (blind statistical divergence vs Grok-4.6, CONTESTED on sign-flip or >=20pp), redteam_packet.py (GPT-5.1 game-theory/market-maker adversarial packet: who's positioned against the call, the pain trade, what proves it wrong), coherence_packet.py (Gemini-3-Pro long-context check of a new call against the full ledger+doctrine history for contradictions with binding rules or killed patterns). All three run every 30min via cron job hlops-contested-flag and ping Olivier ONLY on a genuine CONTESTED/red-team/coherence finding, silent otherwise. This already satisfies "debate + game theory + awareness of disagreement" — confirmed operational, nothing new built.

OLIVIER-INPUT: correction logged — "often both can be right, just not on the same timeframe/schedule." Adopted as reasoning discipline this entry; promotion to a numbered binding rule pending next retro / explicit approval.

---

---
#086 — SILENT DIRECTION-FLIP CAUGHT BY OLIVIER + RECONCILED CALL (interactive Telegram session) — 2026-08-17 12:03 UTC. Read-only; account untouched.

MISTAKE (self-logged, Olivier caught it): two live chat reads of the SAME open call (#three in calls.json, up=64,579/dn=63,001, committed 10:49 UTC) gave the sequential path in OPPOSITE order four minutes apart — 11:25 UTC framed Move 1 = down-poke into 62,520–62,730 (favored) then Move 2 = up; 11:57 UTC framed Move 1 = up-push into 65,475–65,968 (favored) then Move 2 = down-reject — with NO explicit statement that the primary direction had flipped. There was a real, evidenced trigger (5m volume +965% with CVD confirming at 11:57 vs FADING/DIVERGING at 11:25), but doctrine #7 (continuity: state how scenarios evolved, delta not restart) requires calling that out explicitly. It wasn't. By 12:01 UTC the burst had already faded back to FADING/DIVERGING on both 5m and 1h — the up-first flip was itself the fake, resolved in under 4 minutes.

RECONCILED CALL (Olivier-confirmed as the standing read, 12:03 UTC): reverts to the ORIGINAL down-first sequential path from 11:25, now stated as a delta (whipsaw rejected, not a restart).
- MOVE 1 (favored ~55%): down-poke into 62,520–62,730 (strongest confluence all session, unchanged) — mechanism: unbacked pushes both directions, no positioning crowd, this is the L1 "spring" pool (wick+reclaim ≠ break).
  invalidation: hourly acceptance below ~62,000 with no reclaim.
- MOVE 2 (conditional on Move 1 tagging the pool, ~58%): reclaims/bounces toward 63,474–63,500, then 65,475–65,968 on further acceptance.
  invalidation: fails to reclaim, accepts <62,000 → trend-down not a bounce.
- Tripwire: 63,001 (px 63,599 at reconciliation time, just above it — Move 1 not yet triggered).

PROCESS FIX (binding on every future read, not just this one): any time a call's PRIMARY direction/order changes from the immediately prior read of the SAME open call, state that explicitly as "reversed from the Xh:XXm read because Y changed" — never silently present a differently-ordered path as if it were the only read given. A whipsaw that reverses within minutes should be named as a whipsaw, not upgraded to a new primary on one data point.

---

---
#087 — P2 LIQ-MAP CONFIRMS 61,868 LONG-LIQ CLUSTER (Olivier-supplied Coinglass screenshot) — 2026-08-17 12:12 UTC. Read-only; account untouched.

Olivier asked why the desk wasn't tagging "the massive 61.8k liquidity" and supplied a Coinglass cumulative-liquidation heatmap screenshot (current price 63,579 marked). The chart shows a sharp step-down in the cumulative LONG-liquidation curve concentrated at ~61,868.74 — a real, sizeable cluster, confirmed visually, not a small/noise entry.

GAP IDENTIFIED: the desk's automated `collector.jsonl` liq-map ticks (checked first, incorrectly reported "nothing massive near 61,800") only scan ~115–124 Hyperliquid addresses directly — a thin, venue-local sample. This Coinglass picture is a SEPARATE, cross-exchange, leverage-ESTIMATED dataset (per doctrine #27: single-exchange Binance + 24h + Model-1 estimation, not literal resting orders) with a much larger effective sample. The two pictures are not interchangeable and neither is a substitute for the other; this session only pulled the HL-collector one before Olivier supplied the Coinglass view.

STRUCTURAL REASON THIS ISN'T AUTOMATIC (per doctrine #27's own automation caveat, re-confirmed): P2 liq-map capture requires an interactive browser session (extension + decrypt hook) and is INTERACTIVE-ONLY — scheduled/headless cron firings have no browser and cannot fetch this layer on their own. It only enters a read when a human pastes/screenshots it, as happened here. Not a bug in the automated pipeline; a known, documented capability boundary.

RECONCILIATION WITH THE STANDING CALL (#086): does NOT contradict it — REINFORCES it. 61,868 sits almost exactly on the desk's pre-existing historical invalidation line (61,900–62,000, lesson L1: drawn below the pool so a wick-and-reclaim scores as correct, not a loss) and sits BELOW Move 1's target shelf (62,520–62,730). Read: 62,520–62,730 is the shallow spring target; 61,868 is the deeper magnet/pool if that shallow shelf fails to hold — consistent nested structure, not two competing levels.

ACTION: current call's Move-1 down-side context is amended to explicitly name 61,868 (Coinglass-confirmed cluster) as the secondary/deeper downside magnet below the primary 62,520–62,730 shelf, should Move 1 extend past the shallow shelf without reclaiming.

---

---
#088 — "BIGGER POOL = HIGHER-PROB TARGET" CHALLENGED AGAINST RULE #24 (interactive session) — 2026-08-17 12:15 UTC. Read-only; account untouched.

Olivier asked whether the 61,868 Coinglass cluster (#087) should be read as a HIGHER-probability target than stopping at the 62,520–62,730 shelf, given its size. Two things reconciled:

(1) UPGRADE: 61,868 is not purely a liq-map estimate — `structure.py`'s own mechanical output independently shows 61,645–61,880 as a real confluence zone (score 84, TL-sup + swingL, TFs 1d/1h). Two independent observation families (structure + cross-venue liq-map) landing near the same price is genuine confluence — stronger secondary-target case than #087 gave it credit for.

(2) PUSHBACK (not adopted): "bigger pool pulls price past the nearer shelf" is the specific claim rule #24 (T-002 Test A + T-003) already tested and REJECTED — 0/4 tests, no price-observable clustering at liquidation radii across BTC/ETH/SOL; leverage is dynamic (top-ups/cross-margin/partial closes) enough that static pool-size does not predict where price travels. Elevating 61,868 to PRIMARY over 62,520–62,730 on size alone would re-adopt a mechanism this desk's own backtest killed.

RESOLUTION: 62,520–62,730 stays Move-1 PRIMARY (score 390 vs 84, 4 TFs vs 2 — the harder evidence). 61,868 is upgraded from vague-secondary to a real, dual-confirmed secondary target (own structure + liq-map, not just "a deeper magnet if the shelf fails"). Standing call's target levels/probabilities UNCHANGED; only the evidentiary weight behind the secondary target is strengthened and now correctly cites both supporting rules and the rule that bounds it.

---

---
#089 — GEMINI COHERENCE CHECK CAUGHT A REAL L1 VIOLATION — invalidation drifted above the pool it names — 2026-08-17 15:28 UTC. Read-only; account untouched.

As part of Olivier's "bulletproof test" (independent Grok blind-audit + GPT-5.1 red-team + Gemini-3-Pro coherence check, each asked to show full reasoning, not just a verdict, run against the live open call), the coherence check flagged a genuine contradiction: the call's stated invalidation ("hourly acceptance <62,000, no reclaim") sits ABOVE the top of its own named secondary pool (61,821-61,976, Coinglass 61,868 per #087). L1 (lessons.json candidate, applied #084, cited #087) requires the invalidation sit BELOW the pool it's scored against, specifically so a wick-into-the-pool-then-reclaim scores as a correct spring/reclaim call, not a loss.

ROOT CAUSE: the invalidation figure (62,000) was carried forward unchanged from #086, written when the pool was only loosely described (~61,900-62,000). #087 later pinned the pool precisely at 61,821-61,976/61,868 — but nobody re-applied L1's placement rule to the refined number, so the invalidation silently drifted from roughly-at-the-pool to clearly-above-it.

VERIFIED by re-reading `data/lessons.json` L1 text directly and comparing to the call's stated invalidation and pool figures — not taken on the subagent's say-so alone.

FIX APPLIED: invalidation on the live call is corrected to sit BELOW the named pool — "hourly acceptance below ~61,800 (below the 61,821-61,976 pool), no reclaim" — so a wick-and-reclaim of the pool itself scores correctly per L1. up/dn/p_up/targets unchanged; only the invalidation wording is corrected.

PROCESS LESSON: whenever a pool/level gets re-pinned more precisely (as #087 did), the invalidation line for any OPEN call referencing that pool must be re-checked against L1, not left at its original looser wording. Added as a standing check, not just a one-off fix.

---

---
#090 — 4-WAY REASONING AUDIT (Grok blind + GPT-5.1 red-team + Gemini coherence + own trail) + DYNAMIC MULTI-LEG SCENARIO + PRIMARY-LEAN DELTA — 2026-08-17 15:33 UTC. Read-only; account untouched.

Olivier's "bulletproof test": ran the full independent-reasoning bundle (doctrine's actual disagreement-handling infra — blind audit + adversarial red-team + coherence check, not voting) and reviewed each trail's SPECIFIC claims against what's actually happened, not just each one's p_up number.

GRADES:
- Grok (blind, zero exposure to our thesis/levels): p_up=0.47, up=65,000, dn=62,600 — near coin-flip, explicitly flagged funding-regime ambiguity (squeeze-vs-distribution, undecidable from a single snapshot) as its reason for pulling toward 50/50. ITS dn LANDED INSIDE our primary shelf (62,499-62,730) and up LANDED AT THE EDGE of our Move-2 zone (65,050-65,155) — independent confirmation of the same boxes from zero shared data. Real signal.
- GPT-5.1 (red-team, given the call, argued against it): named the mechanism precisely — squeeze through 64,427-64,746 (the single largest cluster on the board, $2.88M) into 65,700, skipping Move1's down-leg entirely, right target box via wrong path. CURRENTLY THE BEST-PERFORMING TRAIL: mark has moved from 63,579 (call's context at commit) to 64,011 without the down-leg ever firing, tracking toward exactly this cluster.
- Gemini (coherence): found the real L1 invalidation-placement defect, already fixed as #089. Not directional, but the most concretely useful output of the four — caught an actual process bug, not an opinion.
- Own trail: weakest directional performer this session — held down-first as primary through 12:15; price has not delivered that leg as of this entry.

DYNAMIC MULTI-LEG SCENARIO (Olivier): proposed a 4-leg chop before resolution — up-leg stalls just below the 64,427-64,746 cluster (~64,300-400) without fully triggering it → down-leg to just ABOVE 61,821-61,976 (probe, not full tag) → back up to retest ~64,400 → genuine down-leg to actually tag 61,868. Logged as a live alternate path, consistent with doctrine (scenarios are dynamic/re-evaluated every pulse, not fixed at commit) — more legs than the 2-move minimum format, still sequential/conditional, not a fork.

PRIMARY-LEAN DELTA (stated explicitly per #086 discipline, not silently restated): given price has moved from 63,579 to 64,011 since commit with NO down-leg firing, and GPT-5.1's squeeze mechanism is the trail best matching actual price behavior so far, the up-first/squeeze-through-64,746 path is elevated to CO-EQUAL with the original down-first primary, not left as an also-mentioned alternate. This is a genuine change from the framing held through 12:15-15:16 — named as such, with the evidence (price action + red-team trail performance) that drove it, per the binding continuity rule.

STANDING PATH (revised): Path A (~50%, was primary): down-poke 62,499-62,730 → (if fails) 61,821-61,976 → reclaim toward 63,474+/65,475+. Path B (~50%, elevated from alternate): squeeze through 64,427-64,746 → 65,475-65,983, skipping the down-leg. Tripwires: 63,001 (below = Path A live), 64,746 acceptance (above = Path B live/confirmed). Invalidation for Path A's deep leg: below ~61,800 (per #089 fix).

---

---
#091 — SKILL_WORKSHOP "update" APPLY OVERWRITES FULL SKILL.md INSTEAD OF APPENDING — confirmed TWICE, standing verification check now mandatory — 2026-08-17 15:47 UTC. Read-only re: trading; tooling process fix.

SECOND occurrence today of the same bug: `skill_workshop(action="apply")` on an "update" proposal replaces SKILL.md's entire content with just the new `proposal_content`, rather than merging/appending it into the existing doctrine. First occurrence: the "2 next moves" sequential-path amendment this morning wiped doctrine #1-59 down to 54 lines (caught ~15:20 UTC while investigating an unrelated cron bug, fixed via git rollback.json + manual append, committed 1315a44). Second occurrence: the "ON THE LINE" exhaustion/continuation-check amendment (15:45 UTC) wiped the just-restored 936-line doctrine down to 47 lines/0 rules again — caught immediately this time (verified via `wc -l` + doctrine-rule grep BEFORE trusting the apply result), fixed the same way, committed 808b251.

Olivier confirmed ("yes"): this must become a standing, permanent check — not something relied on being remembered case-by-case.

STANDING RULE (binding, applies to every future skill_workshop apply on this skill, logged here AND in TOOLS.md):
1. BEFORE any skill_workshop apply on hyperliquid-ops: record `wc -l SKILL.md` and doctrine-rule count (`grep -c "^[0-9]\+\. \*\*" SKILL.md`).
2. AFTER apply: re-run both checks. If line count or rule count dropped sharply (not just the expected small addition), the apply overwrote instead of merging — treat as a live incident, not a maybe.
3. If overwritten: pull `/root/.openclaw/skill-workshop/proposals/<id>/rollback.json`'s `previousContent`, combine with the new proposal's body (strip its own frontmatter), write back, verify counts again, commit to git with a clear message naming this as a recurrence.
4. Never assume a clean apply just because the tool call itself returned success — the tool's success response does not mean the merge was correct.

This is a tooling-safety gap in `skill_workshop`, not a doctrine issue — raised here for the record; the actual root-cause fix (upstream tool behavior) is outside this skill's scope, so the verification habit is the mitigation until/unless that's addressed.

---

---
#092 — call_evolve.py reports MOVE 2 PROGRESS AS IF PRIMARY — script has no sequential-path awareness (real bug, not just orchestrator quality) — 2026-08-17 16:02 UTC. Read-only; account untouched.

Olivier caught: the 16:00 UTC call-evolve report said "price has moved 72% of the way toward the up target" and framed this as STRENGTHENED/bullish-leaning, while the live call's Move 1 (per doctrine, must happen FIRST) is a DOWN-poke to 62,499-62,730. The script put "the second move ahead" of the first — exactly the fork-vs-path error the morning's amendment was supposed to kill, but reintroduced by the SCRIPT itself, not just by narrative framing.

ROOT CAUSE (verified in scripts/call_evolve.py): `pos_in_range` is computed purely from the raw up/dn pair stored in calls.json (64,579/63,001) with NO knowledge of the sequential Move1(down)/Move2(up-conditional) structure this call actually carries. It cannot distinguish "price approaching the up-target directly (bullish)" from "price approaching the up-target by SKIPPING Move 1's down-leg entirely (the alternate/squeeze path, #090)" — both currently look identical to this script's math. It just reports raw distance-to-up as "STRENGTHENED" regardless of which path produced it.

SEPARATE FROM (but surfaced alongside) the Haiku orchestration-quality issue: same job's 16:00 UTC run also sent a message despite its own text concluding "No messaging required per doctrine #10" — a distinct reliability failure. Olivier's call: revert BOTH hlops-call-evolve and hlops-contested-flag orchestration from Haiku 4.5 back to Sonnet-5 ("i prefer the orchestrator is the best") — cost savings not worth it if judgment quality suffers on a job whose entire point is deciding when to interrupt Olivier. Applied immediately.

STANDING FOLLOW-UP (not yet fixed): call_evolve.py itself needs a structural update to carry the call's Move1/Move2 sequence (not just up/dn/p_up) so its `reason` string can correctly say something like "66% toward Move 2's target, but this requires Move 1 (62,499-62,730 down-poke) to have fired first — it has NOT, so this progress is via the ALTERNATE squeeze path (#090), not confirmation of the primary sequence" instead of reporting raw distance as unqualified STRENGTHENED. Flagging as an open script-level gap, separate from the orchestration-model choice.

---

---
#093 — On-demand 3-model cross-check (post-cron-disable), squeeze-alternate lean downgraded on short-conviction evidence — 2026-08-17 16:52 UTC. Read-only; account untouched.

First on-demand cross-check run after disabling hlops-contested-flag's cron (per Olivier's cost-reduction decision this session): confirms the desk can still get the same 3-model safety net (Grok blind-audit / GPT-5.1 red-team / Gemini coherence) by spawning it manually alongside a "next 2 moves" ask, at zero idle cost between asks. Olivier's explicit call: "we can do the cross check anyways" — now the default going forward.

Results on the standing call (ts=1786963783916, up=64,579/dn=63,001/p_up=0.56, Move1 down-poke 62,494-62,730 -> Move2 reclaim to 65,475-65,987, co-equal alternate squeeze through 64,427-64,746):
- Grok blind audit: p_up=0.54, up=65,400, dn=62,900 — independently landed inside the same zone, no divergence, not contested.
- GPT-5.1 red-team: MATERIAL FINDING. Shorts have built for the full 72h drift window with zero positive-funding hours, deepening premium (-3.05bp->-4.23bp), and still-rising OI — a persistent, conviction-funded short book, not weak hands near capitulation. The near-price short-liq clusters at the squeeze zone (~$4.2M combined at 64,757/66,039) are trivial against $2.78B OI / $1.78B daily volume — not enough fuel to force a clean cascade. Read: expect repeated REJECTION near 64,400-64,700 rather than a clean squeeze-through.
- Gemini coherence check: NO CONTRADICTION vs doctrine (#2 two-scenario format, L1/#089 invalidation placement, #085 frozen-commit discipline) or ledger continuity (#090's standing path).

ACTION: no change to up/dn/p_up (frozen commit stays frozen per #085). But the PRIMARY-vs-ALTERNATE split is adjusted from genuinely co-equal (50/50, set in #090) to A LEAN toward primary: ~55% down-poke-first / ~45% squeeze-alternate, on the specific evidence that the short side funding this squeeze zone looks too well-capitalized to fold easily. This is a probability-lean delta on the ALTERNATE path only, not a reversal of the primary thesis — flagged per #086 discipline since it changes the relative weighting of an already-open call's paths.

---

---
#094 — On-demand 3-model cross-check (post-call, not blocking) run on the standing call — 2026-08-17 16:49-16:52 UTC. Read-only; account untouched.

Context: earlier today all 4 hlops crons (collector, call-evolve, contested-flag, sunday-retro) were disabled per Olivier's cost directive (~$200/day → ~$200/month target). Olivier asked whether the 3-model cross-check (previously auto-fired by hlops-contested-flag) could still happen "anyways" without the standing cron — confirmed yes: run it manually, on-demand, folded into/after a "next 2 moves" ask, rather than 24/7 background polling. New default going forward: call delivered first, cross-check runs after (non-blocking), only when asked — costs money only on actual asks, not idle.

Results on the standing call (ts=1786963783916, up=64,579/dn=63,001/p_up=0.56, Move1 down-poke 62,494-62,730 → Move2 reclaim 65,475-65,987, co-equal alternate squeeze through 64,427-64,746 skipping Move1):

- **Grok-4.6 blind audit** (raw numbers only, no thesis/narrative given): p_up=0.54, up=65,400, dn=62,900 — independently landed in the same zone as the desk's own call. NOT CONTESTED (divergence well under the 20pp/#57 threshold).
- **GPT-5.1 red-team** (given the actual call, argued the incentive case against it): MATERIAL FINDING. Shorts have built a persistent, self-funded book for 72h straight — 0 positive-funding hours, premium intensifying -3.05bp→-4.23bp, OI still rising (not capitulating). The near-price short-liq clusters that would fuel a clean squeeze (~$4.2M combined at 64,757/66,039) are trivial against $2.78B OI / $1.78B 24h volume — not a forcing mechanism at this size. Read: expect repeated REJECTION near 64,400-64,700 rather than a clean squeeze-through. This specifically threatens the ALTERNATE/co-equal squeeze leg, NOT the primary down-poke-first thesis.
- **Gemini-3-Pro coherence check** (full doctrine+ledger review): NO CONTRADICTION. Sequential-path-with-alternate format matches the Aug-17 amendment (rule #2, two-scenarios-max); L1 invalidation placement (#089) respected; up/dn/p_up match the frozen original commit (no #085 violation); faithful continuation of the last standing read (#090), no silent direction flip.

ACTION: no change to up/dn/p_up (frozen commit stays frozen per #085). But the PRIMARY-vs-ALTERNATE split is adjusted from genuinely co-equal (50/50, set in #090) to A LEAN toward primary: ~55% down-poke-first / ~45% squeeze-alternate, on the specific evidence that the short side funding this squeeze zone looks too well-capitalized to fold easily. This is a probability-lean delta on the ALTERNATE path only, not a reversal of the primary thesis — flagged per #086 discipline since it changes the relative weighting of an already-open call's paths.

---

_(next entry will be #095, appended below this line and committed)_
