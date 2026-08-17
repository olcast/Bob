#!/usr/bin/env python3
"""DISCOVERY signal sweep — BTC ONLY, never pooled with other coins (BTC trades differently;
pooling assets manufactures fake edges). A battery of DECORRELATED signal families graded
uniformly at Olivier's real params: +0.5% target / -0.3% stop / 5bp round-trip, EXCURSION-graded
(MFE/MAE), walk-forward, each vs a MATCHED random-entry control (same n, same long/short mix),
OOS train/test split for stability. Trial count = denominator (printed). NOTHING here is a
candidate until it beats random AND survives OOS AND then passes blind pre-registered validation
(R4/A4/A5/A6). This is a hypothesis generator, not an edge oracle."""
import json, time, urllib.request, statistics, random, os
random.seed(7)
COST_ENV=float(os.environ.get('COST_BP','5'))/1e4  # 5bp default; set COST_BP=0 to see pure gross pattern edge
API="https://api.hyperliquid.xyz/info"
TFMS={'1h':3600000,'2h':7200000,'4h':14400000}

def fetch(coin, iv, days):
    end=int(time.time()*1000); step=TFMS[iv]; cur=end-days*86400_000; seen={}
    while cur<end:
        ce=min(cur+4800*step,end)
        r=urllib.request.Request(API,data=json.dumps({"type":"candleSnapshot","req":{"coin":coin,"interval":iv,"startTime":cur,"endTime":ce}}).encode(),headers={"Content-Type":"application/json"})
        try: d=json.load(urllib.request.urlopen(r,timeout=60))
        except Exception: d=[]
        if not d: cur=ce+step; continue
        for c in d: seen[c['t']]=c
        cur=max(c['t'] for c in d)+step
    cd=[seen[t] for t in sorted(seen)]
    return cd

def atr(H,L,C,n=14):
    tr=[H[0]-L[0]]
    for i in range(1,len(C)): tr.append(max(H[i]-L[i],abs(H[i]-C[i-1]),abs(L[i]-C[i-1])))
    out=[None]*len(C); s=sum(tr[:n])/n if len(tr)>=n else tr[0]
    for i in range(len(C)): out[i]=sum(tr[:i+1])/(i+1) if i<n else (s:=(s*(n-1)+tr[i])/n)
    return out

def sma(x,n):
    out=[None]*len(x); s=0.0
    for i in range(len(x)):
        s+=x[i]
        if i>=n: s-=x[i-n]
        if i>=n-1: out[i]=s/n
    return out
def std(x,n):
    out=[None]*len(x)
    for i in range(n-1,len(x)):
        w=x[i-n+1:i+1]; m=sum(w)/n; out[i]=(sum((v-m)**2 for v in w)/n)**0.5
    return out

def grade(dr,i,O,H,L,C,n,HOR,TGT,STOP,COST):
    e=C[i]; mfe=0.0; mae=0.0
    if dr>0:
        tp=e*(1+TGT); sl=e*(1-STOP)
        for f in range(i+1,min(i+1+HOR,n)):
            mfe=max(mfe,(H[f]-e)/e); mae=min(mae,(L[f]-e)/e)
            if L[f]<=sl: return (-STOP-COST)*100,False,mfe*100,mae*100
            if H[f]>=tp: return (TGT-COST)*100,True,mfe*100,mae*100
        return ((C[min(i+HOR,n-1)]/e-1)-COST)*100,None,mfe*100,mae*100
    else:
        tp=e*(1-TGT); sl=e*(1+STOP)
        for f in range(i+1,min(i+1+HOR,n)):
            mfe=max(mfe,(e-L[f])/e); mae=min(mae,(e-H[f])/e)
            if H[f]>=sl: return (-STOP-COST)*100,False,mfe*100,mae*100
            if L[f]<=tp: return (TGT-COST)*100,True,mfe*100,mae*100
        return ((e/C[min(i+HOR,n-1)]-1)-COST)*100,None,mfe*100,mae*100

def signals(iv,O,H,L,C,V,n,A,REF):
    """each family -> list of (index, dir). Refractory REF applied per family."""
    S20=sma(C,20); D20=std(C,20); out={}
    def refr(evs):
        keep=[]; last=-10**9
        for i,d in sorted(evs):
            if i-last>=REF: keep.append((i,d)); last=i
        return keep
    # 1 overextension mean-reversion (fade z>2)
    e=[]
    for i in range(20,n-1):
        if D20[i] and D20[i]>0:
            z=(C[i]-S20[i])/D20[i]
            if z>2: e.append((i,-1))
            elif z<-2: e.append((i,1))
    out["MR overext z>2 (fade)"]=refr(e)
    # 2 consecutive candles (fade 4-in-a-row)
    e=[]
    for i in range(5,n-1):
        up=all(C[j]>C[j-1] for j in range(i-3,i+1)); dn=all(C[j]<C[j-1] for j in range(i-3,i+1))
        if up: e.append((i,-1))
        elif dn: e.append((i,1))
    out["MR 4-consec (fade)"]=refr(e)
    # 3 NR7 compression -> breakout continuation
    e=[]
    for i in range(8,n-1):
        rng=[H[j]-L[j] for j in range(i-7,i)]
        if (H[i-1]-L[i-1])==min(rng):
            if C[i]>H[i-1]: e.append((i,1))
            elif C[i]<L[i-1]: e.append((i,-1))
    out["MOM NR7 breakout"]=refr(e)
    # 4 Donchian-20 breakout continuation
    e=[]
    for i in range(21,n-1):
        if C[i]>max(H[i-20:i]): e.append((i,1))
        elif C[i]<min(L[i-20:i]): e.append((i,-1))
    out["MOM Donchian20 break"]=refr(e)
    # 5 large-range bar: follow vs fade
    ef=[]; ed=[]
    for i in range(15,n-1):
        if A[i-1] and (H[i-1]-L[i-1])>2*A[i-1]:
            d=1 if C[i-1]>O[i-1] else -1
            ef.append((i,d)); ed.append((i,-d))
    out["large-range FOLLOW"]=refr(ef); out["large-range FADE"]=refr(ed)
    # 6 volume spike: continuation vs fade
    ef=[]; ed=[]
    for i in range(21,n-1):
        vm=statistics.median(V[i-20:i]) or 1e-9
        if V[i-1]>3*vm:
            d=1 if C[i-1]>O[i-1] else -1
            ef.append((i,d)); ed.append((i,-d))
    out["vol-spike CONT"]=refr(ef); out["vol-spike FADE"]=refr(ed)
    # 7 inside-bar breakout
    e=[]
    for i in range(3,n-1):
        if H[i-1]<H[i-2] and L[i-1]>L[i-2]:
            if C[i]>H[i-1]: e.append((i,1))
            elif C[i]<L[i-1]: e.append((i,-1))
    out["inside-bar breakout"]=refr(e)
    return out

