#!/usr/bin/env python3
"""ADMISSION-TEST harness — shallow-sweep → reclaim, BTC ONLY (never pooled).
The excursion is real (85% reach +0.5%) but the −0.3% bracket is refuted (stop inside the −1.42%
noise). This searches, on TRAIN only, for a bracket that makes it TRADEABLE after cost, then reports
that bracket's TEST performance ONCE — with the A6 microstructure null (swept-but-no-reclaim), a
base-rate null, a regime split (A5), proper scoring (A4), and trial-count as denominator. If nothing
clears TEST after cost, the signal is a real move but NOT a tradeable edge → benched, logged, not buried.

FROZEN signal spec: level = confirmed fractal swing low (k=3, known only at p+k → no look-ahead);
shallow sweep = bar low in [L·(1−0.24%), L); reclaim = same bar closes > L; first sweep of each level;
LONG. Refractory H/3."""
import json,time,urllib.request,statistics,random,math
random.seed(3)
API="https://api.hyperliquid.xyz/info"; TFMS={'1h':3600000,'4h':14400000}
def fetch(coin,iv,days):
    end=int(time.time()*1000);step=TFMS[iv];cur=end-days*86400_000;seen={}
    while cur<end:
        ce=min(cur+4800*step,end)
        r=urllib.request.Request(API,data=json.dumps({"type":"candleSnapshot","req":{"coin":coin,"interval":iv,"startTime":cur,"endTime":ce}}).encode(),headers={"Content-Type":"application/json"})
        try:d=json.load(urllib.request.urlopen(r,timeout=60))
        except Exception:d=[]
        if not d:cur=ce+step;continue
        for c in d:seen[c['t']]=c
        cur=max(c['t'] for c in d)+step
    return [seen[t] for t in sorted(seen)]
def atr(H,L,C,n=14):
    tr=[H[0]-L[0]]
    for i in range(1,len(C)):tr.append(max(H[i]-L[i],abs(H[i]-C[i-1]),abs(L[i]-C[i-1])))
    out=[None]*len(C);s=sum(tr[:n])/n if len(C)>=n else tr[0]
    for i in range(len(C)):out[i]=sum(tr[:i+1])/(i+1) if i<n else (s:=(s*(n-1)+tr[i])/n)
    return out
def sma(x,n):
    out=[None]*len(x);s=0.0
    for i in range(len(x)):
        s+=x[i]
        if i>=n:s-=x[i-n]
        if i>=n-1:out[i]=s/n
    return out
def piv_low(L,k):return [i for i in range(k,len(L)-k) if L[i]==min(L[i-k:i+k+1])]

def events(Hi,Lo,C,n,k=3,shallow=0.0024,lookahead=40,REF=8):
    pl=piv_low(Lo,k); confirmed=[(p,p+k,Lo[p]) for p in pl]
    ev=[]; used=-10**9
    for p,c,L in confirmed:
        for i in range(c,min(c+lookahead,n-1)):
            if Lo[i]<L and Lo[i]>=L*(1-shallow) and C[i]>L:   # shallow sweep + same-bar reclaim
                if i-used>=REF: ev.append((i,L,Lo[i])); used=i
                break
            if C[i]<L*(1-shallow): break                       # level decisively lost, abandon
    return ev
def swept_no_reclaim(Hi,Lo,C,n,k=3,shallow=0.0024,lookahead=40,REF=8):
    pl=piv_low(Lo,k); ev=[];used=-10**9
    for p in pl:
        c=p+k; L=Lo[p]
        for i in range(c,min(c+lookahead,n-1)):
            if Lo[i]<L and Lo[i]>=L*(1-shallow) and C[i]<=L:   # swept shallow but did NOT reclaim
                if i-used>=REF: ev.append((i,L,Lo[i]));used=i
                break
            if C[i]<L*(1-shallow): break
    return ev

