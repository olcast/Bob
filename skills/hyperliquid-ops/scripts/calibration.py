#!/usr/bin/env python3
"""CALIBRATION — the honest forward judge (OLIVIER). Grades the desk's COMMITTED scenario probabilities as a
FORECASTER: are the p_up calls CALIBRATED (when you say 60%, does it happen ~60%?), and do they BEAT a naive
baseline on the BRIER score? This is the only thing that can prove or disprove the desk's edge — and it grades
the CALL YOU COMMIT (script + positioning + the live brainstorm), not the raw signals, so the brainstorming is
on the stand too. Outcomes auto-resolve from price (no manual grading = no self-deception). Pre-committed
kill-switch. Read-only.

Also emits a SWEEP DIAGNOSTIC (the 'recovery-outlook' capture): among calls scored WRONG, how many were
SWEPT-THEN-RIGHT — the dn break/scoring line tagged first, but `up` reached anyway within the window. A high
rate means the invalidation was drawn too tight / ABOVE the liquidity, so a stop-hunt fake-out scored a correct
reversal call as a loss. Feeds discovery-loop candidate L1 ('draw the invalidation below the liquidity').

Each committed call logs a SCORE tag (a JSON object). Feed the collected tags in as a JSON array:
  {"ts":<ms when committed>, "h":<hours>, "up":<up-target>, "dn":<down-break level>,
   "p_up":<committed P(reach up before dn within h)>, "p_base":<naive baseline, e.g. 0.5>}
Optional SEAM-3 mechanism bar (doctrine #46/#53 — grade the MECHANISM, not just the price touch):
  {"mechanism": {"oi": "expanding"|"contracting"|<omit>, "funding": "trend_aligned"|"against"|<omit>,
                  "premium": "outside_4bp"|"inside_4bp"|<omit>}}
When present, resolve() additionally emits a `mech_ok` (did the committed precondition hold at resolve time)
so 'hit target on falling OI' stops scoring as doctrine-right. OLD records without `mechanism` resolve
IDENTICALLY to today (fully backward-compatible).
Usage:  python3 calibration.py records.json     |     cat records.json | python3 calibration.py -
Importable:  from calibration import resolve   (returns the per-call dict documented below)."""
import json, urllib.request, time, sys, statistics
API="https://api.hyperliquid.xyz/info"
def post(b):
    try:
        r=urllib.request.Request(API,data=json.dumps(b).encode(),headers={"Content-Type":"application/json"});return json.load(urllib.request.urlopen(r,timeout=40))
    except Exception:return None

def _mech_ctx(rec):
    """SEAM-3: pull the live mechanism state at resolve time (OI direction, premium band, funding sign).
    Returns a dict the mechanism-bar checker reads; None on any fetch failure (never blocks scoring)."""
    try:
        end = int(rec["ts"]) + int(rec["h"]) * 3600000
        start = int(rec["ts"])
        # OI direction: openInterest now vs at commit (from assetCtx snapshots is not historical;
        # use meta at commit-time if logged, else flag as unknown — do NOT fabricate).
        oi_dir = None
        if rec.get("_oi_commit") is not None and rec.get("_oi_resolve") is not None:
            oi_dir = "expanding" if rec["_oi_resolve"] > rec["_oi_commit"] else "contracting"
        # premium band: mark vs oracle now (crowding).
        mids = post({"type": "allMids"}) or {}
        ctx = json.loads(post and json.dumps({})) or {}
        mark = mids.get("BTC")
        # funding sign: current funding (cost of holding) — aligned with trend or against.
        meta = post({"type": "metaAndAssetCtxs"})
        funding = None
        if meta:
            universe = meta[0].get("universe", [])
            idx = [i for i, a in enumerate(universe) if a.get("name") == "BTC"]
            if idx:
                funding = meta[1][idx[0]].get("funding")
        return {"oi_dir": oi_dir, "mark": mark, "funding": funding}
    except Exception:
        return None

