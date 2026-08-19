#!/usr/bin/env python3
"""CARRY TERM-STRUCTURE (D8) — the funding/basis CURVE, not the spot rate.

D4 (funding) is ONE hourly print; D3 (basis) is ONE perp-vs-spot level. The independent object
all three models flagged (#3 unanimous) is the TERM STRUCTURE: the crowd's carry at multiple
horizons, so you can see whether crowding is FRONT-END (flushed soon) or held OUT THE CURVE
(structural). Also computes the carry-vs-convexity RESIDUAL that breaks the +0.41 basis↔funding
redundancy: funding (carry you pay) minus basis/horizon (the positional premium) — when they
DISAGREE, that IS the contradiction D3×D4 cannot currently emit.

Horizons:
  spot premium   : HL mark − index  (now)
  funding 1h     : HL hourly funding, annualized
  funding 8h     : Binance/Bybit 8h funding, annualized  (the complex's "distant" carry)
  funding 4h     : BinPerp/BybitPerp predicted (HL's own cross-venue feed)

Read-only, descriptive, FREE data only. BTC. Collected forward — P3–P5 ablate before any live use.
"""
import json, urllib.request, time

HL = "https://api.hyperliquid.xyz/info"

def post(body):
    try:
        r = urllib.request.Request(HL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        return json.load(urllib.request.urlopen(r, timeout=30))
    except Exception:
        return None

def get(url):
    try:
        r = urllib.request.Request(url, headers={"User-Agent": "desk/1.0"})
        return json.load(urllib.request.urlopen(r, timeout=15))
    except Exception:
        return None

def annualize(rate, hours):
    return rate * (365 * 24 / hours) * 100

def build():
    out = {"terms": {}, "curve": {}, "residual": None}
    # HL mark + oracle + 1h funding
    mids = post({"type": "allMids"}) or {}
    meta = post({"type": "metaAndAssetCtxs"})
    mark = float(mids.get("BTC", 0)) if mids.get("BTC") else None
    oracle = None; funding_1h = None
    if meta and len(meta) >= 2:
        uni = meta[0]["universe"]; idx = [i for i, a in enumerate(uni) if a.get("name") == "BTC"]
        if idx:
            ctx = meta[1][idx[0]]
            oracle = float(ctx.get("oraclePx", 0) or 0)
            funding_1h = float(ctx.get("funding", 0) or 0)
    if mark and oracle and oracle:
        out["terms"]["spot_premium_bp"] = round((mark - oracle) / oracle * 10000, 2)
    if funding_1h is not None:
        out["terms"]["funding_1h_ann_pct"] = round(annualize(funding_1h, 1), 4)
    # CEX 8h funding (Binance premiumIndex + Bybit tickers)
    bin_f = by_f = None
    b = get("https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT")
    if isinstance(b, dict) and "lastFundingRate" in b:
        bin_f = float(b["lastFundingRate"])
    by = get("https://api.bybit.com/v5/market/tickers?category=linear&symbol=BTCUSDT")
    if isinstance(by, dict) and by.get("retCode") == 0:
        lst = by.get("result", {}).get("list", [])
        if lst:
            by_f = float(lst[0].get("fundingRate", 0))
    cex_8h = []
    if bin_f is not None:
        cex_8h.append(annualize(bin_f, 8))
    if by_f is not None:
        cex_8h.append(annualize(by_f, 8))
    if cex_8h:
        out["terms"]["funding_8h_cex_ann_pct"] = round(sum(cex_8h) / len(cex_8h), 4)
    # HL predicted cross-venue funding (1h/4h/8h horizons in one feed)
    pf = post({"type": "predictedFundings"})
    if isinstance(pf, list):
        for row in pf:
            if isinstance(row, list) and len(row) >= 2 and row[0] == "BTC":
                for venue, v in row[1]:
                    if isinstance(v, dict):
                        rate = float(v.get("fundingRate", 0))
                        hrs = float(v.get("fundingIntervalHours", 8))
                        out["terms"][f"pred_{venue}_{int(hrs)}h_ann_pct"] = round(annualize(rate, hrs), 4)
                break
    # curve = read the SLOPE across horizons
    t = out["terms"]
    if "funding_1h_ann_pct" in t and "funding_8h_cex_ann_pct" in t:
        out["curve"]["slope_1h_to_8h_pct"] = round(t["funding_8h_cex_ann_pct"] - t["funding_1h_ann_pct"], 4)
        out["curve"]["reading"] = (
            "FRONT-LOADED (near carry > distant — crowd flipping fast, flush candidate)"
            if out["curve"]["slope_1h_to_8h_pct"] < 0 else
            "BACKWARD-HEAVY (distant carry > near — crowd holding out the curve, structural)"
        )
    # carry-vs-convexity residual: funding − basis/horizon. Basis is a LEVEL (stock); funding is
    # a RATE (flow). The residual isolates the part of funding NOT explained by the basis level.
    if t.get("spot_premium_bp") is not None and t.get("funding_1h_ann_pct") is not None:
        # normalize: 1bp spot premium ~ some annualized carry. We report the SIGN divergence, not a fit.
        prem = t["spot_premium_bp"]; fund = t["funding_1h_ann_pct"]
        out["residual"] = {
            "note": "premium extreme + funding NOT extreme (or reverse) = the D3×D4 contradiction",
            "premium_extreme": abs(prem) > 4.0,
            "funding_high": fund > 10.0,  # 10% ann = nominally high carry
            "contradiction": (abs(prem) > 4.0) != (fund > 10.0),
        }
    return out

def render(o):
    t = o.get("terms", {}); c = o.get("curve", {}); r = o.get("residual")
    print("=========== CARRY TERM-STRUCTURE (D8) — BTC, funding/basis at multiple horizons ===========")
    for k in sorted(t):
        print(f"  {k:<28} {t[k]}")
    if "slope_1h_to_8h_pct" in c:
        print(f"  slope 1h→8h            {c['slope_1h_to_8h_pct']:+.4f}% ann  ({c.get('reading','')})")
    if r:
        print(f"  carry-vs-convexity     premium_extreme={r['premium_extreme']} funding_high={r['funding_high']} "
              f"-> contradiction={r['contradiction']}")
    print("  Mechanism: crowding front-loaded flushes; crowding out the curve is structural. Residual is")
    print("  the independent object breaking the +0.41 basis↔funding redundancy (#47). Forward only.")
    return

if __name__ == "__main__":
    render(build())
