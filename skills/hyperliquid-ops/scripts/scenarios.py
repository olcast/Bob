#!/usr/bin/env python3
"""PATH SCENARIOS — the disciplined form of an 'Elliott count' (OLIVIER). NOT wave-labelling: it emits the
2 most probable NEXT LEGS as a PATH, each anchored to a REAL structural level, each carrying a MECHANISM
(#41 washing-machine / #43 liquidity-harvest / #45 positioning) and an explicit INVALIDATION (falsifiable).
Anti-Elliott guardrail baked in (#46/#47): conviction is DOWNGRADED when positioning is neutral and the
tape is coiled — the tool refuses to manufacture a confident path out of an edgeless state. BTC ONLY, HL.
Read-only; analysis, not a recommendation or an order. Run AFTER the Step-0 macro gate (this does not
replace macro_preflight.py / oi_flow.py; it consumes their verdict, passed in by the operator)."""
import statistics, time, json, urllib.request
from edge_ensemble import atr, desc_res, ph, pl
API="https://api.hyperliquid.xyz/info"; TFMS={'15m':900000,'1h':3600000,'4h':14400000}
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

def load(iv,days):
    cd=fetch(iv,days)
    return ([float(c['o']) for c in cd],[float(c['h']) for c in cd],[float(c['l']) for c in cd],
            [float(c['c']) for c in cd],[float(c['v']) for c in cd],[int(c['t']) for c in cd])
O1,H1,L1,C1,V1,T1=load("1h",30); O4,H4,L4,C4,V4,T4=load("4h",160)
px=C1[-1]; ts=T1[-1]; n1=len(C1); n4=len(C4)
a1=atr(H1,L1,C1)[-1]; a4=atr(H4,L4,C4)[-1]

# structural levels: pivot swing highs/lows on 1h(10d) and 4h(30d)
piv_hi=sorted(set([round(H1[i]) for i in ph(H1,3)]+[round(H4[i]) for i in ph(H4,3)]))
piv_lo=sorted(set([round(L1[i]) for i in pl(L1,3)]+[round(L4[i]) for i in pl(L4,3)]))
res=sorted(h for h in piv_hi if h>px+150)
sup=sorted((l for l in piv_lo if l<px-150),reverse=True)
res=res[:4]; sup=sup[:4]

# ranges + range-position
hi7=max(H1[-168:]); lo7=min(L1[-168:]); hi3=max(H1[-72:]); lo3=min(L1[-72:])
pos7=(px-lo7)/(hi7-lo7) if hi7>lo7 else .5
# regime: efficiency ratio over last 24 * 1h
W=24; num=abs(C1[-1]-C1[-1-W]); den=sum(abs(C1[-1-k]-C1[-2-k]) for k in range(W)) or 1e-9; eff=num/den
# descending-resistance line now (if a valid down-sloping res exists)
mc=desc_res(H1,n1); line=None
if mc[-1] is not None:
    m,c0=mc[-1]; lv=m*(n1-1)+c0
    if lv>px: line=lv
# positioning proxy (basis needs spot; here we flag regime + range only; real crowd read comes from oi_flow.py)

print(f"BTC PATH SCENARIOS — px {px:,.0f}  (1h close, ts {time.strftime('%Y-%m-%d %H:%M UTC',time.gmtime(ts/1000))})")
print(f"  ATR: 1h ${a1:,.0f}  4h ${a4:,.0f}   (a $300 leg = {300/a1:.1f}x the 1h ATR — small; legs below are sized to STRUCTURE)")
print(f"  Range: 7d [{lo7:,.0f} .. {hi7:,.0f}]  pos {pos7*100:.0f}%   3d [{lo3:,.0f} .. {hi3:,.0f}]")
print(f"  Regime (24h efficiency ratio): {eff:.2f}  [{'TRENDING' if eff>=.5 else 'RANGING/coil'}]")
print(f"  Nearest resistance above: "+", ".join(f'{r:,.0f} (+${r-px:,.0f})' for r in res[:3]))
print(f"  Nearest support   below: "+", ".join(f'{s:,.0f} (-${px-s:,.0f})' for s in sup[:3]))
if line: print(f"  Descending-resistance line now ~{line:,.0f} (+${line-px:,.0f}) — the E2 reject level")
print()
# ---- the 2-leg path (range-rotation primary, given coil) ----
nearest_res=res[0] if res else px+a1*3; nearest_sup=sup[0] if sup else px-a1*3
up_room=nearest_res-px; dn_room=px-nearest_sup
first="UP toward resistance" if (pos7<0.5 or up_room<dn_room) else "DOWN toward support"
print("PRIMARY PATH (2 legs), given a coiled/ranging tape — LOW-to-MODERATE conviction (see guardrail):")
if first.startswith("UP"):
    print(f"  LEG 1 — UP grab: {px:,.0f} -> {nearest_res:,.0f}  (+${up_room:,.0f})  mechanism: coil resolves toward the")
    print(f"          nearer liquidity (stops above {nearest_res:,.0f}); poke/tag the level. Trigger: acceptance >{px+a1:,.0f}.")
    print(f"  LEG 2 — DOWN wash: {nearest_res:,.0f} -> {max(nearest_sup,px-a1*2):,.0f}  reject at resistance (E2), rotate back")
    print(f"          down through {px:,.0f} toward {max(nearest_sup, px-a1*2):,.0f}. Mechanism: reversion (#41), reject-short (#40).")
    print(f"  INVALIDATION: 1h CLOSE and hold ABOVE {nearest_res:,.0f} (+~${up_room:,.0f}) = not a poke, it's a breakout -> path is UP-continuation, not rotation.")
else:
    print(f"  LEG 1 — DOWN grab: {px:,.0f} -> {nearest_sup:,.0f}  (-${dn_room:,.0f})  mechanism: coil resolves toward the")
    print(f"          nearer liquidity (stops/liqs below {nearest_sup:,.0f}); poke the level. Trigger: acceptance <{px-a1:,.0f}.")
    print(f"  LEG 2 — UP reclaim: {nearest_sup:,.0f} -> {min(nearest_res,px+a1*2):,.0f}  poke-low->reclaim (E4), rotate back up.")
    print(f"          Mechanism: down-poke gets bought (#40 long-bias), reversion (#41).")
    print(f"  INVALIDATION: 1h CLOSE and hold BELOW {nearest_sup:,.0f} (-~${dn_room:,.0f}) = breakdown, not a poke -> path is DOWN-continuation.")
print()
print("CONVICTION GUARDRAIL (#46/#47): this is RANGE mechanics on a quiet, coiled, neutral-positioning tape.")
print("With no crowd to squeeze (oi_flow: BTC premium neutral) and a scheduled catalyst ahead, treat the")
print("above as the DEFAULT rotation, not a high-conviction call. The real directional leg waits on the")
print("catalyst (name it in the answer). The signal ARMS only if a reject/reclaim coincides with a positioning")
print("extreme (state_view.py) — right now it does not. Read-only analysis; execution + sizing are the desk's.")
