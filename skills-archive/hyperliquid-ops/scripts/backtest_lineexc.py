#!/usr/bin/env python3
"""Line-relative EXCURSION backtest (Olivier's framing): the trendline is the reference.
For each fresh reclaim of a descending resistance line, measure how far ABOVE price runs
(from the reclaim close) before it REVERSES = closes back below the line (round-trip) or H.
Symmetric for breakdowns of an ascending support line: how far BELOW before it reverses
back above. Report the excursion distribution up vs down + the asymmetry, plus fraction that
reach the +0.5% tradeable target, walk-forward, own-lines (no look-ahead: a pivot at p is
known only at p+k), OOS train/test split. DISCOVERY/in-sample -> needs blind before weight."""
import json, time, urllib.request, statistics
API="https://api.hyperliquid.xyz/info"

def fetch(coin, iv, days):
    end=int(time.time()*1000); start=end-days*86400_000
    r=urllib.request.Request(API,data=json.dumps({"type":"candleSnapshot","req":{"coin":coin,"interval":iv,"startTime":start,"endTime":end}}).encode(),headers={"Content-Type":"application/json"})
    return sorted(json.load(urllib.request.urlopen(r,timeout=60)),key=lambda k:k["t"])

def piv_h(H,k): return [i for i in range(k,len(H)-k) if H[i]==max(H[i-k:i+k+1])]
def piv_l(L,k): return [i for i in range(k,len(L)-k) if L[i]==min(L[i-k:i+k+1])]

def lines(vals, piv, k, want_desc):
    """mc[i] = (m,c0) of the line through the last two CONFIRMED pivots, only if it has the
    wanted slope sign (descending for resistance / ascending for support)."""
    n=len(vals); conf=sorted([(p,p+k) for p in piv],key=lambda x:x[1])
    mc=[None]*n; got=[]; cp=0
    for i in range(n):
        while cp<len(conf) and conf[cp][1]<=i: got.append(conf[cp][0]); cp+=1
        if len(got)>=2:
            p1,p2=got[-2],got[-1]
            if p2<i:
                desc=vals[p2]<vals[p1]
                if desc==want_desc:
                    m=(vals[p2]-vals[p1])/(p2-p1); mc[i]=(m,vals[p1]-m*p1)
    return mc

def pct_stats(xs):
    xs=sorted(xs); n=len(xs)
    q=lambda p: xs[min(n-1,int(p*n))]
    return statistics.median(xs), q(0.25), q(0.75)

def run(coin, iv, days, H, k=3, TGT=0.005):
    cd=fetch(coin,iv,days)
    O=[float(c["o"]) for c in cd]; Hi=[float(c["h"]) for c in cd]
    Lo=[float(c["l"]) for c in cd]; C=[float(c["c"]) for c in cd]; n=len(C)
    res=lines(Hi,piv_h(Hi,k),k,True)     # descending resistance
    sup=lines(Lo,piv_l(Lo,k),k,False)    # ascending support
    REF=max(3,H//4)

    up=[]; last=-10**9                    # reclaim excursions
    for i in range(k+5,n-2):
        if res[i] is None: continue
        m,c0=res[i]; Li=m*i+c0; Lp=m*(i-1)+c0
        if not (C[i-1]<=Lp and C[i]>Li) or i-last<REF: continue
        e=C[i]; peak=0.0; mae=0.0; end=None
        for f in range(i+1,min(i+1+H,n)):
            peak=max(peak,(Hi[f]-e)/e); mae=min(mae,(Lo[f]-e)/e)
            if C[f] < m*f+c0: end=f; break        # closed back below line = reversal
        up.append((peak*100, mae*100, (end-i if end else H), end is not None)); last=i

    dn=[]; last=-10**9                    # breakdown excursions
    for i in range(k+5,n-2):
        if sup[i] is None: continue
        m,c0=sup[i]; Si=m*i+c0; Sp=m*(i-1)+c0
        if not (C[i-1]>=Sp and C[i]<Si) or i-last<REF: continue
        e=C[i]; peak=0.0; mfe=0.0; end=None
        for f in range(i+1,min(i+1+H,n)):
            peak=max(peak,(e-Lo[f])/e); mfe=max(mfe,(Hi[f]-e)/e)
            if C[f] > m*f+c0: end=f; break        # closed back above line = reversal
        dn.append((peak*100, mfe*100, (end-i if end else H), end is not None)); last=i

    def rep(tag,ev,col):
        if len(ev)<8: print(f"  {tag:26s} n={len(ev):3d} (too few)"); return
        pk=[x[col] for x in ev]; med,q1,q3=pct_stats(pk)
        hit=100*sum(1 for x in ev if x[col]>=TGT*100)/len(ev)
        rt=100*sum(1 for x in ev if x[3])/len(ev)
        tt=statistics.median([x[2] for x in ev])
        print(f"  {tag:26s} n={len(ev):3d}  medExc={med:+.2f}%  [q1 {q1:+.2f} / q3 {q3:+.2f}]  "
              f"reach±0.5%={hit:3.0f}%  round-trip={rt:3.0f}%  medBars={tt:.0f}")

    def oos(ev,col):
        if len(ev)<16: return "n/a"
        h=len(ev)//2
        return f"train {statistics.median([x[col] for x in ev[:h]]):+.2f}% / test {statistics.median([x[col] for x in ev[h:]]):+.2f}%"

    per={"1m":1,"5m":5,"15m":15,"30m":30,"1h":60,"4h":240}[iv]
    print(f"\n[{coin} {iv} {days}d ~{n}bars  H={H}({H*per//60}h)]  line-relative excursion  DISCOVERY/in-sample")
    rep("UP  reclaim→peak-above", up, 0)
    print(f"       OOS med peak-above:  {oos(up,0)}")
    rep("DOWN breakdown→peak-below", dn, 0)
    print(f"       OOS med peak-below:  {oos(dn,0)}")
    if up and dn:
        mu=statistics.median([x[0] for x in up]); md=statistics.median([x[0] for x in dn])
        print(f"  ASYMMETRY med(up {mu:+.2f}%) vs med(down {md:+.2f}%) -> "
              f"{'UP excursions bigger' if mu>md else 'DOWN excursions bigger'} "
              f"(ratio {mu/md:.2f})" if md else "")

if __name__=="__main__":
    for iv,days,H in [("15m",52,32),("1h",208,24),("4h",800,18)]:
        run("BTC",iv,days,H)
