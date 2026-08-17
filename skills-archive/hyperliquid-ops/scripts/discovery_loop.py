#!/usr/bin/env python3
"""DISCOVERY LOOP — the desk's self-improvement engine (OLIVIER). The mechanism by which ONE agent's learning
becomes EVERY agent's: it turns resolved calls into PROPOSED doctrine so all instances/firings come to read the
market the same way — WITHOUT the program-level overfitting trap (audit #53). A candidate lesson earns
promotion only after it holds up FORWARD across the bar (default 5 supporting calls); stale doctrine gets
flagged for RETIREMENT (the arm #53 said was missing). It PROPOSES; it NEVER edits the skill. Only Olivier
SAVING the skill propagates a promotion to all agents — that human save-step is the safety catch, and it keeps
mission one intact (the deliverable stays 'the 2 next probable moves'; read-only; BTC-only).

Inputs (both JSON):
  calls.json   — array of SCORE records (same shape calibration.py eats): {ts,h,up,dn,p_up,p_base,...}
  lessons.json — the lab-notebook: {promotion_bar_default, lessons:[{id,status,statement,metric,bar,...}]}
Usage:  python3 discovery_loop.py calls.json lessons.json
Read-only, auto-resolved from price. The Sunday-retro engine — run it right after calibration.py."""
import json, sys, time, statistics
from calibration import resolve                       # shared resolver — one source of truth for outcomes

def load(p):
    try: return json.loads((open(p).read() or "null"))
    except Exception as e: print(f"  (could not read {p}: {e})"); return None

def metrics(resolved):
    n=len(resolved); wrong=[res for _,res in resolved if res["o"]==0]
    swept=[res for res in wrong if res["swept_then_right"]]
    depths=[r["sweep_depth"] for r in swept if r["sweep_depth"] is not None]
    return {"n":n,
            "up_rate":(statistics.mean(res['o'] for _,res in resolved) if n else None),
            "n_wrong":len(wrong), "n_swept":len(swept),
            "swept_rate":(len(swept)/len(wrong) if wrong else None),
            "median_sweep_depth":(statistics.median(depths) if depths else None)}

def evaluate(lesson, m):
    """Return (verdict, detail). verdict in {PROMOTE, WATCH, RETIRE, KEEP, INSUFFICIENT}.
    Deliberately small & readable — a rules FRAMEWORK would itself be overfitting surface (#53)."""
    metric=lesson.get("metric"); bar=lesson.get("bar",{}) or {}; status=lesson.get("status")
    if status=="candidate":
        if metric=="swept_then_right_rate":
            mw=bar.get("min_wrong",5); rg=bar.get("rate_gte",0.4)
            if m["n_wrong"]<mw:
                return ("INSUFFICIENT", f"{m['n_wrong']}/{mw} wrong-calls of evidence"+("" if m['swept_rate'] is None else f" · so-far {m['swept_rate']:.0%}"))
            if m["swept_rate"] is not None and m["swept_rate"]>=rg:
                return ("PROMOTE", f"{m['swept_rate']:.0%} swept-then-right over {m['n_wrong']} wrong calls (bar {rg:.0%}/{mw}) — break-lines wrong-sided; adopt.")
            return ("WATCH", f"{m['swept_rate']:.0%} < {rg:.0%} over {m['n_wrong']} wrong calls — not yet.")
        return ("INSUFFICIENT", f"no auto-evaluator for metric '{metric}' — track by hand at the retro")
    if status in ("promoted","doctrine"):
        g=lesson.get("retire_if",{}) or {}
        if g.get("metric")=="swept_then_right_rate" and m["n_wrong"]>=g.get("min_wrong",8) and m["swept_rate"] is not None and m["swept_rate"]<g.get("rate_lt",0.15):
            return ("RETIRE", f"guard tripped: swept-rate {m['swept_rate']:.0%} < {g.get('rate_lt',0.15):.0%} over {m['n_wrong']} — the problem it fixed no longer shows; demote.")
        return ("KEEP", "holding — guard not tripped")
    return ("KEEP", "")

