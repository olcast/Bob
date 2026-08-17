#!/usr/bin/env python3
"""
orderflow.py — real order flow for a Hyperliquid perp: aggressor-side tape,
cumulative delta, absorption detection and resting-book imbalance.

Candle volume tells you how much traded. It does not tell you who was
hitting. This does: every print on the websocket tape carries the aggressor
side, so buy volume and sell volume separate cleanly, and the difference
(delta / CVD) is the actual flow.

Two things it is built to catch:
  * DIVERGENCE  — price makes a new high while CVD does not (buyers are
    thinning out into strength), or a new low while CVD holds (sellers are
    being absorbed).
  * ABSORPTION  — heavy one-sided volume that fails to move price. Someone
    large is on the other side taking it. This usually marks the turn.

Usage:
    python3 scripts/orderflow.py                      # xyz:SP500, 90s
    python3 scripts/orderflow.py --coin BTC --secs 120
    python3 scripts/orderflow.py --coin xyz:SP500 --secs 180 --json

Read-only: public websocket tape + public l2Book. Never touches /exchange.
"""

import argparse
import asyncio
import datetime
import json
import statistics
import sys
import urllib.request
from collections import defaultdict

WS = "wss://api.hyperliquid.xyz/ws"
API = "https://api.hyperliquid.xyz/info"


def post(body):
    req = urllib.request.Request(
        API, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=20))


def book_snapshot(coin):
    """Resting liquidity. This is intent that has NOT traded — it can be
    pulled at any moment, so it is weaker evidence than the tape. Read it for
    where the walls are, not for what will happen."""
    b = post({"type": "l2Book", "coin": coin})
    bids, asks = b["levels"]
    if not bids or not asks:
        return None
    best_bid, best_ask = float(bids[0]["px"]), float(asks[0]["px"])
    mid = (best_bid + best_ask) / 2

    def side_depth(levels, lo, hi):
        return sum(float(x["sz"]) for x in levels
                   if lo <= abs(float(x["px"]) - mid) / mid * 10000 <= hi)

    bands = []
    for lo, hi, label in [(0, 5, "0-5bp"), (5, 15, "5-15bp"), (15, 50, "15-50bp")]:
        bd, ad = side_depth(bids, lo, hi), side_depth(asks, lo, hi)
        tot = bd + ad
        bands.append({"band": label, "bid": bd, "ask": ad,
                      "imbalance": (bd - ad) / tot if tot else 0.0})

    def walls(levels, n=3):
        return sorted(((float(x["px"]), float(x["sz"])) for x in levels),
                      key=lambda t: -t[1])[:n]

    return {"mid": mid, "spread": best_ask - best_bid, "bands": bands,
            "bid_walls": walls(bids), "ask_walls": walls(asks)}


async def collect(coin, secs):
    import websockets
    trades = []
    try:
        async with websockets.connect(WS, ping_interval=20, open_timeout=15) as ws:
            await ws.send(json.dumps({"method": "subscribe",
                                      "subscription": {"type": "trades", "coin": coin}}))
            end = asyncio.get_event_loop().time() + secs
            while asyncio.get_event_loop().time() < end:
                try:
                    remaining = end - asyncio.get_event_loop().time()
                    raw = await asyncio.wait_for(ws.recv(), timeout=max(1.0, remaining))
                except asyncio.TimeoutError:
                    break
                msg = json.loads(raw)
                if msg.get("channel") != "trades":
                    continue
                for t in msg.get("data", []):
                    # side "B" = an aggressive BUY lifting the offer,
                    # "A" = an aggressive SELL hitting the bid.
                    trades.append({"px": float(t["px"]), "sz": float(t["sz"]),
                                   "side": t["side"], "time": t["time"]})
    except Exception as e:  # noqa: BLE001
        print(f"WS ERROR: {e}", file=sys.stderr)
    return trades


