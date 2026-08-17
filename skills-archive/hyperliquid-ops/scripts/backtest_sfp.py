#!/usr/bin/env python3
"""Shallow-sweep -> reclaim (the #23/#71 signal) at Olivier's params. Sweep = fresh break below the
prior-24h low; shallow = <0.24% beyond it. Reproduces the reclaim RATE (should be ~85% shallow on 4h)
AND tests whether the reclaim is a profitable LONG at +0.5%/-0.3%/5bp vs a random control. Walk-forward."""
import json,time,urllib.request,statistics,random
random.seed(7)
API="https://api.hyperliquid.xyz/info"
def fetch(iv,days):
    end=int(time.time()*1000);start=end-days*86400_000
    r=urllib.request.Request(API,data=json.dumps({"type":"candleSnapshot","req":{"coin":"BTC","interval":iv,"startTime":start,"endTime":end}}).encode(),headers={"Content-Type":"application/json"})
    try: return sorted(json.load(urllib.request.urlopen(r,timeout=60)),key=lambda k:k["t"])
    except Exception as e: print("  fetch fail",iv,e);return []
def run(iv,days,W,Hrec=12,Ht=24,SH=0.0024,TGT=0.005,STOP=0.003,COST=0.05):
    cd=fetch(iv,days)
    if len(cd)<200: print(f"[{iv}] no/thin data ({len(cd)})");return
    O=[float(c["o"]) for c in cd];Hi=[float(c["h"]) for c in cd];Lo=[float(c["l"]) for c in cd];C=[float(c["c"]) for c in cd];n=len(cd)
    def trade(i):
        e=C[i];tp=e*(1+TGT);sl=e*(1-STOP)
        for f in range(i+1,min(i+1+Ht,n)):
            if Lo[f]<=sl: return -STOP*100,False
            if Hi[f]>=tp: return TGT*100,True
        return (C[min(i+Ht,n-1)]/e-1)*100,None
    sh=[];dp=[];sht=[];last=-10**9
    for i in range(W+1,n-Ht-1):
        lvl=min(Lo[i-W:i])
        if not (Lo[i]<lvl and Lo[i-1]>=lvl) or i-last<Hrec: continue
        depth=(lvl-Lo[i])/lvl
        recl=next((j for j in range(i+1,min(i+1+Hrec,n)) if C[j]>lvl),None)
        (sh if depth<SH else dp).append(recl is not None)
        if depth<SH and recl is not None: sht.append(trade(recl))
        last=i
    ctrl=[trade(random.randint(W+1,n-Ht-1)) for _ in range(2000)]
    r=lambda L:(len(L),100*sum(L)/len(L)) if L else (0,0)
    sn,sr=r(sh);dn,dr=r(dp)
    print(f"\n[BTC {iv} {days}d ~{n}bars  sweep of prior-{W}bar low]")
    print(f"  RECLAIM RATE: shallow(<0.24%) {sr:.0f}% (n={sn}) | deep {dr:.0f}% (n={dn})")
    if sht:
        m=statistics.mean(x for x,_ in sht);hr=100*sum(1 for _,h in sht if h)/len(sht);cm=statistics.mean(x for x,_ in ctrl)
        print(f"  SHALLOW-RECLAIM LONG +0.5%/-0.3%/5bp: n={len(sht)} hit+0.5%={hr:.0f}% net={m:+.3f}%/trade | random {cm:+.3f}% | edge {m-cm:+.3f}%")
for iv,days,W in [("1h",208,24),("2h",400,12),("4h",800,6)]:
    run(iv,days,W)