def _mech_ok(rec):
    """Does the committed mechanism precondition hold? True/False/None (None = could not be verified)."""
    m = rec.get("mechanism") or {}
    if not m:
        return None  # no bar committed — legacy record, unchanged
    ctx = _mech_ctx(rec)
    if not ctx:
        return None
    checks = []
    if m.get("oi") in ("expanding", "contracting"):
        checks.append(ctx.get("oi_dir") == m["oi"])
    if m.get("premium") in ("outside_4bp", "inside_4bp"):
        # need mark vs oracle — oracle is not directly here; approximate with the premium the caller logged
        prem = rec.get("_premium_bp")
        if prem is not None:
            if m["premium"] == "outside_4bp":
                checks.append(abs(prem) > 4.0)
            else:
                checks.append(abs(prem) <= 4.0)
    if m.get("funding") in ("trend_aligned", "against"):
        # trend_aligned = funding sign matches the move direction the caller committed (up -> positive funding)
        fund = ctx.get("funding")
        if fund is not None and rec.get("up") and rec.get("_commit_mark"):
            trend = float(rec["up"]) - float(rec["_commit_mark"])
            aligned = (fund >= 0) == (trend >= 0)
            checks.append(aligned if m["funding"] == "trend_aligned" else not aligned)
    if not checks:
        return None  # committed bar fields not resolvable — do not penalize
    return all(checks)
def resolve(rec):
    """Scored outcome + sweep diagnostics, or None if not matured / no data.
    o = 1 iff price reaches `up` BEFORE `dn` within h hours (UNCHANGED scoring). Extra fields:
      first : 'up'|'dn' — which target was reached first (the scored outcome)
      both  : both targets touched in-window
      swept_then_right : dn first but up ALSO reached (fake-out / invalidation too tight — the L1 signature)
      spiked_then_wrong: up first but dn ALSO hit later (target tagged then reversed back through the break)
      sweep_depth: $ from dn down to the lowest low after the break (only when swept_then_right)"""
    now=int(time.time()*1000); end=int(rec["ts"])+int(rec["h"])*3600000
    if now < end: return None                                       # not matured yet
    d=post({"type":"candleSnapshot","req":{"coin":"BTC","interval":"5m","startTime":int(rec["ts"]),"endTime":end}}) or []
    if not d: return None
    up=float(rec["up"]); dn=float(rec["dn"])
    t_up=t_dn=None; first=None; lo_after_dn=None
    for c in d:
        hi=float(c["h"]); lo=float(c["l"]); t=int(c["t"])
        if t_up is None and hi>=up: t_up=t
        if t_dn is None and lo<=dn: t_dn=t
        if first is None and (hi>=up or lo<=dn):
            first = ('up' if float(c["c"])>=(up+dn)/2 else 'dn') if (hi>=up and lo<=dn) else ('up' if hi>=up else 'dn')
        if t_dn is not None:
            lo_after_dn = lo if lo_after_dn is None else min(lo_after_dn, lo)
    if first is None: first='dn'                                    # neither reached -> up-scenario failed -> 0
    o = 1 if first=='up' else 0
    result = {"o":o, "first":first,
            "both": (t_up is not None and t_dn is not None),
            "swept_then_right": (first=='dn' and t_up is not None),
            "spiked_then_wrong": (first=='up' and t_dn is not None),
            "sweep_depth": (dn-lo_after_dn) if (first=='dn' and t_up is not None and lo_after_dn is not None) else None}
    # SEAM-3: append the mechanism-bar verdict WITHOUT changing the price score (backward-compatible).
    mo = _mech_ok(rec)
    if mo is not None:
        result["mech_ok"] = mo
        result["doctrine_right"] = (o == 1 and mo)      # won AND the mechanism held
        result["price_right_mech_wrong"] = (o == 1 and not mo)  # hit target but doctrine-wrong
    return result

