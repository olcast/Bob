#!/usr/bin/env python3
"""Headless trigger for the hlops-call-evolve cron: returns a JSON {fire: true/false} so the job
only wakes the agent when there is actually an OPEN call to evolve. Prevents ~96 empty 15-min runs/day
when calls.json has no unresolved call (nothing to track => skip, save tokens). Fire condition: at
least one call where now < ts + h*3600s (horizon not yet elapsed) AND neither up nor dn target has been
reached yet (still OPEN). Read-only: reads calls.json + a single mark fetch; touches nothing.

Usage: python3 call_evolve_trigger.py   -> prints {"fire": true} or {"fire": false}
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
    fire = False
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
        fire = True
        break
    print(json.dumps({"fire": fire}))

if __name__ == "__main__":
    main()
