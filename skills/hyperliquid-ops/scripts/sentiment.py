#!/usr/bin/env python3
"""SENTIMENT — closes the one 9-family dimension the desk had NO automated script for.
Crypto Fear & Greed Index (alternative.me): free, no key, no auth. Read-only HTTP GET.
Does not gate any call by itself — logged as one input into the Sentiment family alongside
the human read (analyst posture, narrative tone), same as every other family in this desk.

Usage: python3 sentiment.py
Added 2026-08-17 (OLIVIER — gap found while auditing the live doctrine: Sentiment family had
no automated leg, only human read). Read-only, no keys, no exchange calls.
"""
import json, urllib.request, sys, time

FNG_URL = "https://api.alternative.me/fng/?limit=2"  # today + yesterday, for delta

def fetch():
    try:
        req = urllib.request.Request(FNG_URL, headers={"User-Agent": "hl-ops-desk/1.0"})
        return json.load(urllib.request.urlopen(req, timeout=10))
    except Exception as e:
        print(f"  (fear&greed fetch failed: {e})")
        return None

def main():
    d = fetch()
    if not d or "data" not in d or not d["data"]:
        print(json.dumps({"kind": "sentiment", "ok": False}))
        return
    today, prior = d["data"][0], (d["data"][1] if len(d["data"]) > 1 else None)
    val = int(today["value"]); cls = today["value_classification"]
    delta = (val - int(prior["value"])) if prior else None
    row = {
        "ts": int(time.time() * 1000), "kind": "sentiment", "source": "alternative.me_fng",
        "value": val, "classification": cls, "delta_1d": delta,
        "extreme": val <= 20 or val >= 80,   # matches desk's "Extreme fear/greed" language
    }
    print(json.dumps(row))
    tag = "EXTREME" if row["extreme"] else "normal"
    arrow = "" if delta is None else (f" (Δ{delta:+d})" if delta else " (flat)")
    print(f"  Fear&Greed: {val} [{cls}]{arrow} — {tag}. Logged as one Sentiment-family input; does not gate.")

if __name__ == "__main__":
    main()
