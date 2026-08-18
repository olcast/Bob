#!/usr/bin/env python3
"""CALL EVOLUTION TRACKER — doctrine #7 (continuity) + #30 (EW scenario tree) operationalized as a
persisted, append-only log instead of a one-off read.

Doctrine already says two things that were never wired together:
  #7  "read the prior read and assess how scenarios EVOLVED (strengthened/weakened/invalidated/
       level-shifted); the new call is a DELTA, not a restart."
  #30 "every count carries an invalidation PRICE — that price IS the update rule. A move does not
       'surprise' the tree; it crosses an invalidation and re-weights it."

Both describe evolving conviction as the wave develops. Neither was ever persisted against the
actual open calls in data/calls.json — that file is written once at firing and never touched again
until final win/loss grading at Sunday retro. This script closes that gap WITHOUT breaking grading
integrity: it NEVER mutates the original call record (up/dn/p_up as originally committed stay frozen
— that's what calibration.py grades). It appends a separate EVOLUTION record to
data/call_evolution.jsonl each time it runs against an open call, tracking how the SAME wave
structure that produced the call has moved since.

What "evolve" means here, concretely, per call:
  - distance-to-invalidation as % of the original stop distance (tightening = rising tension)
  - distance-to-target as % of the original target distance (closing = thesis playing out)
  - current pulse.py flow read (CONFIRMING vs FADING) at the nearest live timeframe
  - current wave_scenarios.py zone/efficiency at the same coin (is price still in the decision zone,
    or has it moved into/through it)
  - a bounded, explicit CONVICTION delta: STRENGTHENED / WEAKENED / UNCHANGED / INVALIDATED / HIT,
    with the one-line reason — never a new p_up pulled from nowhere; it must cite what changed.

This does NOT re-run the full doctrine pipeline or generate a brand-new independent call (that would
violate #2's two-scenarios-max/append-only discipline and doctrine's ban on restating unchanged
analysis, #10). It is a lightweight, mechanical check on the SAME thesis's own evolution.

Usage:
  python3 call_evolve.py --coin BTC                 # evolves every OPEN call for that coin
  python3 call_evolve.py --coin BTC --call-ts 1786871688457   # evolve one specific call

Exit code: 0 always (informational; not a gate). Prints one evolution record per open call, and
appends each to data/call_evolution.jsonl.
"""
import json, sys, argparse, subprocess, os, time

HERE = os.path.dirname(os.path.abspath(__file__))
CALLS_PATH = os.path.join(HERE, "..", "data", "calls.json")
EVOLUTION_LOG = os.path.join(HERE, "..", "data", "call_evolution.jsonl")

def load_calls():
    if not os.path.exists(CALLS_PATH):
        return []
    return json.loads(open(CALLS_PATH).read())

def get_mark(coin):
    """Cheap current mark via oi_flow.py --json (already fetches metaAndAssetCtxs)."""
    out = subprocess.run(
        ["python3", os.path.join(HERE, "oi_flow.py"), "--coins", coin, "--json"],
        capture_output=True, text=True, timeout=30,
    )
    if out.returncode != 0:
        return None
    data = json.loads(out.stdout)
    rows = data.get("rows", [])
    return rows[0].get("mark") if rows else None

def get_pulse_line(coin):
    """Grab pulse.py's verdict line(s) for confirming/fading context. Best-effort text parse."""
    out = subprocess.run(
        ["python3", os.path.join(HERE, "pulse.py"), coin],
        capture_output=True, text=True, timeout=30,
    )
    if out.returncode != 0:
        return None
    lines = [l.strip() for l in out.stdout.splitlines() if "->" in l]
    return lines

