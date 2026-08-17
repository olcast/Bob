#!/usr/bin/env python3
"""EDGE ENSEMBLE / DECORRELATION / ROBUSTNESS — the combiner's first real evaluation (VCP-COMBINER-001).
BTC ONLY, NO stop / NO cost / NO bracket — pure directional content (d·fwd-return), the trader owns
execution. Freezes the candidate edges, then for each: mean content vs matched random + BOOTSTRAP 90% CI
+ WALK-FORWARD (4 folds) OOS sign-stability. Then the whole point: the DECORRELATION MATRIX of the edges'
daily PnL, an EQUAL-WEIGHT ensemble, and the effective number of INDEPENDENT bets (the thing that actually
scales an ensemble's information ratio). HONEST: this is rigorous OOS but NOT true blind — the data was
seen during discovery. True blind = forward; the collector is accruing it. Nothing here is ADMITTED.

Edges (frozen): E1 vol-spike-FADE (1h), E2 resTL-REJECT short (1h), E3 fade-strong-trend (1h; the
'comes back for it' retracement), E4 poke-low->reclaim long (15m, its native TF — reported separately
since it lives on a different clock)."""
import json,time,urllib.request,statistics,math,random
random.seed(13)
API="https://api.hyperliquid.xyz/info"; TFMS={'15m':900000,'1h':3600000}
def fetch(iv,days):
    step=TFMS[iv];end=int(time.time()*1000);cur=end-int(days*86400_000);seen={}
    while cur<end:
        r=urllib.request.Request(API,data=json.dumps({"type":"candleSnapshot","req":{"coin":"BTC","interval":iv,"startTime":cur,"endTime":min(cur+4800*step,end)}}).encode(),headers={"Content-Type":"application/json"})
        try:d=json.load(urllib.request.urlopen(r,timeout=60))
        except Exception:d=[]
        if not d:cur+=4800*step;continue
        for c in d:seen[c['t']]=c
        cur=max(c['t'] for c in d)+step
    return [seen[t] for t in sorted(seen)]
def atr(H,L,C,n=14):
    tr=[H[0]-L[0]]
    for i in range(1,len(C)):tr.append(max(H[i]-L[i],abs(H[i]-C[i-1]),abs(L[i]-C[i-1])))
    o=[None]*len(C);s=sum(tr[:n])/n if len(C)>=n else tr[0]
    for i in range(len(C)):o[i]=sum(tr[:i+1])/(i+1) if i<n else (s:=(s*(n-1)+tr[i])/n)
    return o
def ph(H,k):return [i for i in range(k,len(H)-k) if H[i]==max(H[i-k:i+k+1])]
def pl(L,k):return [i for i in range(k,len(L)-k) if L[i]==min(L[i-k:i+k+1])]
def desc_res(H,n,k=3):
    conf=sorted([(p,p+k) for p in ph(H,k)],key=lambda x:x[1]);mc=[None]*n;g=[];cp=0
    for i in range(n):
        while cp<len(conf) and conf[cp][1]<=i:g.append(conf[cp][0]);cp+=1
        if len(g)>=2:
            p1,p2=g[-2],g[-1]
            if p2<i and H[p2]<H[p1]:m=(H[p2]-H[p1])/(p2-p1);mc[i]=(m,H[p1]-m*p1)
    return mc

def fwd(d,i,C,n,h): return d*(C[i+h]/C[i]-1)*100 if i+h<n else None

def E_volspike(O,H,L,C,V,n,A,REF,h):
    ev=[];last=-10**9
    for i in range(21,n-1):
        vm=statistics.median(V[i-20:i]) or 1e-9
        if V[i-1]>3*vm:
            d=-(1 if C[i-1]>O[i-1] else -1)   # FADE
            if i-last>=REF:ev.append((i,d));last=i
    return ev
def E_resreject(O,H,L,C,n,REF,h,tol=0.0015):
    res=desc_res(H,n);ev=[];last=-10**9
    for i in range(5,n-1):
        if res[i] is None:continue
        m,c0=res[i];li=m*i+c0
        if H[i]>=li*(1-tol) and C[i]<li*(1-0.0005):
            if i-last>=REF:ev.append((i,-1));last=i
    return ev
def E_fadetrend(C,n,REF,h,k=24,thr=0.02):
    ev=[];last=-10**9
    for i in range(k,n-1):
        R=C[i]/C[i-k]-1
        if abs(R)>=thr:
            if i-last>=REF:ev.append((i,-1 if R>0 else 1));last=i
    return ev
def E_pokereclaim(O,H,L,C,n,REF,h):
    ev=[];used=-10**9
    for p in pl(L,3):
        c=p+3;Lv=L[p]
        for i in range(c,min(c+40,n-1)):
            if L[i]<Lv and L[i]>=Lv*(1-0.0024) and C[i]>Lv:
                if i-used>=REF:ev.append((i,1));used=i
                break
            if C[i]<Lv*(1-0.0024):break
    return ev

def content(ev,C,n,h):
    r=[fwd(d,i,C,n,h) for i,d in ev];r=[x for x in r if x is not None];return r
def boot_ci(x,B=2000):
    if len(x)<10:return (0,0,0)
    m=statistics.mean(x);ms=[]
    for _ in range(B):
        s=[x[random.randint(0,len(x)-1)] for _ in range(len(x))];ms.append(statistics.mean(s))
    ms.sort();return m,ms[int(0.05*B)],ms[int(0.95*B)]
