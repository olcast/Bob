#!/usr/bin/env python3
"""Early-vs-strict DESCENDING-trendline reclaim backtest, walk-forward, own-lines.
Lines identified algorithmically (structure.py logic): last two CONFIRMED descending
pivot highs (a pivot at p is only 'known' at p+k -> no look-ahead). A reclaim = close
crosses above that line. EARLY = reclaim on an impulsive candle (vol>1.5x med or body>0.5 ATR),
enter at reclaim close. STRICT = price holds above the line for 2 more bars, enter at bar i+2.
Both measured to a +0.8% target vs a reclaim-fail stop (line -0.2%) over H bars, and by raw
forward-H return after a 25bp round-trip cost, vs the unconditional drift baseline.
DISCOVERY / in-sample, single venue+asset -> needs blind + regime-split validation (R4/A5/A6)
before ANY live weight."""
import json, time, urllib.request, statistics, sys
API="https://api.hyperliquid.xyz/info"

def fetch(coin, interval, days):
    end=int(time.time()*1000); start=end-days*86400_000
    r=urllib.request.Request(API,data=json.dumps({"type":"candleSnapshot","req":{"coin":coin,"interval":interval,"startTime":start,"endTime":end}}).encode(),headers={"Content-Type":"application/json"})
    return sorted(json.load(urllib.request.urlopen(r,timeout=60)),key=lambda k:k["t"])

def rolling_atr(H,L,C,n=14):
    tr=[H[0]-L[0]]
    for i in range(1,len(C)):
        tr.append(max(H[i]-L[i],abs(H[i]-C[i-1]),abs(L[i]-C[i-1])))
    out=[None]*len(C); s=sum(tr[:n])/n
    for i in range(len(C)):
        out[i]=sum(tr[:i+1])/(i+1) if i<n else (s:=(s*(n-1)+tr[i])/n)
    return out

def pivot_highs(H,k):
    return [i for i in range(k,len(H)-k) if H[i]==max(H[i-k:i+k+1])]

def backtest(coin, interval, days, H, k=3, cost=0.0025):
    cd=fetch(coin,interval,days)
    O=[float(c["o"]) for c in cd]; Hi=[float(c["h"]) for c in cd]
    Lo=[float(c["l"]) for c in cd]; C=[float(c["c"]) for c in cd]; V=[float(c["v"]) for c in cd]
    n=len(C); A=rolling_atr(Hi,Lo,C)
    conf=[(p,p+k) for p in pivot_highs(Hi,k)]
    early=[]; strict=[]; last=-10**9
    # unconditional drift baseline over same horizon
    base=[(C[i+H]-C[i])/C[i]*100 for i in range(k+30,n-H)]
    i=k+30
    while i < n-H-3:
        avail=[p for (p,ci) in conf if ci<=i and p<i]
        if len(avail)<2: i+=1; continue
        p1,p2=avail[-2],avail[-1]
        if Hi[p2]>=Hi[p1]: i+=1; continue            # need a descending (lower) high
        m=(Hi[p2]-Hi[p1])/(p2-p1); c0=Hi[p1]-m*p1
        Li=m*i+c0; Lim1=m*(i-1)+c0
        if not (C[i-1]<=Lim1 and C[i]>Li): i+=1; continue   # fresh cross above from below
        if i-last<H: i+=1; continue                          # refractory: don't recount a move
        atr=A[i] or (Hi[i]-Lo[i]); vmed=statistics.median(V[max(0,i-20):i]) or 1e-9
        # EARLY
        if (V[i]>1.5*vmed) or ((C[i]-O[i])>0.5*atr):
            e=C[i]; stop=Li-0.002*e; tgt=e*1.008; win=None
            for f in range(i+1,i+1+H):
                if Lo[f]<=stop: win=False; break
                if Hi[f]>=tgt: win=True; break
            if win is None: win=C[i+H]>e
            early.append((win,(C[i+H]-e)/e*100)); last=i
        # STRICT (hold above line 2 bars, enter i+2)
        if C[i]>Li and C[i+1]>m*(i+1)+c0 and C[i+2]>m*(i+2)+c0:
            e2=i+2; e=C[e2]; L2=m*e2+c0; stop=L2-0.002*e; tgt=e*1.008; win=None
            end=min(e2+H,n-1)
            for f in range(e2+1,end+1):
                if Lo[f]<=stop: win=False; break
                if Hi[f]>=tgt: win=True; break
            if win is None: win=C[end]>e
            strict.append((win,(C[end]-e)/e*100)); last=max(last,i)
        i+=1
    def show(name,ev):
        if not ev: print(f"  {name:6s} 0 events"); return
        w=[x for x,_ in ev if x is not None]
        hr=100*sum(w)/len(w) if w else 0
        fs=100*sum(1 for x,_ in ev if x is False)/len(ev)
        fwd=[f for _,f in ev]; net=statistics.mean(fwd)-cost*100
        print(f"  {name:6s} n={len(ev):3d}  hit={hr:3.0f}%  false-start={fs:3.0f}%  "
              f"medFwd={statistics.median(fwd):+.2f}%  meanFwd(after25bp)={net:+.2f}%")
    print(f"\n[{coin} {interval} {days}d ~{n}bars H={H}]  DISCOVERY/in-sample")
    print(f"  BASELINE unconditional {H}-bar drift: mean {statistics.mean(base):+.2f}%  median {statistics.median(base):+.2f}%")
    show("EARLY",early); show("STRICT",strict)

if __name__=="__main__":
    backtest("BTC","1h",208,24)
    backtest("BTC","4h",800,18)
