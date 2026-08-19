#!/usr/bin/env python3
"""CROSS-VENUE DIVERGENCE (D7) — the "island problem" sensor. OLIVIER + unanimous 3-model gap #1.

The desk's D3 basis and D4 funding are HL-VENUE-LOCAL. BTC's real book is HL + Binance + Bybit + OKX
+ CME. The same perp premium or funding extreme on HL means two OPPOSITE things depending on whether the
rest of the complex agrees:

  - LOCAL dislocation  : HL premium/funding extreme + CEX flat  -> arbable, mean-reverts (often HL-only).
  - SYSTEMIC crowd      : HL extreme + CEX taker/OI/funding agreeing -> the real crowd, travels.

Doctrine #44/#46 already says basis LEADS the reversal. But it measures ONE venue's basis. This sensor
measures the SAME contract across venues, and emits the DIVERGENCE vector:

  mark_gap_bp      : HL BTC mark  −  CEX-composite mid  (bp of mid). Positive = HL trades rich.
  funding_gap      : HL 1h funding (annualized) − CEX 8h funding (annualized). Sign + magnitude = who is
                     paying MORE to be long here vs there.
  oi_share         : HL OI as a fraction of HL+CEX composite (where does the size actually live).
  venue_lead       : which venue's mark moved first over the last N candles (first-to-move on impulses).

The signal is NOT any single gap — it is whether the gaps are CONSISTENT (systemic) or SPLIT (local).
Mechanism: venue-local positioning gets arb'd away (fades); global positioning travels (persists).

FREE data only: HL /info (mark, predictedFundings, metaAndAssetCtxs OI), Binance fapi premiumIndex +
openInterest, Bybit v5 tickers. No paid feeds.

Read-only, descriptive. BTC only. Collected forward — do NOT back-test this into a live combo yet
(doctrine #46/#53: it must first show it flips a decision, via VCP P3–P5 ablation).
"""
import json, urllib.request, time, statistics, math

HL = "https://api.hyperliquid.xyz/info"
BIN_PI = "https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT"
BIN_OI = "https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT"
BYBIT_T = "https://api.bybit.com/v5/market/tickers?category=linear&symbol=BTCUSDT"

def get(url, timeout=15):
    try:
        r = urllib.request.Request(url, headers={"User-Agent": "desk/1.0"})
        return json.load(urllib.request.urlopen(r, timeout=timeout))
    except Exception as e:
        return {"_err": str(e)}

def hl_post(b):
    try:
        r = urllib.request.Request(HL, data=json.dumps(b).encode(), headers={"Content-Type": "application/json"})
        return json.load(urllib.request.urlopen(r, timeout=20))
    except Exception as e:
        return {"_err": str(e)}

def hl_mark_oi_funding():
    """HL BTC mark + OI + current funding (1h)."""
    out = {}
    mids = hl_post({"type": "allMids"})
    meta = hl_post({"type": "metaAndAssetCtxs"})
    if isinstance(mids, dict) and "BTC" in mids:
        out["mark"] = float(mids["BTC"])
    if isinstance(meta, list) and len(meta) >= 2:
        universe = meta[0].get("universe", [])
        idx = [i for i, a in enumerate(universe) if a.get("name") == "BTC"]
        if idx:
            ctx = meta[1][idx[0]]
            out["oi"] = float(ctx.get("openInterest", 0) or 0)
            out["funding_1h"] = float(ctx.get("funding", 0) or 0)
    # predictedFundings for horizon-normalized cross-venue funding
    pf = hl_post({"type": "predictedFundings"})
    if isinstance(pf, list):
        for row in pf:
            if isinstance(row, list) and len(row) >= 2 and row[0] == "BTC":
                for venue, v in row[1]:
                    if isinstance(v, dict):
                        rate = float(v.get("fundingRate", 0))
                        hrs = float(v.get("fundingIntervalHours", 8))
                        out[f"funding_{venue}"] = {
                            "rate": rate,
                            "annualized_pct": round(rate * (365 * 24 / hrs) * 100, 4),
                        }
                break
    return out

def cex_composite():
    """Binance + Bybit mark/funding/OI -> composite mid + funding (annualized) + OI."""
    out = {}
    b = get(BIN_PI); bb = get(BIN_OI); by = get(BYBIT_T)
    marks = []; fundings = {}; ois = []
    if isinstance(b, dict) and "markPrice" in b:
        marks.append(float(b["markPrice"]))
        fundings["binance"] = float(b.get("lastFundingRate", 0))
    if isinstance(bb, dict) and "openInterest" in bb:
        ois.append(float(bb["openInterest"]))
    if isinstance(by, dict) and by.get("retCode") == 0:
        lst = by.get("result", {}).get("list", [])
        if lst:
            m = lst[0]
            marks.append(float(m.get("markPrice", 0)))
            fundings["bybit"] = float(m.get("fundingRate", 0))
            ois.append(float(m.get("openInterestValue", 0) or m.get("openInterest", 0)))
    if marks:
        out["mark"] = statistics.mean(marks)
    # annualize 8h funding (Binance/Bybit interval is 8h) -> pct
    out["funding_annualized_pct"] = {}
    for venue, rate in fundings.items():
        out["funding_annualized_pct"][venue] = round(rate * (365 * 24 / 8) * 100, 4)
    if ois:
        out["oi_usd"] = sum(ois)
    return out

