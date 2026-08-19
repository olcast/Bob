#!/usr/bin/env python3
"""desk_collect.py — ONE-FIRE collection + interpretation runner for the whole desk.

Runs the forward collector (market/book/hlp/liqmap/liqevent) + oi-age cohort, then the live
cross-venue / carry-term / jump-geometry / options-skew sensors, persists every ledger, and emits
the joint-state interpretation (D1..D11). This is what the scheduler fires every cadence.

READ-ONLY: /info + Deribit public + Binance/Bybit public. Never /exchange, never keys.

Usage: python3 desk_collect.py [--cap N] [--liqevents] [--lookback M] [--coins BTC]
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(HERE, "..")

def run(script, args, label):
    p = subprocess.run([sys.executable, os.path.join(HERE, script)] + args,
                       cwd=HERE, capture_output=True, text=True, timeout=300)
    ok = p.returncode == 0
    print(f"[{label}] {'OK' if ok else 'FAIL('+str(p.returncode)+')'}")
    out = (p.stdout or "").strip()
    if out:
        print(out)
    if p.stderr and not ok:
        print("  stderr:", p.stderr.strip()[:400])
    return ok

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, default=150)
    ap.add_argument("--liqevents", action="store_true")
    ap.add_argument("--lookback", type=int, default=30)
    ap.add_argument("--coins", default="BTC")
    a = ap.parse_args()
    coins_tail = a.coins.replace(",", "_")

    t0 = time.time()
    print(f"=== desk_collect {time.strftime('%Y-%m-%d %H:%M:%S')}Z · coins={a.coins} · cap={a.cap} ===")

    # 1) forward collector (market/book/hlp/liqmap/liqevent) — the tape
    coll_args = ["--once", "--cap", str(a.cap), "--coins", a.coins]
    if a.liqevents: coll_args += ["--liqevents", "--lookback", str(a.lookback)]
    run("collector.py", coll_args, "collector")

    # 2) oi-age cohort (D11) — persists cohort.json + cohort.jsonl
    run("oi_age.py", ["--cap", str(a.cap), "--coins", a.coins], "oi-age")

    # 3) live sensors (D7–D10) — deterministic, free APIs
    run("carry_term_structure.py", [], "carry-term D8")
    run("jump_geometry.py", ["--interval", "1h", "--bars", "96"], "jump-geom D9")
    run("options_skew.py", [], "options-skew D10")

    # 4) joint-state interpretation D1..D11 (cross_venue D7 is inside state_view)
    run("state_view.py", [], "joint-state D1-D11")

    print(f"=== desk_collect done in {int(time.time()-t0)}s ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
