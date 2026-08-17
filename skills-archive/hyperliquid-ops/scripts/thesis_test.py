#!/usr/bin/env python3
"""THESIS TEST (OLIVIER) — BTC ONLY, NO stop / NO cost / NO bracket. Two families, both directions:
 (1) REVERSAL off a poke — 'BTC rarely makes a big move without first poking the other way': fade
     the poke. poke-low→reclaim = LONG; poke-high→reject = SHORT.
 (2) TREND CONTINUATION via trendline — break→retest-hold (rebreak) and touch→reject.
Pure predictive content: directional forward return d·(C[i+h]/C[i]−1) vs matched random, MFE/MAE,
reach, OOS split, on 5m/15m/1h/4h. A stop cannot invalidate anything here — we measure where price
GOES. Execution (entry/size/exit) is the trader's separate layer."""
import statistics, random
from discovery_excursion import fetch, atr, sma, pl, ph, fstats
random.seed(9)

def desc_res(Hi,n,k=3):
    conf=sorted([(p,p+k) for p in ph(Hi,k)],key=lambda x:x[1]); mc=[None]*n; got=[]; cp=0
    for i in range(n):
        while cp<len(conf) and conf[cp][1]<=i: got.append(conf[cp][0]); cp+=1
        if len(got)>=2:
            p1,p2=got[-2],got[-1]
            if p2<i and Hi[p2]<Hi[p1]: m=(Hi[p2]-Hi[p1])/(p2-p1); mc[i]=(m,Hi[p1]-m*p1)
    return mc
def asc_sup(Lo,n,k=3):
    conf=sorted([(p,p+k) for p in pl(Lo,k)],key=lambda x:x[1]); mc=[None]*n; got=[]; cp=0
    for i in range(n):
        while cp<len(conf) and conf[cp][1]<=i: got.append(conf[cp][0]); cp+=1
        if len(got)>=2:
            p1,p2=got[-2],got[-1]
            if p2<i and Lo[p2]>Lo[p1]: m=(Lo[p2]-Lo[p1])/(p2-p1); mc[i]=(m,Lo[p1]-m*p1)
    return mc

def gen(O,H,L,C,n,A,REF,tol=0.0015,W=8):
    res=desc_res(H,n); sup=asc_sup(L,n); out={}
    def rf(e):
        k=[];last=-10**9
        for i,d in sorted(e):
            if i-last>=REF:k.append((i,d));last=i
        return k
    # (1) reversal — poke-low -> reclaim = LONG
    e=[];used=-10**9
    for p in pl(L,3):
        c=p+3;Lv=L[p]
        for i in range(c,min(c+40,n-1)):
            if L[i]<Lv and L[i]>=Lv*(1-0.0024) and C[i]>Lv:
                if i-used>=REF:e.append((i,1));used=i
                break
            if C[i]<Lv*(1-0.0024):break
    out["REV poke-low->reclaim (long)"]=rf(e)
    # (1) reversal — poke-high -> reject = SHORT  (mirror)
    e=[];used=-10**9
    for p in ph(H,3):
        c=p+3;Hv=H[p]
        for i in range(c,min(c+40,n-1)):
            if H[i]>Hv and H[i]<=Hv*(1+0.0024) and C[i]<Hv:
                if i-used>=REF:e.append((i,-1));used=i
                break
            if C[i]>Hv*(1+0.0024):break
    out["REV poke-high->reject (short)"]=rf(e)
    # (2) continuation — descending-res BREAK up then RETEST-hold = LONG
    e=[];last=-10**9
    for i in range(5,n-1):
        if res[i] is None:continue
        m,c0=res[i];li=m*i+c0;lp=m*(i-1)+c0
        if C[i-1]<=lp and C[i]>li:                    # broke up
            for j in range(i+1,min(i+1+W,n-1)):
                lj=m*j+c0
                if L[j]<=lj*(1+tol) and C[j]>lj:      # retest and hold above
                    if j-last>=REF:e.append((j,1));last=j
                    break
    out["CONT resTL break+retest (long)"]=rf(e)
    # (2) continuation — ascending-sup BREAK down then RETEST-reject = SHORT
    e=[];last=-10**9
    for i in range(5,n-1):
        if sup[i] is None:continue
        m,c0=sup[i];li=m*i+c0;lp=m*(i-1)+c0
        if C[i-1]>=lp and C[i]<li:
            for j in range(i+1,min(i+1+W,n-1)):
                lj=m*j+c0
                if H[j]>=lj*(1-tol) and C[j]<lj:
                    if j-last>=REF:e.append((j,-1));last=j
                    break
    out["CONT supTL break+retest (short)"]=rf(e)
    # (2) continuation — REJECT at unbroken descending res = SHORT (trend-down continues)
    e=[];last=-10**9
    for i in range(5,n-1):
        if res[i] is None:continue
        m,c0=res[i];li=m*i+c0
        if H[i]>=li*(1-tol) and C[i]<li*(1-0.0005):   # tagged line, closed back below
            if i-last>=REF:e.append((i,-1));last=i
    out["CONT resTL reject (short)"]=rf(e)
    # (2) continuation — HOLD at unbroken ascending sup = LONG (trend-up continues)
    e=[];last=-10**9
    for i in range(5,n-1):
        if sup[i] is None:continue
        m,c0=sup[i];li=m*i+c0
        if L[i]<=li*(1+tol) and C[i]>li*(1+0.0005):
            if i-last>=REF:e.append((i,1));last=i
    out["CONT supTL hold (long)"]=rf(e)
    return out

