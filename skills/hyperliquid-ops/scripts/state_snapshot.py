#!/usr/bin/env python3
"""CANONICAL STATE — single source of truth for every agent (2026-08-18, orchestration fix #2).

The misattribution failure class (66%/85% quoted from memory instead of the artifact) happens
because each agent reaches for a DIFFERENT file — or a recalled number. This script serializes
everything the desk needs into ONE object, data/state.json, that producer / challenger /
provenance-gate / falsifiability / level-watch / retro ALL read.

Sections:
  - live_call       : data/current_call.json (scenario + entries + provenance + probabilities)
  - base_rates      : data/backtest_rates.json's battery, flattened to a rate->{n,hit,reached,fwd} map
  - entries         : the ACTIVE entry triggers extracted from live_call.entry_spec
  - generated       : timestamp + source files + a hash so staleness is detectable

Read-only. No model, no network (base rates read from the persisted artifact, never re-derived here).

Usage:
  state_snapshot.py            # write data/state.json
  state_snapshot.py --out -    # print JSON to stdout
  state_snapshot.py --check    # exit 1 if stale sources (current_call newer than state.json)
"""
import json, os, sys, time, hashlib

D = os.path.join(os.path.dirname(__file__), "..", "data")
F_CALL = os.path.join(D, "current_call.json")
F_RATES = os.path.join(D, "backtest_rates.json")
F_OUT = os.path.join(D, "state.json")


def load(p, default):
    try:
        with open(p) as f:
            return json.load(f)
    except Exception:
        return default


def flatten_rates(rates):
    """backtest_rates.json -> rate label -> {n, hit_pct, reached_pct, med_reach_pct, fwd_pct}."""
    out = {}
    batt = rates.get("battery", {}) or {}
    for script, body in batt.items():
        for f in body.get("findings", []) or []:
            key = f"{script}:{f.get('name','?')}"
            out[key] = {
                "n": f.get("n"),
                "hit_pct": f.get("hit_pct"),
                "reached_pct": f.get("reached_pct"),
                "med_reach_pct": f.get("med_reach_pct"),
                "fwd_pct": f.get("fwd_pct"),
            }
    return out


def extract_entries(call):
    """Pull the ACTIVE entries from current_call.entry_spec into a machine-readable list."""
    spec = call.get("entry_spec", {}) or {}
    entries = []
    for mv in ("move1", "move2"):
        m = spec.get(mv) or {}
        if not m:
            continue
        entries.append({
            "move": mv,
            "action": m.get("action"),
            "entry": m.get("entry"),
            "soft_inval": m.get("soft_inval"),
            "hard_inval": m.get("hard_inval"),
            "use": m.get("use"),
        })
    return entries


def build():
    call = load(F_CALL, {})
    rates = load(F_RATES, {})
    out = {
        "schema": "hlops-state-v1",
        "generated_utc": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "generated_ts": int(time.time() * 1000),
        "live_call": call,
        "base_rates": flatten_rates(rates),
        "entries": extract_entries(call),
        "_sources": {
            "current_call": F_CALL,
            "backtest_rates": F_RATES,
            "call_mtime": int(os.path.getmtime(F_CALL)) if os.path.exists(F_CALL) else None,
            "rates_mtime": int(os.path.getmtime(F_RATES)) if os.path.exists(F_RATES) else None,
        },
    }
    return out


def main():
    out = build()
    if "--out" in sys.argv and sys.argv[sys.argv.index("--out") + 1] == "-":
        print(json.dumps(out, indent=2))
        return
    if "--check" in sys.argv:
        # stale if state.json older than current_call.json
        if not os.path.exists(F_OUT):
            print("state.json missing — run state_snapshot.py"); sys.exit(1)
        old = json.load(open(F_OUT))
        old_m = old.get("_sources", {}).get("call_mtime")
        new_m = int(os.path.getmtime(F_CALL)) if os.path.exists(F_CALL) else 0
        if new_m > (old_m or 0):
            print(f"state.json STALE (current_call modified {new_m} > state {old_m})"); sys.exit(1)
        print("state.json fresh"); sys.exit(0)
    with open(F_OUT, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {F_OUT}  ({len(out['base_rates'])} base rates, {len(out['entries'])} entries)")


if __name__ == "__main__":
    main()
