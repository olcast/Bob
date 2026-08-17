#!/usr/bin/env python3
"""Hyperliquid trading-operations fetcher (READ-ONLY).

Pulls positions, PnL, funding, and fills for configured wallets from the
public Hyperliquid info endpoint (https://api.hyperliquid.xyz/info).
Sweeps ALL perp dexes (main dex + HIP-3 builder dexes like "xyz"), since
positions can live on any of them. This script never signs anything and never
touches the /exchange endpoint — it cannot place orders or move funds.

Usage:
  python3 hl_ops.py positions [--address 0x...] [--fixture DIR]
  python3 hl_ops.py pnl       [--days 7]
  python3 hl_ops.py funding   [--days 7]
  python3 hl_ops.py fills     [--days 7]
  python3 hl_ops.py all       [--days 7]

Wallets come from ../config.json unless --address is given.
Output is a single JSON document on stdout for Claude to format.
--fixture DIR reads {clearinghouseState,metaAndAssetCtxs,userFunding,
userFills,portfolio}.json from DIR instead of the network (for testing).
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

API_URL = "https://api.hyperliquid.xyz/info"
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FIXTURE_DIR = None
MAX_DEXES = 100


def info(body, fixture_name=None):
    """POST to the info endpoint, or read a fixture file when --fixture is set."""
    if FIXTURE_DIR and fixture_name:
        path = os.path.join(FIXTURE_DIR, fixture_name + ".json")
        with open(path) as f:
            return json.load(f)
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except (urllib.error.URLError, OSError) as e:
        sys.exit(
            "ERROR: cannot reach api.hyperliquid.xyz ({}).\n"
            "If running in a sandboxed environment, api.hyperliquid.xyz must be "
            "allowed in the network settings. Otherwise check connectivity.".format(e)
        )


def load_wallets(address):
    if address:
        return [{"name": "ad-hoc", "address": address}]
    cfg_path = os.path.join(SKILL_DIR, "config.json")
    try:
        with open(cfg_path) as f:
            wallets = json.load(f).get("wallets", [])
    except FileNotFoundError:
        wallets = []
    if not wallets:
        sys.exit(
            "ERROR: no wallet configured. Add one to config.json "
            '({"wallets": [{"name": "Main", "address": "0x..."}]}) '
            "or pass --address 0x..."
        )
    return wallets


def f(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def perp_dexes():
    """All perp dex names. '' is the main dex; others are HIP-3 builder dexes."""
    if FIXTURE_DIR:
        return [""]
    dexes = info({"type": "perpDexs"})
    names = []
    for d in dexes[:MAX_DEXES]:
        names.append("" if d is None else d.get("name", ""))
    return names or [""]


def mark_prices(dex=""):
    """coin -> {markPx, funding (hourly rate), openInterest} for one perp dex."""
    body = {"type": "metaAndAssetCtxs"}
    if dex:
        body["dex"] = dex
    meta, ctxs = info(body, "metaAndAssetCtxs")
    out = {}
    for asset, ctx in zip(meta["universe"], ctxs):
        out[asset["name"]] = {
            "markPx": f(ctx.get("markPx")),
            "fundingHourly": f(ctx.get("funding")),
            "openInterest": f(ctx.get("openInterest")),
        }
    return out


def positions(wallet, dexes):
    """Sweep every perp dex; aggregate positions and per-dex account balances."""
    rows, per_dex = [], []
    totals = {"accountValueUsd": 0.0, "totalNotionalUsd": 0.0,
              "totalMarginUsedUsd": 0.0, "withdrawableUsd": 0.0}
    for dex in dexes:
        body = {"type": "clearinghouseState", "user": wallet}
        if dex:
            body["dex"] = dex
        st = info(body, "clearinghouseState")
        ms = st.get("marginSummary", {})
        acct_val = f(ms.get("accountValue"))
        asset_pos = st.get("assetPositions", [])
        if acct_val == 0 and not asset_pos:
            continue  # no footprint on this dex
        totals["accountValueUsd"] += acct_val
        totals["totalNotionalUsd"] += f(ms.get("totalNtlPos"))
        totals["totalMarginUsedUsd"] += f(ms.get("totalMarginUsed"))
        totals["withdrawableUsd"] += f(st.get("withdrawable"))
        per_dex.append({"dex": dex or "main", "accountValueUsd": acct_val,
                        "positionCount": len(asset_pos)})
        marks = mark_prices(dex) if asset_pos else {}
        for ap in asset_pos:
            p = ap["position"]
            szi = f(p.get("szi"))
            coin = p.get("coin")
            mark = marks.get(coin, {})
            lev = p.get("leverage", {})
            entry = f(p.get("entryPx"))
            liq = f(p.get("liquidationPx")) or None
            mark_px = mark.get("markPx")
            liq_dist_pct = None
            if liq and mark_px:
                liq_dist_pct = abs(liq - mark_px) / mark_px * 100
            rows.append({
                "dex": dex or "main",
                "coin": coin,
                "side": "LONG" if szi > 0 else "SHORT",
                "size": abs(szi),
                "entryPx": entry,
                "markPx": mark_px,
                "liquidationPx": liq,
                "liqDistancePct": liq_dist_pct,
                "leverage": "{}x {}".format(lev.get("value"), lev.get("type")),
                "positionValueUsd": f(p.get("positionValue")),
                "marginUsedUsd": f(p.get("marginUsed")),
                "unrealizedPnlUsd": f(p.get("unrealizedPnl")),
                "returnOnEquity": f(p.get("returnOnEquity")),
                "fundingSinceOpenUsd": -f(p.get("cumFunding", {}).get("sinceOpen")),
                "currentFundingHourly": mark.get("fundingHourly"),
                "currentFundingAprPct": (mark.get("fundingHourly") or 0) * 24 * 365 * 100,
            })
    totals["perDex"] = per_dex
    totals["positions"] = rows
    return totals


def funding(wallet, days):
    """Account-wide funding ledger (covers all dexes)."""
    start = int((time.time() - days * 86400) * 1000)
    events = info(
        {"type": "userFunding", "user": wallet, "startTime": start}, "userFunding"
    )
    by_coin = {}
    for ev in events:
        d = ev.get("delta", {})
        if d.get("type") != "funding":
            continue
        c = by_coin.setdefault(d.get("coin"), {"paidUsd": 0.0, "receivedUsd": 0.0, "events": 0})
        usdc = f(d.get("usdc"))
        # positive usdc = received, negative = paid
        if usdc >= 0:
            c["receivedUsd"] += usdc
        else:
            c["paidUsd"] += -usdc
        c["events"] += 1
    total = sum(c["receivedUsd"] - c["paidUsd"] for c in by_coin.values())
    return {"days": days, "netFundingUsd": total, "byCoin": by_coin}


def fills(wallet, days):
    """Account-wide fills (covers all dexes)."""
    start = int((time.time() - days * 86400) * 1000)
    all_fills, cursor = [], start
    # Paginate: responses cap at ~500 elements for by-time queries.
    for _ in range(20):
        batch = info(
            {"type": "userFillsByTime", "user": wallet, "startTime": cursor},
            "userFills",
        )
        all_fills.extend(batch)
        if FIXTURE_DIR or len(batch) < 500:
            break
        cursor = batch[-1]["time"] + 1
    realized = sum(f(x.get("closedPnl")) for x in all_fills)
    fees = sum(f(x.get("fee")) for x in all_fills)
    volume = sum(f(x.get("px")) * f(x.get("sz")) for x in all_fills)
    recent = [
        {
            "time": x.get("time"),
            "coin": x.get("coin"),
            "dir": x.get("dir"),
            "px": f(x.get("px")),
            "sz": f(x.get("sz")),
            "closedPnl": f(x.get("closedPnl")),
            "fee": f(x.get("fee")),
        }
        for x in sorted(all_fills, key=lambda x: x.get("time", 0), reverse=True)[:20]
    ]
    return {
        "days": days,
        "fillCount": len(all_fills),
        "volumeUsd": volume,
        "realizedPnlUsd": realized,
        "feesUsd": fees,
        "realizedPnlNetOfFeesUsd": realized - fees,
        "recentFills": recent,
    }


def pnl(wallet):
    port = dict(info({"type": "portfolio", "user": wallet}, "portfolio"))
    out = {}
    for period in ("day", "week", "month", "allTime"):
        p = port.get(period)
        if not p:
            continue
        hist = p.get("pnlHistory") or []
        acct = p.get("accountValueHistory") or []
        out[period] = {
            "pnlUsd": f(hist[-1][1]) if hist else None,
            "accountValueUsd": f(acct[-1][1]) if acct else None,
            "volumeUsd": f(p.get("vlm")),
        }
    return out


def market_scan(held):
    """Market context for idea generation. `held` = [(dex, coin), ...].

    Surfaces objective conditions only: 24h movers, funding extremes, where
    held coins sit in their 7d range, and cross-venue predicted funding.
    Interpretation (and the decision that there is NO trade) belongs to the
    reader, not this script.
    """
    meta, ctxs = info({"type": "metaAndAssetCtxs"}, "metaAndAssetCtxs")
    rows = []
    for asset, ctx in zip(meta["universe"], ctxs):
        mark, prev = f(ctx.get("markPx")), f(ctx.get("prevDayPx"))
        rows.append({
            "coin": asset["name"],
            "markPx": mark,
            "chg24hPct": (mark / prev - 1) * 100 if prev else None,
            "fundingAprPct": f(ctx.get("funding")) * 24 * 365 * 100,
            "openInterestUsd": f(ctx.get("openInterest")) * mark,
            "dayVolumeUsd": f(ctx.get("dayNtlVlm")),
        })
    by_vol = sorted(rows, key=lambda r: -r["dayVolumeUsd"])[:10]
    movers = sorted((r for r in rows if r["chg24hPct"] is not None),
                    key=lambda r: -abs(r["chg24hPct"]))[:8]
    fund_ext = sorted(rows, key=lambda r: -abs(r["fundingAprPct"]))[:8]

    held_detail = []
    if not FIXTURE_DIR:
        now = int(time.time() * 1000)
        start = now - 7 * 86400 * 1000
        for dex, coin in held:
            candles = info({"type": "candleSnapshot", "req": {
                "coin": coin, "interval": "4h", "startTime": start, "endTime": now}})
            if not candles:
                continue
            highs = [f(c.get("h")) for c in candles]
            lows = [f(c.get("l")) for c in candles]
            close = f(candles[-1].get("c"))
            hi, lo = max(highs), min(lows)
            held_detail.append({
                "dex": dex, "coin": coin, "lastPx": close,
                "sevenDayHigh": hi, "sevenDayLow": lo,
                "pctFromSevenDayHigh": (close / hi - 1) * 100 if hi else None,
                "pctFromSevenDayLow": (close / lo - 1) * 100 if lo else None,
                "chg7dPct": (close / f(candles[0].get("o")) - 1) * 100
                            if f(candles[0].get("o")) else None,
            })
        held_main = {c for d, c in held if d == "main"}
        if held_main:
            pf = {}
            for coin, venues in info({"type": "predictedFundings"}):
                if coin in held_main:
                    pf[coin] = {v: f(d.get("fundingRate")) * 24 * 365 * 100
                                for v, d in venues if d}
            for h in held_detail:
                if h["coin"] in pf:
                    h["predictedFundingAprByVenuePct"] = pf[h["coin"]]

    return {"topByVolume": by_vol, "topMovers24h": movers,
            "fundingExtremes": fund_ext, "heldCoins": held_detail}


def main():
    global FIXTURE_DIR
    ap = argparse.ArgumentParser()
    ap.add_argument("command",
                    choices=["positions", "pnl", "funding", "fills", "all", "scan"])
    ap.add_argument("--address")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--fixture")
    args = ap.parse_args()
    FIXTURE_DIR = args.fixture

    wallets = load_wallets(args.address)
    dexes = perp_dexes() if args.command in ("positions", "all", "scan") else []
    report = {"generatedAt": int(time.time() * 1000), "command": args.command, "wallets": []}
    for w in wallets:
        entry = {"name": w.get("name"), "address": w["address"]}
        if args.command in ("positions", "all", "scan"):
            entry["positions"] = positions(w["address"], dexes)
        if args.command == "scan":
            held = [(r["dex"], r["coin"]) for r in entry["positions"]["positions"]]
            entry["marketScan"] = market_scan(held)
        if args.command in ("pnl", "all"):
            entry["pnl"] = pnl(w["address"])
        if args.command in ("funding", "all"):
            entry["funding"] = funding(w["address"], args.days)
        if args.command in ("fills", "pnl", "all"):
            entry["fills"] = fills(w["address"], args.days)
        report["wallets"].append(entry)
    json.dump(report, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
