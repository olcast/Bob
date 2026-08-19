#!/usr/bin/env python3
"""preflight_freshness.py — STALE-DATA GATE for any full-stack / next-moves run.

The rule (Olivier, 2026-08-19): if you ask for a full-stack run (all models → next moves) and
there's a gap between your request and the last data-collection tick, that gap MUST be filled
BEFORE any model sees the data. No model reasons against a stale tape.

What this does:
  --check   : exit 0 if the forward tape (collector.jsonl) is FRESH (within --max-age-min of now);
              exit 1 if STALE. Prints last-tick age + coin coverage.
  (no flag) : if stale, run a full desk_collect() to backfill, then re-verify.

Notes on what "the gap" means — honest split:
  - Candle/funding/OI history SELF-HEALS: state_view re-reads ~200d of 1h candles live from the API
    every run, so there is never a historical candle gap regardless of collector uptime.
  - The forward tape's unique, NON-backfillable rows are point-in-time snapshots: liqmap/underwater
    (per-address entryPx), liqevent (realized fills), oiage (cohort). These can't be reconstructed
    after the fact — the ONLY fix is a fresh collect BEFORE the models run. That is what this gate
    does: it forces one fresh collect() so the snapshot the models see is current.

Read-only. No model. Free APIs only.
"""
import json, os, sys, time, subprocess, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
LEDGER = os.path.join(DATA, "collector.jsonl")

def last_tick_ms():
    try:
        with open(LEDGER) as f:
            last = None
            for l in f:
                if not l.strip(): continue
                r = json.loads(l)
                t = r.get("ts")
                if t and t > (last or 0): last = t
            return last
    except Exception:
        return None

def age_min(last_ms):
    if not last_ms: return None
    return (int(time.time() * 1000) - last_ms) / 60_000.0

def check(max_age_min=65):
    last = last_tick_ms()
    age = age_min(last)
    if last is None:
        print(f"[freshness] no collector tape yet — STALE")
        return 1
    status = "FRESH" if age <= max_age_min else "STALE"
    print(f"[freshness] last tick {age:.1f}min ago (max {max_age_min}min) — {status}")
    return 0 if age <= max_age_min else 1

def backfill_and_verify(max_age_min=65):
    code = check(max_age_min)
    if code == 0:
        print("[freshness] tape is fresh — proceeding without re-collect")
        return 0
    print(f"[freshness] tape stale — running desk_collect to backfill BEFORE models fire ...")
    p = subprocess.run([sys.executable, os.path.join(HERE, "desk_collect.py"),
                        "--cap", "400", "--liqevents", "--lookback", "20",
                        "--coins", "BTC,ETH,SOL,HYPE,SPX", "--light-coins", "PAXG"],
                       cwd=HERE, timeout=900)
    if p.returncode != 0:
        print(f"[freshness] desk_collect FAILED (rc={p.returncode}) — DO NOT proceed to models")
        return 1
    return check(max_age_min)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="check only, exit 1 if stale")
    ap.add_argument("--max-age-min", type=int, default=65)
    a = ap.parse_args()
    if a.check:
        sys.exit(check(a.max_age_min))
    sys.exit(backfill_and_verify(a.max_age_min))
