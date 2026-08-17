#!/usr/bin/env python3
"""ANALOG PATH — 'think of the signal like a bug': REPRO the current state and read what happened NEXT,
empirically, instead of narrating it. Fingerprint RIGHT NOW across the desk's dimensions (regime = coil via
efficiency ratio, volatility compression via ATR-now/ATR-median, range-position in the trailing week), pull
EVERY historical 1h bar that matches that fingerprint, and measure the forward $K-leg PATH: which $K move
came FIRST (up vs down), and whether the SECOND $K leg CONTINUED or REVERSED (the washing-machine rotation,
#41). This is ONE conditioning — the current state — NOT a scan of combinations, so it dodges the Elliott
trap (#46): we are reproducing today's bug, not mining. BTC ONLY, HL, no stop/cost. Read-only, empirical,
in-sample-conditional; honest n + overlap caveat. K defaults to $300 (OLIVIER's leg size)."""
import json,urllib.request,time,statistics
API="https://api.hyperliquid.xyz/info"; K=300.0; MAXH=120   # $ leg, max 5-day search per path
def fetch(days):
    step=3600000;end=int(time.time()*1000);cur=end-int(days*86400_000);seen={}
    while cur<end:
        r=urllib.request.Request(API,data=json.dumps({"type":"candleSnapshot","req":{"coin":"BTC","interval":"1h","startTime":cur,"endTime":min(cur+4800*step,end)}}).encode(),headers={"Content-Type":"application/json"})
        try:d=json.load(urllib.request.urlopen(r,timeout=60))
        except Exception:d=[]
        if not d:cur+=4800*step;continue
        for c in d:seen[c['t']]=c
        cur=max(c['t'] for c in d)+step
    return [seen[t] for t in sorted(seen)]

cd=fetch(300);O=[float(c['o']) for c in cd];H=[float(c['h']) for c in cd];L=[float(c['l']) for c in cd]
C=[float(c['c']) for c in cd];T=[int(c['t']) for c in cd];n=len(C)
def tr(i): return H[i]-L[i] if i==0 else max(H[i]-L[i],abs(H[i]-C[i-1]),abs(L[i]-C[i-1]))
ATR=[None]*n; s=0
for i in range(n):
    s+= tr(i)
    if i>=14: s-=tr(i-14); ATR[i]=s/14
    elif i>0: ATR[i]=s/(i+1)
    else: ATR[i]=tr(0)
atrmed=statistics.median([a for a in ATR[200:] if a])
def eff(i,W=24):
    if i-W<0: return None
    num=abs(C[i]-C[i-W]); den=sum(abs(C[i-k]-C[i-1-k]) for k in range(W)) or 1e-9; return num/den
def rangepos(i,win=168):
    if i-win<0: return None
    hi=max(H[i-win:i+1]); lo=min(L[i-win:i+1]); return (C[i]-lo)/(hi-lo) if hi>lo else .5
EFF=[eff(i) for i in range(n)];RP=[rangepos(i) for i in range(n)];ATRC=[ (ATR[i]/atrmed) if ATR[i] else None for i in range(n)]

cur=n-1
e0,r0,c0,px=EFF[cur],RP[cur],ATRC[cur],C[cur]
print(f"NOW (bar {cur}, {time.strftime('%Y-%m-%d %H:%M UTC',time.gmtime(T[cur]/1000))}): px {px:,.0f}  efficiency {e0:.2f}  range-pos {r0*100:.0f}%  ATR-compression {c0:.2f}  (K=${K:.0f} legs)")

def path(i):
    """from bar i: find first +/-K (leg1), then from there first continue/reverse-K (leg2). Returns (leg1dir, hrs1, leg2, hrs2) or None."""
    entry=C[i]; d1=0; b1=None
    for j in range(i+1,min(i+MAXH,n)):
        up=H[j]-entry>=K; dn=entry-L[j]>=K
        if up and dn: d1=(1 if C[j]>=entry else -1); b1=j; break   # rare both-in-bar -> close side
        if up: d1=1;b1=j;break
        if dn: d1=-1;b1=j;break
    if not b1: return None
    ref=entry+d1*K
    for j in range(b1,min(b1+MAXH,n)):
        cont=(H[j]-ref>=K) if d1>0 else (ref-L[j]>=K)   # another K same dir
        rev =(ref-L[j]>=K) if d1>0 else (H[j]-ref>=K)   # K back the other way
        if cont and rev: leg2=('continue' if C[j]>=ref else 'reverse') if d1>0 else ('continue' if C[j]<=ref else 'reverse')
        elif cont: leg2='continue'
        elif rev: leg2='reverse'
        else: continue
        return (d1,(T[b1]-T[i])/3600000,leg2,(T[j]-T[b1])/3600000)
    return (d1,(T[b1]-T[i])/3600000,'unresolved',None)

# match window: bars whose (eff, range-pos, atr-compression) are close to NOW
matches=[]
for i in range(200,n-MAXH):
    if EFF[i] is None or RP[i] is None or ATRC[i] is None: continue
    if abs(EFF[i]-e0)<=0.15 and abs(RP[i]-r0)<=0.18 and abs(ATRC[i]-c0)<=0.45:
        matches.append(i)
paths=[path(i) for i in matches]; paths=[p for p in paths if p]
n1=len(paths); up1=sum(1 for p in paths if p[0]>0); dn1=n1-up1
res=[p for p in paths if p[2] in ('continue','reverse')]
cont=sum(1 for p in res if p[2]=='continue'); rev=sum(1 for p in res if p[2]=='reverse')
# leg2 split conditioned on leg1 dir
def split(dir):
    s=[p for p in res if p[0]==dir]; c=sum(1 for p in s if p[2]=='continue'); return len(s),c,len(s)-c
print(f"\nANALOGS to NOW: {n1} historical bars matched the fingerprint (of {n-MAXH-200} candidate bars, ~{100*n1/max(1,n-MAXH-200):.0f}%).")
if n1>=15:
    print(f"  LEG 1 — which ${K:.0f} move came FIRST:  UP {100*up1/n1:.0f}%  ·  DOWN {100*dn1/n1:.0f}%   (n={n1}, median time to leg1 {statistics.median([p[1] for p in paths]):.0f}h)")
    if res:
        print(f"  LEG 2 — after leg1, the next ${K:.0f}:  CONTINUE {100*cont/len(res):.0f}%  ·  REVERSE {100*rev/len(res):.0f}%   (n={len(res)}; REVERSE = washing-machine rotation #41)")
        for d,lab in [(1,'after an UP leg1'),(-1,'after a DOWN leg1')]:
            ns,cc,rr=split(d)
            if ns>=8: print(f"       {lab}: continue {100*cc/ns:.0f}% / reverse {100*rr/ns:.0f}%  (n={ns})")
    unresolved=n1-len(res)
    if unresolved: print(f"  ({unresolved} paths had a leg1 but no second ${K:.0f} within {MAXH}h — chop.)")
else:
    print("  too few analogs to read — loosen the fingerprint or accept the state is unusual (itself information).")
print("\nCAVEAT: analogs overlap in time (not independent) → treat % as directional, not precise; ONE conditioning")
print("(today's state), no scan, so no multiple-comparison inflation. Empirical repro of the CURRENT bug, read-only.")