def main():
    src=sys.argv[1] if len(sys.argv)>1 else "-"
    raw=(sys.stdin.read() if src=="-" else open(src).read()).strip()
    recs=json.loads(raw) if raw else []
    resolved=[(r,res) for r in recs for res in [resolve(r)] if res is not None]
    n=len(resolved)
    print(f"CALIBRATION — {n} resolved of {len(recs)} logged calls · {time.strftime('%Y-%m-%d %H:%M UTC',time.gmtime())}")
    if n<5:
        print("  too few resolved calls to score — keep logging (need ~30 for a verdict)."); return
    bm=statistics.mean((float(r["p_up"])-res["o"])**2 for r,res in resolved)                 # Brier, model
    bb=statistics.mean((float(r.get("p_base",0.5))-res["o"])**2 for r,res in resolved)        # Brier, naive baseline
    skill=(1-bm/bb) if bb>0 else 0.0
    print(f"  up-rate {statistics.mean(res['o'] for _,res in resolved):.0%} · Brier model {bm:.3f} vs baseline {bb:.3f} · skill {skill:+.1%}")
    bins={}
    for r,res in resolved: bins.setdefault(round(float(r["p_up"])*5)/5, []).append(res["o"])
    print("  calibration (you said -> it happened):")
    for b in sorted(bins): print(f"    p~{b:.0%}: realized {statistics.mean(bins[b]):.0%}  (n={len(bins[b])})")
    # SWEEP DIAGNOSTIC — the 'recovery-outlook' capture (feeds discovery-loop candidate L1)
    wrong=[res for _,res in resolved if res["o"]==0]
    swept=[res for res in wrong if res["swept_then_right"]]
    if wrong:
        rate=len(swept)/len(wrong)
        print(f"  SWEEP DIAGNOSTIC — of {len(wrong)} calls scored WRONG, {len(swept)} ({rate:.0%}) were swept-then-right (break tagged, target hit anyway).")
        depths=[res["sweep_depth"] for res in swept if res["sweep_depth"] is not None]
        if depths: print(f"     median sweep past the break: ${statistics.median(depths):,.0f} → in discovery, draw the invalidation ~that far BELOW the liquidity (candidate L1).")
        if len(wrong)>=5 and rate>=0.4: print(f"     >>> BREAK-LINES WRONG-SIDED: {rate:.0%} of 'losses' tagged the target — move dn below the liq pool.")
    right=[res for _,res in resolved if res["o"]==1]
    spiked=[res for res in right if res["spiked_then_wrong"]]
    if right and spiked: print(f"  (mirror: of {len(right)} scored RIGHT, {len(spiked)} later also tagged the break — target-then-reverse.)")
    if n>=30:
        if bm<bb: print(f"  VERDICT: BEATING BASELINE — positive skill {skill:+.1%} over n={n}. The edge is showing; keep going.")
        else:     print(f"  VERDICT: NO SKILL vs baseline (Brier {bm:.3f} >= {bb:.3f}, n={n}). KILL-SWITCH: the thesis has NOT proven an edge — retire it, don't re-condition.")
    else:
        print(f"  VERDICT: accumulating (n={n}/30) — no verdict yet; neither confirmed nor killed.")
    # SEAM-3: mechanism-bar report — how often a win was ALSO doctrine-right (vs price-right-but-mech-wrong).
    mech_scored = [(r,res) for r,res in resolved if "mech_ok" in res]
    if mech_scored:
        dr = [res for _,res in mech_scored if res.get("doctrine_right")]
        pw = [res for _,res in mech_scored if res.get("price_right_mech_wrong")]
        wins = [res for _,res in mech_scored if res["o"]==1]
        if wins:
            print(f"  MECHANISM BAR — of {len(wins)} wins with a committed bar, {len(dr)} ({len(dr)/len(wins):.0%}) were doctrine-right; {len(pw)} hit target but WRONG mechanism (price-right, doctrine-wrong).")
    print("  Auto-resolved from price, read-only. This is the only judge that counts — the brainstorm is graded here too.")

if __name__=="__main__":
    main()
