#!/usr/bin/env python3
"""NO-RULES DISCOVERY — pure predictive content, BTC ONLY. NO stop, NO cost, NO fixed bracket
(a stop is what INVALIDATES a pattern that would have worked; costs are the trader's business).
For each signal we measure where price actually GOES afterwards, unhindered:
  · directional forward return d·(C[i+h]/C[i]−1) at horizons h  (IC-style: does it predict direction?)
  · median favorable excursion (MFE) vs adverse (MAE) in the signal's direction  (is the path biased?)
  · P(favorable move ≥ 0.5% / ≥ 1.0%)
…each vs a MATCHED random-entry control (same direction mix). The control is NOT a rule that can
invalidate — it is the DEFINITION of 'is there information': a pattern exists iff its forward
distribution differs from random's. Cost/stop-free, so it can only be beaten by real predictive
content, never hidden by a bracket. OOS split. Runs 5m/15m/1h/4h (the 5–15m frame included).
Nothing here is a trade — execution (entry, sizing, exit) is a separate, later, trader-owned layer."""
import json,time,urllib.request,statistics,random
random.seed(5)
API="https://api.hyperliquid.xyz/info"; TFMS={'5m':300000,'15m':900000,'1h':3600000,'4h':14400000}
def fetch(iv,days):
    end=int(time.time()*1000);step=TFMS[iv];cur=end-int(days*86400_000);seen={}
    while cur<end:
        ce=min(cur+4800*step,end)
        r=urllib.request.Request(API,data=json.dumps({"type":"candleSnapshot","req":{"coin":"BTC","interval":iv,"startTime":cur,"endTime":ce}}).encode(),headers={"Content-Type":"application/json"})
        try:d=json.load(urllib.request.urlopen(r,timeout=60))
        except Exception:d=[]
        if not d:cur=ce+step;continue
        for c in d:seen[c['t']]=c
        cur=max(c['t'] for c in d)+step
    return [seen[t] for t in sorted(seen)]
def atr(H,L,C,n=14):
    tr=[H[0]-L[0]]
    for i in range(1,len(C)):tr.append(max(H[i]-L[i],abs(H[i]-C[i-1]),abs(L[i]-C[i-1])))
    o=[None]*len(C);s=sum(tr[:n])/n if len(C)>=n else tr[0]
    for i in range(len(C)):o[i]=sum(tr[:i+1])/(i+1) if i<n else (s:=(s*(n-1)+tr[i])/n)
    return o
def sma(x,n):
    o=[None]*len(x);s=0.0
    for i in range(len(x)):
        s+=x[i]
        if i>=n:s-=x[i-n]
        if i>=n-1:o[i]=s/n
    return o
def pl(L,k):return [i for i in range(k,len(L)-k) if L[i]==min(L[i-k:i+k+1])]
def ph(H,k):return [i for i in range(k,len(H)-k) if H[i]==max(H[i-k:i+k+1])]

def gen(O,H,L,C,V,n,A,REF):
    S=sma(C,20);D=[None]*n
    for i in range(19,n):
        w=C[i-19:i+1];m=sum(w)/20;D[i]=(sum((v-m)**2 for v in w)/20)**0.5
    out={}
    def rf(e):
        k=[];last=-10**9
        for i,d in sorted(e):
            if i-last>=REF:k.append((i,d));last=i
        return k
    e=[]
    for i in range(20,n-1):
        if D[i]:
            z=(C[i]-S[i])/D[i]
            if z>2:e.append((i,-1))
            elif z<-2:e.append((i,1))
    out["MR overext z>2 (fade)"]=rf(e)
    e=[]
    for i in range(5,n-1):
        if all(C[j]>C[j-1] for j in range(i-3,i+1)):e.append((i,-1))
        elif all(C[j]<C[j-1] for j in range(i-3,i+1)):e.append((i,1))
    out["MR 4-consec (fade)"]=rf(e)
    e=[]
    for i in range(21,n-1):
        if C[i]>max(H[i-20:i]):e.append((i,1))
        elif C[i]<min(L[i-20:i]):e.append((i,-1))
    out["MOM Donchian20 break"]=rf(e)
    ef=[];ed=[]
    for i in range(15,n-1):
        if A[i-1] and (H[i-1]-L[i-1])>2*A[i-1]:
            d=1 if C[i-1]>O[i-1] else -1;ef.append((i,d));ed.append((i,-d))
    out["large-range FOLLOW"]=rf(ef);out["large-range FADE"]=rf(ed)
    ef=[];ed=[]
    for i in range(21,n-1):
        vm=statistics.median(V[i-20:i]) or 1e-9
        if V[i-1]>3*vm:
            d=1 if C[i-1]>O[i-1] else -1;ef.append((i,d));ed.append((i,-d))
    out["vol-spike CONT"]=rf(ef);out["vol-spike FADE"]=rf(ed)
    # shallow-sweep -> reclaim (long) : the live thesis
    e=[];used=-10**9
    for p in pl(L,3):
        c=p+3;Lv=L[p]
        for i in range(c,min(c+40,n-1)):
            if L[i]<Lv and L[i]>=Lv*(1-0.0024) and C[i]>Lv:
                if i-used>=REF:e.append((i,1));used=i
                break
            if C[i]<Lv*(1-0.0024):break
    out["shallow-sweep->reclaim (long)"]=rf(e)
    return out