def scoreboard(results, m):
    """Per-source CONTRIBUTION readout for OLIVIER's governance (#56) — NOT an agent-facing reward.
    Credit is OUTCOME-based (a promoted lesson that later moved the terminal metric — 2-moves precision),
    never activity; an honest null is free, a bad candidate costs more than silence. Statelessness is a
    feature: an agent cannot chase a score it cannot remember, so this never becomes a gamed target."""
    from collections import defaultdict
    agg=defaultdict(lambda:{"n":0,"promote":0,"watch":0,"gather":0})
    for L,v in results:
        s=L.get("source") or (f"call#{L.get('spawned_by_call')}" if L.get('spawned_by_call') else "seed")
        a=agg[s]; a["n"]+=1
        a["promote" if v=="PROMOTE" else "watch" if v=="WATCH" else "gather"]+=1
    if not agg: return
    print("\n  CONTRIBUTION SCOREBOARD (governance readout — NOT an agent reward; #56):")
    for s in sorted(agg):
        a=agg[s]; print(f"    {s}: {a['n']} candidate(s) · promote-ready {a['promote']} · on-watch {a['watch']} · gathering {a['gather']}")
    print("    credit = a PROMOTED lesson that later improved the terminal metric (2-moves precision / Brier / swept-rate)")
    print("    vs its promotion-baseline — never for logging. Honest null is free; a bad candidate costs more than silence.")

def main():
    if len(sys.argv)<3: print("usage: python3 discovery_loop.py calls.json lessons.json"); return
    calls=load(sys.argv[1]) or []
    lab=load(sys.argv[2]) or {}
    lessons=lab.get("lessons",[]) if isinstance(lab,dict) else []
    bar_def=lab.get("promotion_bar_default",5) if isinstance(lab,dict) else 5
    resolved=[(r,res) for r in calls for res in [resolve(r)] if res is not None]
    m=metrics(resolved)
    print(f"DISCOVERY LOOP — {time.strftime('%Y-%m-%d %H:%M UTC',time.gmtime())}")
    sr=("n/a" if m['swept_rate'] is None else f"{m['swept_rate']:.0%}")
    ur=("n/a" if m['up_rate'] is None else f"{m['up_rate']:.0%}")
    print(f"  evidence: {m['n']} resolved of {len(calls)} calls · up-rate {ur} · wrong {m['n_wrong']} · swept-then-right {m['n_swept']} ({sr})")
    if not lessons: print("  no lessons on file — lab notebook empty."); return
    print(f"  promotion bar (default): {bar_def} forward supporting calls · candidates gated · doctrine retirable")
    promote=[]; retire=[]; results=[]
    for L in lessons:
        v,detail=evaluate(L,m)
        results.append((L,v))
        tag={"PROMOTE":"PROMOTE ⇧","RETIRE":"RETIRE ⇩","WATCH":"watch","KEEP":"keep","INSUFFICIENT":"gathering"}.get(v,v)
        print(f"  [{L.get('status','?')}] {L.get('id','?')} — {tag}: {detail}")
        print(f"       \"{(L.get('statement','') or '')[:150]}\"")
        if v=="PROMOTE": promote.append(L)
        if v=="RETIRE": retire.append(L)
    if promote:
        print("\n  PROPOSED PROMOTIONS (paste into SKILL.md doctrine, then SAVE the skill to propagate to all agents):")
        for L in promote: print(f"    + {L.get('proposed_doctrine', L.get('statement'))}")
    if retire:
        print("\n  PROPOSED RETIREMENTS (demote in SKILL.md, then SAVE):")
        for L in retire: print(f"    - {L.get('id')}: {(L.get('statement','') or '')[:120]}")
    if not promote and not retire:
        print("\n  nothing earned promotion or retirement this cycle — candidates stay on watch. An honest null is the correct output.")
    scoreboard(results, m)
    print("  PROPOSES only — never auto-edits the skill; the human SAVE is the gate (audit #53: freeze the thesis, retire what fails). Read-only.")

if __name__=="__main__":
    main()
