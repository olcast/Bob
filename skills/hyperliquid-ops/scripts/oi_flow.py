#!/usr/bin/env python3
"""
oi_flow.py — positioning tracker: open interest, funding drift and premium.

Why this exists. On a low-turnover venue the tape is noise and the positioning
is the signal. `xyz:SP500` carries roughly $477M of open interest on $88M of
daily volume — turnover of 0.18. Positions sit there for days. That means the
information is not in who hit the bid in the last ninety seconds; it is in which
side has been paying to hold, for how long, and how much of it is stacked up
waiting to be flushed.

What it measures:
  * OPEN INTEREST, in notional, and its change since the last saved snapshot.
  * TURNOVER (24h volume / OI). Low = a position-holding venue, read funding
    and OI. High = a trading venue, read the tape (orderflow.py).
  * FUNDING DRIFT over 3 days. One hourly print is noise; a rate that has sat
    on one side for seventy-two hours is a crowd that has been paying rent.
  * PREMIUM (mark vs oracle). Sustained premium is leveraged demand, not value.
  * SIGN FLIPS. Funding crossing zero is a positioning reset, and it dates it.

The reads it is built to produce:
  * CROWDED SHORTS  — persistently negative funding + heavy OI = squeeze fuel.
  * CROWDED LONGS   — persistently positive funding + heavy OI = flush fuel.
  * OI vs PRICE     — OI up while price falls means NEW shorts (aggressive).
                      OI down while price falls means longs being liquidated
                      (capitulation, and it exhausts itself).

Usage:
    python3 scripts/oi_flow.py
    python3 scripts/oi_flow.py --coins xyz:SP500,BTC --days 5
    python3 scripts/oi_flow.py --json
    python3 scripts/oi_flow.py --no-save        # don't write a snapshot

Read-only against the exchange: public info endpoint only. Never touches
/exchange. The only thing it writes is its own local snapshot file.
"""

import argparse
import datetime
import json
import os
import statistics
import sys
import time
import urllib.request

API = "https://api.hyperliquid.xyz/info"

DEFAULT_COINS = ["xyz:SP500", "xyz:XYZ100", "xyz:BRENTOIL", "xyz:CL",
                 "xyz:GOLD", "xyz:XLE", "xyz:JP225", "BTC", "ETH", "SOL", "HYPE"]

STATE = os.path.expanduser("~/.hyperliquid-ops/oi_state.json")

HOURS_PER_YEAR = 24 * 365


def post(body):
    req = urllib.request.Request(
        API, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=25))


def contexts():
    """{coin: ctx} across the main dex and the xyz builder dex."""
    out = {}
    for dex in ("", "xyz"):
        body = {"type": "metaAndAssetCtxs"}
        if dex:
            body["dex"] = dex
        meta, ctxs = post(body)
        for u, c in zip(meta["universe"], ctxs):
            mark = float(c["markPx"])
            prev = float(c["prevDayPx"]) if c.get("prevDayPx") else 0.0
            oracle = float(c["oraclePx"]) if c.get("oraclePx") else 0.0
            oi_units = float(c.get("openInterest") or 0)
            out[u["name"]] = {
                "dex": dex or "main",
                "mark": mark,
                "oracle": oracle,
                "chg": (mark / prev - 1) * 100 if prev else 0.0,
                "oi_units": oi_units,
                "oi_usd": oi_units * mark,
                "vlm_usd": float(c.get("dayNtlVlm") or 0),
                "funding_apr": float(c["funding"]) * HOURS_PER_YEAR * 100,
                "premium_bp": (mark / oracle - 1) * 10000 if oracle else 0.0,
            }
    return out


def baselines():
    """The neutral funding rate per dex, measured rather than assumed.

    Hyperliquid funding = premium + an interest-rate component. When positioning
    is perfectly neutral the rate does NOT sit at zero, it sits at that baseline
    — empirically 10.95% APR on the main dex and 5.475% on xyz. Reading raw
    funding as crowding therefore labels every quiet market "crowded longs",
    which is exactly the false positive this function exists to kill. The median
    across the whole dex universe is the honest zero point.
    """
    out = {}
    for dex in ("", "xyz"):
        body = {"type": "metaAndAssetCtxs"}
        if dex:
            body["dex"] = dex
        _meta, ctxs = post(body)
        rates = [float(c["funding"]) * HOURS_PER_YEAR * 100 for c in ctxs]
        out[dex or "main"] = statistics.median(rates) if rates else 0.0
    return out


