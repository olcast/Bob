#!/usr/bin/env python3
"""OPTIONS SKEW / IV TERM-STRUCTURE (D10) — the volatility SURFACE, not the spot vol.

Every volatility signal on the desk is SPOT-shaped (realized vol, volexp, jump share). But the
market prices risk forward through the OPTIONS SURFACE, and its shape carries information spot vol
cannot: whether the crowd is bidding CONVEXITY (tail hedging, downside puts rich) vs SELLING it
(yield harvesting, calls rich), and whether term structure is in CONTANGO (near IV < far IV, normal)
or BACKWARDATION (near IV > far IV, stress — the crowd is paying up for now-risk).

Free data: Deribit public API (no auth, book_summary_by_currency gives full BTC/ETH options chain
with mark prices + OI). Read-only. Forward-only, descriptive. P3–P5 ablate before any live use.

Measures (per currency, default BTC+ETH):
  - ATM IV (nearest expiry, strike ~ spot): the level of the surface
  - 25-delta risk reversal (d25 call IV − d25 put IV): SKEW. >0 calls bid (greed), <0 puts bid (fear)
  - term slope (near ATM IV − far ATM IV): contango/backwardation
  - put-call OI ratio: positioning tilt on the convexity surface
"""
import json, urllib.request, time, math, datetime, argparse

DERIBIT = "https://www.deribit.com/api/v2/public"

def get(path):
    try:
        r = urllib.request.Request(DERIBIT + path, headers={"User-Agent": "desk/1.0"})
        return json.load(urllib.request.urlopen(r, timeout=20)).get("result")
    except Exception:
        return None

def days_to_exp(exp):
    # Deribit expiry labels: DDMMMYY.
    try:
        d = datetime.datetime.strptime(exp, "%d%b%y")
        return max(0, (d.date() - datetime.datetime.now(datetime.UTC).date()).days)
    except Exception:
        return 9999

def index_price(cur):
    inst = ("BTC-PERPETUAL" if cur == "BTC" else "ETH-PERPETUAL")
    t = get(f"/ticker?instrument_name={inst}")
    if t and "index_price" in t:
        return float(t["index_price"])
    return None

def build_one(cur):
    sp = index_price(cur)
    if not sp:
        return {"currency": cur, "error": "no index price"}
    chain = get(f"/get_book_summary_by_currency?currency={cur}&kind=option") or []
    if not chain:
        return {"currency": cur, "error": "no chain"}

    opts = []
    for o in chain:
        nm = o.get("instrument_name", "")
        if not nm.startswith(cur + "-"): continue
        rest = nm[len(cur)+1:].split("-")
        if len(rest) != 3: continue
        exp, strike, cp = rest[0], float(rest[1]), rest[2]
        iv = o.get("mark_iv")
        oi = o.get("open_interest", 0) or 0
        opts.append({"exp": exp, "strike": strike, "cp": cp,
                     "iv": float(iv) if iv is not None else None,
                     "oi": float(oi)})
    if not opts:
        return {"currency": cur, "error": "no parsed options"}

    exps_sorted = sorted({o["exp"] for o in opts}, key=days_to_exp)
    near_exp = exps_sorted[0] if exps_sorted else None
    far_exp = exps_sorted[-1] if len(exps_sorted) > 1 else near_exp

    def atm_iv(exp):
        sub = [o for o in opts if o["exp"] == exp and o["iv"] is not None]
        if not sub: return None
        atm = min(sub, key=lambda o: abs(o["strike"] - sp))
        return atm["iv"], atm["strike"]

    near_atm = atm_iv(near_exp)
    far_atm = atm_iv(far_exp)

    def iv_at(exp, moneyness, cp):
        target = sp * moneyness
        sub = [o for o in opts if o["exp"] == exp and o["cp"] == cp and o["iv"] is not None]
        if not sub: return None
        return min(sub, key=lambda o: abs(o["strike"] - target))["iv"]

    out = {"currency": cur, "spot": round(sp, 1), "near_expiry": near_exp, "far_expiry": far_exp}
    # NOTE: Deribit mark_iv is ALREADY in percent (34.24 = 34.24%), NOT a fraction.
    if near_atm and near_atm[0] is not None:
        out["atm_iv_pct"] = round(near_atm[0], 2)
    if far_atm and far_atm[0] is not None and near_atm and near_atm[0]:
        slope = (far_atm[0] - near_atm[0])  # already in pp
        out["term_slope_pp"] = round(slope, 2)
        out["term_reading"] = ("CONTANGO" if slope > 0 else "BACKWARDATION")
    c25 = iv_at(near_exp, 1.05, "C"); p25 = iv_at(near_exp, 0.95, "P")
    if c25 is not None and p25 is not None:
        rr = (c25 - p25)  # already in pp
        out["rr_25d_pp"] = round(rr, 2)
        out["skew_reading"] = ("PUT SKEW" if rr < 0 else "CALL SKEW")
    pc = [o for o in opts if o["exp"] == near_exp]
    poi = sum(o["oi"] for o in pc if o["cp"] == "P")
    coi = sum(o["oi"] for o in pc if o["cp"] == "C")
    if coi:
        out["put_call_oi"] = round(poi / coi, 3)
        out["oi_reading"] = ("PUT-HEAVY" if poi / coi > 1 else "CALL-HEAVY")
    out["n_options"] = len(opts)
    return out

def build(currencies=("BTC", "ETH")):
    out = {}
    for c in currencies:
        out[c] = build_one(c)
    return out

def render(m):
    print("=========== OPTIONS SKEW / IV TERM-STRUCTURE (D10) — Deribit (free) ===========")
    for cur, o in m.items():
        if "error" in o:
            print(f"  {cur}: error — {o['error']}")
            continue
        print(f"  {cur}: spot={o.get('spot')}  ATM IV(near)={o.get('atm_iv_pct','n/a')}%  "
              f"term={o.get('term_slope_pp','n/a')}pp [{o.get('term_reading','')}]  "
              f"RR25d={o.get('rr_25d_pp','n/a')}pp [{o.get('skew_reading','')}]  "
              f"P/C OI={o.get('put_call_oi','n/a')} [{o.get('oi_reading','')}]")
    print("  Mechanism: surface shape = crowd's priced view of RISK, not direction. Put skew + backwardation")
    print("  = convexity bid (tail hedge). Call skew + contango = yield/complacency. Independent of spot vol.")
    print("  Forward-only, descriptive. P3–P5 ablate before any live use.")
    return

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--coins", default="BTC,ETH")
    a = ap.parse_args()
    render(build(tuple(c.strip() for c in a.coins.split(",") if c.strip())))