def analyse(trades, bucket_secs=15):
    if not trades:
        return None
    trades.sort(key=lambda t: t["time"])
    buy = sum(t["sz"] for t in trades if t["side"] == "B")
    sell = sum(t["sz"] for t in trades if t["side"] == "A")
    total = buy + sell
    sizes = [t["sz"] for t in trades]
    big = sorted(trades, key=lambda t: -t["sz"])[:5]

    t0 = trades[0]["time"]
    buckets = defaultdict(lambda: {"buy": 0.0, "sell": 0.0, "hi": None,
                                   "lo": None, "last": None, "n": 0})
    for t in trades:
        k = int((t["time"] - t0) / 1000 // bucket_secs)
        b = buckets[k]
        b["buy" if t["side"] == "B" else "sell"] += t["sz"]
        b["hi"] = t["px"] if b["hi"] is None else max(b["hi"], t["px"])
        b["lo"] = t["px"] if b["lo"] is None else min(b["lo"], t["px"])
        b["last"] = t["px"]
        b["n"] += 1

    cvd, series = 0.0, []
    for k in sorted(buckets):
        b = buckets[k]
        d = b["buy"] - b["sell"]
        cvd += d
        series.append({"t": k * bucket_secs, "delta": d, "cvd": cvd,
                       "px": b["last"], "hi": b["hi"], "lo": b["lo"],
                       "vol": b["buy"] + b["sell"], "n": b["n"]})

    signals = []
    if len(series) >= 3:
        px_first, px_last = series[0]["px"], series[-1]["px"]
        cvd_last = series[-1]["cvd"]
        px_up, cvd_up = px_last > px_first, cvd_last > 0

        peak_px = max(series, key=lambda s: s["hi"])
        trough_px = min(series, key=lambda s: s["lo"])
        peak_cvd = max(series, key=lambda s: s["cvd"])
        trough_cvd = min(series, key=lambda s: s["cvd"])

        if px_up and not cvd_up:
            signals.append(
                "BEARISH DIVERGENCE: price is higher over the window but net "
                "delta is negative — the move up is being sold into. Longs here "
                "are paying up into supply.")
        if (not px_up) and cvd_up:
            signals.append(
                "BULLISH DIVERGENCE: price is lower but net delta is positive — "
                "sellers are being absorbed. Downside is being bought.")
        if peak_px["t"] > peak_cvd["t"] and px_up:
            signals.append(
                "The price high came AFTER the CVD high — buying pressure "
                "peaked before price did. Classic exhaustion shape.")
        if trough_px["t"] > trough_cvd["t"] and not px_up:
            signals.append(
                "The price low came AFTER the CVD low — selling pressure "
                "peaked before price did. Downside momentum is fading.")

        # absorption: top-volume bucket that barely moved price
        rng_all = [s["hi"] - s["lo"] for s in series if s["hi"] and s["lo"]]
        med_rng = statistics.median(rng_all) if rng_all else 0
        loud = max(series, key=lambda s: s["vol"])
        loud_rng = (loud["hi"] - loud["lo"]) if loud["hi"] else 0
        if med_rng and loud["vol"] > 2 * statistics.median([s["vol"] for s in series]) \
                and loud_rng < med_rng:
            side = "buying" if loud["delta"] > 0 else "selling"
            signals.append(
                f"ABSORPTION at ~{loud['px']:.2f}: the heaviest {side} of the "
                "window moved price less than a typical bucket. Someone large is "
                "on the other side. Absorption at a level usually marks the turn, "
                "not the breakout.")

    return {"trades": len(trades), "buy": buy, "sell": sell, "total": total,
            "delta": buy - sell,
            "delta_pct": (buy - sell) / total * 100 if total else 0,
            "avg_size": total / len(trades), "med_size": statistics.median(sizes),
            "max_size": max(sizes), "big": big, "series": series,
            "signals": signals,
            "px_first": trades[0]["px"], "px_last": trades[-1]["px"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coin", default="xyz:SP500")
    ap.add_argument("--secs", type=int, default=90)
    ap.add_argument("--bucket", type=int, default=15)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    bk = book_snapshot(a.coin)
    tr = asyncio.run(collect(a.coin, a.secs))
    an = analyse(tr, a.bucket)
    now = datetime.datetime.now(datetime.timezone.utc)

    if a.json:
        print(json.dumps({"asOfUtc": now.isoformat(), "coin": a.coin,
                          "windowSecs": a.secs, "book": bk, "flow": an},
                         indent=2, default=str))
        return 0

    print(f"ORDER FLOW — {a.coin} — {a.secs}s window ending "
          f"{now.strftime('%Y-%m-%d %H:%M:%S')} UTC\n")

    if not an:
        print("NO PRINTS in the window. That is itself information: the tape is "
              "dead, so book levels and 'rejections' here are noise, not flow. "
              "Do not read intent into a market nobody is trading.")
        if bk:
            print(f"\nMid {bk['mid']:.3f}  spread {bk['spread']:.3f}")
        return 0

    print(f"Price   {an['px_first']:.3f} -> {an['px_last']:.3f}"
          f"   ({an['px_last'] - an['px_first']:+.3f})")
    print(f"Prints  {an['trades']}   avg size {an['avg_size']:.3f}"
          f"   median {an['med_size']:.3f}   max {an['max_size']:.3f}")
    print(f"Buy vol  {an['buy']:.2f}   Sell vol {an['sell']:.2f}")
    print(f"DELTA    {an['delta']:+.2f}  ({an['delta_pct']:+.1f}% of volume)"
          f"   <- who was actually aggressing\n")

    print(f"{'t+s':>5}{'px':>12}{'vol':>10}{'delta':>10}{'CVD':>11}{'prints':>8}")
    print("-" * 56)
    for s in an["series"]:
        print(f"{s['t']:>5}{s['px']:>12.3f}{s['vol']:>10.2f}"
              f"{s['delta']:>+10.2f}{s['cvd']:>+11.2f}{s['n']:>8}")
    print()

    print("Largest prints:")
    for t in an["big"]:
        side = "BUY " if t["side"] == "B" else "SELL"
        ts = datetime.datetime.fromtimestamp(
            t["time"] / 1000, datetime.timezone.utc).strftime("%H:%M:%S")
        print(f"  {ts}  {side} {t['sz']:>9.3f} @ {t['px']:.3f}")
    print()

    if bk:
        print(f"RESTING BOOK (intent, not flow — can be pulled)   mid "
              f"{bk['mid']:.3f}  spread {bk['spread']:.3f}")
        for b in bk["bands"]:
            lean = ("bid-heavy" if b["imbalance"] > 0.15 else
                    "ask-heavy" if b["imbalance"] < -0.15 else "balanced")
            print(f"  {b['band']:<8} bid {b['bid']:>9.2f}  ask {b['ask']:>9.2f}"
                  f"  imb {b['imbalance']:>+6.2f}  {lean}")
        print(f"  bid walls: {[(round(p,2), round(s,2)) for p, s in bk['bid_walls']]}")
        print(f"  ask walls: {[(round(p,2), round(s,2)) for p, s in bk['ask_walls']]}")
        print()

    if an["signals"]:
        print("SIGNALS:")
        for s in an["signals"]:
            print(f"  * {s}")
    else:
        print("SIGNALS: none — flow and price agree over this window.")
    print()
    print("Caveats: this is one venue and a short window. A single window is a "
          "sample, not a regime — re-run it at the level that matters and at the "
          "session open. Resting size is not flow; only prints are.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