def long_path(entry,stop,tgt,j0,H,Hi,Lo,C,n):
    for f in range(j0,min(j0+H,n)):
        if Lo[f]<=stop: return -(entry-stop)/entry, False
        if Hi[f]>=tgt: return (tgt-entry)/entry, True
    return (C[min(j0+H-1,n-1)]/entry-1), None

def grade_reclaim(ev,Hi,Lo,C,n,H,stop_frac,tgt=0.005,cost=0.0005):
    out=[]
    for i,L,swlo in ev:
        e=C[i]; st=e*(1-stop_frac); tp=e*(1+tgt)
        r,win=long_path(e,st,tp,i+1,H,Hi,Lo,C,n)
        out.append((r*100-cost*100, win, i))
    return out
def grade_dip(ev,Hi,Lo,C,n,H,tgt,stop_frac=0.005,Wwait=6,cost=0.0005):
    out=[];fills=0
    for i,L,swlo in ev:
        e=L; filled=None
        for j in range(i+1,min(i+1+Wwait,n)):
            if Lo[j]<=e: filled=j; break
        if filled is None: continue
        fills+=1; st=e*(1-stop_frac); tp=e*(1+tgt)
        r,win=long_path(e,st,tp,filled+1,H,Hi,Lo,C,n)
        out.append((r*100-cost*100, win, i))
    return out,fills

def summ(g):
    if not g: return (0,0.0,0.0)
    net=[x[0] for x in g]; wins=[x[1] for x in g if x[1] is not None]
    hr=100*sum(wins)/len(wins) if wins else 0
    return len(g),hr,statistics.mean(net)
def split(g,C_index_time_order=True):
    h=len(g)//2; return g[:h],g[h:]
def logloss_brier(labels,p):
    p=min(max(p,1e-6),1-1e-6); ll=-statistics.mean(y*math.log(p)+(1-y)*math.log(1-p) for y in labels)
    br=statistics.mean((y-p)**2 for y in labels); return ll,br