def stat(ev):
    if not ev: return (0,0,0,0,0,0)
    net=[x[0] for x in ev]; hit=[x[1] for x in ev if x[1] is not None]
    mfe=[x[2] for x in ev]; mae=[x[3] for x in ev]
    hr=100*sum(hit)/len(hit) if hit else 0
    reach=100*sum(1 for m in mfe if m>=0.5)/len(mfe)
    return len(ev),hr,statistics.mean(net),statistics.median(mfe),statistics.median(mae),reach

def run(coin,iv,days,HOR,TGT=0.005,STOP=0.003,COST=0.0005,REF=None):  # COST=0.0005 = 5bp round-trip
    cd=fetch(coin,iv,days)
    O=[float(c["o"]) for c in cd];H=[float(c["h"]) for c in cd];L=[float(c["l"]) for c in cd]
    C=[float(c["c"]) for c in cd];V=[float(c["v"]) for c in cd];T=[int(c["t"]) for c in cd]
    n=len(C);A=atr(H,L,C);REF=REF or max(3,HOR//3)
    fam=signals(iv,O,H,L,C,V,n,A,REF)
    print(f"\n===== {coin} {iv} {days}d (~{n} bars) · +0.5%/-0.3%/{COST*1e4:.0f}bp · HOR={HOR} · EXCURSION-graded · DISCOVERY/in-sample =====")
    print(f"  {'signal':24s} {'n':>4} {'hit%':>5} {'net%':>7} {'medMFE':>7} {'medMAE':>7} {'reach.5':>7} {'vsRAND':>7} {'OOStr/te net':>16}")
    trials=0; survivors=[]
    for name,evs in fam.items():
        if len(evs)<20:
            print(f"  {name:24s} {len(evs):>4}  (too few)"); trials+=1; continue
        graded=[(grade(d,i,O,H,L,C,n,HOR,TGT,STOP,COST),i,d) for i,d in evs]
        ev=[g[0] for g in graded]
        dirs=[d for _,_,d in graded]
        # matched random control: same n, same dir mix
        ctrl=[]
        for d in dirs:
            j=random.randint(20,n-2); ctrl.append(grade(d,j,O,H,L,C,n,HOR,TGT,STOP,COST))
        nn,hr,net,mfe,mae,reach=stat(ev); _,_,cnet,_,_,_=stat(ctrl)
        # OOS split by time (event order == time order)
        h=len(ev)//2
        tr=statistics.mean(x[0] for x in ev[:h]); te=statistics.mean(x[0] for x in ev[h:])
        edge=net-cnet; trials+=1
        flag=""
        # SURVIVES only if profitable after cost AND beats random AND both OOS halves net-positive
        if net>0.02 and edge>0.03 and tr>0 and te>0 and nn>=30: flag="  <-- SURVIVES(disc)"; survivors.append((coin,iv,name,nn,net,edge,tr,te))
        print(f"  {name:24s} {nn:>4} {hr:>5.0f} {net:>+7.3f} {mfe:>+7.2f} {mae:>+7.2f} {reach:>7.0f} {edge:>+7.3f} {tr:>+7.2f}/{te:>+6.2f}{flag}")
    return trials,survivors

if __name__=="__main__":
    TOT=0; SURV=[]
    for iv,days,HOR in [("1h",208,24),("2h",400,18),("4h",800,18)]:
        t,s=run("BTC",iv,days,HOR,COST=COST_ENV); TOT+=t; SURV+=s
    print(f"\n===== TRIAL COUNT (denominator) = {TOT} signal×TF cells tested, BTC only =====")
    if SURV:
        print("DISCOVERY SURVIVORS (beat random + OOS-consistent; NOT admitted — need blind/regime/proper-score/null):")
        for c,iv,nm,nn,net,edge,tr,te in SURV:
            print(f"  {c} {iv} {nm}: n={nn} net={net:+.3f}% vsRand={edge:+.3f}% OOS {tr:+.2f}/{te:+.2f}")
    else:
        print("NO survivors cleared the discovery bar (beat random + both OOS halves positive). Expected — most patterns are null after costs.")