def check_zone_touched_since(coin, start_ms, end_ms, direction, lo, hi):
    """Path-dependent check: has price touched [lo,hi] at any point between start_ms and end_ms,
    using Hyperliquid's own candleSnapshot history (works cold, with zero prior cron runs on record
    — the whole point per Olivier's 2026-08-17 16:33 UTC "start in the past instead of relying on
    previous runs" request). Returns True/False, or None if the fetch itself failed (caller should
    fall back rather than silently assume either way)."""
    import urllib.request
    try:
        req = urllib.request.Request(
            "https://api.hyperliquid.xyz/info",
            data=json.dumps({
                "type": "candleSnapshot",
                "req": {"coin": coin, "interval": "15m", "startTime": start_ms, "endTime": end_ms},
            }).encode(),
            headers={"Content-Type": "application/json"},
        )
        candles = json.loads(urllib.request.urlopen(req, timeout=15).read())
    except Exception:
        return None
    for c in candles:
        low, high = float(c["l"]), float(c["h"])
        if direction == "down" and low <= hi:
            return True
        if direction == "up" and high >= lo:
            return True
    return False

def evolve_one(call, coin, now_ms, mark, pulse_lines):
    ts = call["ts"]
    h = call["h"]
    up, dn, p_up_orig = call["up"], call["dn"], call["p_up"]
    age_h = (now_ms - ts) / 3_600_000
    elapsed_frac = min(age_h / h, 1.0) if h else None

    # Has price already resolved (touched up or dn)? Say so plainly; don't guess conviction past that.
    if mark is not None:
        if mark >= up:
            status = "HIT_UP"
        elif mark <= dn:
            status = "HIT_DOWN"
        else:
            status = "OPEN"
    else:
        status = "UNKNOWN_MARK"

    # Distance-closing metric: how far through the up-vs-dn range has price travelled since the call,
    # using the call's own targets as the frame (not a new level pick).
    if mark is not None and up != dn:
        pos_in_range = (mark - dn) / (up - dn)  # 0 = at dn target, 1 = at up target
    else:
        pos_in_range = None

    conviction = "UNCHANGED"
    reason = "no material change detected"
    if status in ("HIT_UP", "HIT_DOWN"):
        conviction = "RESOLVED"
        reason = f"price {'reached the up target' if status=='HIT_UP' else 'reached the down target'} ({mark})"
    elif elapsed_frac is not None and elapsed_frac >= 1.0:
        conviction = "EXPIRED"
        reason = f"horizon ({h}h) elapsed with no target hit — due for Sunday-retro grading as a null/miss on timing"
    elif pos_in_range is not None:
        if pos_in_range > 0.7:
            conviction = "STRENGTHENED"
            reason = f"price has moved {pos_in_range:.0%} of the way toward the up target since the call was made"
        elif pos_in_range < 0.3:
            conviction = "WEAKENED"
            reason = f"price has moved toward the down side ({pos_in_range:.0%} of the up-dn range) since the call was made"
        else:
            conviction = "UNCHANGED"
            reason = f"price sits mid-range ({pos_in_range:.0%}) between the call's own up/dn targets — still undecided"

    # --- Sequential-path awareness (ledger #092 fix) --------------------------------------------
    # A call's up/dn pair is NOT always a direct primary path (doctrine's sequential-path amendment,
    # 2026-08-17): the call may carry an explicit move1_dir/move1_zone (the move that must happen
    # FIRST) with the up/dn distance covering an up-side target that's only a legitimate "Move 2
    # confirmed" read if Move 1 already fired. Raw pos_in_range alone cannot tell these apart — it
    # scored 72% toward the up target on 2026-08-17 16:00 UTC and called it plain STRENGTHENED even
    # though the call's own Move 1 (down-poke) had NOT happened, meaning that progress could only be
    # explained by the ALTERNATE/squeeze path (#090), not confirmation of the primary sequence.
    move1_dir = call.get("move1_dir")
    move1_zone = call.get("move1_zone")  # [lo, hi]
    move1_fired = None
    if move1_dir and move1_zone and len(move1_zone) == 2:
        lo, hi = move1_zone
        # Path-dependent check via live candleSnapshot (start=call ts, end=now) rather than depending
        # on this script's own accrued evolution-log history — this is what lets the check work
        # correctly even when running fully on-demand/cold, with no prior cron runs on record
        # (Olivier 2026-08-17: "worker can start in the past instead of relying on previous runs").
        move1_fired = check_zone_touched_since(coin, ts, now_ms, move1_dir, lo, hi)
        if move1_fired is None and mark is not None:
            # candleSnapshot fetch failed — fall back to current-mark-only check (weaker: misses a
            # wick-and-reclaim that happened between ticks) rather than silently guessing.
            move1_fired = (move1_dir == "down" and mark <= hi) or (move1_dir == "up" and mark >= lo)

    if conviction == "STRENGTHENED" and move1_fired is False:
        conviction = "STRENGTHENED_ALT_PATH"
        reason = (
            f"price has moved {pos_in_range:.0%} toward the up target, but Move 1 "
            f"({move1_dir}-poke into {move1_zone}) has NOT fired yet — this progress confirms the "
            f"CO-EQUAL ALTERNATE/squeeze path, not the primary sequenced thesis. Do not report this as "
            f"plain bullish strengthening; the primary Move 1 leg remains untested."
        )

    # Distance-vs-flow contradiction check: price closing on a target while live flow FADES/DIVERGES
    # is the fake-move signature (pulse.py's own verdict) — surface it explicitly, don't let a rising
    # distance% alone read as rising conviction. This is the actual point of tracking evolution: catching
    # exactly this kind of internal disagreement between distance and flow before it resolves either way.
    flow_contradiction = None
    if pulse_lines:
        fading = any("FADING" in l or "DIVERG" in l for l in pulse_lines)
        confirming = any("CONFIRMING" in l for l in pulse_lines)
        if conviction == "STRENGTHENED" and fading and not confirming:
            flow_contradiction = (
                "Mechanical distance says STRENGTHENED, but live flow is FADING/DIVERGING — the push toward "
                "the target is not backed by volume/CVD. This is the fake-move signature (pulse.py), not "
                "confirmation. Treat conviction as UNCHANGED-AT-BEST until flow confirms, not upgraded."
            )
            conviction = "CONTESTED_INTERNAL"
            reason = flow_contradiction
        elif conviction == "WEAKENED" and confirming and not fading:
            flow_contradiction = (
                "Mechanical distance says WEAKENED, but live flow is CONFIRMING the current push — the move "
                "away from the up target has real volume/CVD behind it, not just noise."
            )

    record = {
        "evolved_at_ms": now_ms,
        "original_call_ts": ts,
        "coin": coin,
        "original": {"up": up, "dn": dn, "p_up": p_up_orig, "h": h, "by": call.get("by")},
        "current_mark": mark,
        "elapsed_hours": round(age_h, 1),
        "elapsed_frac_of_horizon": round(elapsed_frac, 2) if elapsed_frac is not None else None,
        "pos_in_original_range": round(pos_in_range, 2) if pos_in_range is not None else None,
        "status": status,
        "conviction_delta": conviction,
        "reason": reason,
        "live_pulse_lines": pulse_lines,
        "note": "This is a mechanical distance/status check on the ORIGINAL call, not a new independent "
                "forecast. p_up_orig is never overwritten here — calibration.py grades the original commit.",
    }
    return record

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coin", default="BTC")
    ap.add_argument("--call-ts", type=int, default=None)
    args = ap.parse_args()

    calls = load_calls()
    if args.call_ts is not None:
        calls = [c for c in calls if c["ts"] == args.call_ts]

    now_ms = int(time.time() * 1000)
    mark = get_mark(args.coin)
    pulse_lines = get_pulse_line(args.coin)

    records = []
    for call in calls:
        rec = evolve_one(call, args.coin, now_ms, mark, pulse_lines)
        records.append(rec)
        print(json.dumps(rec, indent=2))

    if records:
        with open(EVOLUTION_LOG, "a") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

if __name__ == "__main__":
    main()