def walkfwd(ev,C,n,h,folds=4):
    ev=sorted(ev);sz=len(ev)//folds;signs=[]
    for f in range(folds):
        seg=ev[f*sz:(f+1)*sz] if f<folds-1 else ev[f*sz:]
        r=content(seg,C,n,h);signs.append(1 if r and statistics.mean(r)>0 else (0 if not r else -1))
    return signs
def daily(ev,T,C,n,h):
    pnl={}
    for i,d in ev:
        v=fwd(d,i,C,n,h)
        if v is None:continue
        day=T[i]//86400000; pnl[day]=pnl.get(day,0.0)+v
    return pnl
def corr(a,b,days):
    xa=[a.get(d,0.0) for d in days];xb=[b.get(d,0.0) for d in days]
    n=len(days);ma=sum(xa)/n;mb=sum(xb)/n
    cov=sum((xa[i]-ma)*(xb[i]-mb) for i in range(n))/n
    va=sum((v-ma)**2 for v in xa)/n;vb=sum((v-mb)**2 for v in xb)/n
    return cov/math.sqrt(va*vb) if va>0 and vb>0 else 0.0

if __name__=="__main__":
    # ---- 1h edges on a common clock ----
    cd=fetch("1h",208);O=[float(c["o"]) for c in cd];H=[float(c["h"]) for c in cd];L=[float(c["l"]) for c in cd]
    C=[float(c["c"]) for c in cd];V=[float(c["v"]) for c in cd];T=[int(c["t"]) for c in cd];n=len(C);A=atr(H,L,C);h=12;REF=6
    edges={"E1 vol-spike FADE":E_volspike(O,H,L,C,V,n,A,REF,h),
           "E2 resTL REJECT short":E_resreject(O,H,L,C,n,REF,h),
           "E3 fade-strong-trend":E_fadetrend(C,n,REF,h)}
    print("===== PER-EDGE (BTC 1h 208d, fwd@12, NO stop/cost) — content vs random, bootstrap 90% CI, walk-forward =====")
    randmean=statistics.mean([fwd(random.choice([-1,1]),random.randint(20,n-2),C,n,h) or 0 for _ in range(4000)])
    dpnl={}
    for nm,ev in edges.items():
        r=content(ev,C,n,h);m,lo,hi=boot_ci(r);wf=walkfwd(ev,C,n,h)
        dpnl[nm]=daily(ev,T,C,n,h)
        sig="CI>0" if lo>0 else ("CI<0" if hi<0 else "CI spans 0")
        print(f"  {nm:24s} n={len(r):4d} mean={m:+.3f}% CI90[{lo:+.3f},{hi:+.3f}] {sig:11s} vsRand~{m-randmean:+.3f}  walkfwd signs={wf}")
    days=sorted(set().union(*[set(d) for d in dpnl.values()]))
    print(f"\n===== DECORRELATION MATRIX (daily PnL, {len(days)} active days) — the whole point of an ensemble =====")
    names=list(dpnl); print("        "+"  ".join(f"{n_[:8]:>8}" for n_ in names))
    M=[[corr(dpnl[a],dpnl[b],days) for b in names] for a in names]
    for i,a in enumerate(names): print(f"  {a[:8]:8s} "+"  ".join(f"{M[i][j]:>8.2f}" for j in range(len(names))))
    # equal-weight ensemble daily pnl + effective independent bets
    ens={d:statistics.mean([dpnl[nm].get(d,0.0) for nm in names]) for d in days}
    em=statistics.mean(ens.values());es=statistics.pstdev(ens.values()) or 1e-9
    avg_off=statistics.mean(M[i][j] for i in range(len(names)) for j in range(len(names)) if i!=j)
    Neff=len(names)/(1+(len(names)-1)*max(0,avg_off))
    indiv_sharpe=[statistics.mean(list(dpnl[nm].values()))/(statistics.pstdev(list(dpnl[nm].values()))or 1e-9) for nm in names]
    print(f"\n  avg off-diagonal corr = {avg_off:+.2f}  ->  effective independent bets N_eff = {Neff:.2f} (of {len(names)})")
    print(f"  equal-weight ensemble daily: mean {em:+.3f}%  std {es:.3f}  daily-Sharpe {em/es:+.2f}  vs best-single {max(indiv_sharpe):+.2f}")
    print("  ("+("ensemble > best single ⇒ decorrelation IS paying here" if em/es>max(indiv_sharpe) else "ensemble <= best single ⇒ decorrelation is NOT paying here — do NOT claim it")+")")

    # ---- E4 poke-low->reclaim on its native 15m clock (reported separately) ----
    cd2=fetch("15m",52);C2=[float(c["c"]) for c in cd2];H2=[float(c["h"]) for c in cd2];L2=[float(c["l"]) for c in cd2];O2=[float(c["o"]) for c in cd2];n2=len(C2)
    ev4=E_pokereclaim(O2,H2,L2,C2,n2,8,16);r4=content(ev4,C2,n2,16);m4,lo4,hi4=boot_ci(r4)
    print(f"\n  E4 poke-low->reclaim (15m, native clock): n={len(r4)} mean={m4:+.3f}% CI90[{lo4:+.3f},{hi4:+.3f}] "
          f"{'CI>0' if lo4>0 else 'CI spans 0'} — add on its own clock; decorrelation vs the 1h set is the next step.")
    print("\nVERDICT: edges with CI90 excluding 0 AND sign-stable walk-forward are robust IN-SAMPLE-OOS; still")
    print("owe a pre-registered FORWARD (true-blind) run before ADMITTED. The N_eff and ensemble-Sharpe say")
    print("whether combining them beats the best single — the RenTec payoff — net of their correlation.")