def run(coin,iv,days,H):
    cd=fetch(coin,iv,days)
    Hi=[float(c["h"]) for c in cd];Lo=[float(c["l"]) for c in cd];C=[float(c["c"]) for c in cd]
    n=len(C);A=atr(Hi,Lo,C);S200=sma(C,200)
    ev=events(Hi,Lo,C,n); nul=swept_no_reclaim(Hi,Lo,C,n)
    print(f"\n===== {coin} {iv} {days}d (~{n} bars) · shallow-sweep→reclaim LONG · H={H} · target +0.5% · BTC-only =====")
    print(f"  events n={len(ev)}   (microstructure-null 'swept-no-reclaim' n={len(nul)})")
    variants=[]  # (name, grader)
    for s in [0.003,0.005,0.008,0.012,0.015,0.020]:
        variants.append((f"reclaim stop-{s*100:.1f}%", ("reclaim",s)))
    variants.append(("dip-entry@L tgt+0.5%", ("dip",0.005)))
    variants.append(("dip-entry@L tgt+1.0%", ("dip",0.010)))
    print(f"  {'variant':22s} {'n':>4} {'hit%':>5} {'net5bp':>7} {'net25bp':>8} {'TRAINnet':>8} {'TESTnet':>7}")
    rows=[]
    for name,(kind,par) in variants:
        if kind=="reclaim":
            g=grade_reclaim(ev,Hi,Lo,C,n,H,par); g25=grade_reclaim(ev,Hi,Lo,C,n,H,par,cost=0.0025)
        else:
            g,fills=grade_dip(ev,Hi,Lo,C,n,H,par); g25,_=grade_dip(ev,Hi,Lo,C,n,H,par,cost=0.0025)
        nn,hr,net=summ(g); _,_,net25=summ(g25)
        tr,te=split(g); _,_,trn=summ(tr); _,_,ten=summ(te)
        rows.append((name,kind,par,nn,hr,net,net25,trn,ten,g))
        print(f"  {name:22s} {nn:>4} {hr:>5.0f} {net:>+7.3f} {net25:>+8.3f} {trn:>+8.3f} {ten:>+7.3f}")
    # choose best by TRAIN net (honest: pick on train, report test)
    best=max(rows,key=lambda r:r[7])
    name,kind,par,nn,hr,net,net25,trn,ten,g=best
    print(f"  --> CHOSEN by TRAIN: {name}  | TEST net {ten:+.3f}%/tr ({'POSITIVE' if ten>0 else 'negative'} after 5bp)")
    # microstructure null on the chosen bracket
    if kind=="reclaim":
        gnull=grade_reclaim(nul,Hi,Lo,C,n,H,par)
    else:
        gnull,_=grade_dip(nul,Hi,Lo,C,n,H,par)
    _,_,nullnet=summ(gnull)
    # base-rate null: random entries same bracket
    if kind=="reclaim":
        rev=[(random.randint(1,n-2),0,0) for _ in range(len(ev))]; gbase=grade_reclaim(rev,Hi,Lo,C,n,H,par)
    else:
        gbase=[( (long_path(C[random.randint(1,n-2)],C[0],C[0], 0,1,Hi,Lo,C,n)[0]),None,0) for _ in range(1)]  # placeholder
        gbase=[]
        for _ in range(len(ev)):
            j=random.randint(1,n-2); e=C[j]; r,w=long_path(e,e*(1-0.005),e*(1+par),j+1,H,Hi,Lo,C,n); gbase.append((r*100-0.05,w,j))
    _,_,basenet=summ(gbase)
    print(f"      A6 microstructure null (swept-no-reclaim), same bracket: net {nullnet:+.3f}%/tr")
    print(f"      base-rate null (random entry), same bracket:            net {basenet:+.3f}%/tr")
    print(f"      => reclaim adds vs null: {net-nullnet:+.3f}%  vs base: {net-basenet:+.3f}%")
    # regime split (SMA200 state at event) on chosen
    up=[x for x in g if x[2]<n and S200[x[2]] is not None and C[x[2]]>S200[x[2]]]
    dn=[x for x in g if x[2]<n and S200[x[2]] is not None and C[x[2]]<=S200[x[2]]]
    _,_,un=summ(up); _,_,dnn=summ(dn)
    print(f"      A5 regime (SMA200 @event): UP n={len(up)} net {un:+.3f}%  |  DOWN n={len(dn)} net {dnn:+.3f}%")
    # proper scoring on TEST: signal hit-rate (train) vs base rate as forecasts
    tr,te=split(g)
    lab=[1 if x[1] else 0 for x in te if x[1] is not None]
    if lab and tr:
        ptr=sum(1 for x in tr if x[1])/max(1,sum(1 for x in tr if x[1] is not None))
        # base rate of the win-label over random draws
        base_lab=[1 if x[1] else 0 for x in gbase if x[1] is not None]; pbase=sum(base_lab)/len(base_lab) if base_lab else 0.5
        lls,brs=logloss_brier(lab,ptr); llb,brb=logloss_brier(lab,pbase)
        print(f"      A4 proper-scoring (TEST label=win): signal-forecast p={ptr:.2f} logloss {lls:.3f}/Brier {brs:.3f}  vs  base p={pbase:.2f} logloss {llb:.3f}  -> signal {'ADDS' if lls<llb else 'no info'}")
    print(f"      TRIAL COUNT (bracket variants tried) = {len(variants)}")
    return ten>0

if __name__=="__main__":
    verdicts={}
    for iv,days,H in [("1h",208,24),("4h",800,18)]:
        verdicts[iv]=run("BTC",iv,days,H)
    print("\n===== VERDICT (BTC-only, TEST net>0 after 5bp on the train-chosen bracket) =====")
    for iv,v in verdicts.items():
        print(f"  {iv}: {'PASS (tradeable candidate — proceed to blind/regime/proper-score gate)' if v else 'FAIL (excursion real, bracket not tradeable OOS — stays CANDIDATE/benched)'}")
    print("  NOTE: even a PASS here is TRAIN-chosen; it must still clear a pre-registered BLIND run + A5/A6/A4 before ADMITTED. This harness is the design+first-pass step, not the admission decision.")
