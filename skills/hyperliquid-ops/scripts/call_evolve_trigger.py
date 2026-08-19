#!/usr/bin/env python3
"""Headless trigger for the cross-check (and call-evolve) cron.

Olivier 2026-08-19: the cross-check must ALWAYS produce a call — never abort to silence.
Old behavior returned {fire: false} when no open call existed, and the cross-check treated
that as "stop silently", which starved the desk of fresh reads exactly when it needed one.

NEW semantics — return a MODE, not a boolean:
  {"mode": "fresh",  "open_count": 0, ...}  -> no open call: originators generate a NEW call
  {"mode": "evolve", "open_ts": [...], ...} -> >=1 open call: originators EVOLVE the open one(s)

An OPEN call = now < ts + h*3600s (horizon not elapsed) AND neither up nor dn target reached.
Read-only: reads calls.json + a single mark fetch; touches nothing.

Usage: python3 call_evolve_trigger.py   -> prints {"mode": "fresh"|"evolve", ...}
"""
import json, os, time, urllib.request, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CALLS = os.path.join(HERE, "..", "data", "calls.json")
API = "https://api.hyperliquid.xyz/info"

def load_calls():
    try:
        return json.loads(open(CALLS).read())
    except Exception:
        return []

def get_mark(coin="BTC"):
    try:
        req = urllib.request.Request(
            API,
            data=json.dumps({"type": "allMids"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        d = json.loads(urllib.request.urlopen(req, timeout=20).read())
        return float(d.get(coin))
    except Exception:
        return None

def main():
    calls = load_calls()
    now = int(time.time() * 1000)
    mark = get_mark()
    open_tss = []
    for c in calls:
        ts = int(c.get("ts", 0))
        h = int(c.get("h", 0))
        end = ts + h * 3600000
        if now >= end:
            continue  # horizon elapsed => not open
        up = float(c.get("up", 0))
        dn = float(c.get("dn", 0))
        if mark is not None and (mark >= up or mark <= dn):
            continue  # already resolved
        open_tss.append(ts)

    if open_tss:
        print(json.dumps({"mode": "evolve", "open_count": len(open_tss), "open_ts": open_tss, "mark": mark}))
    else:
        print(json.dumps({"mode": "fresh", "open_count": 0, "mark": mark}))

if __name__ == "__main__":
    main()