# Premium noise floor, in basis points. Below this the perp is at fair value and
# there is no positioning story to tell.
PREM_FLOOR_BP = 4.0


def funding_drift(coin, days):
    """Hourly history -> who has actually been paying, measured on PREMIUM.

    Premium is the perp's deviation from the oracle, i.e. what leveraged demand
    is willing to pay over spot. It is the clean crowding signal. The funding
    rate is premium plus a constant, so it is not.
    """
    start = int(time.time() * 1000) - days * 86400000
    try:
        h = post({"type": "fundingHistory", "coin": coin, "startTime": start})
    except Exception:  # noqa: BLE001
        return None
    if not h:
        return None
    rates = [float(x["fundingRate"]) for x in h]
    prem = [float(x["premium"]) * 10000 for x in h]  # bp
    n = len(rates)

    cum_pct = sum(rates) * 100                      # cost of being long, %
    mean_apr = statistics.mean(rates) * HOURS_PER_YEAR * 100
    mean_prem = statistics.mean(prem)

    pos = sum(1 for p in prem if p > PREM_FLOOR_BP)
    neg = sum(1 for p in prem if p < -PREM_FLOOR_BP)
    flat = n - pos - neg

    # a flip only counts if the premium was meaningful on BOTH sides of it —
    # otherwise every wobble across zero reads as a "positioning reset"
    flip_hours_ago = None
    sig = [1 if p > PREM_FLOOR_BP else (-1 if p < -PREM_FLOOR_BP else 0)
           for p in prem]
    last = next((s for s in reversed(sig) if s), 0)
    if last:
        for i in range(n - 2, -1, -1):
            if sig[i] and sig[i] != last:
                flip_hours_ago = n - 1 - i
                break

    half = n // 2 or 1
    early, late = statistics.mean(prem[:half]), statistics.mean(prem[half:])

    return {"hours": n, "cum_pct": cum_pct, "mean_apr": mean_apr,
            "mean_prem_bp": mean_prem, "pos_hours": pos, "neg_hours": neg,
            "flat_hours": flat,
            "pct_one_side": max(pos, neg) / n * 100,
            "side": ("longs paying up" if mean_prem > 0 else
                     "shorts paying up" if mean_prem < 0 else "flat"),
            "early_prem_bp": early, "late_prem_bp": late,
            "building": abs(late) > abs(early),
            "flip_hours_ago": flip_hours_ago}


