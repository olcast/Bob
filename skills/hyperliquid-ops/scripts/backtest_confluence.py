#!/usr/bin/env python3
"""Multi-TF confluence reclaim backtest, walk-forward, own-lines.
For a base timeframe, detect fresh reclaims of the active descending resistance
(line through the last two CONFIRMED descending pivot highs; pivot p known only at p+k).
Tag each reclaim CONFLUENT if, at that timestamp, a live higher-TF descending line sits
within 0.4% of the reclaimed line (structure.py confluence tol); else ISOLATED.
Compare forward outcome (target +0.8% vs reclaim-fail stop line-0.2%, H bars; and mean
fwd with cost removed) confluent vs isolated vs unconditional drift.
DISCOVERY / in-sample, single venue+asset -> needs blind + regime-split validation."""
import json, time, urllib.request, statistics, bisect
API="https://api.hyperliquid.xyz/info"

def fetch(coin, iv, days):
    end=int(time.time()*1000); start=end-days*86400_000
    r=urllib.request.Request(API,data=json.dumps({"type":"candleSnapshot","req":{"coin":coin,"interval":iv,"startTime":start,"endTime":end}}).encode(),headers={"Content-Type":"application/json"})
    return sorted(json.load(urllib.request.urlopen(r,timeout=60)),key=lambda k:k["t"])

def piv_highs(H,k):
    return [i for i in range(k,len(H)-k) if H[i]==max(H[i-k:i+k+1])]

def build(coin, iv, days, k=3):
    cd=fetch(coin,iv,days)
    O=[float(c["o"]) for c in cd]; H=[float(c["h"]) for c in cd]; L=[float(c["l"]) for c in cd]
    C=[float(c["c"]) for c in cd]; V=[float(c["v"]) for c in cd]; T=[int(c["t"]) for c in cd]
    n=len(C)
    conf=sorted([(p,p+k) for p in piv_highs(H,k)], key=lambda x:x[1])
    mc=[None]*n; confirmed=[]; cp=0
    for i in range(n):
        while cp<len(conf) and conf[cp][1]<=i:
            confirmed.append(conf[cp][0]); cp+=1
        if len(confirmed)>=2:
            p1,p2=confirmed[-2],confirmed[-1]
            if H[p2]<H[p1] and p2<i:
                m=(H[p2]-H[p1])/(p2-p1); mc[i]=(m,H[p1]-m*p1)
    return dict(T=T,O=O,H=H,L=L,C=C,V=V,mc=mc,n=n)

def hval(hs,t):
    b=bisect.bisect_right(hs["T"],t)-1
    if b<0 or hs["mc"][b] is None: return None
    m,c0=hs["mc"][b]; return m*b+c0

CACHE={}
def get(coin,iv,days):
    key=(coin,iv,days)
    if key not in CACHE: CACHE[key]=build(coin,iv,days)
    return CACHE[key]

def run(coin, base_iv, days, H, highers, tolpct=0.004, cost=0.0):
    bs=get(coin,base_iv,days); hb={iv:get(coin,iv,d) for iv,d in highers}
    T,C,Hh,Ll,mc,n=bs["T"],bs["C"],bs["H"],bs["L"],bs["mc"],bs["n"]
    drift=[(C[i+H]-C[i])/C[i]*100 for i in range(30,n-H)]
    confl=[]; iso=[]; last=-10**9
    for i in range(30,n-H-1):
        if mc[i] is None: continue
        m,c0=mc[i]; Li=m*i+c0; Lp=m*(i-1)+c0
        if not (C[i-1]<=Lp and C[i]>Li): continue
        if i-last<H: continue
        tol=C[i]*tolpct; deg=0
        for iv,_ in highers:
            hv=hval(hb[iv],T[i])
            if hv is not None and abs(hv-Li)<=tol: deg+=1
        e=C[i]; stop=Li-0.002*e; tgt=e*1.008; win=None
        for f in range(i+1,i+1+H):
            if Ll[f]<=stop: win=False; break
            if Hh[f]>=tgt: win=True; break
        if win is None: win=C[i+H]>e
        fwd=(C[i+H]-e)/e*100
        (confl if deg>=1 else iso).append((win,fwd,deg)); last=i
    def show(nm,ev):
        if not ev: print(f"  {nm:22s} 0 events"); return
        w=[x for x,_,_ in ev if x is not None]; hr=100*sum(w)/len(w) if w else 0
        fs=100*sum(1 for x,_,_ in ev if x is False)/len(ev)
        f=[x for _,x,_ in ev]
        print(f"  {nm:22s} n={len(ev):3d}  hit={hr:3.0f}%  false-start={fs:3.0f}%  "
              f"medFwd={statistics.median(f):+.2f}%  mean(raw, cost removed)={statistics.mean(f)-cost:+.2f}%")
    hl=",".join(iv for iv,_ in highers)
    print(f"\n[{coin} base {base_iv} {days}d ~{n}bars  H={H}  confluence vs {hl}]  DISCOVERY/in-sample")
    print(f"  DRIFT baseline {H}-bar: mean {statistics.mean(drift):+.2f}%")
    show("CONFLUENT (>=1 HTF)",confl); show("ISOLATED (lone line)",iso)
    # degree breakdown
    for d in (1,2,3):
        ev=[x for x in confl if x[2]==d]
        if len(ev)>=8:
            f=[x for _,x,_ in ev]; hr=100*sum(1 for x,_,_ in ev if x)/len([1 for x,_,_ in ev if x is not None])
            print(f"     deg={d}: n={len(ev):3d} hit={hr:3.0f}% mean(raw, cost removed)={statistics.mean(f)-cost:+.2f}%")

if __name__=="__main__":
    run("BTC","5m",17,48,[("15m",52),("1h",208),("4h",800)])
    run("BTC","15m",52,32,[("1h",208),("4h",800)])
    run("BTC","1h",208,24,[("4h",800),("1d",1500)])
