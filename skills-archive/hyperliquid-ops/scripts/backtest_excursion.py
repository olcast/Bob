#!/usr/bin/env python3
"""1h shallow-sweep -> reclaim, graded by EXCURSION (MFE/MAE/velocity) not fixed-time, + OOS regime split.
Per entry over the next 24h: MFE (max run up), MAE (max heat down), time-to-peak, velocity=MFE/hrs.
'Held' = MAE never worse than -0.3% (didn't go lower before the move). Expectancy = first-touch +0.5%/-0.3%, 5bp."""
import json,time,urllib.request,statistics
API="https://api.hyperliquid.xyz/info"
def fetch(iv,days):
    end=int(time.time()*1000);start=end-days*86400_000
    r=urllib.request.Request(API,data=json.dumps({"type":"candleSnapshot","req":{"coin":"BTC","interval":iv,"startTime":start,"endTime":end}}).encode(),headers={"Content-Type":"application/json"})
    return sorted(json.load(urllib.request.urlopen(r,timeout=60)),key=lambda k:k["t"])
cd=fetch("1h",208);O=[float(c["o"]) for c in cd];H=[float(c["h"]) for c in cd];L=[float(c["l"]) for c in cd];C=[float(c["c"]) for c in cd];n=len(cd)
W=24;Wm=24;SH=0.0024;ev=[];last=-999
for i in range(W+1,n-Wm-1):
    lvl=min(L[i-W:i])
    if not (L[i]<lvl and L[i-1]>=lvl) or i-last<12: continue
    if (lvl-L[i])/lvl>=SH: continue
    recl=next((j for j in range(i+1,min(i+13,n)) if C[j]>lvl),None)
    if recl is not None: ev.append(recl);last=i
def prof(idx):
    MFE=[];MAE=[];TT=[];VEL=[];EXP=[];held=p05=p10=0
    for e in idx:
        ent=C[e];hi=[(H[j]-ent)/ent*100 for j in range(e+1,min(e+1+Wm,n))];lo=[(L[j]-ent)/ent*100 for j in range(e+1,min(e+1+Wm,n))]
        if not hi: continue
        mfe=max(hi);t=hi.index(mfe)+1;mae=min(lo)
        MFE.append(mfe);MAE.append(mae);TT.append(t);VEL.append(mfe/t)
        held+=mae>-0.3;p05+=mfe>=0.5;p10+=mfe>=1.0
        r=None
        for j in range(e+1,min(e+1+Wm,n)):
            if L[j]<=ent*0.997: r=-0.3;break
            if H[j]>=ent*1.005: r=0.5;break
        EXP.append((r if r is not None else (C[min(e+Wm,n-1)]/ent-1)*100)-0.05)
    k=len(MFE)
    return k,statistics.median(MFE),statistics.median(MAE),statistics.median(TT),statistics.median(VEL),100*held/k,100*p05/k,100*p10/k,statistics.mean(EXP)
mid=n//2
print(f"1h shallow-sweep->reclaim | {n} bars/208d | n_events={len(ev)}  (excursion over next 24h)")
for nm,idx in [("FULL",ev),("TRAIN 1st-half",[e for e in ev if e<mid]),("TEST 2nd-half (OOS)",[e for e in ev if e>=mid])]:
    k,mfe,mae,tt,vel,held,p05,p10,exp=prof(idx)
    print(f"\n  {nm}  n={k}")
    print(f"    median MFE (run up)   {mfe:+.2f}%      median MAE (heat)  {mae:+.2f}%")
    print(f"    median time-to-peak   {tt:.0f}h        median velocity    {vel:.3f}%/h")
    print(f"    held (MAE>-0.3%)      {held:.0f}%        reached +0.5% {p05:.0f}%   +1.0% {p10:.0f}%")
    print(f"    expectancy +0.5/-0.3/5bp = {exp:+.3f}%/trade")