def venue_lead(hours=6):
    """First-to-move on impulses: compare HL vs Binance kline direction over recent 5m closes.
    Approx — full lead-lag (100–500ms) needs websocket; this is a coarse 5m-candle cousin."""
    try:
        import datetime
        now = int(time.time() * 1000)
        interval = "5m"
        win = hours * 12  # 5m bars per hour
        hl = hl_post({"type": "candleSnapshot", "req": {"coin": "BTC", "interval": interval,
                     "startTime": now - hours * 3600_000, "endTime": now}})
        # Binance klines
        burl = f"https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=5m&limit={win}"
        bkl = get(burl)
        if not (isinstance(hl, list) and hl) or not (isinstance(bkl, list) and bkl):
            return None
        def closes(cands):
            return [float(c["c"]) for c in cands]
        hlc = closes(hl); bc = [float(k[4]) for k in bkl]
        m = min(len(hlc), len(bc))
        hlc = hlc[-m:]; bc = bc[-m:]
        # lead-lag: correlation of HL return with Binance return at lags -3..+3
        best = (0, None)
        for lag in range(-3, 4):
            xs = [(hlc[i] / hlc[i-1] - 1) for i in range(1, m)]
            ys = [(bc[i+lag] / bc[i+lag-1] - 1) for i in range(1, m) if 0 < i+lag < m]
            n = min(len(xs), len(ys))
            if n < 20:
                continue
            xs = xs[:n]; ys = ys[:n]
            mx, my = statistics.mean(xs), statistics.mean(ys)
            vx = math.sqrt(sum((x-mx)**2 for x in xs)); vy = math.sqrt(sum((y-my)**2 for y in ys))
            if vx == 0 or vy == 0:
                continue
            r = sum((xs[k]-mx)*(ys[k]-my) for k in range(n)) / (vx*vy)
            if abs(r) > abs(best[0]):
                best = (r, lag)
        return {"corr": round(best[0], 3), "lead_lag_hl_wins_by": f"{best[1]} bars (hl leads bins if >0)" if best[1] is not None else None}
    except Exception as e:
        return {"_err": str(e)}

def build():
    hl = hl_mark_oi_funding()
    cx = cex_composite()
    lead = venue_lead()
    out = {"hl": hl, "cex": cx, "lead_lag": lead, "divergence": {}}
    if "mark" in hl and "mark" in cx:
        out["divergence"]["mark_gap_bp"] = round((hl["mark"] - cx["mark"]) / cx["mark"] * 1e4, 2)
    if "funding_annualized_pct" in cx and "funding_1h" in hl:
        hl_ann = hl["funding_1h"] * (365 * 24 / 1) * 100  # HL funding is 1h -> annualize
        cex_ann = statistics.mean(cx["funding_annualized_pct"].values())
        out["divergence"]["funding_gap_pct"] = round(hl_ann - cex_ann, 4)
        out["divergence"]["hl_funding_ann_pct"] = round(hl_ann, 4)
        out["divergence"]["cex_funding_ann_pct"] = round(cex_ann, 4)
    # OI unit fix: HL openInterest is in CONTRACT BASE (BTC count); CEX OI is USD notional.
    # Normalize HL to USD notional by mark price so the share is apples-to-apples.
    if "oi" in hl and "oi_usd" in cx and "mark" in hl:
        hl_usd = hl["oi"] * hl["mark"]
        out["divergence"]["oi_share_hl_pct"] = round(hl_usd / (hl_usd + cx["oi_usd"]) * 100, 2)
        out["divergence"]["hl_oi_usd"] = round(hl_usd, 0)
    return out

def render(o):
    d = o.get("divergence", {})
    hl = o.get("hl", {}); cx = o.get("cex", {}); lead = o.get("lead_lag", {})
    print("=========== CROSS-VENUE DIVERGENCE (D7) — BTC, HL vs Binance/Bybit ===========")
    print(f"  HL mark          {hl.get('mark','n/a')}   OI {hl.get('oi','n/a'):,.0f}")
    print(f"  CEX mark         {cx.get('mark','n/a')}   OI ${cx.get('oi_usd',0):,.0f}")
    print(f"  mark_gap_bp      {d.get('mark_gap_bp','n/a')}  (HL rich if >0)")
    print(f"  funding HL {d.get('hl_funding_ann_pct','n/a')}% vs CEX {d.get('cex_funding_ann_pct','n/a')}% ann  -> gap {d.get('funding_gap_pct','n/a')}%")
    print(f"  OI share HL      {d.get('oi_share_hl_pct','n/a')}% of HL+CEX   (HL ${d.get('hl_oi_usd',0):,.0f} notional)")
    if lead and "corr" in lead:
        print(f"  lead-lag (5m)    corr {lead.get('corr')} · {lead.get('lead_lag_hl_wins_by','')}")
    # the read (mechanism, not a signal)
    mg = d.get("mark_gap_bp"); fg = d.get("funding_gap_pct")
    if mg is not None and fg is not None:
        same = (mg > 0) == (fg > 0)
        print(f"  READ: mark_gap {'+' if mg>0 else '-'} and funding_gap {'+' if fg>0 else '-'} are "
              + ("SAME-SIGN (consistent — global/systemic read)" if same
                 else "OPPOSITE-SIGN (split — local dislocation / arb candidate)"))
    print("  Mechanism: local premium decays (arb'd), global travels (persists). Collected FORWARD only.")
    return

if __name__ == "__main__":
    render(build())