def load_state(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return None


def save_state(path, payload):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(payload, f)
        return True
    except Exception as e:  # noqa: BLE001
        print(f"(could not save snapshot: {e})", file=sys.stderr)
        return False


def read_positioning(row):
    """Turn the numbers into the two or three sentences that are actually
    tradeable. Every claim here names the number behind it."""
    notes = []
    d, c = row.get("drift"), row
    turnover = c["vlm_usd"] / c["oi_usd"] if c["oi_usd"] else 0

    # Small books produce enormous funding and premium numbers that mean
    # nothing — one participant moves them. Say so and stop.
    if c["oi_usd"] < 10e6:
        return [f"TOO SMALL TO READ: ${c['oi_usd']/1e6:.1f}m open interest. "
                f"Funding ({c['excess_apr']:+.0f}% excess APR) and premium "
                f"({c['premium_bp']:+.1f}bp) here are one participant, not a "
                "crowd. Ignore this row."]

    if d and d["hours"] >= 24:
        crowded = d["pct_one_side"] >= 70 and abs(d["mean_prem_bp"]) >= PREM_FLOOR_BP
        if crowded and d["mean_prem_bp"] < 0:
            notes.append(
                f"CROWDED SHORTS: perp held below oracle {d['neg_hours']}/"
                f"{d['hours']}h, mean {d['mean_prem_bp']:.1f}bp discount — shorts "
                f"are paying up to stay short. Squeeze fuel, and it is "
                f"{'building' if d['building'] else 'fading'} "
                f"({d['early_prem_bp']:.1f}bp -> {d['late_prem_bp']:.1f}bp).")
        if crowded and d["mean_prem_bp"] > 0:
            notes.append(
                f"CROWDED LONGS: perp held above oracle {d['pos_hours']}/"
                f"{d['hours']}h, mean {d['mean_prem_bp']:.1f}bp premium, longs "
                f"paying {d['cum_pct']:.3f}% in funding over the window. "
                f"Leveraged length paying rent is what gets flushed first "
                f"({'building' if d['building'] else 'fading'}: "
                f"{d['early_prem_bp']:.1f}bp -> {d['late_prem_bp']:.1f}bp).")
        if not crowded and d["flat_hours"] / d["hours"] > 0.8:
            notes.append(
                f"Positioning is NEUTRAL — premium inside +/-{PREM_FLOOR_BP:.0f}bp "
                f"for {d['flat_hours']}/{d['hours']}h. No crowd to squeeze or "
                "flush. Do not manufacture one out of the funding rate.")
        if d["flip_hours_ago"] is not None and d["flip_hours_ago"] <= 12:
            notes.append(
                f"Premium flipped sign {d['flip_hours_ago']}h ago (a real flip: "
                "meaningful on both sides) — the older crowding read is stale.")

    if c["oi_usd"] > 0:
        if turnover < 0.4:
            notes.append(
                f"Turnover {turnover:.2f} (24h volume / OI) — this is a "
                "position-holding venue, not a trading venue. Read funding and "
                "OI here; the 90-second tape is noise.")
        elif turnover > 2.0:
            notes.append(
                f"Turnover {turnover:.2f} — genuinely traded. The tape "
                "(orderflow.py) carries real information on this one.")

    if abs(c["premium_bp"]) > 15:
        side = "over" if c["premium_bp"] > 0 else "under"
        notes.append(
            f"Perp is {abs(c['premium_bp']):.0f}bp {side} the oracle. Sustained "
            "premium is leveraged demand, not value — it mean-reverts via "
            "funding or via a flush.")

    doi = c.get("d_oi_pct")
    if doi is not None and abs(doi) >= 1.0:
        if doi > 0 and c["chg"] < 0:
            notes.append(
                f"OI +{doi:.1f}% while price is {c['chg']:+.2f}% — NEW shorts "
                "being put on, not longs covering. Aggressive, and it builds the "
                "fuel for the squeeze rather than relieving it.")
        elif doi < 0 and c["chg"] < 0:
            notes.append(
                f"OI {doi:.1f}% while price is {c['chg']:+.2f}% — longs being "
                "closed out. Capitulation exhausts itself; this is late in a "
                "move, not early.")
        elif doi > 0 and c["chg"] > 0:
            notes.append(
                f"OI +{doi:.1f}% with price {c['chg']:+.2f}% — new length "
                "chasing. Confirms the move and builds downside fuel at once.")
        elif doi < 0 and c["chg"] > 0:
            notes.append(
                f"OI {doi:.1f}% with price {c['chg']:+.2f}% — shorts covering, "
                "not new buying. Squeezes end when the covering does.")
    return notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coins", default=",".join(DEFAULT_COINS))
    ap.add_argument("--days", type=int, default=3,
                    help="funding history window (default 3)")
    ap.add_argument("--state", default=STATE, help="snapshot file path")
    ap.add_argument("--no-save", action="store_true",
                    help="read the previous snapshot but do not overwrite it")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    coins = [c.strip() for c in a.coins.split(",") if c.strip()]

    try:
        ctx = contexts()
    except Exception as e:  # noqa: BLE001
        print(f"FETCH FAILED: {e}\nDo not proceed on cached numbers.",
              file=sys.stderr)
        return 2

    try:
        base = baselines()
    except Exception:  # noqa: BLE001
        base = {"main": 10.95, "xyz": 5.475}

    prev = load_state(a.state)
    prev_oi = (prev or {}).get("oi_units", (prev or {}).get("oi_usd", {}))
    prev_ts = (prev or {}).get("ts")
    age_h = (time.time() - prev_ts) / 3600 if prev_ts else None

    rows = []
    for coin in coins:
        c = ctx.get(coin)
        if not c:
            continue
        row = dict(coin=coin, **c)
        row["turnover"] = c["vlm_usd"] / c["oi_usd"] if c["oi_usd"] else 0
        row["baseline_apr"] = base.get(c["dex"], 0.0)
        row["excess_apr"] = c["funding_apr"] - row["baseline_apr"]
        po = prev_oi.get(coin)
        if po:
            mk = c.get("mark") or c.get("markPx")
            cur_units = (c["oi_usd"] / mk) if mk else c["oi_usd"]      # OI change on UNITS, not notional
            row["d_oi_pct"] = (cur_units / po - 1) * 100                # so a pure price move no longer fabricates "flow"
        row["drift"] = funding_drift(coin, a.days)
        row["reads"] = read_positioning(row)
        rows.append(row)

    now = datetime.datetime.now(datetime.timezone.utc)

    if not a.no_save:
        save_state(a.state, {"ts": time.time(),
                             "oi_units": {r["coin"]: ((r["oi_usd"]/(r.get("mark") or r.get("markPx"))) if (r.get("mark") or r.get("markPx")) else r["oi_usd"]) for r in rows},
                             "oi_usd": {r["coin"]: r["oi_usd"] for r in rows}})

    if a.json:
        print(json.dumps({"asOfUtc": now.isoformat(), "snapshotAgeHours": age_h,
                          "rows": rows}, indent=2, default=str))
        return 0

    print(f"POSITIONING — OI, FUNDING DRIFT, PREMIUM — "
          f"{now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    if age_h is None:
        print("No previous snapshot on this machine, so there is NO OI delta "
              "this run. Say that out loud rather than implying a change. "
              "Run it again later and the delta appears.")
    else:
        print(f"OI change measured against a snapshot {age_h:.1f}h old.")
    print()

    print("Neutral funding baseline (measured, median of each dex): "
          + ", ".join(f"{k} {v:.2f}% APR" for k, v in base.items())
          + ". Only the EXCESS over that baseline is positioning.")
    print()

    hdr = (f"{'coin':<14}{'mark':>11}{'24h%':>8}{'OI $m':>9}{'dOI%':>8}"
           f"{'turn':>7}{'excAPR':>9}{'prem bp':>9}{f'{a.days}d prem':>10}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        d = r["drift"]
        doi = f"{r['d_oi_pct']:+.1f}" if r.get("d_oi_pct") is not None else "  -"
        print(f"{r['coin']:<14}{r['mark']:>11.3f}{r['chg']:>7.2f}%"
              f"{r['oi_usd']/1e6:>9.1f}{doi:>8}{r['turnover']:>7.2f}"
              f"{r['excess_apr']:>8.1f}%{r['premium_bp']:>9.1f}"
              f"{(d['mean_prem_bp'] if d else 0):>10.1f}")
    print()
    print("turn = 24h volume / open interest. Under ~0.4 the tape is noise and "
          "positioning is the signal; over ~2 the tape is worth reading.")
    print(f"excAPR = funding minus the dex baseline. prem bp = perp vs oracle "
          f"now; {a.days}d prem = its mean over the window. Inside "
          f"+/-{PREM_FLOOR_BP:.0f}bp is fair value, not a crowd.")
    print()

    any_read = False
    for r in rows:
        if not r["reads"]:
            continue
        any_read = True
        print(f"{r['coin']}")
        for n in r["reads"]:
            print(f"  * {n}")
        print()
    if not any_read:
        print("No positioning extremes: funding is two-sided, OI is stable and "
              "premiums are inside 15bp. Nothing is crowded, so there is no "
              "squeeze or flush setup to lean on. That is a real answer.")
        print()

    print("Caveats: OI is venue-local — it is Hyperliquid positioning, not the "
          "underlying market's. Funding tells you who is paying, never which "
          "way price goes next: crowded can stay crowded for weeks. Use this to "
          "size the fuel behind a move you already have a reason to expect.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
