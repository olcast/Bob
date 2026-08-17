#!/usr/bin/env python3
"""MARKET-STRUCTURE TEST (OLIVIER model: 'BTC is a leverage washing machine — ranges until it
trends, comes back for it after, and kills faraway leverage via funding while trending'). BTC ONLY.
Three measurable claims:
 (1) RANGES UNTIL IT TRENDS  -> variance ratio VR(q): <1 mean-reverting (range), ~/>1 trending.
 (2) COMES BACK FOR IT       -> after a trend leg (>thr over k bars), median retracement over next m.
 (3) KILLS FARAWAY LEVERAGE VIA FUNDING -> during strong trends, is funding extreme AND aligned with
     the trend (crowd chasing, paying to hold) = the slow bleed? (180d paginated fundingHistory.)
Descriptive structure, not a trade. No look-ahead in the claims (VR & funding-bin are contemporaneous
descriptors; retracement is forward but purely observational)."""
import json,time,urllib.request,statistics,math,bisect
API="https://api.hyperliquid.xyz/info"
def post(b,tries=3):
    for a in range(tries):
        try:
            r=urllib.request.Request(API,data=json.dumps(b).encode(),headers={"Content-Type":"application/json"})
            return json.load(urllib.request.urlopen(r,timeout=60))
        except Exception:
            if a==tries-1:return None
            time.sleep(0.5)
def candles(iv,days):
    step={'1h':3600000,'4h':14400000}[iv];end=int(time.time()*1000);cur=end-days*86400_000;seen={}
    while cur<end:
        d=post({"type":"candleSnapshot","req":{"coin":"BTC","interval":iv,"startTime":cur,"endTime":min(cur+4800*step,end)}}) or []
        if not d:cur+=4800*step;continue
        for c in d:seen[c['t']]=c
        cur=max(c['t'] for c in d)+step
    return [seen[t] for t in sorted(seen)]
def funding(days):
    end=int(time.time()*1000);cur=end-days*86400_000;seen={}
    while cur<end:
        d=post({"type":"fundingHistory","coin":"BTC","startTime":cur,"endTime":min(cur+19*86400_000,end)}) or []
        if not d:cur+=19*86400_000;continue
        for r in d:seen[r['time']]=r
        nt=max(r['time'] for r in d)
        if nt<=cur:break
        cur=nt+1
    return [seen[t] for t in sorted(seen)]

def variance_ratio(C,qs):
    r=[math.log(C[i]/C[i-1]) for i in range(1,len(C))]
    v1=statistics.pvariance(r); out={}
    for q in qs:
        rq=[sum(r[i:i+q]) for i in range(0,len(r)-q+1)]
        out[q]=(statistics.pvariance(rq)/q)/v1 if v1>0 else float('nan')
    return out

def retracement(C,k,thr,m):
    # trend leg = |k-bar return| > thr ending at i; retrace = adverse move over next m / leg size
    up=[];dn=[]
    n=len(C);i=k
    while i<n-m:
        R=C[i]/C[i-k]-1
        if abs(R)>=thr:
            fwd=C[i+1:i+1+m]
            if R>0:  # up-leg; retrace = how far back down
                adverse=(C[i]-min(fwd))/ (C[i]-C[i-k])
                up.append(max(0.0,adverse))
            else:
                adverse=(max(fwd)-C[i])/ (C[i-k]-C[i])
                dn.append(max(0.0,adverse))
            i+=m//2
        else: i+=1
    return up,dn

def funding_by_trend(C,T,fh,win=24):
    fr=[None]*len(C)
    for r in fh:
        j=bisect.bisect_right(T,int(r["time"]))-1
        if 0<=j<len(C): fr[j]=float(r["fundingRate"])
    last=None
    for i in range(len(C)):
        if fr[i] is None: fr[i]=last
        else: last=fr[i]
    rows=[]
    for i in range(win,len(C)):
        if fr[i] is None: continue
        trend=C[i]/C[i-win]-1                      # trailing directional move
        aligned=fr[i]*(1 if trend>0 else -1)       # funding paying the trend side? (crowd chasing)
        rows.append((abs(trend),fr[i],aligned))
    rows.sort()
    # quintiles by |trend|
    qn=len(rows)//5
    print("  |trailing 24-bar move| quintile -> mean funding/hr, mean trend-aligned funding, mean |funding|")
    for k in range(5):
        seg=rows[k*qn:(k+1)*qn] if k<4 else rows[4*qn:]
        mt=statistics.mean(x[0] for x in seg)*100
        mf=statistics.mean(x[1] for x in seg)
        ma=statistics.mean(x[2] for x in seg)
        mabs=statistics.mean(abs(x[1]) for x in seg)
        print(f"    Q{k+1} |move|~{mt:5.2f}%  funding {mf:+.3e}  aligned {ma:+.3e}  |funding| {mabs:.3e}")

if __name__=="__main__":
    print("===== (1) RANGES UNTIL IT TRENDS — variance ratio VR(q) (<1 range/mean-revert, >1 trend) =====")
    for iv,days in [("1h",208),("4h",800)]:
        C=[float(c["c"]) for c in candles(iv,days)]
        vr=variance_ratio(C,[2,4,8,16,24,48])
        print(f"  BTC {iv} {days}d (~{len(C)} bars): " + "  ".join(f"VR{q}={vr[q]:.2f}" for q in [2,4,8,16,24,48]))
    print("\n===== (2) COMES BACK FOR IT — median retracement of a trend leg over the next window =====")
    for iv,days,k,thr,m in [("1h",208,24,0.03,24),("1h",208,12,0.02,12),("4h",800,12,0.06,12)]:
        C=[float(c["c"]) for c in candles(iv,days)]
        up,dn=retracement(C,k,thr,m)
        mu=statistics.median(up) if up else float('nan'); md=statistics.median(dn) if dn else float('nan')
        print(f"  {iv} leg>{thr*100:.0f}% over {k} bars, look {m} fwd: up-legs n={len(up)} med retrace {mu*100:.0f}% | down-legs n={len(dn)} med retrace {md*100:.0f}%")
    print("\n===== (3) KILLS FARAWAY LEVERAGE VIA FUNDING — funding vs trend strength (1h, 180d) =====")
    cd=candles("1h",180); C=[float(c["c"]) for c in cd]; T=[int(c["t"]) for c in cd]
    funding_by_trend(C,T,funding(180),win=24)
