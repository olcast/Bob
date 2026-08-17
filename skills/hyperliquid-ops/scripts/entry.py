#!/usr/bin/env python3
"""ENTRY — the best price to JOIN the live scenario (OLIVIER). The desk's edge is REVERSALS AT LEVELS, so the
best entry is NEVER mid-range — it is the poke/tag where the move begins, with the make-or-break as the
invalidation. Prices the two doctrine entries: LONG the flush-&-reclaim into support, SHORT the tag-&-reject
at resistance. IMPORTANT — the LONG's base target is the RESISTANCE / MAGNET (the move-1 target the bounce
runs to), NOT any continuation level; a continuation target (e.g. 'then 65,475 on acceptance') is shown
SEPARATELY as an extension only, since it applies only AFTER price accepts through the magnet. BTC only,
read-only, ~1s.
Usage:  python3 entry.py <support> <resistance> [down_target] [continuation_target]
        e.g. python3 entry.py 62800 63474 62000 65475
        (support=make-or-break/floor · resistance=magnet/ceiling · down_target=short objective ·
         continuation=where the long extends ONLY on acceptance >resistance)"""
import json,urllib.request,time,sys
API="https://api.hyperliquid.xyz/info"
def post(b):
    try:
        r=urllib.request.Request(API,data=json.dumps(b).encode(),headers={"Content-Type":"application/json"});return json.load(urllib.request.urlopen(r,timeout=30))
    except Exception:return None
a=[x.replace(',','') for x in sys.argv[1:]]
if len(a)<2: print("usage: python3 entry.py <support> <resistance> [down_target] [continuation_target]"); sys.exit()
S=float(a[0]); R=float(a[1])
DT=float(a[2]) if len(a)>2 else S-(R-S)              # SHORT's down objective
EXT=float(a[3]) if len(a)>3 and a[3] else None       # LONG's continuation (only ON acceptance > R)
P=float((post({'type':'allMids'}) or {}).get('BTC',0) or 0)
if not P: print("price unavailable (allMids failed) — try again in a moment."); sys.exit()
buf=max(150.0, 0.0035*P)                              # 'acceptance beyond the level' = the risk (invalidation) unit
rrL=(R-S)/buf if buf>0 else 0                         # LONG: reclaim support -> the MAGNET (move-1 target)
rrE=((EXT-S)/buf) if (EXT and buf>0) else None        # LONG extension: only if it accepts through the magnet
rrS=(R-DT)/buf if buf>0 else 0                        # SHORT: reject resistance -> down objective
mid=(S+R)/2; midband=(R-S)*0.25; dL=abs(P-S); dS=abs(P-R)

print(f"ENTRY — join the live scenario · BTC {P:,.0f} · {time.strftime('%H:%M UTC',time.gmtime())}")
print(f"  scenario rails: support/make-or-break {S:,.0f} · resistance/magnet {R:,.0f}  (you are {P-mid:+,.0f} vs mid {mid:,.0f})")
ext_txt = f"  ·  extends to {EXT:,.0f} ONLY on acceptance >{R:,.0f} ({rrE:.1f}:1)" if rrE else ""
print(f"  LONG  flush-&-reclaim  -> entry {S:,.0f} · invalidation <{S-buf:,.0f} · target {R:,.0f} (magnet) · R:R {rrL:.1f}:1  ({S-P:+,.0f} from here){ext_txt}")
print(f"  SHORT tag-&-reject     -> entry {R:,.0f} · invalidation >{R+buf:,.0f} · target {DT:,.0f} · R:R {rrS:.1f}:1  ({R-P:+,.0f} from here)")
if min(dL,dS)>midband:
    print(f"  >>> WAIT — you are MID-RANGE ({P-mid:+,.0f} off mid); do NOT chase. Let price come to a rail:")
    print(f"      long only on a reclaim of {S:,.0f}, short only on a reject at {R:,.0f}.")
else:
    if dL<=dS: side,e,rr,verb,lvl = "LONG",S,rrL,"reclaims","support"
    else:      side,e,rr,verb,lvl = "SHORT",R,rrS,"rejects","resistance"
    print(f"  >>> NEAREST RAIL: {side} at {e:,.0f} (R:R {rr:.1f}:1) — arm it only if price {verb} the {lvl}; {e-P:+,.0f} away.")
print(f"  HOW WE GET THERE: enter ON the rail — LONG only if a poke into {S:,.0f} RECLAIMS (target the {R:,.0f} magnet;")
print(f"      let a runner ride only if it ACCEPTS through); SHORT only if a tag of {R:,.0f} REJECTS. Time it with check.py at the level.")
print("  Read-only — best-entry math for the standing scenario; the trade and sizing are yours. Not financial advice.")
