#!/usr/bin/env python3
"""Cost/timeframe sweep at Olivier's real params (target +0.5% / stop -0.3% / COST REMOVED).
Re-tests the reclaim family (impulsive/quiet, post-impulse/flat) + RSI-divergence-at-low across
5m/15m/30m/1h, each vs its OWN random-entry control using identical trade management. Walk-forward,
own-lines (structure.py logic; pivots known only at p+k). ~6h refractory (H/4). DISCOVERY/in-sample;
window differs per TF (5m~17d ... 1h~208d) — note regime coverage. Needs blind/OOS before any weight."""
import json,time,urllib.request,statistics,random
random.seed(42)
API="https://api.hyperliquid.xyz/info"
TFMS={'1m':60000,'5m':300000,'15m':900000,'30m':1800000,'1h':3600000}
def fetch(iv,days):
    end=int(time.time()*1000);step=TFMS[iv];cursor=end-days*86400_000;seen={}
    while cursor<end:
        ce=min(cursor+4800*step,end)
        r=urllib.request.Request(API,data=json.dumps({"type":"candleSnapshot","req":{"coin":"BTC","interval":iv,"startTime":cursor,"endTime":ce}}).encode(),headers={"Content-Type":"application/json"})
        try: data=json.load(urllib.request.urlopen(r,timeout=60))
        except Exception: data=[]
        if not data: cursor=ce+step; continue
        for c in data: seen[c['t']]=c
        cursor=max(c['t'] for c in data)+step
    return [seen[t] for t in sorted(seen)]
def atr(H,L,C,n=14):
    tr=[H[0]-L[0]]
    for i in range(1,len(C)): tr.append(max(H[i]-L[i],abs(H[i]-C[i-1]),abs(L[i]-C[i-1])))
    out=[None]*len(C);s=sum(tr[:n])/n
    for i in range(len(C)): out[i]=sum(tr[:i+1])/(i+1) if i<n else (s:=(s*(n-1)+tr[i])/n)
    return out
def fr_high(H,k):return [i for i in range(k,len(H)-k) if H[i]==max(H[i-k:i+k+1])]
def fr_low(L,k):return [i for i in range(k,len(L)-k) if L[i]==min(L[i-k:i+k+1])]
def rsi(C,n=14):
    g=[0.0]*len(C);l=[0.0]*len(C)
    for i in range(1,len(C)):
        d=C[i]-C[i-1];g[i]=max(d,0.0);l[i]=max(-d,0.0)
    out=[None]*len(C)
    if len(C)<=n: return out
    ag=sum(g[1:n+1])/n;al=sum(l[1:n+1])/n
    for i in range(n,len(C)):
        if i>n: ag=(ag*(n-1)+g[i])/n;al=(al*(n-1)+l[i])/n
        out[i]=100-100/(1+(ag/al if al>0 else 999))
    return out
def run(iv,days,H,TGT=0.005,STOP=0.003,COST=0.0,k=3,L=20):  # COST=0.0 (Olivier 2026-08-18: measure signal, not friction)
    cd=fetch(iv,days)
    O=[float(c["o"]) for c in cd];Hi=[float(c["h"]) for c in cd];Lo=[float(c["l"]) for c in cd];C=[float(c["c"]) for c in cd]
    n=len(C);A=atr(Hi,Lo,C);RS=rsi(C);REF=max(3,H//4)
    conf=sorted([(p,p+k) for p in fr_high(Hi,k)],key=lambda x:x[1]);mc=[None]*n;cf=[];cp=0
    for i in range(n):
        while cp<len(conf) and conf[cp][1]<=i: cf.append(conf[cp][0]);cp+=1
        if len(cf)>=2:
            p1,p2=cf[-2],cf[-1]
            if Hi[p2]<Hi[p1] and p2<i: m=(Hi[p2]-Hi[p1])/(p2-p1);mc[i]=(m,Hi[p1]-m*p1)
    def trade(i):
        e=C[i];tp=e*(1+TGT);sl=e*(1-STOP)
        for f in range(i+1,min(i+1+H,n)):
            if Lo[f]<=sl: return -STOP*100,False
            if Hi[f]>=tp: return TGT*100,True
        return (C[min(i+H,n-1)]/e-1)*100,None
    B={"reclaim impulsive":[],"reclaim quiet":[],"reclaim post-impulse":[],"reclaim flat":[],"RSI-div at low":[]}
    last=-10**9
    for i in range(L+5,n-2):
        if mc[i] is None: continue
        m,c0=mc[i];Li=m*i+c0;Lp=m*(i-1)+c0
        if not (C[i-1]<=Lp and C[i]>Li) or i-last<REF: continue
        net,hit=trade(i);net-=COST
        B["reclaim impulsive" if (C[i]-O[i])>0.5*(A[i] or (Hi[i]-Lo[i])) else "reclaim quiet"].append((net,hit))
        sl_i=min(range(i-L,i),key=lambda x:Lo[x]);shelf=Lo[sl_i]
        impulse=(C[i]-shelf)/shelf>=0.008 and any((C[j]-O[j])>1.2*A[j] for j in range(sl_i,i+1))
        B["reclaim post-impulse" if impulse else "reclaim flat"].append((net,hit));last=i
    fl=fr_low(Lo,k);ld=-10**9
    for a in range(1,len(fl)):
        p,q=fl[a-1],fl[a];e=q+k
        if e>=n-2 or RS[p] is None or RS[q] is None: continue
        if Lo[q]<Lo[p] and RS[q]>RS[p]+2 and e-ld>=REF:
            net,hit=trade(e);B["RSI-div at low"].append((net-COST,hit));ld=e
    ctrl=[]
    for _ in range(1500):
        i=random.randint(L+5,n-2);net,hit=trade(i);ctrl.append((net-COST,hit))
    def st(ev):return len(ev),100*sum(1 for _,h in ev if h)/len(ev),statistics.mean(x for x,_ in ev)
    cn,ch,cm=st(ctrl)
    print(f"\n[BTC {iv}  {days}d (~{n} bars)  +0.5%/-0.3%/cost-removed  H={H}({H*({'1m':1,'5m':5,'15m':15,'30m':30,'1h':60}[iv])//60}h)]")
    print(f"  {'RANDOM control':26s} n={cn:4d} hit={ch:3.0f}% net={cm:+.3f}%")
    for name,ev in B.items():
        if len(ev)<10: print(f"  {name:26s} n={len(ev):4d}  (too few)");continue
        nn,hh,mm=st(ev);d=mm-cm
        print(f"  {name:26s} n={nn:4d} hit={hh:3.0f}% net={mm:+.3f}%  vs random {d:+.3f}%{'  <— beats' if d>0.02 else ''}")
for iv,days,H in [("1m",45,360),("5m",45,72),("15m",45,24),("30m",45,12),("1h",45,6)]:
    run(iv,days,H)
