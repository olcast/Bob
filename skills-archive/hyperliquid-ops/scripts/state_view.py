#!/usr/bin/env python3
"""JOINT MARKET-STATE VIEW (OLIVIER: 'you always have to SEE ALL DIMENSIONS AT THE SAME TIME, their
relationships'). The antidote to the infinite-combination / Elliott trap (#46) is NOT to reduce to one
univariate signal — it is to hold the market as ONE joint state vector and read the CONFIGURATION across
every dimension at once, plus how the dimensions relate. Testing dimensions one pair at a time = the
Elliott trap; reading them jointly, with a mechanism + forward test, is the disciplined form of the same
holism. BTC ONLY, HL perp × HL spot, 1h. Read-only, descriptive. Prints: (A) the STATE VECTOR right now —
every dimension's current value + trailing-percentile/regime label, on one screen; (B) the RELATIONSHIP
MATRIX — how the dimensions co-move (which are decorrelated = independent information, which are redundant);
(C) the CONFLUENCE READ — which dimensions currently AGREE vs CONTRADICT, and whether the joint config is
one of the pre-registered signal regions (PREREG-reversal-x-basis.md). The signal is a REGION of this
state, never a dimension in isolation."""
import statistics, math, bisect, urllib.request, json, time
from edge_ensemble import fetch, atr, E_resreject, E_pokereclaim
API="https://api.hyperliquid.xyz/info"
def post(b):
    try:
        r=urllib.request.Request(API,data=json.dumps(b).encode(),headers={"Content-Type":"application/json"});return json.load(urllib.request.urlopen(r,timeout=60))
    except Exception:return None
def spot_closes(days):
    step=3600000;end=int(time.time()*1000);cur=end-days*86400_000;seen={}
    while cur<end:
        d=post({"type":"candleSnapshot","req":{"coin":"@142","interval":"1h","startTime":cur,"endTime":min(cur+4800*step,end)}}) or []
        if not d:cur+=4800*step;continue
        for c in d:seen[int(c['t'])]=float(c['c'])
        cur=max(int(c['t']) for c in d)+step
    return seen
def funding_map(days):
    end=int(time.time()*1000);cur=end-days*86400_000;seen={}
    while cur<end:
        d=post({"type":"fundingHistory","coin":"BTC","startTime":cur,"endTime":min(cur+19*86400_000,end)}) or []
        if not d:cur+=19*86400_000;continue
        for r in d:seen[int(r['time'])]=float(r['fundingRate'])
        nt=max(int(r['time']) for r in d)
        if nt<=cur:break
        cur=nt+1
    return seen

cd=fetch("1h",200);O=[float(c['o']) for c in cd];H=[float(c['h']) for c in cd];L=[float(c['l']) for c in cd]
C=[float(c['c']) for c in cd];V=[float(c['v']) for c in cd];T=[int(c['t']) for c in cd];n=len(C);A=atr(H,L,C)
sp=spot_closes(200);fu=funding_map(180);fk=sorted(fu)

# ===== the DIMENSIONS (one scalar per 1h bar; a joint state vector) =====
trend =[ (C[i]/C[i-24]-1) if i>=24 else 0.0 for i in range(n)]                       # D1 impulse/trend (signed trailing move)
def eff(i,W=24):                                                                     # D2 regime: efficiency ratio (high=trend, low=range)
    if i-W<0: return 0.0
    num=abs(C[i]-C[i-W]); den=sum(abs(C[j]-C[j-1]) for j in range(i-W+1,i+1)) or 1e-9; return num/den
effr=[eff(i) for i in range(n)]
basis=[None]*n
for i in range(n):
    s=sp.get(T[i]); basis[i]=(C[i]/s-1)*1e4 if s else None                           # D3 positioning: perp-spot basis (bp)
fund=[None]*n
for i in range(n):
    j=bisect.bisect_right(fk,T[i])-1; fund[i]=fu[fk[j]] if j>=0 else None            # D4 funding (per hr)
falign=[ (fund[i]*(1 if trend[i]>0 else -1)) if fund[i] is not None else None for i in range(n)]  # funding paying the trend side
volexp=[0.0]*n
for i in range(4,n):
    b=statistics.mean(V[i-3:i]) or 1e-9; volexp[i]=V[i]/b-1                          # D5 flow: volume expansion vs 3-bar base
sv=[ (1 if C[i]>=O[i] else -1)*V[i] for i in range(n)];cvd=[0.0]*n
for i in range(1,n): cvd[i]=cvd[i-1]+sv[i]
cvdslope=[ (cvd[i]-cvd[i-6]) if i>=6 else 0.0 for i in range(n)]                     # D5b flow: candle-CVD-proxy slope
# D6 price-structure trigger: +1 poke-reclaim (long setup) / -1 resTL-reject (short setup) / 0 none
setup=[0]*n
for i,_ in E_pokereclaim(O,H,L,C,n,6,12): setup[i]=1
for i,_ in E_resreject(O,H,L,C,n,6,12): setup[i]=-1

