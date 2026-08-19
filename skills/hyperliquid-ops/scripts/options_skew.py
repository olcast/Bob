#!/usr/bin/env python3
"""OPTIONS SKEW / IV TERM-STRUCTURE (D10) — the volatility SURFACE, not the spot vol.

Every volatility signal on the desk is SPOT-shaped (realized vol, volexp, jump share). But the
market prices risk forward through the OPTIONS SURFACE, and its shape carries information spot vol
cannot: whether the crowd is bidding CONVEXITY (tail hedging, downside puts rich) vs SELLING it
(yield harvesting, calls rich), and whether term structure is in CONTANGO (near IV < far IV, normal)
or BACKWARDATION (near IV > far IV, stress — the crowd is paying up for now-risk).

Free data: Deribit public API (no auth, book_summary_by_currency gives full BTC options chain with
mark prices + OI). Read-only. Forward-only, descriptive. P3–P5 ablate before any live use.

Measures:
  - ATM IV (nearest expiry, strike ~ spot): the level of the surface
  - 25-delta risk reversal (d25 call IV − d25 put IV): SKEW. >0 calls bid (greed), <0 puts bid (fear)
  - term slope (near ATM IV − far ATM IV): contango/backwardation
  - put-call OI ratio: positioning tilt on the convexity surface
"""
import json, urllib.request, time, math

DERIBIT = "https://www.deribit.com/api/v2/public"

def get(path):
    try:
        r = urllib.request.Request(DERIBIT + path, headers={"User-Agent": "desk/1.0"})
        return json.load(urllib.request.urlopen(r, timeout=20)).get("result")
    except Exception:
        return None

def index_price():
    t = get("/ticker?instrument_name=BTC-PERPETUAL")
    if t and "index_price" in t:
        return float(t["index_price"])
    return None

def build():
    sp = index_price()
    if not sp:
        return {"error": "no index price"}
    chain = get("/get_book_summary_by_currency?currency=BTC&kind=option") or []
    if not chain:
        return {"error": "no chain"}

    # parse each option: instrument name BTC-DDMMMYY-XXXXX-C/P, mark_price, open_interest, strike
    opts = []
    for o in chain:
        nm = o.get("instrument_name", "")
        if not nm.startswith("BTC-"): continue
        rest = nm[4:].split("-")
        if len(rest) != 3: continue
        exp, strike, cp = rest[0], float(rest[1]), rest[2]
        mk = o.get("mark_price")
        if mk is None: continue
        iv = o.get("mark_iv")
        oi = o.get("open_interest", 0) or 0
        # expiry ts (approx from name is unreliable; use creation of chain + days)
        opts.append({"exp": exp, "strike": strike, "cp": cp,
                     "iv": float(iv) if iv is not None else None,
                     "oi": float(oi)})
    if not opts:
        return {"error": "no parsed options"}

    # nearest-expiry subset: group by exp string, pick the min (Deribit expiries sortable by name is messy)
    # Use instrument creation timestamps are same; instead sort by days-to-expiry estimated from expiry label
    exps = sorted({o["exp"] for o in opts})

    def days_to_exp(exp):
        # Deribit expiry labels: DDMMMYY. Parse roughly.
        import datetime
        try:
            d = datetime.datetime.strptime(exp, "%d%b%y")
            return max(0, (d.date() - datetime.datetime.now(datetime.UTC).date()).days)
        except Exception:
            return 9999

    exps_sorted = sorted(exps, key=days_to_exp)
    near_exp = exps_sorted[0] if exps_sorted else None
    far_exp = exps_sorted[-1] if len(exps_sorted) > 1 else near_exp

    # ATM = strike closest to spot in nearest expiry
    def atm_iv(exp):
        sub = [o for o in opts if o["exp"] == exp and o["iv"] is not None]
        if not sub: return None
        atm = min(sub, key=lambda o: abs(o["strike"] - sp))
        return atm["iv"], atm["strike"]

    near_atm = atm_iv(near_exp)
    far_atm = atm_iv(far_exp)

    # 25-delta risk reversal: approximate delta by moneyness; compute call/put IV at ~ATM±0.25 delta
    # Simpler robust proxy: IV of the call at strike ~ 1.05*spot vs put at ~0.95*spot (nearest expiry)
    def iv_at(exp, moneyness, cp):
        target = sp * moneyness
        sub = [o for o in opts if o["exp"] == exp and o["cp"] == cp and o["iv"] is not None]
        if not sub: return None
        return min(sub, key=lambda o: abs(o["strike"] - target))["iv"]

    out = {"spot": sp, "near_expiry": near_exp, "far_expiry": far_exp}
    # NOTE: Deribit mark_iv is ALREADY in percent (34.24 = 34.24%), NOT a fraction.
    if near_atm and near_atm[0] is not None:
        out["atm_iv_pct"] = round(near_atm[0], 2)
    if far_atm and far_atm[0] is not None and near_atm and near_atm[0]:
        slope = (far_atm[0] - near_atm[0])  # already in pp
        out["term_slope_pp"] = round(slope, 2)   # + = contango, - = backwardation
        out["term_reading"] = ("CONTANGO (near<far — normal)" if slope > 0 else
                               "BACKWARDATION (near>far — stress/convexity bid)")
    c25 = iv_at(near_exp, 1.05, "C"); p25 = iv_at(near_exp, 0.95, "P")
    if c25 is not None and p25 is not None:
        rr = (c25 - p25)  # already in pp
        out["rr_25d_pp"] = round(rr, 2)
        out["skew_reading"] = ("PUT SKEW (puts rich — fear/tail bid)" if rr < 0 else
                               "CALL SKEW (calls rich — greed/speculation)")
    # put-call OI ratio (all expiries, nearest expiry)
    pc = [o for o in opts if o["exp"] == near_exp]
    poi = sum(o["oi"] for o in pc if o["cp"] == "P")
    coi = sum(o["oi"] for o in pc if o["cp"] == "C")
    if coi:
        out["put_call_oi"] = round(poi / coi, 3)
        out["oi_reading"] = ("PUT-HEAVY (defensive positioning)" if poi / coi > 1 else
                             "CALL-HEAVY (speculative positioning)")
    out["n_options"] = len(opts)
    return out

def render(o):
    if "error" in o:
        print(f"D10 OPTIONS SKEW — error: {o['error']}")
        return
    print("=========== OPTIONS SKEW / IV TERM-STRUCTURE (D10) — BTC (Deribit, free) ===========")
    print(f"  spot                 {o.get('spot')}")
    print(f"  ATM IV (near)        {o.get('atm_iv_pct','n/a')}%   ({o.get('near_expiry')})")
    print(f"  term slope (near→far){o.get('term_slope_pp','n/a')}pp  {o.get('term_reading','')}")
    print(f"  25d risk reversal    {o.get('rr_25d_pp','n/a')}pp  {o.get('skew_reading','')}")
    print(f"  put/call OI          {o.get('put_call_oi','n/a')}  {o.get('oi_reading','')}")
    print(f"  n options parsed     {o.get('n_options','n/a')}")
    print("  Mechanism: surface shape = crowd's priced view of RISK, not direction. Put skew + backwardation")
    print("  = convexity bid (tail hedge). Call skew + contango = yield/complacency. Independent of spot vol.")
    print("  Forward-only, descriptive. P3–P5 ablate before any live use.")
    return

if __name__ == "__main__":
    render(build())
