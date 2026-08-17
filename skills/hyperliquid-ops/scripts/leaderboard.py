#!/usr/bin/env python3
"""LEADERBOARD — the co-desk competition scoreboard (doctrine #57). Ranks the desks (by:Claude vs by:Grok, and
any other source) on FORWARD calibration — Brier vs the 0.5 baseline — CONDITIONED ON REGIME (trend/range,
high/low-vol, weekend/weekday), with an independence check (near-identical cross-desk calls = echoes, discounted)
and CONTESTED detection (material cross-desk disagreements = the high-information moments; who wins them).

It is a GOVERNANCE READOUT for OLIVIER — 'who to trust, in which regime' — never a reward fed back to a desk
(#56/#57): statelessness is the safeguard. Same shared resolver and call store as calibration.py; the Sunday
retro gathers all call-*.json from Drive into one array and feeds it here.

Usage:  python3 leaderboard.py calls.json    (calls = array of SCORE records, each with a "by" field)
Read-only, auto-resolved from price."""
import json, sys, time, statistics
from calibration import resolve, post          # shared resolver + API poster (one source of truth)

def desk(by):
    b=(by or "").lower()
    if "grok" in b: return "Grok"
    if "claude" in b: return "Claude"
    return by or "unknown"

def regime(ts):
    """Trailing market state AT the call's ts → tags. trend/range (24h efficiency ratio), vol (24h range%),
    weekend/weekday (UTC). Empty price history → just the session tag."""
    end=int(ts); d=post({"type":"candleSnapshot","req":{"coin":"BTC","interval":"1h","startTime":end-25*3600_000,"endTime":end}}) or []
    tags=[]
    if len(d)>=12:
        C=[float(x['c']) for x in d]; H=[float(x['h']) for x in d]; L=[float(x['l']) for x in d]
        er=abs(C[-1]-C[0])/(sum(abs(C[i]-C[i-1]) for i in range(1,len(C))) or 1e-9)
        tags.append("trend" if er>=0.35 else "range")
        tags.append("highvol" if (max(H)-min(L))/C[-1]>=0.03 else "lowvol")
    tags.append("weekend" if time.gmtime(end/1000).tm_wday>=5 else "weekday")
    return tags

def score(rows):
    if not rows: return None
    bm=statistics.mean((r['p']-r['o'])**2 for r in rows)
    bb=statistics.mean((r['pb']-r['o'])**2 for r in rows)
    return {"n":len(rows),"up":statistics.mean(r['o'] for r in rows),"bm":bm,"bb":bb,"skill":(1-bm/bb) if bb>0 else 0.0}

def main():
    if len(sys.argv)<2: print("usage: python3 leaderboard.py calls.json"); return
    calls=json.loads((open(sys.argv[1]).read() or "[]"))
    rows=[]; unresolved=0
    for c in calls:
        res=resolve(c)
        if res is None: unresolved+=1; continue
        rows.append({"by":desk(c.get("by")),"o":res["o"],"p":float(c["p_up"]),"pb":float(c.get("p_base",0.5)),
                     "ts":int(c["ts"]),"up":float(c["up"]),"dn":float(c["dn"]),"reg":regime(int(c["ts"]))})
    print(f"LEADERBOARD — {len(rows)} resolved of {len(calls)} calls ({unresolved} unmatured) · {time.strftime('%Y-%m-%d %H:%M UTC',time.gmtime())}")
    if not rows:
        print("  nothing resolved yet — accumulating. No standing until n>=~20 per desk/regime. Keep logging blind, independent calls."); return
    desks=sorted(set(r['by'] for r in rows))
    print("\n  OVERALL (Brier lower=better; skill = 1 - model/baseline, higher=better):")
    for dk in desks:
        s=score([r for r in rows if r['by']==dk])
        print(f"    {dk:8s} n={s['n']:2d} · up-rate {s['up']:.0%} · Brier {s['bm']:.3f} vs base {s['bb']:.3f} · skill {s['skill']:+.1%}")
    for dim,opts in [("trend / range",["trend","range"]),("volatility",["highvol","lowvol"]),("session",["weekend","weekday"])]:
        line=[]
        for opt in opts:
            for dk in desks:
                s=score([r for r in rows if r['by']==dk and opt in r['reg']])
                if s: line.append(f"[{opt}] {dk} n={s['n']} skill {s['skill']:+.0%}")
        if line: print(f"\n  BY {dim}:  " + "  ·  ".join(line))
    # independence — near-identical cross-desk calls are echoes, not two votes
    echoes=sum(1 for i in range(len(rows)) for j in range(i+1,len(rows))
               if rows[i]['by']!=rows[j]['by'] and abs(rows[i]['ts']-rows[j]['ts'])<6*3600_000
               and abs(rows[i]['up']-rows[j]['up'])<80 and abs(rows[i]['dn']-rows[j]['dn'])<80 and abs(rows[i]['p']-rows[j]['p'])<0.06)
    if echoes: print(f"\n  INDEPENDENCE: {echoes} near-identical cross-desk pair(s) — echoes, discounted (an echo is not a second vote).")
    # CONTESTED — cross-desk, close in time, material disagreement; who called it better
    contested=[]
    for i in range(len(rows)):
        for j in range(i+1,len(rows)):
            a,b=rows[i],rows[j]
            if a['by']!=b['by'] and abs(a['ts']-b['ts'])<6*3600_000 and (abs(a['p']-b['p'])>=0.15 or (a['p']-0.5)*(b['p']-0.5)<0):
                contested.append(a['by'] if abs(a['p']-a['o'])<abs(b['p']-b['o']) else b['by'])
    if contested:
        wins={}
        for w in contested: wins[w]=wins.get(w,0)+1
        print(f"\n  CONTESTED: {len(contested)} disagreement pair(s) (the high-information moments) — "+", ".join(f"{dk} won {c}" for dk,c in sorted(wins.items(),key=lambda x:-x[1])))
    print("\n  VERDICT:")
    ready=[dk for dk in desks if score([r for r in rows if r['by']==dk])['n']>=20]
    if not ready:
        print("    accumulating — no desk at n>=20 yet; no standing declared.")
    else:
        best=max(ready,key=lambda dk:score([r for r in rows if r['by']==dk])['skill'])
        print(f"    at n>=20: {best} leads overall on skill; weight the desk that owns each regime (table above).")
    print("  Governance readout for OLIVIER — never fed back to a desk as a target (#56/#57). Read-only, auto-resolved from price.")

if __name__=="__main__": main()
