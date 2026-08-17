#!/usr/bin/env python3
"""THINK LIKE THE MARKET MAKER — regime filter on the robust reversal edges (OLIVIER lens). BTC ONLY,
no stop/cost. The MM (HLP vault on HL) FADES retail noise while the market washes/ranges, but stands
aside / gets run over when real informed flow TRENDS. Prediction: the reversal edges (E2 resTL-reject,
E4 poke-reclaim) carry content in the RANGE regime and lose it (or invert) in the TREND regime. Split
each edge's events by local trend strength |C[i]/C[i-W]-1| (below median = RANGE / MM in control; above
= TREND / MM steps back) and compare directional forward content. If the split is clean, the MM lens is
a real, free improvement to the edges (trade the fade only when the machine is washing, not trending)."""
import statistics
from edge_ensemble import fetch, atr, E_resreject, E_pokereclaim, content, fwd

def split_by_trend(ev, C, n, h, W):
    trail=[]
    for i,d in ev:
        if i-W>=0: trail.append(abs(C[i]/C[i-W]-1))
        else: trail.append(0.0)
    med=statistics.median(trail) if trail else 0.0
    rng=[ev[k] for k in range(len(ev)) if trail[k]<med]
    trd=[ev[k] for k in range(len(ev)) if trail[k]>=med]
    def stat(e):
        r=content(e,C,n,h); return (len(r), statistics.mean(r) if r else 0.0)
    return med, stat(rng), stat(trd), stat(ev)

if __name__=="__main__":
    print("===== MARKET-MAKER REGIME FILTER — reversal edges: RANGE (MM in control) vs TREND (MM steps back) =====")
    # E2 resTL-reject short, 1h
    cd=fetch("1h",208);O=[float(c['o']) for c in cd];H=[float(c['h']) for c in cd];L=[float(c['l']) for c in cd];C=[float(c['c']) for c in cd];n=len(C)
    ev=E_resreject(O,H,L,C,n,6,12); med,rg,td,al=split_by_trend(ev,C,n,12,24)
    print(f"\n  E2 resTL-REJECT short (1h, fwd@12)  split at |24h move| median {med*100:.2f}%")
    print(f"     ALL    n={al[0]:4d}  content {al[1]:+.3f}%")
    print(f"     RANGE  n={rg[0]:4d}  content {rg[1]:+.3f}%   (MM fading noise)")
    print(f"     TREND  n={td[0]:4d}  content {td[1]:+.3f}%   (MM steps aside)")
    print(f"     -> range-minus-trend = {rg[1]-td[1]:+.3f}%  ({'MM lens HELPS' if rg[1]>td[1]+0.03 else 'no clean split'})")
    # E4 poke-low->reclaim long, 15m
    cd2=fetch("15m",52);O2=[float(c['o']) for c in cd2];H2=[float(c['h']) for c in cd2];L2=[float(c['l']) for c in cd2];C2=[float(c['c']) for c in cd2];n2=len(C2)
    ev2=E_pokereclaim(O2,H2,L2,C2,n2,8,16); med2,rg2,td2,al2=split_by_trend(ev2,C2,n2,16,32)
    print(f"\n  E4 poke-low->reclaim long (15m, fwd@16)  split at |trailing move| median {med2*100:.2f}%")
    print(f"     ALL    n={al2[0]:4d}  content {al2[1]:+.3f}%")
    print(f"     RANGE  n={rg2[0]:4d}  content {rg2[1]:+.3f}%   (MM fading noise)")
    print(f"     TREND  n={td2[0]:4d}  content {td2[1]:+.3f}%   (MM steps aside)")
    print(f"     -> range-minus-trend = {rg2[1]-td2[1]:+.3f}%  ({'MM lens HELPS' if rg2[1]>td2[1]+0.03 else 'no clean split'})")
    print("\nMM lens: if RANGE content > TREND content, the edge is MM-fading-noise behaviour — trade the")
    print("fade only while the machine washes, stand aside when it trends. The HLP vault inventory (collector")
    print("'hlp' rows, forward-only) is the direct read of where the house MM is exposed = the next positioning edge.")