def tpct(series,i,win=1440):                                                        # trailing percentile (past-only, no look-ahead)
    lo=max(0,i-win);hist=[x for x in series[lo:i] if x is not None]
    if len(hist)<20 or series[i] is None: return None
    return sum(1 for x in hist if x<=series[i])/len(hist)

# ===== (A) STATE VECTOR NOW =====
i=n-1
def lab(p,hi=.7,lo=.3):
    return "—" if p is None else ("HIGH/extreme" if p>=hi else ("LOW/extreme" if p<=lo else "mid"))
bp=tpct(basis,i);fp=tpct(fund,i);ep=tpct(effr,i);vp=tpct(volexp,i);tp=tpct([abs(x) for x in trend],i)
print(f"=========== JOINT STATE — BTC 1h  (bar {i}, {n} bars, HL perp × spot @142) ===========")
print(f"  D1 TREND (24h move)        {trend[i]*100:+6.2f}%      |move| pctile {tp if tp is None else round(tp,2)}  [{lab(tp)}]")
print(f"  D2 REGIME (efficiency)     {effr[i]:6.2f}       pctile {ep if ep is None else round(ep,2)}  [{'TRENDING' if (ep or 0)>=.7 else ('RANGING' if (ep or 1)<=.3 else 'mixed')}]")
print(f"  D3 POSITIONING (basis bp)  {('%+6.1f'%basis[i]) if basis[i] is not None else '   n/a'}      pctile {bp if bp is None else round(bp,2)}  [{'PERP PREMIUM' if (bp or 0)>=.7 else ('PERP DISCOUNT' if (bp or 1)<=.3 else 'flat')}]")
print(f"  D4 FUNDING (/hr)           {('%+.2e'%fund[i]) if fund[i] is not None else '  n/a'}   pctile {fp if fp is None else round(fp,2)}  aligned={('%+.1e'%falign[i]) if falign[i] is not None else 'n/a'}")
print(f"  D5 FLOW volexp / CVDslope  {volexp[i]:+6.2f} / {cvdslope[i]:+.0f}   volexp pctile {vp if vp is None else round(vp,2)}  [{'EXPANDING' if (vp or 0)>=.7 else ('QUIET' if (vp or 1)<=.3 else 'normal')}]")
print(f"  D6 PRICE-STRUCTURE setup   {'poke-reclaim LONG' if setup[i]==1 else ('resTL-reject SHORT' if setup[i]==-1 else 'none')}")

# ===== (B) RELATIONSHIP MATRIX (how the dimensions co-move) =====
dims={"trend":trend,"regime":effr,"basis":basis,"funding":fund,"volexp":volexp,"cvdslp":cvdslope}
def corr(a,b):
    xs=[(a[k],b[k]) for k in range(n) if a[k] is not None and b[k] is not None]
    if len(xs)<50: return 0.0
    xa=[p[0] for p in xs];xb=[p[1] for p in xs];m=len(xs);ma=sum(xa)/m;mb=sum(xb)/m
    va=math.sqrt(sum((x-ma)**2 for x in xa));vb=math.sqrt(sum((x-mb)**2 for x in xb))
    return sum((xa[k]-ma)*(xb[k]-mb) for k in range(m))/(va*vb) if va>0 and vb>0 else 0.0
names=list(dims)
print("\n=========== RELATIONSHIPS — dimension co-movement (|r|<0.2 = independent info; high = redundant) ===========")
print("          "+"  ".join(f"{x:>7}" for x in names))
for a in names: print(f"  {a:7s} "+"  ".join(f"{corr(dims[a],dims[b]):>7.2f}" for b in names))

# ===== (C) CONFLUENCE READ — do the dimensions AGREE right now, and is this a pre-registered signal region? =====
print("\n=========== CONFLUENCE READ (the joint configuration, tied to mechanism #41/#43/#45) ===========")
si = max(0, n-2)   # last CLOSED bar — the detectors never set the forming bar n-1 (was dead code reading setup[n-1]==0)
armS = setup[si]==-1 and bp is not None and bp>=0.7
armL = setup[si]==1  and bp is not None and bp<=0.3
if armS: print("  >>> S-LEG ARMED: resTL-reject SHORT × perp-PREMIUM (crowded longs trapped) — pre-reg region hit.")
elif armL: print("  >>> L-LEG ARMED: poke-reclaim LONG × perp-DISCOUNT (crowded shorts trapped) — pre-reg region hit.")
elif setup[si]!=0: print(f"  price-structure fired ({'SHORT' if setup[si]==-1 else 'LONG'}) but POSITIONING does NOT confirm (basis pctile {bp}). Per #45, price alone = weak. No region.")
else: print("  no price-structure trigger on the last bar. State is informational only (watch basis + regime + funding for the setup to arm).")
print("  Mechanism check: a reversal is a leverage-harvest (#43); it is a SIGNAL only when the basis says")
print("  the offside crowd is trapped (#45, basis LEADS #46) and ideally funding has bled them (#41).")
print("\nRead ALL SIX rows together, not one at a time (that is the Elliott trap). The signal is a REGION of")
print("this vector; the relationship matrix says which rows are independent evidence vs the same bet twice.")
print("Descriptive + read-only. The pre-registered region is judged FORWARD (PREREG-reversal-x-basis.md).")
