#!/usr/bin/env python3
"""
macro_preflight.py — mandatory pre-flight before any level call or trade idea.

Purpose: turn "don't explain the price away" from an intention into a stop
condition. It prints a timestamped cross-asset snapshot, flags every asset
moving more than a threshold, checks a short list of macro relationships that
should hold, and emits a VOID / CLEAR verdict.

The verdict is not a trade signal. It answers one question: am I allowed to
start talking about levels yet, or is there an unexplained move I have to go
find a story for first?

Usage:
    python3 scripts/macro_preflight.py
    python3 scripts/macro_preflight.py --thesis risk-on
    python3 scripts/macro_preflight.py --thesis risk-off --threshold 1.5
    python3 scripts/macro_preflight.py --json

Read-only. Public info endpoint only. Never touches /exchange.
"""

import argparse
import datetime
import json
import sys
import urllib.request

API = "https://api.hyperliquid.xyz/info"

# The macro complex. Commodities and FX are the tell; the index is the follower.
# (label, coin, dex)  dex "" = main perp dex
MACRO = [
    ("Brent (HL basis ~-$10)", "xyz:BRENTOIL", "xyz"),
    ("WTI",                    "xyz:CL",       "xyz"),
    ("Energy equities",        "xyz:XLE",      "xyz"),
    ("Gold",                   "xyz:GOLD",     "xyz"),
    ("Silver",                 "xyz:SILVER",   "xyz"),
    ("Dollar index",           "xyz:DXY",      "xyz"),
    ("Euro",                   "xyz:EUR",      "xyz"),
    ("Yen",                    "xyz:JPY",      "xyz"),
    ("S&P 500",                "xyz:SP500",    "xyz"),
    ("Nasdaq-ish",             "xyz:XYZ100",   "xyz"),
    ("Nikkei",                 "xyz:JP225",    "xyz"),
    ("Korea 200",              "xyz:KR200",    "xyz"),
    ("VIX",                    "xyz:VIX",      "xyz"),
    ("Bitcoin",                "BTC",          ""),
    ("Ether",                  "ETH",          ""),
    ("Solana",                 "SOL",          ""),
    ("Hyperliquid",            "HYPE",         ""),
]

# Assets whose printed value is a stub / not live on the venue. Never quote
# these as market prices; they sit at a constant until the deployer updates.
STALE_SUSPECTS = {"xyz:VIX", "xyz:DXY", "xyz:URANIUM", "xyz:ALUMINIUM",
                  "xyz:CORN", "xyz:WHEAT", "xyz:TTF", "xyz:NIFTY",
                  "xyz:IBOV", "xyz:H100", "xyz:VOL", "xyz:GEV", "xyz:KRW"}


def post(body):
    req = urllib.request.Request(
        API, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=20))


def load():
    """Return {coin: {...}} for every coin on the main and xyz dexes."""
    out = {}
    for dex in ("", "xyz"):
        body = {"type": "metaAndAssetCtxs"}
        if dex:
            body["dex"] = dex
        meta, ctxs = post(body)
        for u, c in zip(meta["universe"], ctxs):
            name = u["name"]
            mark = float(c["markPx"])
            prev = float(c["prevDayPx"]) if c.get("prevDayPx") else 0.0
            out[name] = {
                "dex": dex or "main",
                "mark": mark,
                "oracle": float(c["oraclePx"]) if c.get("oraclePx") else 0.0,
                "prev": prev,
                "chg": (mark / prev - 1) * 100 if prev else 0.0,
                "funding_apr": float(c["funding"]) * 24 * 365 * 100,
                "oi": float(c.get("openInterest") or 0),
                "vlm": float(c.get("dayNtlVlm") or 0),
            }
    return out


