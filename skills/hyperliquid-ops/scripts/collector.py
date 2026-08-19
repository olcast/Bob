#!/usr/bin/env python3
"""HL-OPS forward collector — snapshots the FORWARD-ONLY 'goldmine' observables that
Hyperliquid exposes and nobody can backfill, so the VCP-ABLATION P2 layer starts
filling from today. READ-ONLY: touches only /info. Never /exchange, never keys.

Each tick appends timestamped JSONL rows (kind ∈ market|book|hlp|liqmap|liqevent):
  market   — per coin: mark/oracle/mid, funding, OI, premium, day notional vol, impact spread
  book     — l2Book depth bands (±0.1/0.25/0.5/1%) + top-3 bid/ask walls
  hlp      — Hyperliquid's own market-maker net inventory (sum over HLP's child vaults),
             total vault equity + APR. The unique observable a CEX never broadcasts.
  liqmap   — TRUE liquidation map: exact per-position liquidationPx (HL computes it, not a
             leverage guess) aggregated by price bucket across every address we've harvested.
             Long liqs = forced SELL below mark (down-fuel); short liqs = forced BUY above (up-fuel).
  liqevent — realized liquidations pulled from tagged fills (px/sz/side/method), ground truth.

Coverage compounds: addresses discovered from the public trades feed persist in an address
book across runs, so the map sharpens the longer it runs. Bounded per-tick sweep keeps runtime
finite. Run as a one-shot each firing (--once) or as a daemon (--loop --interval SEC).

  python3 collector.py --once
  python3 collector.py --loop --interval 300 --coins BTC,ETH,SOL,HYPE
"""
import json, time, os, urllib.request, argparse, statistics

API = "https://api.hyperliquid.xyz/info"
HLP = "0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"        # Hyperliquid Provider master vault
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
LEDGER = os.path.join(DATA, "collector.jsonl")
BOOK   = os.path.join(DATA, "addressbook.json")           # persisted, compounds coverage

def post(body, tries=3):
    for a in range(tries):
        try:
            r = urllib.request.Request(API, data=json.dumps(body).encode(),
                                       headers={"Content-Type": "application/json"})
            return json.load(urllib.request.urlopen(r, timeout=30))
        except Exception:
            if a == tries - 1: return None
            time.sleep(0.6 * (a + 1))

def now_ms(): return int(time.time() * 1000)

def emit(rows):
    os.makedirs(DATA, exist_ok=True)
    with open(LEDGER, "a") as f:
        for r in rows: f.write(json.dumps(r, separators=(",", ":")) + "\n")

def load_book():
    try:
        with open(BOOK) as f: return json.load(f)
    except Exception: return {}      # addr -> last_seen_ms

def save_book(b):
    os.makedirs(DATA, exist_ok=True)
    with open(BOOK, "w") as f: json.dump(b, f)

# ------------------------------------------------------------------ market + book
def collect_market(ts, coins, mac):
    uni = {u["name"]: i for i, u in enumerate(mac[0]["universe"])}
    ctx = mac[1]; rows = []
    for c in coins:
        if c not in uni: continue
        x = ctx[uni[c]]
        ip = x.get("impactPxs") or [None, None]
        rows.append({"ts": ts, "kind": "market", "coin": c,
                     "mark": float(x["markPx"]), "oracle": float(x["oraclePx"]),
                     "mid": float(x["midPx"]) if x.get("midPx") else None,
                     "funding": float(x["funding"]), "oi": float(x["openInterest"]),
                     "premium": float(x["premium"]) if x.get("premium") else None,
                     "dayNtlVlm": float(x["dayNtlVlm"]),
                     "impactBp": (float(ip[1]) - float(ip[0])) / float(x["markPx"]) * 1e4
                                 if ip[0] else None})
    return rows

def collect_book(ts, coins):
    rows = []
    for c in coins:
        b = post({"type": "l2Book", "coin": c})
        if not b or "levels" not in b: continue
        bids, asks = b["levels"]
        if not bids or not asks: continue
        mark = (float(bids[0]["px"]) + float(asks[0]["px"])) / 2
        def depth(levels, pct):
            lo, hi = mark * (1 - pct), mark * (1 + pct)
            return round(sum(float(l["sz"]) for l in levels
                             if lo <= float(l["px"]) <= hi), 4)
        def walls(levels, n=3):
            return [[float(l["px"]), float(l["sz"])]
                    for l in sorted(levels, key=lambda l: -float(l["sz"]))[:n]]
        rows.append({"ts": ts, "kind": "book", "coin": c, "mark": mark,
                     "bidDepth": {p: depth(bids, p) for p in (0.001, 0.0025, 0.005, 0.01)},
                     "askDepth": {p: depth(asks, p) for p in (0.001, 0.0025, 0.005, 0.01)},
                     "bidWalls": walls(bids), "askWalls": walls(asks)})
        time.sleep(0.15)
    return rows