def run(iv,days,HOR,HS):
    cd=fetch(iv,days)
    O=[float(c["o"]) for c in cd];H=[float(c["h"]) for c in cd];L=[float(c["l"]) for c in cd]
    C=[float(c["c"]) for c in cd];n=len(C);A=atr(H,L,C);REF=max(3,HOR//3)
    fam=gen(O,H,L,C,n,A,REF); hh=HS[len(HS)//2]
    print(f"\n===== BTC {iv} {days}d (~{n}) · NO stop/cost/bracket · fwd@{hh}bars vs random · OOS · BTC-only =====")
    print(f"  {'signal':32s} {'n':>4} {'MFE':>6} {'MAE':>6} {'r0.5':>5} {'fwd':>7} {'RAND':>7} {'EDGE':>7} {'OOStr/te':>13}")
    for name,evs in fam.items():
        if len(evs)<20: print(f"  {name:32s} {len(evs):>4}  (too few)");continue
        s=fstats(evs,O,H,L,C,n,HOR,HS); dirs=[d for _,d in evs]
        cs=fstats([(random.randint(20,n-2),d) for d in dirs],O,H,L,C,n,HOR,HS)
        edge=s["fwd"][hh]-cs["fwd"][hh]; ev2=sorted(evs);hf=len(ev2)//2
        tr=fstats(ev2[:hf],O,H,L,C,n,HOR,[hh])["fwd"][hh]; te=fstats(ev2[hf:],O,H,L,C,n,HOR,[hh])["fwd"][hh]
        flag="  <-- CONTENT" if (abs(edge)>0.03 and (tr>0)==(te>0) and (tr>0)==(edge>0) and s["n"]>=25) else ""
        print(f"  {name:32s} {s['n']:>4} {s['MFE']:>+6.2f} {s['MAE']:>+6.2f} {s['r05']:>5.0f} {s['fwd'][hh]:>+7.3f} {cs['fwd'][hh]:>+7.3f} {edge:>+7.3f} {tr:>+6.2f}/{te:>+5.2f}{flag}")

if __name__=="__main__":
    for iv,days,HOR,HS in [("5m",17,48,[6,12,24,48]),("15m",52,32,[4,8,16,32]),("1h",208,24,[3,6,12,24]),("4h",800,18,[3,6,12,18])]:
        run(iv,days,HOR,HS)
    print("\nCONTENT = directional forward return beats matched random by >0.03% at the mid horizon,")
    print("OOS-sign-consistent. REVERSAL family = the 'poke the other way' thesis; CONT family = trendline")
    print("rebreak/reject. Both graded stop-free (no rule can invalidate a real move).")
