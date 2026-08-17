#!/usr/bin/env python3
"""PULSE — the quick at-a-level flow check (OLIVIER): does volume + CVD CONFIRM the current push
(-> CONTINUATION, let it run) or is it FADING / DIVERGING (-> FAKE, fade / expect reversal)? This is
THE READ step 4 (signals + RATE-OF-CHANGE adjudicate) made instant — run it when price reaches a magnet /
level to call continue-vs-fake. BTC only, 5m + 1h, read-only, ~2 seconds.
Usage:  python3 pulse.py            (current flow)
        python3 pulse.py 63474      (also show distance to a target level)"""
import json,urllib.request,time,statistics,sys
API="https://api.hyperliquid.xyz/info"
def post(b):
    try:
        r=urllib.request.Request(API,data=json.dumps(b).encode(),headers={"Content-Type":"application/json"});return json.load(urllib.request.urlopen(r,timeout=30))
    except Exception:return None
def candles(iv,bars):
    step={'5m':300000,'1h':3600000}[iv];end=int(time.time()*1000)
    d=post({"type":"candleSnapshot","req":{"coin":"BTC","interval":iv,"startTime":end-bars*step,"endTime":end}}) or []
    return d
def pulse(d):
    O=[float(c['o']) for c in d];C=[float(c['c']) for c in d];V=[float(c['v']) for c in d];n=len(C)
    base=statistics.mean(V[-7:-1]) or 1e-9; exp=V[-1]/base-1                       # volume vs prior-6 baseline
    sv=[(1 if C[i]>=O[i] else -1)*V[i] for i in range(n)];cvd=[0.0]*n
    for i in range(1,n):cvd[i]=cvd[i-1]+sv[i]
    slope=cvd[-1]-cvd[-7] if n>=7 else 0.0                                         # CVD slope (buy/sell) last 6
    accel=slope-((cvd[-7]-cvd[-13]) if n>=13 else 0.0)                             # is that flow accelerating?
    pdir=1 if C[-1]>C[-7] else -1                                                  # recent price direction
    confirm=(slope>0)==(pdir>0)                                                    # CVD moving WITH price?
    if exp>0.20 and confirm and accel*pdir>0:
        v="CONFIRMING -> CONTINUATION  (flow backs the push — let it run)"
    elif exp<-0.10 or (not confirm) or accel*pdir<0:
        v="FADING/DIVERGING -> FAKE risk  (flow not backing the push — fade / expect reversal)"
    else:
        v="NEUTRAL  (no clear flow signal yet)"
    return C[-1],exp,slope,accel,pdir,v

print(f"PULSE — BTC flow check  {time.strftime('%Y-%m-%d %H:%M UTC',time.gmtime())}")
tgt=None
if len(sys.argv)>1:
    try:tgt=float(sys.argv[1].replace(',',''))
    except Exception:tgt=None
px=None
for iv,bars in [('5m',36),('1h',24)]:
    d=candles(iv,bars)
    if len(d)>=3: d=d[:-1]   # drop the still-forming bar (its partial volume reads as a false 'fade')
    if not d:print(f"  {iv}: no data");continue
    px,exp,slope,accel,pdir,v=pulse(d)
    print(f"  {iv}: px {px:,.0f} · vol {exp:+.0%} ({'EXPANDING' if exp>0.2 else ('fading' if exp<-0.1 else 'flat')}) · "
          f"CVD {'+buy' if slope>0 else '-sell'} slope {slope:+.0f} · accel {accel:+.0f} · price {'UP' if pdir>0 else 'DOWN'}")
    print(f"       -> {v}")
if tgt and px:
    print(f"\n  target {tgt:,.0f}: {tgt-px:+,.0f} away. When price reaches it, re-run pulse: CONFIRMING => it continues "
          f"through; FADING => fade it. (This is step-4 adjudication at the magnet.)")
print("\nRule: volume EXPANDING + CVD moving WITH price + accelerating = the push is real (continuation).")
print("Volume fading OR CVD diverging OR decelerating = the fake (reversal risk). Read-only.")
