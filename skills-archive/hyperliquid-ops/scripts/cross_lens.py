#!/usr/bin/env python3
"""CROSS-LENS — hunt the signal at the INTERSECTIONS (OLIVIER: confluence / correlation / contradiction /
combination; 'think of the signal like a bug' → isolate the exact conditions under which it fires).
BTC ONLY, 1h, NO stop/cost, content = directional fwd return vs the sample's own base rate. Takes the
robust reversal edges and CONDITIONS them on the other lenses — recent-move (#43), trend-direction
('poke the OTHER way'), perp↔spot basis (#44 positioning), funding (#41 bleed) — to find where 2 lenses
CONFLUE (content sharpens) vs CONTRADICT (content flips). Plus the decorrelation matrix incl. the
positioning edge. This is the combiner's real question: not average signals, but find the CONDITIONS."""
import statistics, math, bisect, urllib.request, json, time, random
random.seed(21)
from edge_ensemble import fetch, atr, E_resreject, E_pokereclaim, E_volspike, content, fwd
API="https://api.hyperliquid.xyz/info"
def post(b):
    try:
        r=urllib.request.Request(API,data=json.dumps(b).encode(),headers={"Content-Type":"application/json"});return json.load(urllib.request.urlopen(r,timeout=60))
    except Exception:return None
def spot_closes(days):
    step=3600000;end=int(time.time()*1000);cur=end-days*86400_000;seen={}
    while cur<end:
        d=post({"type":"candleSnapshot","req":{"coin":"@142","interval":"1h","startTime":cur,"endTime":min(cur+4800*step,end)}}) or []
        if not d:cur+=4800*step;continue
        for c in d:seen[int(c['t'])]=float(c['c'])
        cur=max(int(c['t']) for c in d)+step
    return seen
def funding_map(days):
    end=int(time.time()*1000);cur=end-days*86400_000;seen={}
    while cur<end:
        d=post({"type":"fundingHistory","coin":"BTC","startTime":cur,"endTime":min(cur+19*86400_000,end)}) or []
        if not d:cur+=19*86400_000;continue
        for r in d:seen[int(r['time'])]=float(r['fundingRate'])
        nt=max(int(r['time']) for r in d)
        if nt<=cur:break
        cur=nt+1
    return seen

cd=fetch("1h",200);O=[float(c['o']) for c in cd];H=[float(c['h']) for c in cd];L=[float(c['l']) for c in cd]
C=[float(c['c']) for c in cd];V=[float(c['v']) for c in cd];T=[int(c['t']) for c in cd];n=len(C);A=atr(H,L,C);h=12;REF=6
sp=spot_closes(200);fu=funding_map(180)
# per-bar lenses
prem=[None]*n
for i in range(n):
    s=sp.get(T[i]); prem[i]=(C[i]/s-1)*1e4 if s else None
fk=sorted(fu); fund=[None]*n
for i in range(n):
    j=bisect.bisect_right(fk,T[i])-1; fund[i]=fu[fk[j]] if j>=0 else None