# ------------------------------------------------------------------ HLP inventory
def collect_hlp(ts, coins):
    vd = post({"type": "vaultDetails", "vaultAddress": HLP})
    equity, apr, kids = None, None, []
    if isinstance(vd, dict):
        apr = vd.get("apr")
        rel = vd.get("relationship", {})
        if rel.get("type") == "parent":
            kids = rel.get("data", {}).get("childAddresses", [])
        pf = dict(vd.get("portfolio", []))
        av = pf.get("allTime", {}).get("accountValueHistory", [])
        if av: equity = float(av[-1][1])
    # net inventory = sum of signed size across master + all child vaults
    net = {}          # coin -> {"szi":..., "ntl":..., "liqPx":[...]}
    for addr in [HLP] + kids:
        cs = post({"type": "clearinghouseState", "user": addr})
        if not isinstance(cs, dict): continue
        for p in cs.get("assetPositions", []):
            pos = p["position"]; c = pos["coin"]
            if coins and c not in coins: continue
            szi = float(pos["szi"]); mark = float(pos.get("entryPx") or 0)
            d = net.setdefault(c, {"szi": 0.0, "ntl": 0.0})
            d["szi"] += szi
            d["ntl"] += abs(szi) * mark
        time.sleep(0.1)
    return [{"ts": ts, "kind": "hlp", "equity": equity, "apr": apr,
             "nChildVaults": len(kids),
             "inventory": {c: {"szi": round(v["szi"], 4), "ntlUsd": round(v["ntl"], 0)}
                           for c, v in net.items()}}]

# ------------------------------------------------------------------ TRUE liq-map
def harvest(coins, book, ts):
    """append fresh addresses from the public trades feed to the persistent book."""
    for c in coins:
        tr = post({"type": "recentTrades", "coin": c}) or []
        for t in tr:
            for u in t.get("users", []):
                if u and u != "0x" + "0" * 40:
                    book[u] = ts
        time.sleep(0.1)
    return book

def collect_liqmap(ts, coins, book, cap, mac, bucket_pct=0.005):
    """Sweep a bounded, most-recently-seen slice of the address book; aggregate exact
    liquidationPx * notional into price buckets, per coin, split long/short (down/up fuel)."""
    uni = {u["name"]: i for i, u in enumerate(mac[0]["universe"])}
    marks = {c: float(mac[1][uni[c]]["markPx"]) for c in coins if c in uni}
    addrs = sorted(book, key=lambda a: -book[a])[:cap]      # freshest first
    # coin -> side -> bucketprice -> notionalUsd
    agg = {c: {"long": {}, "short": {}} for c in coins}
    seen_positions = {c: 0 for c in coins}
    liqevents = []
    for a in addrs:
        cs = post({"type": "clearinghouseState", "user": a})
        if not isinstance(cs, dict): continue
        for p in cs.get("assetPositions", []):
            pos = p["position"]; c = pos["coin"]
            if c not in marks: continue
            lp = pos.get("liquidationPx")
            if not lp: continue
            lp = float(lp); szi = float(pos["szi"]); mark = marks[c]
            ntl = abs(szi) * mark
            side = "long" if szi > 0 else "short"            # long liq below, short liq above
            bucket = round(lp / (mark * bucket_pct)) * (mark * bucket_pct)
            agg[c][side][bucket] = agg[c][side].get(bucket, 0.0) + ntl
            seen_positions[c] += 1
            # COST-BASIS / UNDERWATER (SEAM candidate #6 — was DISCARDED): capture entryPx alongside
            # liquidationPx so the desk can later read the UNDERWATER MASS (who is trapped, by how much),
            # not just the liq geometry. entryPx and uPnL are the 'position', liqPx is the 'exit'.
            ep = pos.get("entryPx")
            dd = agg[c].setdefault("_underwater", {"n": 0, "usd": 0.0, "dist_pct": []})
            if ep:
                ep = float(ep); dd["n"] += 1; dd["usd"] += ntl
                dd["dist_pct"].append(round((mark - ep) / ep * 100, 3) if szi > 0 else round((ep - mark) / ep * 100, 3))  # adverse-distance pct
        time.sleep(0.08)
    rows = []
    for c in coins:
        if not (agg[c]["long"] or agg[c]["short"]): continue
        mark = marks.get(c)
        def top(side):
            return sorted(([round(px, 1), round(n, 0)] for px, n in agg[c][side].items()),
                          key=lambda x: -x[1])[:12]
        down = sum(agg[c]["long"].values())     # forced sells below = down-fuel
        up   = sum(agg[c]["short"].values())    # forced buys above  = up-fuel
        uw = agg[c].get("_underwater", {}); uw_dist = uw.get("dist_pct", [])
        rows.append({"ts": ts, "kind": "liqmap", "coin": c, "mark": mark,
                     "nPositions": seen_positions[c], "nAddrScanned": len(addrs),
                     "downFuelUsd": round(down, 0), "upFuelUsd": round(up, 0),
                     "fuelSkew": round((up - down) / (up + down), 3) if (up + down) else None,
                     "underwaterUsd": round(uw.get("usd", 0.0), 0),
                     "underwaterN": uw.get("n", 0),
                     "underwaterMedDistPct": round(statistics.median(uw_dist), 3) if uw_dist else None,
                     "longLiqClusters": top("long"), "shortLiqClusters": top("short")})
    return rows

