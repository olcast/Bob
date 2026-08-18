#!/usr/bin/env python3
"""FALSIFIABILITY SCORE — the incentive design's second leg (OLIVIER, 2026-08-18).

Adds a second scored dimension BEYOND call-hit: REASONING INTEGRITY. An honest call that
the market whips is worth MORE than a lucky-but-unfalsifiable call, because only the honest
one is gradeable and therefore learnable. Reads STRUCTURED fields (not regex) so it doesn't
false-flag a call's own provenance annotations.

Score 0.0–1.0. Complements calibration.py (the outcome judge) — does NOT replace it.

Usage:
  falsifiability_score.py <call.json>       # file
  cat call.json | falsifiability_score.py -  # stdin
Exit 0 = at/above bar (0.60), 1 = below bar."""
import json, sys

def score(call):
    checks = {}
    prov = call.get("provenance", {})
    probs = call.get("probabilities", {})

    # 1. Death-price named (doctrine rule 22b) — the thesis-death condition for the PRIMARY.
    checks["death_price_named"] = bool(call.get("death_price") and str(call["death_price"]).strip())

    # 2. Tripwire vs target mutual exclusivity: the primary fade target must not straddle
    #    the down tripwire. Compare structured tripwires with move zones.
    trip = call.get("tripwires") or {}
    zones = []
    for k in ("move1_zone", "move2_zone", "move3_zone"):
        z = call.get(k)
        if isinstance(z, list) and len(z) == 2:
            zones.append((k, float(z[0]), float(z[1])))
    dn_trip = None
    if "down" in trip:
        dn_trip = float(trip["down"])
    elif isinstance(call.get("dn"), (int, float)):
        dn_trip = float(call["dn"])
    exclusive = True
    if dn_trip is not None:
        for k, lo, hi in zones:
            if lo < dn_trip < hi:
                exclusive = False  # a zone straddles the down tripwire
    checks["tripwire_target_exclusive"] = exclusive

    # 3. Probabilities derive + sum ≈1.0 with a named residual (C4 class).
    if isinstance(probs, dict) and probs:
        vals = [float(v) for v in probs.values() if isinstance(v, (int, float))]
        tot = sum(vals)
        residual_named = any("resid" in k.lower() or "chop" in k.lower() for k in probs)
        checks["probabilities_sum_valid"] = (abs(tot - 1.0) <= 0.02) and residual_named
    else:
        checks["probabilities_sum_valid"] = False

    # 4. Provenance present: active base rates are backed by {rate,n,source};
    #    demoted/retired figures are still "documented" (they carry status + disposition).
    if prov:
        backed = all(
            (isinstance(v, dict) and v.get("status") in ("DEMOTED", "retired", "disowned"))
            or (isinstance(v, dict) and {"rate", "n", "source"} <= set(v.keys()))
            for v in prov.values()
        )
    else:
        backed = False
    checks["provenance_present"] = backed

    # 5. move-2 belongs to the SAME path as move-1 (S5 fork-vs-sequential splice).
    #    Detect a splice: move2_zone far below the down-tripwire in a way that copies the
    #    alternative path's terminus rather than the primary's sequential leg.
    splice = False
    m2 = call.get("move2_zone")
    if isinstance(m2, list) and len(m2) == 2 and dn_trip is not None:
        # if move2 zone's low is a long way below the down tripwire AND there's a separate
        # path_b terminus stored, it's a splice.
        if call.get("path_b_terminus") and float(m2[1]) < dn_trip - 300:
            splice = True
    checks["move2_not_spliced"] = not splice

    # 6. move-3 (deep terminus / R-044 stand-aside) coherence: if present, it must name
    #    a stand-aside or a contingent trigger (reload-short / reclaim-long) and an
    #    up-invalidation. A move3_zone with NO contingent trigger + invalidation is a
    #    half-specified deep leg (protocol gap), not a graded branch.
    m3 = call.get("move3_zone")
    if isinstance(m3, list) and len(m3) == 2:
        has_cont = bool(call.get("move3_contingent_reload_short") or call.get("move3_contingent_reclaim_long"))
        has_inval = bool(call.get("move3_invalid_up") is not None)
        checks["move3_wellformed"] = has_cont and has_inval
    else:
        checks["move3_wellformed"] = True  # no move3 present -> nothing to check

    w = {
        "death_price_named": 0.35,
        "tripwire_target_exclusive": 0.15,
        "probabilities_sum_valid": 0.15,
        "provenance_present": 0.20,
        "move2_not_spliced": 0.15,
    }
    s = sum(w[k] for k in w if checks.get(k, False))
    return round(s, 2), {k: (checks.get(k), w[k]) for k in w}

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "-"
    raw = (sys.stdin.read() if src == "-" else open(src).read()).strip()
    try:
        call = json.loads(raw)
    except Exception as e:
        print(f"falsifiability: parse error ({e})"); sys.exit(2)
    s, bd = score(call)
    print(f"FALSIFIABILITY SCORE: {s:.2f} / 1.00  (reasoning integrity — not outcome)")
    for k, (ok, wt) in bd.items():
        print(f"  {'✓' if ok else '✗'} {k} ({wt:.0%}): {'PASS' if ok else 'FAIL'}")
    if s < 0.6:
        print("  → BELOW BAR: reasoning not honestly gradeable; fix before treating levels as directional.")
    sys.exit(0 if s >= 0.6 else 1)

if __name__ == "__main__":
    main()
