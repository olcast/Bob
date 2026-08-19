#!/usr/bin/env python3
"""JUMP GEOMETRY (D9) — realized-vol / bipower / jump-share.

Every flow lens on the desk is DIFFUSION-shaped (velocity % change, acceleration, CVD slope, vol
expansion). But perps DIE IN JUMPS (liq cascades, oracle moves, weekend re-marks on xyz). Doctrine
#41's own model is a 'leverage washing machine — perps die in jumps'. So the honest regime question
is: is this hour's move a smooth diffusion (pulse 'efficiency' is valid) or a jump (pulse's diffusion
estimator is in the wrong physical regime)?

Barndorff-Nielsen/Shephard bipower variation estimates the CONTINUOUS (non-jump) variance from the
product of adjacent absolute returns; the jump contribution is `J = 1 − BV/RV`. High J => the move
was jumpy => diffusion lenses under-read it => be suspicious of 'accelerating efficiency' verdicts.

RV  = realized variance = sum of squared log-returns over the window.
BV  = bipower variation = (pi/2) * sum(|r_i| * |r_{i-1}|)  (robust to jumps).
J   = 1 − BV/RV  (fraction of variance from jumps; clamp to [0,1]).

Computed from candles already pulled everywhere (5m/15m/1h). FREE. Read-only. BTC. Forward only.
"""
import json, urllib.request, time, math, statistics, argparse

HL = "https://api.hyperliquid.xyz/info"

def post(body):
    try:
        r = urllib.request.Request(HL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        return json.load(urllib.request.urlopen(r, timeout=30))
    except Exception:
        return None

def jump_share(closes, times):
    """Return {rv, bv, J, vol_pct, n} from a list of closes (chronological). J = jump share of variance."""
    n = len(closes)
    if n < 3:
        return None
    logr = [math.log(closes[i] / closes[i-1]) for i in range(1, n)]
    rv = sum(r * r for r in logr)
    # bipower: pi/2 * sum(|r_i| |r_{i-1}|)
    bv = (math.pi / 2) * sum(abs(logr[i]) * abs(logr[i-1]) for i in range(1, len(logr)))
    if rv <= 0:
        return {"rv": 0.0, "bv": 0.0, "J": 0.0, "vol_ann_pct": 0.0, "n": n}
    J = max(0.0, min(1.0, 1 - bv / rv))
    vol = math.sqrt(rv / (n - 1)) * math.sqrt(365 * 24)  # rough annualized (assumes 1h bars)
    return {"rv": rv, "bv": bv, "J": round(J, 3), "vol_ann_pct": round(vol * 100, 2), "n": n}

def build(interval="1h", bars=96):
    now = int(time.time() * 1000)
    step = {"5m": 300_000, "15m": 900_000, "1h": 3_600_000, "4h": 14_400_000}[interval]
    d = post({"type": "candleSnapshot", "req": {"coin": "BTC", "interval": interval,
              "startTime": now - bars * step, "endTime": now}}) or []
    if not d:
        return None
    closes = [float(c["c"]) for c in d]
    times = [int(c["t"]) for c in d]
    # full-window jump share + a rolling profile across sub-windows
    full = jump_share(closes, times)
    # rolling: split into ~8 sub-windows to see if jumpiness is NOW vs historical
    sub = []
    w = max(4, len(closes) // 8)
    for i in range(w, len(closes) + 1, w):
        seg = closes[max(0, i-w):i]
        js = jump_share(seg, times[max(0, i-w):i])
        if js:
            sub.append(round(js["J"], 3))
    return {"interval": interval, "bars": bars, "full": full,
            "rolling_J": sub,
            "reading": jump_read(full, sub)}

def jump_read(full, rolling_J):
    if not full:
        return "no data"
    J = full["J"]
    regime = "SMOOTH (diffusion — efficiency lenses valid)" if J < 0.30 else (
             "MIXED" if J < 0.60 else "JUMP-DOMINATED (diffusion lenses WRONG regime)")
    recent = rolling_J[-3:] if rolling_J else []
    accel = ("JUMPINESS RISING" if recent and recent[-1] > statistics.mean(recent[:-1]) + 0.1
             else ("JUMPINESS FADING" if recent and recent[-1] < statistics.mean(recent[:-1]) - 0.1
                   else "JUMPINESS STABLE"))
    return f"{regime} · {accel}"

def render(o):
    f = o.get("full", {}); r = o.get("rolling_J", [])
    print(f"=========== JUMP GEOMETRY (D9) — BTC {o.get('interval')} x {o.get('bars')} bars ===========")
    if f:
        print(f"  RV (realized var)      {f.get('rv',0):.2e}")
        print(f"  BV (bipower var)       {f.get('bv',0):.2e}")
        print(f"  J (jump share)         {f.get('J')}   ({f.get('n')} bars)")
        print(f"  vol (ann)              {f.get('vol_ann_pct')}%")
    print(f"  rolling J (old→new)    {r}")
    print(f"  READ: {o.get('reading','')}")
    print("  Mechanism: perps die in jumps (#41). J>0.6 => pulse 'efficiency' is in the wrong regime;")
    print("  trust acceptance/occupancy + jump geometry over diffusion velocity. Forward only.")
    return

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", default="1h")
    ap.add_argument("--bars", type=int, default=96)
    a = ap.parse_args()
    o = build(a.interval, a.bars)
    if o:
        render(o)
    else:
        print("no candle data returned")
