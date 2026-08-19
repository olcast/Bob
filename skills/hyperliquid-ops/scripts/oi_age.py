#!/usr/bin/env python3
"""OI-AGE / COHORT HALF-LIFE (D11) — how STALE the crowd's position is, not just how big.

OI (D-mount) and liqmap (D-geometry) both answer "how much" and "where". The missing object is
"how OLD": a position opened 3 days ago at $61k is a DIFFERENT animal to one opened 3 hours ago at
$64k — different pain tolerance, different stop discipline, different liquidation behavior. Grok's
unique contribution to the 3-model audit was 'funding-tax / OI-age': the crowd that has been paying
funding for days is more fragile than the one that just entered.

Mechanism: track each address's entryPx + first-seen time across ticks (persisted like the address
book). Cohort age = time since entryPx was last materially changed. Underwater OLD cohorts = fuel
that has already bled funding = most likely to capitulate on the next flush.

Free data: clearinghouseState (already swept by collector). Read-only. Forward-only, descriptive.
"""
import json, os, time, urllib.request, argparse, statistics

API = "https://api.hyperliquid.xyz/info"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
COHORT = os.path.join(DATA, "cohort.json")      # addr -> {"entryPx", "firstSeen": ms, "lastPx": ms}
COHORT_LEDGER = os.path.join(DATA, "cohort.jsonl")

def post(body, tries=3):
    for a in range(tries):
        try:
            r = urllib.request.Request(API, data=json.dumps(body).encode(),
                                       headers={"Content-Type": "application/json"})
            return json.load(urllib.request.urlopen(r, timeout=30))
        except Exception:
            if a == tries - 1: return None
            time.sleep(0.6 * (a + 1))

def load():
    try:
        with open(COHORT) as f: return json.load(f)
    except Exception: return {}

def save(c):
    os.makedirs(DATA, exist_ok=True)
    with open(COHORT, "w") as f: json.dump(c, f)

def load_book():
    try:
        with open(os.path.join(DATA, "addressbook.json")) as f: return json.load(f)
    except Exception: return {}

def build(cap=150, coins=("BTC",)):
    ts = int(time.time() * 1000)
    mac = post({"type": "metaAndAssetCtxs"})
    if not mac or len(mac) < 2:
        return None
    uni = {u["name"]: i for i, u in enumerate(mac[0]["universe"])}
    marks = {c: float(mac[1][uni[c]]["markPx"]) for c in coins if c in uni}
    book = load_book()
    addrs = sorted(book, key=lambda a: -book[a])[:cap]
    cohort = load()

    # per-coin aggregation of entryPx age and underwater depth
    # coin -> list of {"age_hours", "adverse_pct", "szi": signed, "ntl": usd}
    agg = {c: [] for c in coins}

    for a in addrs:
        cs = post({"type": "clearinghouseState", "user": a})
        if not isinstance(cs, dict): continue
        prev = cohort.get(a, {})
        prev_ep = prev.get("entryPx")
        first_seen = prev.get("firstSeen", ts)
        for p in cs.get("assetPositions", []):
            pos = p["position"]; c = pos["coin"]
            if c not in marks: continue
            szi = float(pos["szi"]); ep = pos.get("entryPx")
            mark = marks[c]
            if not ep: continue
            epf = float(ep); ntl = abs(szi) * mark
            # adverse distance (long: below entry = losing; short: above entry = losing)
            adv = ((mark - epf) / epf * 100) if szi > 0 else ((epf - mark) / epf * 100)
            age_h = (ts - first_seen) / 3_600_000.0
            # entryPx materially changed => reset cohort age (new position)
            if prev_ep is None or abs(epf - float(prev_ep)) / float(prev_ep) > 0.02:
                first_seen = ts; age_h = 0.0
            cohort[a] = {"entryPx": round(epf, 2), "firstSeen": first_seen, "lastPx": ts}
            agg[c].append({"age_h": age_h, "adv": round(adv, 3), "ntl": ntl, "szi": szi})
        time.sleep(0.06)

    save(cohort)

    rows = []
    out = {}
    for c in coins:
        recs = agg[c]
        if not recs: continue
        ages = [r["age_h"] for r in recs]
        advs = [r["adv"] for r in recs]
        total_ntl = sum(r["ntl"] for r in recs)
        # half-life: median age in hours (half the notional is older than this)
        half_life = statistics.median(ages)
        # OLD + UNDERWATER = capitulation fuel (age > 24h AND adverse)
        old_uw = [r for r in recs if r["age_h"] > 24 and r["adv"] < 0]
        old_uw_ntl = sum(r["ntl"] for r in old_uw)
        # FRESH = just entered (age < 6h)
        fresh = [r for r in recs if r["age_h"] < 6]
        fresh_ntl = sum(r["ntl"] for r in fresh)
        row = {"ts": ts, "kind": "oiage", "coin": c,
               "nCohort": len(recs), "totalNtl": round(total_ntl, 0),
               "medianAgeH": round(half_life, 1),
               "oldUnderwaterNtl": round(old_uw_ntl, 0),
               "oldUnderwaterShare": round(old_uw_ntl / total_ntl, 3) if total_ntl else None,
               "freshNtl": round(fresh_ntl, 0),
               "freshShare": round(fresh_ntl / total_ntl, 3) if total_ntl else None,
               "medianAdversePct": round(statistics.median(advs), 3)}
        rows.append(row)
        out[c] = row

    # append to ledger
    with open(COHORT_LEDGER, "a") as f:
        for r in rows: f.write(json.dumps(r, separators=(",", ":")) + "\n")
    return out

def render(o):
    if not o:
        print("no cohort data"); return
    print("=========== OI-AGE / COHORT HALF-LIFE (D11) — BTC ===========")
    for c, r in o.items():
        print(f"  {c}: nCohort={r['nCohort']}  totalNtl=${r['totalNtl']:,.0f}")
        print(f"      medianAge={r['medianAgeH']}h  old+underwater={r['oldUnderwaterShare'] if r['oldUnderwaterShare'] is not None else 'n/a'} "
              f"(${r['oldUnderwaterNtl']:,.0f})  fresh={r['freshShare'] if r['freshShare'] is not None else 'n/a'} "
              f"(${r['freshNtl']:,.0f})  medAdverse={r['medianAdversePct']}%")
    print("  Mechanism: OLD+UNDERWATER = has paid funding for days + is losing = capitulation fuel on")
    print("  the next flush. FRESH = scale-ins / new money. Half-life = how quickly the book turns over.")
    print("  Forward-only, descriptive. P3–P5 ablate before any live use.")
    return

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, default=150)
    ap.add_argument("--coins", default="BTC")
    a = ap.parse_args()
    coins = tuple(c.strip() for c in a.coins.split(",") if c.strip())
    render(build(a.cap, coins))