def relationship_checks(d, thr):
    """Macro relationships that normally hold. A break is not an error — it is
    the most interesting thing on the page, and it must be explained."""
    notes = []

    def g(coin):
        return d.get(coin)

    spx, brent, gold, dxy, btc = (g("xyz:SP500"), g("xyz:BRENTOIL"),
                                  g("xyz:GOLD"), g("xyz:DXY"), g("BTC"))

    if spx and brent:
        if spx["chg"] > thr and brent["chg"] > thr:
            notes.append(
                "Equities AND oil both up hard. Either growth is being repriced "
                "up, or an inflation/rates story is building underneath the "
                "equity rally. Check rate pricing before calling this risk-on.")
        if spx["chg"] < -thr and brent["chg"] < -thr:
            notes.append(
                "Equities AND oil both down hard. That is a demand/growth scare, "
                "not a supply story. Different playbook from a geopolitical bid.")

    if spx and gold:
        if gold["chg"] > thr and spx["chg"] > thr:
            notes.append(
                "Gold and equities rallying together usually means falling real "
                "yields (easier policy priced), not fear. Confirm against rate "
                "pricing rather than assuming a haven bid.")
        if gold["chg"] > thr and spx["chg"] < -thr:
            notes.append(
                "Classic haven rotation: gold bid, equities offered. Look for the "
                "event driving it before fading either leg.")

    if btc and spx:
        if abs(btc["chg"] - spx["chg"]) > 3 * thr:
            notes.append(
                f"Crypto and equities have decoupled ({btc['chg']:+.2f}% vs "
                f"{spx['chg']:+.2f}%). Crypto-native flow is driving, so do not "
                "route a macro view through BTC or HYPE today.")

    if dxy and dxy["chg"] == 0 and dxy["mark"]:
        notes.append(
            "DXY is printing an unchanged stub — treat it as unavailable, not as "
            "a flat dollar. Get the dollar read from EUR/JPY instead.")

    return notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--thesis", default=None,
                    help="one-line statement of the view about to be argued "
                         "(e.g. 'risk-on into FOMC'); recorded in the output so "
                         "the void test has something to test against")
    ap.add_argument("--threshold", type=float, default=2.0,
                    help="percent 24h move that forces an explanation (default 2.0)")
    ap.add_argument("--json", action="store_true", help="raw JSON out")
    args = ap.parse_args()
    thr = args.threshold

    try:
        d = load()
    except Exception as e:  # noqa: BLE001
        print(f"FETCH FAILED: {e}\n"
              "Do not proceed on cached numbers. Say the data is unavailable.",
              file=sys.stderr)
        return 2

    now = datetime.datetime.now(datetime.timezone.utc)
    rows, movers, stale = [], [], []
    for label, coin, _dex in MACRO:
        v = d.get(coin)
        if not v:
            continue
        row = dict(label=label, coin=coin, **v)
        rows.append(row)
        if coin in STALE_SUSPECTS and v["chg"] == 0.0:
            stale.append(row)
        elif abs(v["chg"]) >= thr:
            movers.append(row)

    movers.sort(key=lambda r: -abs(r["chg"]))
    notes = relationship_checks(d, thr)

    if args.json:
        print(json.dumps({"asOfUtc": now.isoformat(), "thesis": args.thesis,
                          "thresholdPct": thr, "rows": rows, "movers": movers,
                          "staleStubs": stale, "relationshipNotes": notes,
                          "verdict": "VOID" if movers else "CLEAR"}, indent=2))
        return 0

    print(f"MACRO PRE-FLIGHT — as of {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("Every price below carries this timestamp. Do not quote it as current "
          "more than ~30 minutes from now; re-run instead.")
    if args.thesis:
        print(f"Thesis under test: {args.thesis}")
    print()

    print(f"{'asset':<26}{'mark':>12}{'24h%':>9}{'fundAPR%':>11}")
    print("-" * 58)
    for r in rows:
        flag = "  <-- stub" if r in stale else ("  *" if r in movers else "")
        print(f"{r['label']:<26}{r['mark']:>12.3f}{r['chg']:>8.2f}%"
              f"{r['funding_apr']:>10.1f}%{flag}")
    print()

    if stale:
        print("STUBS (constant price, not live) — never quote these as markets:")
        for r in stale:
            print(f"  - {r['label']} ({r['coin']})")
        print()

    if notes:
        print("RELATIONSHIP NOTES:")
        for n in notes:
            print(f"  - {n}")
        print()

    if movers:
        print(f"VERDICT: **VOID** — {len(movers)} asset(s) moved >= {thr}% in 24h.")
        print("No level calls, entries or targets until EACH of these is matched "
              "to a named, dated story from a search or the inbox. If a mover "
              "contradicts the thesis and no story explains it, the price is "
              "right and the thesis is wrong — start over.\n")
        for r in movers:
            print(f"  [ ] {r['label']:<24}{r['chg']:+7.2f}%   story: ______________")
    else:
        print(f"VERDICT: **CLEAR** — nothing moved >= {thr}% in 24h.")
        print("Quiet tape. Proceed to levels, but a quiet tape ahead of a known "
              "catalyst is coiled, not safe — check the 72h calendar anyway.")
    print()
    print("Reminder: this is a gate, not a signal. It says whether you may start "
          "talking about levels. It does not say which way.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
