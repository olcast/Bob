#!/usr/bin/env python3
"""ENTRY-PROXIMITY TRIGGER (orchestration fix #1 + #3, 2026-08-18).

The fleet fires producer/challenger on a TIME schedule, but the scenarios now have
EVENT-DRIVEN triggers (15m close < 63,930). This script decides whether the live entries
are NEAR, and if so, signals a faster wake — so the machines wake WHEN the trigger is
near, not on a blind timer.

Reads data/state.json (the canonical object), pulls the current BTC mark, and compares
distance to every live entry level. Output:
  - a JSON decision {proximity: "hot"|"warm"|"cold", distance_pct, entries:[...]}
  - exit 0 = hot/warm (release faster cadence), exit 1 = cold (blind-timer default)

The level-watch cron's trigger script calls this; when it returns "hot", the watch job
drops from 30m to 5m until resolved (implemented in the cron trigger script, not here —
this script is the pure proximity decision).

Usage:
  entry_proximity.py            # decision on stdout + exit code
  entry_proximity.py --hot <pct>   # hot threshold as a FRACTION (default 0.002 = 0.2%)
"""
import json, os, sys, time, urllib.request

D = os.path.join(os.path.dirname(__file__), "..", "data")
F_STATE = os.path.join(D, "state.json")
API = "https://api.hyperliquid.xyz/info"
HOT = 0.002  # within 0.2% = hot


def post(b):
    r = urllib.request.Request(API, data=json.dumps(b).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r, timeout=40))


def get_mark():
    try:
        return float(post({"type": "allMids"})["BTC"])
    except Exception:
        return None


def parse_price(s):
    """Pull the first numeric price out of an entry string like '15m close below 63,930'."""
    import re
    if s is None:
        return None
    t = str(s).replace(",", "")   # strip thousands separators (63,930 -> 63930)
    m = re.search(r'(\d{4,6})', t)
    return float(m.group(1)) if m else None


def main():
    if "--hot" in sys.argv:
        global HOT
        HOT = float(sys.argv[sys.argv.index("--hot") + 1])
    state = {}
    if os.path.exists(F_STATE):
        try:
            state = json.load(open(F_STATE))
        except Exception:
            state = {}
    entries = state.get("entries", []) or []
    mark = get_mark()

    if mark is None or not entries:
        print(json.dumps({"ok": False, "proximity": "unknown", "mark": mark}))
        sys.exit(1)

    dists = []
    for e in entries:
        p = parse_price(e.get("entry"))
        if p is None:
            continue
        d = abs(mark - p) / mark
        dists.append({"move": e.get("move"), "entry": e.get("entry"), "price": p, "dist_pct": round(d * 100, 3)})

    mind = min((d["dist_pct"] for d in dists), default=None)
    if mind is None:
        print(json.dumps({"ok": False, "proximity": "unknown", "mark": mark}))
        sys.exit(1)

    prox = "hot" if mind <= HOT * 100 else ("warm" if mind <= HOT * 100 * 3 else "cold")
    print(json.dumps({"ok": True, "mark": mark, "proximity": prox, "min_dist_pct": round(mind, 3), "entries": dists}))
    # NOTIFY semantics: ONLY "hot" (within HOT) is a user-facing trigger. "warm" is a
    # cadence hint (wake faster), NOT a notify. Exit 0 = should wake faster (hot OR warm);
    # the notify decision is made by the calling agent reading the "proximity" field, not
    # by this exit code. (Fixes the recurring "warm ping" leak: warm stayed in the exit-0
    # band AND the agent treated exit-0 as 'notify', so any 0.2-0.6% proximity notified.)
    sys.exit(0 if prox in ("hot", "warm") else 1)


if __name__ == "__main__":
    main()