def fstats(evs,O,H,L,C,n,HOR,HS):
    rets={h:[] for h in HS};mfe=[];mae=[];r05=0;r10=0
    for i,d in evs:
        for h in HS:
            if i+h<n:rets[h].append(d*(C[i+h]/C[i]-1)*100)
        e=C[i];up=0.0;dn=0.0
        for f in range(i+1,min(i+1+HOR,n)):
            if d>0:up=max(up,(H[f]-e)/e);dn=min(dn,(L[f]-e)/e)
            else:up=max(up,(e-L[f])/e);dn=min(dn,(e-H[f])/e)
        mfe.append(up*100);mae.append(dn*100)
        if up>=0.005:r05+=1
        if up>=0.010:r10+=1
    m=lambda a:statistics.mean(a) if a else 0.0
    md=lambda a:statistics.median(a) if a else 0.0
    return {"n":len(evs),"fwd":{h:m(rets[h]) for h in HS},"MFE":md(mfe),"MAE":md(mae),
            "r05":100*r05/len(evs) if evs else 0,"r10":100*r10/len(evs) if evs else 0}

def run(iv,days,HOR,HS):
    cd=fetch(iv,days)
    O=[float(c["o"]) for c in cd];H=[float(c["h"]) for c in cd];L=[float(c["l"]) for c in cd]
    C=[float(c["c"]) for c in cd];V=[float(c["v"]) for c in cd];n=len(C);A=atr(H,L,C)
    REF=max(3,HOR//3);fam=gen(O,H,L,C,V,n,A,REF)
    print(f"\n===== BTC {iv} {days}d (~{n} bars) · NO stop / NO cost / NO bracket · MFE/MAE over {HOR} bars · fwd-return at {HS} bars · BTC-only =====")
    hh=HS[len(HS)//2]  # headline horizon
    print(f"  {'signal':26s} {'n':>4} {'MFE':>6} {'MAE':>6} {'r0.5':>5} {'fwd@'+str(hh):>7} {'RANDfwd':>7} {'EDGE':>7} {'OOS tr/te':>13}")
    for name,evs in fam.items():
        if len(evs)<20:
            print(f"  {name:26s} {len(evs):>4}  (too few)");continue
        s=fstats(evs,O,H,L,C,n,HOR,HS)
        dirs=[d for _,d in evs]
        ctrl=[(random.randint(20,n-2),d) for d in dirs]
        cs=fstats(ctrl,O,H,L,C,n,HOR,HS)
        edge=s["fwd"][hh]-cs["fwd"][hh]
        ev2=sorted(evs);half=len(ev2)//2
        tr=fstats(ev2[:half],O,H,L,C,n,HOR,[hh])["fwd"][hh]; te=fstats(ev2[half:],O,H,L,C,n,HOR,[hh])["fwd"][hh]
        flag=""
        if abs(edge)>0.03 and (tr>0)==(te>0) and (tr>0)==(edge>0) and s["n"]>=25: flag="  <-- CONTENT"
        print(f"  {name:26s} {s['n']:>4} {s['MFE']:>+6.2f} {s['MAE']:>+6.2f} {s['r05']:>5.0f} {s['fwd'][hh]:>+7.3f} {cs['fwd'][hh]:>+7.3f} {edge:>+7.3f} {tr:>+6.2f}/{te:>+5.2f}{flag}")

if __name__=="__main__":
    for iv,days,HOR,HS in [("5m",17,48,[6,12,24,48]),("15m",52,32,[4,8,16,32]),("1h",208,24,[3,6,12,24]),("4h",800,18,[3,6,12,18])]:
        run(iv,days,HOR,HS)
    print("\nCONTENT flag = signal's forward directional return beats matched random by >0.03% at the")
    print("headline horizon AND is OOS-sign-consistent. That means predictive content (a real pattern),")
    print("stop/cost-free. Turning content into money is the EXECUTION layer (entry/size/exit) — separate.")
