#!/usr/bin/env python3
"""CHECK — the "is my move-2 armed?" run-now checker (OLIVIER). Given a DECISION level from the live scenario
(e.g. the 63,474 magnet: "tag = fake -> reject-short UNLESS it accepts >63,474"), answer the real question —
do I act at this level NOW? — via three tests: (a) has price REACHED the level, (b) has it ACCEPTED beyond it
(2 closed 5m + a closed 15m holding past it = the "unless" / continuation clause), (c) the FLOW at it
(volume + CVD rate-of-change). BTC only, read-only, ~2s.

Usage:  python3 check.py 63474            # default 'reject': you want to FADE a tag of the level
        python3 check.py 63474 reject     #   ARMED if it tags & rejects (no acceptance, flow not backing)
        python3 check.py 62800 reclaim    # 'reclaim': you want to GO WITH acceptance through the level
Read-only. Analysis, not a trade instruction."""
import json,urllib.request,time,statistics,sys
API="https://api.hyperliquid.xyz/info"
def post(b):
    try:
        r=urllib.request.Request(API,data=json.dumps(b).encode(),headers={"Content-Type":"application/json"});return json.load(urllib.request.urlopen(r,timeout=30))
    except Exception:return None
def closes(iv,bars):
    step={'5m':300000,'15m':900000}[iv];end=int(time.time()*1000)
    d=post({"type":"candleSnapshot","req":{"coin":"BTC","interval":iv,"startTime":end-bars*step,"endTime":end}}) or []
    return d[:-1] if len(d)>=2 else d      # closed bars only (drop the forming one)
def flow(d):
    O=[float(c['o']) for c in d];C=[float(c['c']) for c in d];V=[float(c['v']) for c in d];n=len(C)
    base=statistics.mean(V[-7:-1]) or 1e-9; exp=V[-1]/base-1
    sv=[(1 if C[i]>=O[i] else -1)*V[i] for i in range(n)];cvd=[0.0]*n
    for i in range(1,n):cvd[i]=cvd[i-1]+sv[i]
    return exp,(cvd[-1]-cvd[-7] if n>=7 else 0.0)

if len(sys.argv)<2:
    print("usage: python3 check.py <level> [reject|reclaim]"); sys.exit()
lvl=float(sys.argv[1].replace(',','')); mode=sys.argv[2] if len(sys.argv)>2 else "reject"
mid=float((post({'type':'allMids'}) or {}).get('BTC',0) or 0)
if not mid: print("price unavailable (allMids failed) — try again in a moment."); sys.exit()
d5=closes('5m',24); d15=closes('15m',16)
c5=[float(c['c']) for c in d5];h5=[float(c['h']) for c in d5];l5=[float(c['l']) for c in d5]
c15=[float(c['c']) for c in d15]
band=lvl*0.0007
above = lvl>mid                                                   # level sits ABOVE price?
reached = (max(h5[-6:])>=lvl-band) if above else (min(l5[-6:])<=lvl+band)
if above: accepted = c5[-1]>lvl and c5[-2]>lvl and (c15[-1]>lvl if c15 else False)
else:     accepted = c5[-1]<lvl and c5[-2]<lvl and (c15[-1]<lvl if c15 else False)
exp,slope=flow(d5)
# is the PUSH into the level being backed by flow? (up-push wants +CVD; down-push wants -CVD)
push_backed = (slope>0 and exp>0) if above else (slope<0 and exp>0)
push_failing = (exp<-0.1) or (slope<0 if above else slope>0)

print(f"CHECK — BTC {mid:,.0f}  vs {lvl:,.0f} [{mode}]  {time.strftime('%H:%M UTC',time.gmtime())}")
print(f"  distance {lvl-mid:+,.0f} · recent 5m high {max(h5[-6:]):,.0f} / low {min(l5[-6:]):,.0f}")
print(f"  reached {lvl:,.0f}? {'YES' if reached else 'no'} · accepted {'above' if above else 'below'} it? "
      f"{'YES (2x5m+15m closed through)' if accepted else 'no'} · flow: vol {exp:+.0%}, CVD {slope:+.0f}")
if not reached:
    print(f"  VERDICT: NOT THERE YET — {lvl-mid:+,.0f} away. Nothing armed. Re-run when price tags {lvl:,.0f}.")
elif mode=="reject":
    if accepted:
        print(f"  VERDICT: VOIDED (continuation) — price ACCEPTED through {lvl:,.0f} (the 'unless' clause fired).")
        print(f"           Do NOT fade it. This is the go-with; the reversal scenario is off.")
    elif push_failing:
        print(f"  VERDICT: REJECT ARMED — tagged {lvl:,.0f}, NO acceptance, flow not backing the push.")
        print(f"           The fade/reject is on (your reject-{'short' if above else 'long'}).")
    else:
        print(f"  VERDICT: WAIT — at {lvl:,.0f} but flow still backing the push and no failure yet.")
        print(f"           Let it prove rejection (a close back off the level) before you fade.")
else:  # reclaim / go-with
    if accepted and push_backed:
        print(f"  VERDICT: RECLAIM ARMED — accepted through {lvl:,.0f} with flow backing it. The go-with is on.")
    else:
        print(f"  VERDICT: WAIT — not a clean accepted reclaim yet (need 2x5m+15m close through {lvl:,.0f} + flow backing).")
print("  Read-only. Analysis, not a trade instruction.")
