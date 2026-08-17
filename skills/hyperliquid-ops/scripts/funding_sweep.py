#!/usr/bin/env python3
"""DISCOVERY — HL-specific POSITIONING family, BTC ONLY (never pooled). Tests whether funding /
premium EXTREMES carry a fade edge (crowded longs paying -> short; crowded shorts paying -> long)
— the family most likely to be DECORRELATED from price-pattern signals, and the reason HL's
transparency ('the mine') might matter. Data: fundingHistory (paginated; endpoint caps 500 rows
~21d per call) aligned to 1h candles. Excursion-graded, +0.5%/-0.3%/5bp, vs matched random control,
OOS split, trial-counted. DISCOVERY/in-sample — nothing admitted without blind/regime/proper-score."""
import json,time,urllib.request,statistics,random
random.seed(11)
API="https://api.hyperliquid.xyz/info"
def post(b):
    r=urllib.request.Request(API,data=json.dumps(b).encode(),headers={"Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(r,timeout=60))

def funding(coin,days):
    end=int(time.time()*1000); cur=end-days*86400_000; seen={}
    while cur<end:
        d=post({"type":"fundingHistory","coin":coin,"startTime":cur,"endTime":min(cur+19*86400_000,end)})
        if not d: cur+=19*86400_000; continue
        for r in d: seen[r['time']]=r
        nt=max(r['time'] for r in d)
        if nt<=cur: break
        cur=nt+1
    return [seen[t] for t in sorted(seen)]

def candles(coin,iv,days):
    end=int(time.time()*1000); step=3600000; cur=end-days*86400_000; seen={}
    while cur<end:
        d=post({"type":"candleSnapshot","req":{"coin":coin,"interval":iv,"startTime":cur,"endTime":min(cur+4800*step,end)}})
        if not d: cur+=4800*step; continue
        for c in d: seen[c['t']]=c
        cur=max(c['t'] for c in d)+step
    return [seen[t] for t in sorted(seen)]

def grade(dr,i,O,H,L,C,n,HOR,TGT=0.005,STOP=0.003,COST=0.0005):
    e=C[i];mfe=0.0;mae=0.0
    if dr>0:
        tp=e*(1+TGT);sl=e*(1-STOP)
        for f in range(i+1,min(i+1+HOR,n)):
            mfe=max(mfe,(H[f]-e)/e);mae=min(mae,(L[f]-e)/e)
            if L[f]<=sl: return (-STOP-COST)*100,False,mfe*100,mae*100
            if H[f]>=tp: return (TGT-COST)*100,True,mfe*100,mae*100
        return ((C[min(i+HOR,n-1)]/e-1)-COST)*100,None,mfe*100,mae*100
    else:
        tp=e*(1-TGT);sl=e*(1+STOP)
        for f in range(i+1,min(i+1+HOR,n)):
            mfe=max(mfe,(e-L[f])/e);mae=min(mae,(e-H[f])/e)
            if H[f]>=sl: return (-STOP-COST)*100,False,mfe*100,mae*100
            if L[f]<=tp: return (TGT-COST)*100,True,mfe*100,mae*100
        return ((e/C[min(i+HOR,n-1)]-1)-COST)*100,None,mfe*100,mae*100

def st(ev):
    if not ev: return (0,0,0,0)
    net=[x[0] for x in ev];mfe=[x[2] for x in ev]
    reach=100*sum(1 for m in mfe if m>=0.5)/len(mfe)
    return len(ev),statistics.mean(net),statistics.median(mfe),reach

def run(coin="BTC",days=180,HOR=24,W=168,Q=0.9):
    fh=funding(coin,days); cd=candles(coin,"1h",days)
    T=[int(c["t"]) for c in cd];O=[float(c["o"]) for c in cd];H=[float(c["h"]) for c in cd]
    L=[float(c["l"]) for c in cd];C=[float(c["c"]) for c in cd];n=len(C)
    # align funding to candle index (nearest prior candle)
    fr=[None]*n; pr=[None]*n; import bisect
    for r in fh:
        k=bisect.bisect_right(T,int(r["time"]))-1
        if 0<=k<n: fr[k]=float(r["fundingRate"]); pr[k]=float(r["premium"])
    # forward-fill
    lastf=None;lastp=None
    for i in range(n):
        if fr[i] is None: fr[i]=lastf; pr[i]=lastp
        else: lastf=fr[i];lastp=pr[i]
    span=round((T[-1]-T[0])/86400000)
    print(f"\n===== {coin} 1h · funding history {len(fh)} pts, aligned {span}d · +0.5%/-0.3%/5bp · HOR={HOR} · DISCOVERY =====")
    print(f"  funding stats: median={statistics.median([x for x in fr if x is not None]):.2e}  "
          f"p10/p90 over data — extremes are the test")
    def rolling_q(x,i,w,q):
        s=[v for v in x[max(0,i-w):i] if v is not None]
        if len(s)<w//2: return None,None
        s=sorted(s); return s[int(0.1*len(s))], s[int(0.9*len(s))]
    tests={}
    ef=[];  # funding-extreme fade
    for i in range(W,n-1):
        if fr[i] is None: continue
        lo,hi=rolling_q(fr,i,W,Q)
        if lo is None: continue
        if fr[i]>=hi: ef.append((i,-1))      # crowded longs paying -> fade short
        elif fr[i]<=lo: ef.append((i,1))     # crowded shorts paying -> fade long
    tests["funding-extreme FADE"]=ef
    ep=[]  # premium-extreme fade
    for i in range(W,n-1):
        if pr[i] is None: continue
        lo,hi=rolling_q(pr,i,W,Q)
        if lo is None: continue
        if pr[i]>=hi: ep.append((i,-1))
        elif pr[i]<=lo: ep.append((i,1))
    tests["premium-extreme FADE"]=ep
    # also test the CONTINUATION side (funding-extreme = trend confirmation, don't fade)
    tests["funding-extreme FOLLOW"]=[(i,-d) for i,d in ef]
    trials=0;surv=[]
    print(f"  {'signal':26s} {'n':>4} {'net%':>7} {'medMFE':>7} {'reach.5':>7} {'vsRAND':>7} {'OOStr/te':>14}")
    for name,evs in tests.items():
        trials+=1
        if len(evs)<20: print(f"  {name:26s} {len(evs):>4}  (too few — BTC funding rarely extreme)"); continue
        # refractory HOR/2
        keep=[];last=-10**9
        for i,d in sorted(evs):
            if i-last>=HOR//2: keep.append((i,d));last=i
        ev=[grade(d,i,O,H,L,C,n,HOR) for i,d in keep]
        ctrl=[grade(d,random.randint(1,n-2),O,H,L,C,n,HOR) for _,d in keep]
        nn,net,mfe,reach=st(ev); _,cnet,_,_=st(ctrl)
        h=len(ev)//2; tr=statistics.mean(x[0] for x in ev[:h]); te=statistics.mean(x[0] for x in ev[h:])
        edge=net-cnet; flag=""
        if net>0.02 and edge>0.03 and tr>0 and te>0 and nn>=30: flag="  <-- SURVIVES(disc)"; surv.append((name,nn,net,edge))
        print(f"  {name:26s} {nn:>4} {net:>+7.3f} {mfe:>+7.2f} {reach:>7.0f} {edge:>+7.3f} {tr:>+6.2f}/{te:>+6.2f}{flag}")
    return trials,surv

if __name__=="__main__":
    t,s=run("BTC",days=180)
    print(f"\n  positioning-family trials (BTC only) = {t}")
    print("  SURVIVORS:", s if s else "none (funding-extreme fade/follow shows no cost-surviving edge on BTC)")