# ------------------------------------------------------------------ realized liq events
def collect_liqevents(ts, coins, book, cap, lookback_min=30):
    """Pull realized liquidations (tagged fills) for the freshest addresses. Ground truth."""
    addrs = sorted(book, key=lambda a: -book[a])[:cap]
    start = ts - lookback_min * 60_000
    out = []
    for a in addrs:
        fills = post({"type": "userFillsByTime", "user": a, "startTime": start, "endTime": ts})
        if not isinstance(fills, list): continue
        for f in fills:
            liq = f.get("liquidation")
            if liq and f.get("coin") in coins:
                out.append({"ts": ts, "kind": "liqevent", "coin": f["coin"],
                            "t": f["time"], "px": float(f["px"]), "sz": float(f["sz"]),
                            "side": f["side"], "dir": f.get("dir"),
                            "closedPnl": float(f.get("closedPnl", 0)),
                            "method": liq.get("method"), "markPx": float(liq.get("markPx", 0))})
        time.sleep(0.08)
    # dedup by (coin, t, px, sz)
    seen = set(); uniq = []
    for e in out:
        k = (e["coin"], e["t"], e["px"], e["sz"])
        if k not in seen: seen.add(k); uniq.append(e)
    return uniq

# ------------------------------------------------------------------ one tick
def tick(coins, cap, do_liqevents, lookback=30, light_coins=()):
    ts = now_ms()
    mac = post({"type": "metaAndAssetCtxs"})
    if not mac:
        print("  metaAndAssetCtxs failed — skipping tick"); return 0
    book = load_book()
    book = harvest(coins, book, ts)
    rows = []
    # MAIN coins: full depth (market + book + hlp + liqmap + liqevent)
    rows += collect_market(ts, coins, mac)
    rows += collect_book(ts, coins)
    rows += collect_hlp(ts, coins)
    rows += collect_liqmap(ts, coins, book, cap, mac)
    if do_liqevents:
        rows += collect_liqevents(ts, coins, book, min(cap, 120), lookback)
    # LIGHT coins: market/premium/funding/OI only (no deep sweep) — oracle synthetics (PAXG)
    if light_coins:
        rows += collect_market(ts, light_coins, mac)
    save_book(book)
    emit(rows)
    kinds = {}
    for r in rows: kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    print(f"  tick {time.strftime('%H:%M:%S', time.gmtime(ts/1000))}Z  "
          f"rows={len(rows)} {kinds}  addrbook={len(book)}")
    return len(rows)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--interval", type=int, default=300)
    ap.add_argument("--coins", default="BTC,ETH,SOL,HYPE")
    ap.add_argument("--light-coins", default="PAXG",
                    help="oracle-priced synthetics: market/premium/funding/OI only, no deep sweep")
    ap.add_argument("--cap", type=int, default=150, help="max addresses swept per tick")
    ap.add_argument("--liqevents", action="store_true", help="also pull realized liq fills (slower)")
    ap.add_argument("--lookback", type=int, default=30,
                    help="minutes of realized-liq history per tick; set >= run cadence to stay gapless")
    a = ap.parse_args()
    coins = [c.strip() for c in a.coins.split(",") if c.strip()]
    light = [c.strip() for c in a.light_coins.split(",") if c.strip()]
    print(f"HL-OPS collector · coins={coins} · light={light} · cap={a.cap} · lookback={a.lookback}m · ledger={LEDGER}")
    if a.loop:
        while True:
            try: tick(coins, a.cap, a.liqevents, a.lookback, light)
            except Exception as e: print("  tick error:", e)
            time.sleep(a.interval)
    else:
        tick(coins, a.cap, a.liqevents, a.lookback, light)

if __name__ == "__main__":
    main()
