#!/usr/bin/env python3
"""BACKTEST-RATES CAPTURE — the missing link (OLIVIER, 2026-08-18).

The desk HAS 8 walk-forward backtesters in scripts/ (backtest_reclaim/sweep/magnet/
confluence/sfp/lineexc/excursion.py) — but they print to stdout and exit, so their
n/rate/expectancy numbers become ORPHANED folklore. That's exactly why "leg-2 ~66%"
drifted from the measured 55% and "reclaim ~85%" survived its own demotion: nothing
re-ran the backtester and fed its output back into the call path.

This script runs the backtest battery, captures each one's stdout, parses the KEY rate
lines (n=, hit=, meanFwd/expectancy), and persists them to data/backtest_rates.json as a
machine-readable, timestamped fact-store. The provenance gate + producer read THIS file
instead of recalling numbers from memory.

Read-only (this only READS the Hyperliquid candle API and WRITES a local JSON artifact).
Run manually, or via the Sunday retro (add `python3 backtest_rates.py` before calibration).

Usage:
  python3 backtest_rates.py            # full battery
  python3 backtest_rates.py --only reclaim,sweep   # subset
"""
import json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "backtest_rates.json")
BATTERY = [
    "backtest_reclaim.py",
    "backtest_sweep.py",
    "backtest_magnet.py",
    "backtest_confluence.py",
    "backtest_sfp.py",
    "backtest_lineexc.py",
    "backtest_excursion.py",
]

def run_one(script, timeout=180):
    """Run a backtester, return (ok, stdout)."""
    try:
        p = subprocess.run(
            [sys.executable, os.path.join(HERE, script)],
            capture_output=True, text=True, timeout=timeout, cwd=HERE,
        )
        return (p.returncode == 0, p.stdout)
    except subprocess.TimeoutExpired:
        return (False, f"(timeout after {timeout}s)")

def parse(stdout):
    """Extract the key rate lines: n=, hit=, meanFwd/expectancy, plus the reach/timing columns."""
    findings = []
    for line in stdout.splitlines():
        m = re.search(r'n\s*=\s*(\d+)', line)
        if not m:
            continue
        n = int(m.group(1))
        hit = None
        hm = re.search(r'hit\s*=\s*(\d+)\s*%', line)
        if hm:
            hit = int(hm.group(1))
        fwd = None
        fm = re.search(r'(?:meanFwd|expectancy|net|exp)\s*[=(].*?([+-]\d+\.\d+)\s*%', line)
        if fm:
            fwd = float(fm.group(1))
        # TIMING / reach metric (Olivier 2026-08-18): reached+X% within window, medReach
        reach_pct = None
        rm = re.search(r'reached\+[\d.]*%\s*=\s*(\d+)\s*%', line)
        if rm:
            reach_pct = int(rm.group(1))
        med_reach = None
        mm = re.search(r'medReach\s*=\s*([+-]\d+\.\d+)\s*%', line)
        if mm:
            med_reach = float(mm.group(1))
        nm = re.match(r'\s*(\w[\w\s/-]{0,40}?)\s+n\s*=', line)
        name = nm.group(1).strip() if nm else "line"
        findings.append({
            "name": name, "n": n, "hit_pct": hit, "fwd_pct": fwd,
            "reached_pct": reach_pct, "med_reach_pct": med_reach,
            "raw": line.strip()[:160],
        })
    return findings

def main():
    only = None
    if "--only" in sys.argv:
        i = sys.argv.index("--only")
        only = set(sys.argv[i + 1].split(","))
    scripts = [s for s in BATTERY if (not only or s.replace("backtest_", "").replace(".py", "") in only)]

    out = {
        "schema": "hlops-backtest-rates-v1",
        "generated_ts": int(time.time() * 1000),
        "generated_utc": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
        "note": "Walk-forward, own-lines, cost-aware base rates captured from the desk's backtesters. READ THESE (not memory) for any empirical claim. DISCOVERY/in-sample — needs blind/OOS before live weight (R4/A5/A6).",
        "battery": {},
    }
    for s in scripts:
        ok, so = run_one(s)
        key = s.replace("backtest_", "").replace(".py", "")
        fl = parse(so) if ok else []
        out["battery"][key] = {
            "ok": ok,
            "findings": fl,
            "summary": so.strip()[:1200] if ok else so.strip()[:200],
        }
        print(f"{key:14s} {'OK' if ok else 'FAIL'}  {len(fl)} rate-lines captured", file=sys.stderr)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {OUT} ({len(out['battery'])} testers)", file=sys.stderr)
    print(json.dumps({"written": OUT, "generated_utc": out["generated_utc"]}))

if __name__ == "__main__":
    main()
