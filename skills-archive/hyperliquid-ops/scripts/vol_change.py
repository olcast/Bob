#!/usr/bin/env python3
"""VOLUME-*CHANGE* & CVD-PROXY CONFLUENCE (OLIVIER: 'changes in volume', not the level; + the CVD lens).
Raw volume LEVEL added NO confluence to the reversal edges (tested null: HIGH/QUIET/RISING all ~edge-alone).
This asks the sharper question he actually posed — do CHANGES in volume (expansion vs contraction,
acceleration) and a candle-CVD-proxy (signed volume; does the aggressor proxy CONFIRM or DIVERGE at the
poke?) sharpen E2 (resTL-reject short) and E4 (poke-low->reclaim long)? The contrarian read he wants
('those who buy the high / sell the low'): at a price extreme, if the CVD-proxy does NOT confirm, the
aggressors at that extreme are being absorbed = the trapped cohort = stronger fade. BTC ONLY, 1h,
NO stop/cost, content = directional fwd return vs the EDGE ALONE (confluence must beat the edge, not just
random). True CVD (aggressor tape / per-address) is FORWARD-only via the collector; this is the candle
approximation, DISCOVERY / in-sample."""
import statistics
from edge_ensemble import fetch, atr, E_resreject, E_pokereclaim, content, fwd

cd=fetch("1h",208)
O=[float(c['o']) for c in cd];H=[float(c['h']) for c in cd];L=[float(c['l']) for c in cd]
C=[float(c['c']) for c in cd];V=[float(c['v']) for c in cd];n=len(C);REF=6;h=12

# ---- volume-CHANGE lenses (all contemporaneous at the signal bar i; no look-ahead) ----
dV=[0.0]+[ (V[i]/V[i-1]-1) if V[i-1]>0 else 0.0 for i in range(1,n)]        # bar-over-bar change
exp=[0.0]*n                                                                 # expansion vs 3-bar baseline
for i in range(4,n):
    b=statistics.mean(V[i-3:i]) or 1e-9; exp[i]=V[i]/b-1
acc=[0.0]*n                                                                 # acceleration (2nd diff of V)
for i in range(2,n): acc[i]=dV[i]-dV[i-1]
# ---- candle-CVD proxy: signed volume cumulated (up-bar +V, down-bar -V) ----
sv=[ (1 if C[i]>=O[i] else -1)*V[i] for i in range(n)]
cvd=[0.0]*n
for i in range(1,n): cvd[i]=cvd[i-1]+sv[i]
def cvdslope(i,k=6): return (cvd[i]-cvd[i-k]) if i-k>=0 else 0.0             # aggressor-proxy momentum

expv=sorted(exp[4:]); em_hi=expv[int(0.7*len(expv))]; em_lo=expv[int(0.3*len(expv))]

def cc(ev, mask=None):
    r=[fwd(d,i,C,n,h) for (i,d) in ev if (mask is None or mask(i,d))]
    r=[x for x in r if x is not None]; return (len(r), statistics.mean(r) if r else 0.0)

def row(name, ev, masks):
    nn,al=cc(ev); print(f"  {name:6s} ALL n={nn:4d} content {al:+.3f}%")
    for label,mfn in masks:
        n2,c2=cc(ev,mfn); tag="CONFLUENCE" if c2>al+0.05 else ("CONTRADICTION" if c2<al-0.05 else "~")
        print(f"      x {label:46s} n={n2:4d} content {c2:+.3f}%   ({tag} {c2-al:+.3f})")

E2=E_resreject(O,H,L,C,n,REF,h)     # short (d=-1)
E4=E_pokereclaim(O,H,L,C,n,REF,h)   # long  (d=+1)

print(f"VOLUME-*CHANGE* & CVD-PROXY CONFLUENCE — BTC 1h {n} bars, fwd@{h}, changes not level (level was null)\n")
print("== E2 resTL-reject SHORT — condition on volume CHANGE / CVD-proxy ==")
row("E2", E2, [
    ("volume EXPANDING at poke (>3-bar base, top30%)", lambda i,d: exp[i]>=em_hi),
    ("volume CONTRACTING at poke (bottom30%)",         lambda i,d: exp[i]<=em_lo),
    ("volume ACCELERATING (dV rising)",                lambda i,d: acc[i]>0),
    ("CVD-proxy CONFIRMS short (slope<0 = sellers)",   lambda i,d: cvdslope(i)<0),
    ("CVD-proxy DIVERGES (slope>0 at a high = absorb)",lambda i,d: cvdslope(i)>0),
])
print("\n== E4 poke-low->reclaim LONG — condition on volume CHANGE / CVD-proxy ==")
row("E4", E4, [
    ("volume EXPANDING at poke (>3-bar base, top30%)", lambda i,d: exp[i]>=em_hi),
    ("volume CONTRACTING at poke (bottom30%)",         lambda i,d: exp[i]<=em_lo),
    ("volume ACCELERATING (dV rising)",                lambda i,d: acc[i]>0),
    ("CVD-proxy CONFIRMS long (slope>0 = buyers)",     lambda i,d: cvdslope(i)>0),
    ("CVD-proxy DIVERGES (slope<0 at a low = absorb)", lambda i,d: cvdslope(i)<0),
])
print("\nDISCOVERY/in-sample. 'Change in volume' = expansion/contraction/acceleration; CVD-proxy = signed-")
print("candle-volume slope (confirm vs diverge at the poke). True aggressor CVD & per-address profiling are")
print("FORWARD-only via the collector; this candle proxy is the backtestable stand-in.")
