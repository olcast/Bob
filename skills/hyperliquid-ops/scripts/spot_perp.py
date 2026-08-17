#!/usr/bin/env python3
"""SPOT vs PERP — HL only, BTC only. Perp = 'BTC', Spot = '@142' (UBTC/USDC). Backtestable now
(both have candle history). Measures: (1) basis = perp/spot−1 (bp) + its distribution; (2) LEAD-LAG —
does spot lead perp or perp lead spot (cross-corr of returns at lags); (3) BASIS-DIVERGENCE reversion —
when perp trades at an extreme premium/discount to spot, what does perp do next (fade the perp
dislocation?). No stop/cost, content vs random, OOS. CVD/aggressor-flow and trader-profiling are
FORWARD-only (shallow trade tape / per-address harvest) — scoped for the collector, not here."""
import json,urllib.request,time,statistics,math,random
random.seed(17); API="https://api.hyperliquid.xyz/info"
def post(b):
    try:
        r=urllib.request.Request(API,data=json.dumps(b).encode(),headers={"Content-Type":"application/json"})
        return json.load(urllib.request.urlopen(r,timeout=60))
    except Exception:return None
def candles(coin,iv,days):
    step={'1h':3600000}[iv];end=int(time.time()*1000);cur=end-days*86400_000;seen={}
    while cur<end:
        d=post({"type":"candleSnapshot","req":{"coin":coin,"interval":iv,"startTime":cur,"endTime":min(cur+4800*step,end)}}) or []
        if not d:cur+=4800*step;continue
        for c in d:seen[c['t']]=c
        cur=max(c['t'] for c in d)+step
    return {int(c['t']):float(c['c']) for c in seen.values()}

perp=candles("BTC","1h",200); spot=candles("@142","1h",200)
print(f"perp bars {len(perp)}  spot(@142) bars {len(spot)}")
common=sorted(set(perp)&set(spot))
if len(common)<200:
    print(f"  overlap {len(common)} bars — spot history limited; reporting what exists.")
P=[perp[t] for t in common]; S=[spot[t] for t in common]; n=len(P)
basis=[(P[i]/S[i]-1)*1e4 for i in range(n)]   # bp
print(f"  overlap {n} bars. BASIS perp-vs-spot (bp): mean {statistics.mean(basis):+.1f}  sd {statistics.pstdev(basis):.1f}  "
      f"min {min(basis):+.0f}  max {max(basis):+.0f}")
# returns
rp=[P[i]/P[i-1]-1 for i in range(1,n)]; rs=[S[i]/S[i-1]-1 for i in range(1,n)]
def corr(a,b):
    m=min(len(a),len(b));a=a[:m];b=b[:m];ma=sum(a)/m;mb=sum(b)/m
    ca=math.sqrt(sum((x-ma)**2 for x in a));cb=math.sqrt(sum((x-mb)**2 for x in b))
    return sum((a[i]-ma)*(b[i]-mb) for i in range(m))/(ca*cb) if ca>0 and cb>0 else 0
print("\n  LEAD-LAG (corr of returns; >0 at 'spot leads' means spot move predicts next perp move):")
for L in [1,2,3]:
    sp=corr(rs[:-L],rp[L:]); ps=corr(rp[:-L],rs[L:])
    print(f"    lag {L}h: spot(t-{L})→perp(t) {sp:+.3f}   perp(t-{L})→spot(t) {ps:+.3f}   -> {'SPOT leads' if sp>ps+0.02 else ('PERP leads' if ps>sp+0.02 else 'symmetric')}")
# basis-divergence reversion: extreme basis -> forward perp return, vs random
def content(idx,h=6):
    r=[]
    for i in idx:
        if i+h<n: r.append(P[i+h]/P[i]-1)
    return r
srt=sorted(range(n-6),key=lambda i:basis[i])
q=len(srt)//10
hi=srt[-q:]  # perp most PREMIUM to spot
lo=srt[:q]   # perp most DISCOUNT to spot
def m(x): return statistics.mean(x)*100 if x else 0
rand=[P[random.randint(0,n-7)+6]/P[random.randint(0,n-7)] -1 for _ in range(3000)]
print("\n  BASIS-DIVERGENCE reversion (fwd 6h perp return after an extreme basis):")
print(f"    perp PREMIUM decile (fade→short?): fwd {m(content(hi)):+.3f}%   perp DISCOUNT decile (fade→long?): fwd {m(content(lo)):+.3f}%   random {statistics.mean(rand)*100:+.3f}%")
print("    (if premium→negative fwd and discount→positive fwd beyond random, perp dislocations mean-revert to spot = a fade edge)")
print("\nSCOPE: CVD/aggressor + trader-profiling are FORWARD-only (add to collector). This spot↔perp basis")
print("is the backtestable slice; treat any signal here as DISCOVERY (in-sample) pending the usual gate.")