mv=[ (C[i]/C[i-24]-1) if i>=24 else 0.0 for i in range(n)]
premv=[p for p in prem if p is not None]; pmed_hi=sorted(premv)[int(0.7*len(premv))]; pmed_lo=sorted(premv)[int(0.3*len(premv))]
mvabs=sorted(abs(x) for x in mv); mvmed=mvabs[len(mvabs)//2]

def cc(ev, mask=None):
    r=[fwd(d,i,C,n,h) for (i,d) in ev if (mask is None or mask(i,d))]
    r=[x for x in r if x is not None]; return (len(r), statistics.mean(r) if r else 0.0)  # fwd already returns %

base=statistics.mean([fwd(random.choice([-1,1]),random.randint(24,n-14),C,n,h) or 0 for _ in range(4000)])
E2=E_resreject(O,H,L,C,n,REF,h)   # short (dir -1)
E4=E_pokereclaim(O,H,L,C,n,REF,h) # long  (dir +1)
E1=E_volspike(O,H,L,C,V,n,A,REF,h)# fade (both)
print(f"BTC 1h {n} bars · random base fwd@12 = {base:+.3f}%  (edges must beat THIS, and confluence must beat the edge alone)\n")

def row(name, ev, masks):
    nn,al=cc(ev); print(f"  {name:26s} ALL n={nn:4d} content {al:+.3f}%  (vs base {al-base:+.3f})")
    for label,mfn in masks:
        n2,c2=cc(ev,mfn); tag="CONFLUENCE" if c2>al+0.05 else ("CONTRADICTION" if c2<al-0.05 else "~")
        print(f"      × {label:34s} n={n2:4d} content {c2:+.3f}%   ({tag} vs edge-alone {c2-al:+.3f})")

print("== E2 resTL-REJECT short — condition on lenses ==")
row("E2 resTL-reject (short)", E2, [
    ("recent UP move (fade WITH offside)", lambda i,d: mv[i]>mvmed),
    ("perp PREMIUM (longs crowded)",       lambda i,d: prem[i] is not None and prem[i]>=pmed_hi),
    ("perp DISCOUNT (contradiction?)",     lambda i,d: prem[i] is not None and prem[i]<=pmed_lo),
    ("funding>0 (longs pay = crowded)",    lambda i,d: fund[i] is not None and fund[i]>0),
])
print("\n== E4 poke-low->reclaim long — condition on lenses ==")
row("E4 poke-reclaim (long)", E4, [
    ("recent DOWN move (poke the other way)", lambda i,d: mv[i]<-mvmed),
    ("perp DISCOUNT (shorts crowded/cheap)",  lambda i,d: prem[i] is not None and prem[i]<=pmed_lo),
    ("perp PREMIUM (contradiction?)",         lambda i,d: prem[i] is not None and prem[i]>=pmed_hi),
    ("|move| large (fresh liquidity built)",  lambda i,d: abs(mv[i])>mvmed),
])
print("\n== E1 vol-spike FADE — condition on lenses ==")
row("E1 vol-spike-fade", E1, [
    ("after a move (harvest built liq)", lambda i,d: abs(mv[i])>mvmed),
    ("fade aligns w/ perp dislocation",  lambda i,d: prem[i] is not None and ((d<0 and prem[i]>=pmed_hi) or (d>0 and prem[i]<=pmed_lo))),
])
# decorrelation incl perp-premium-fade (E5) on daily pnl
def daily(ev):
    p={}
    for i,d in ev:
        v=fwd(d,i,C,n,h)
        if v is not None:p[T[i]//86400000]=p.get(T[i]//86400000,0.0)+v
    return p
E5=[(i,-1) for i in range(24,n-14) if prem[i] is not None and prem[i]>=pmed_hi]  # fade perp premium = short
E5=[E5[k] for k in range(len(E5)) if k==0 or E5[k][0]-E5[k-1][0]>=REF]
D={"E1":daily(E1),"E2":daily(E2),"E4":daily(E4),"E5 perp-prem-fade":daily(E5)}
days=sorted(set().union(*[set(d) for d in D.values()]));names=list(D)
def corr(a,b):
    xa=[a.get(x,0.) for x in days];xb=[b.get(x,0.) for x in days];m=len(days);ma=sum(xa)/m;mb=sum(xb)/m
    va=math.sqrt(sum((x-ma)**2 for x in xa));vb=math.sqrt(sum((x-mb)**2 for x in xb))
    return sum((xa[i]-ma)*(xb[i]-mb) for i in range(m))/(va*vb) if va>0 and vb>0 else 0
print("\n== DECORRELATION (daily PnL, incl. positioning edge E5) ==")
print("        "+"  ".join(f"{x[:6]:>6}" for x in names))
for a in names: print(f"  {a[:6]:6s} "+"  ".join(f"{corr(D[a],D[b]):>6.2f}" for b in names))
print("\nRead: CONFLUENCE cells (content > edge-alone by >0.05%) = the conditions the signal really lives in")
print("(the 'bug repro'); CONTRADICTION cells = where a lens flips it (also information). DISCOVERY/in-sample.")
