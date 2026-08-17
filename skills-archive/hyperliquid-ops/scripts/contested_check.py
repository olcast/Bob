#!/usr/bin/env python3
"""CONTESTED AUTO-FLAG (doctrine #57) — compares two live SCORE records (e.g. Sonnet-5 desk call vs. a blind
Grok-4.6 audit call, same coin, close in time) and flags CONTESTED when they materially disagree, BEFORE either
one resolves. This is the pre-resolution sibling of leaderboard.py's post-hoc CONTESTED detection: leaderboard.py
scores who-won-the-disagreement AFTER outcomes are known; this script exists to raise the flag the moment a
firing happens, so Olivier gets pinged in real time instead of finding out on the next Sunday retro.

Trigger conditions (either is sufficient):
  - |p_up_a - p_up_b| >= threshold (default 0.20, i.e. 20 percentage points)
  - direction flip: one call leans up (p_up>0.5) and the other leans down (p_up<0.5) at all (a "sign" disagreement,
    regardless of magnitude — this is the doctrine's "material cross-desk disagreement" case, not just distance)

Does NOT grade who is right (that requires resolve() from calibration.py after the window matures — leaderboard.py
does that later). This script is a NOTIFICATION trigger only, read-only, no auto-edits to doctrine or the ledger.

Usage:
  python3 contested_check.py call_a.json call_b.json [--threshold 0.20]
  echo '{"p_up":0.55,"up":63474,"dn":61900,"by":"Claude"}' > /tmp/a.json
  echo '{"p_up":0.30,"up":63500,"dn":62000,"by":"Grok"}'   > /tmp/b.json
  python3 contested_check.py /tmp/a.json /tmp/b.json
Exit code: 0 = not contested, 1 = CONTESTED (so cron/automation can branch on it without parsing text)."""
import json, sys, argparse

def load(path):
    return json.loads(open(path).read())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("call_a")
    ap.add_argument("call_b")
    ap.add_argument("--threshold", type=float, default=0.20)
    args = ap.parse_args()

    a = load(args.call_a)
    b = load(args.call_b)
    pa, pb = float(a["p_up"]), float(b["p_up"])
    by_a = a.get("by", "A")
    by_b = b.get("by", "B")
    diff = abs(pa - pb)
    sign_flip = (pa - 0.5) * (pb - 0.5) < 0
    contested = diff >= args.threshold or sign_flip

    print(f"CONTESTED CHECK — {by_a} p_up={pa:.0%} (up={a.get('up')}, dn={a.get('dn')})  vs  "
          f"{by_b} p_up={pb:.0%} (up={b.get('up')}, dn={b.get('dn')})")
    print(f"  divergence: {diff:.0%}  (threshold {args.threshold:.0%})  ·  sign-flip: {sign_flip}")

    if contested:
        reason = []
        if diff >= args.threshold:
            reason.append(f"divergence {diff:.0%} >= threshold {args.threshold:.0%}")
        if sign_flip:
            reason.append("directions disagree (one leans up, one leans down)")
        print(f"  >>> CONTESTED ({', '.join(reason)}). Flag for Olivier — this is a high-information moment "
              f"per doctrine #57, worth a real look, not a default-null.")
        sys.exit(1)
    else:
        print("  not contested — desks broadly agree, no flag raised.")
        sys.exit(0)

if __name__ == "__main__":
    main()
