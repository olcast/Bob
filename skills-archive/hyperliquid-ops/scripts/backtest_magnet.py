#!/usr/bin/env python3
"""Trendline break+retest x LIQUIDITY (traded-structure proxy). The real liq-map is forward-only, so
'liquidity above' = nearest UNTAPPED prior swing high within 150 bars (where stops/liquidity actually sit).
Split reclaim events by whether a magnet sits 0.3-2% above, and grade by excursion (MFE/MAE, 5bp). 1h/208d."""
import json,time,urllib.request,statistics,random
random.seed(11)
API="https://api.hyperliquid.xyz/info"
def fetch(iv,days):
    end=int(time.time()*1000);start=end-days*86400_000
    r=urllib.request.Request(API,data=json.dumps({"type":"candleSnapshot","req":{"coin":"BTC","interval":iv,"startTime":start,"endTime":end}}).encode(),headers={"Content-Type":"application/json"})
    return sorted(json.load(urllib.request.urlopen(r,timeout=60)),key=lambda k:k["t"])
cd=fetch("1h",208);O=[float(c["o"]) for c in cd];H=[float(c["h"]) for c in cd];L=[float(c["l"]) for c in cd];C=[float(c["c"]) for c in cd];n=len(cd);k=3;Wm=24
fh=[i for i in range(k,n-k) if H[i]==max(H[i-k:i+k+1])]
conf=sorted([(p,p+k) for p in fh],key=lambda x:x[1]);mc=[None]*n;cf=[];cp=0
for i in range(n):
    while cp<len(conf) and conf[cp][1]<=i: cf.append(conf[cp][0]);cp+=1
    if len(cf)>=2:
        p1,p2=cf[-2],cf[-1]
        if H[p2]<H[p1] and p2<i: m=(H[p2]-H[p1])/(p2-p1);mc[i]=(m,H[p1]-m*p1)
def overhead(e):
    best=None
    for h in fh:
        if h<e-150 or h>=e or H[h]<=C[e]: continue
        if max(H[h+1:e+1])<=H[h]:
            d=(H[h]-C[e])/C[e]*100
            if best is None or d<best: best=d
    return best
mag=[];air=[];last=-999
for i in range(30,n-Wm-1):
    if mc[i] is None: continue
    m,c0=mc[i];Li=m*i+c0;Lp=m*(i-1)+c0
    if not (C[i-1]<=Lp and C[i]>Li) or i-last<12: continue
    d=overhead(i);last=i
    ent=C[i];hi=[(H[j]-ent)/ent*100 for j in range(i+1,min(i+1+Wm,n))];lo=[(L[j]-ent)/ent*100 for j in range(i+1,min(i+1+Wm,n))]
    if not hi: continue
    mfe=max(hi);mae=min(lo)
    r=None
    for j in range(i+1,min(i+1+Wm,n)):
        if L[j]<=ent*0.997: r=-0.3;break
        if H[j]>=ent*1.005: r=0.5;break
    exp=(r if r is not None else (C[min(i+Wm,n-1)]/ent-1)*100)-0.05
    rec=(mfe,mae,exp)
    (mag if (d is not None and 0.3<=d<=2.0) else air).append(rec)
ctrl=[]
for _ in range(2000):
    i=random.randint(30,n-Wm-1);ent=C[i]
    r=None
    for j in range(i+1,min(i+1+Wm,n)):
        if L[j]<=ent*0.997: r=-0.3;break
        if H[j]>=ent*1.005: r=0.5;break
    ctrl.append((r if r is not None else (C[min(i+Wm,n-1)]/ent-1)*100)-0.05)
def show(nm,ev):
    if len(ev)<10: print(f"  {nm:32s} n={len(ev)} (too few)");return
    mfe=statistics.median(x[0] for x in ev);mae=statistics.median(x[1] for x in ev);exp=statistics.mean(x[2] for x in ev)
    p05=100*sum(1 for x in ev if x[0]>=0.5)/len(ev)
    print(f"  {nm:32s} n={len(ev):3d} medMFE={mfe:+.2f}% medMAE={mae:+.2f}% reach+0.5%={p05:.0f}% exp={exp:+.3f}%")
print(f"BTC 1h 208d | trendline reclaim split by OVERHEAD MAGNET (untapped swing high 0.3-2% above)")
print(f"  RANDOM control expectancy = {statistics.mean(ctrl):+.3f}%")
show("reclaim -> magnet above (0.3-2%)",mag)
show("reclaim -> air (no magnet <2%)",air)
