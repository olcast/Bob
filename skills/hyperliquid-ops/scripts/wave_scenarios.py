#!/usr/bin/env python3
"""WAVE SCENARIOS — Elliott made FALSIFIABLE (OLIVIER's synthesis). Not wave-labelling as prediction; use
the swing structure ACROSS TIMEFRAMES to (1) ENUMERATE the scenario space — after an impulse leg A->B, the
retrace into the 0.382-0.618 Fib zone either HOLDS and the trend resumes (scenario R = continuation) or
BREAKS through (scenario C = trendline-break / reversal) — and (2) LABEL which actually happened forward.
Then ask OLIVIER's real question: which SIGNALS, and which RATE-OF-CHANGE of signals, at the moment price
entered the zone, discriminated R from C? Elliott stops being unfalsifiable the instant you enumerate the
competing scenarios as concrete levels and let forward data + signals adjudicate (satisfies #46, not
violates it). BTC ONLY, HL, 1h + 4h. No stop/cost. Read-only, in-sample-discovery — owes the usual gate.
The current read prints the live retrace zone (next reversal-vs-break levels) and which scenario today's
signals+RoC favour."""
import json,urllib.request,time,statistics,math,bisect
API="https://api.hyperliquid.xyz/info"; TFMS={'5m':300000,'1h':3600000,'4h':14400000}
def post(b):
    try:
        r=urllib.request.Request(API,data=json.dumps(b).encode(),headers={"Content-Type":"application/json"});return json.load(urllib.request.urlopen(r,timeout=60))
    except Exception:return None
def candles(coin,iv,days):
    step=TFMS[iv];end=int(time.time()*1000);cur=end-int(days*86400_000);seen={}
    while cur<end:
        d=post({"type":"candleSnapshot","req":{"coin":coin,"interval":iv,"startTime":cur,"endTime":min(cur+4800*step,end)}}) or []
        if not d:cur+=4800*step;continue
        for c in d:seen[c['t']]=c
        cur=max(c['t'] for c in d)+step
    return [seen[t] for t in sorted(seen)]
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

def atr(H,L,C,n=14):
    tr=[H[0]-L[0]]
    for i in range(1,len(C)):tr.append(max(H[i]-L[i],abs(H[i]-C[i-1]),abs(L[i]-C[i-1])))
    o=[None]*len(C);s=0
    for i in range(len(C)):
        s+=tr[i]
        if i>=n:s-=tr[i-n];o[i]=s/n
        else:o[i]=s/(i+1)
    return o
def zigzag(H,L,thr):
    n=len(H);piv=[];hi_i,hi,lo_i,lo,d=0,H[0],0,L[0],0
    for i in range(1,n):
        if d>=0:
            if H[i]>=hi:hi,hi_i=H[i],i
            if L[i]<=hi*(1-thr):piv.append((hi_i,hi,1));d=-1;lo,lo_i=L[i],i;continue
        if d<=0:
            if L[i]<=lo:lo,lo_i=L[i],i
            if H[i]>=lo*(1+thr):piv.append((lo_i,lo,-1));d=1;hi,hi_i=H[i],i
    return piv

def run(coin,iv,days,thr,H,fmap):
    cd=candles(coin,iv,days);O=[float(c['o']) for c in cd];Hh=[float(c['h']) for c in cd];L=[float(c['l']) for c in cd]
    C=[float(c['c']) for c in cd];V=[float(c['v']) for c in cd];T=[int(c['t']) for c in cd];n=len(C);A=atr(Hh,L,C)
    amed=statistics.median([x for x in A[100:] if x])
    # per-bar signal series
    def eff(i,W=24):
        if i-W<0:return None
        num=abs(C[i]-C[i-W]);den=sum(abs(C[i-k]-C[i-1-k]) for k in range(W)) or 1e-9;return num/den
    EFF=[eff(i) for i in range(n)]
    VX=[None]*n
    for i in range(4,n):
        b=statistics.mean(V[i-3:i]) or 1e-9;VX[i]=V[i]/b-1
    sv=[(1 if C[i]>=O[i] else -1)*V[i] for i in range(n)];cvd=[0.0]*n
    for i in range(1,n):cvd[i]=cvd[i-1]+sv[i]
    CS=[(cvd[i]-cvd[i-6]) if i>=6 else None for i in range(n)]
    fk=sorted(fmap);FU=[None]*n
    for i in range(n):
        j=bisect.bisect_right(fk,T[i])-1;FU[i]=fmap[fk[j]] if j>=0 else None
    piv=zigzag(Hh,L,thr)
    # map: for each bar, index of last confirmed pivot (confirmed = we passed enough reversal). Approx: pivot k
    # is 'known' once price reversed thr from it; use pivot index+? Conservative: known at the NEXT pivot's index.
    conf=[]  # (confirm_bar_index, pivotpos_index, price, type)
    for k in range(1,len(piv)):
        conf.append((piv[k][0], piv[k-1][0], piv[k-1][1], piv[k-1][2]))  # pivot k-1 is confirmed by the time pivot k forms
    rows=[]
    ci=0
    for k in range(2,len(piv)):
        # leg A->B: A=piv[k-2], B=piv[k-1]; B is a confirmed extreme; retrace leg is toward the current
        A0i,A0p,_=piv[k-2]; Bi,Bp,Bt=piv[k-1]
        rng=abs(Bp-A0p)
        if rng<=0: continue
        up = Bt==1  # B is a swing HIGH -> prior leg was UP -> retrace is DOWN into the zone
        if up:
            r50=Bp-0.5*rng; r24=Bp-0.236*rng; r76=Bp-0.764*rng
        else:
            r50=Bp+0.5*rng; r24=Bp+0.236*rng; r76=Bp+0.764*rng
        # zone entry: first bar after Bi where price touches r50 (causal; B is confirmed by construction since retrace>thr)
        z=None
        for j in range(Bi+1, min(Bi+1+H*2, n)):
            if (up and L[j]<=r50) or ((not up) and Hh[j]>=r50): z=j; break
        if z is None: continue
        # outcome forward from z within H: R (trend resumes -> back toward B past r24) vs C (break past r76)
        y=None
        for j in range(z, min(z+H, n)):
            if up:
                if Hh[j]>=r24: y=1; break      # recovered up toward B -> up-trend resumes (continuation)
                if L[j]<=r76: y=-1; break       # sliced down through zone -> trendline break / reversal
            else:
                if L[j]<=r24: y=1; break         # resumed down toward B -> down-trend resumes
                if Hh[j]>=r76: y=-1; break        # broke up -> trendline break / reversal
        if y is None: continue
        # features + rate-of-change at zone entry z (causal)
        def d(series,k=6):
            return (series[z]-series[z-k]) if (z-k>=0 and series[z] is not None and series[z-k] is not None) else None
        feat={
          'eff':EFF[z], 'd_eff':d(EFF),
          'volexp':VX[z], 'd_volexp':d(VX),
          'cvd_slope':CS[z], 'd_cvd':d(CS),
          'px_vel':(C[z]/C[z-6]-1) if z>=6 else None,
          'atr_compress':(A[z]/amed) if A[z] else None,
          'funding':FU[z], 'd_funding':d(FU),
          'legdir': 1 if up else -1,
        }
        rows.append((z,y,feat))
    return C,T,piv,rows,amed,A,EFF,VX,CS,FU,n

def pbcorr(pairs):
    xs=[p[0] for p in pairs if p[0] is not None];ys=[p[1] for p in pairs if p[0] is not None]
    if len(xs)<20:return None,len(xs)
    mx=sum(xs)/len(xs);my=sum(ys)/len(ys)
    vx=math.sqrt(sum((x-mx)**2 for x in xs));vy=math.sqrt(sum((y-my)**2 for y in ys))
    if vx==0 or vy==0:return 0.0,len(xs)
    return sum((xs[i]-mx)*(ys[i]-my) for i in range(len(xs)))/(vx*vy),len(xs)

fmap=funding_map(180)
print("WAVE SCENARIOS — Elliott made falsifiable: retrace zone HOLDS (R=trend resumes) vs BREAKS (C=reversal),")
print("and which signals + RATE-OF-CHANGE discriminated. BTC. DISCOVERY/in-sample.\n")
STATE={}
for iv,days,thr,H in [("1h",300,0.012,96),("4h",300,0.03,60)]:
    C,T,piv,rows,amed,A,EFF,VX,CS,FU,n=run("BTC",iv,days,thr,H,fmap)
    nR=sum(1 for _,y,_ in rows if y==1);nC=sum(1 for _,y,_ in rows if y==-1);tot=nR+nC
    print(f"===== {iv} — {len(piv)} swings, {tot} zone-decisions  |  R (trend resumes) {100*nR/max(1,tot):.0f}%  ·  C (break/reversal) {100*nC/max(1,tot):.0f}% =====")
    feats=['eff','d_eff','volexp','d_volexp','cvd_slope','d_cvd','px_vel','atr_compress','funding','d_funding','legdir']
    scored=[]
    for f in feats:
        r,nn=pbcorr([(row[2][f],row[1]) for row in rows])
        if r is not None: scored.append((abs(r),r,f,nn))
    scored.sort(reverse=True)
    print("   top discriminators (|point-biserial r| with outcome; +r => higher value favours R=trend-resumes):")
    for ar,r,f,nn in scored[:6]:
        favor = "R trend-resumes" if r>0 else "C break/reversal"
        tag = "  <-- rate-of-change" if f.startswith('d_') or f=='px_vel' else ""
        print(f"     {f:14s} r={r:+.2f} (n={nn})  higher -> {favor}{tag}")
    STATE[iv]=(C,T,piv,rows,amed,A,EFF,VX,CS,FU,n)
    print()

# ---- CURRENT READ (1h leg + 4h context) ----
print("===== CURRENT READ — where the wave structure puts the next reversal-vs-break zone =====")
for iv in ("4h","1h"):
    C,T,piv,rows,amed,A,EFF,VX,CS,FU,n=STATE[iv]
    if len(piv)<2:
        print(f"  {iv}: too few swings"); continue
    Bi,Bp,Bt=piv[-1];A0i,A0p,_=piv[-2];rng=abs(Bp-A0p);up=Bt==1;px=C[-1]
    if up: r38,r50,r61,r76=Bp-0.382*rng,Bp-0.5*rng,Bp-0.618*rng,Bp-0.764*rng
    else:  r38,r50,r61,r76=Bp+0.382*rng,Bp+0.5*rng,Bp+0.618*rng,Bp+0.764*rng
    legdesc = "UP leg (last swing = HIGH; retrace DOWN)" if up else "DOWN leg (last swing = LOW; retrace UP)"
    print(f"  {iv}: last {legdesc}  A {A0p:,.0f} -> B {Bp:,.0f}  (leg ${rng:,.0f})   px {px:,.0f}")
    print(f"       Fib retrace zone (the DECISION area): .382 {r38:,.0f} · .5 {r50:,.0f} · .618 {r61:,.0f} · .786(break) {r76:,.0f}")
    # where is price
    frac = (Bp-px)/rng if up else (px-Bp)/rng
    loc = "past B (impulse extending)" if frac<0 else ("in/near the zone" if 0.30<=frac<=0.80 else ("shallow (<.382)" if frac<0.30 else "beyond .786 = BREAK confirmed"))
    print(f"       price is at {frac*100:+.0f}% retrace -> {loc}")
    # today's signal lean (last bar) using the sign the discriminators implied qualitatively
    eff0=EFF[-1];dv=(VX[-1] if VX[-1] is not None else 0);cs=(CS[-1] if CS[-1] is not None else 0)
    print(f"       live signals: efficiency {eff0:.2f} ({'trending' if (eff0 or 0)>=.5 else 'coil'}) · vol-exp {VX[-1] if VX[-1] is not None else float('nan'):+.2f} · cvd-slope {cs:+.0f} · atr-compress {A[-1]/amed:.2f}")
    # FIB TIME — WHEN, not just where: bars since the last pivot B vs Fibonacci counts (time symmetry)
    step_h={'1h':1,'4h':4}[iv]; barsB=(n-1)-Bi; fibs=[5,8,13,21,34,55,89]
    near=[f for f in fibs if abs(barsB-f)<=1]; nxt=[f for f in fibs if f>barsB][:3]
    def _when(f): return time.strftime('%m-%d %H:%M',time.gmtime((T[Bi]+f*step_h*3600000)/1000))
    tmsg=(f"AT Fib-time {near[0]} bars — a turn is DUE" if near else "next Fib-time windows -> "+", ".join(f"{f}b={_when(f)}" for f in nxt))
    print(f"       FIB TIME: {barsB} bars since B ({time.strftime('%a %m-%d %H:%M',time.gmtime(T[Bi]/1000))}, {barsB*step_h}h ago) -> {tmsg}")
# ---- 5m MICRO-STRUCTURE — the live tape the coarse TFs miss (#49: don't call a path dead against it) ----
d5=candles("BTC","5m",1)
if len(d5)>=20:
    H5=[float(c['h']) for c in d5];L5=[float(c['l']) for c in d5];C5=[float(c['c']) for c in d5];n5=len(C5)
    sh=[i for i in range(3,n5-3) if H5[i]==max(H5[i-3:i+4])][-3:]
    sl=[i for i in range(3,n5-3) if L5[i]==min(L5[i-3:i+4])][-3:]
    hh=len(sh)>=2 and H5[sh[-1]]>H5[sh[-2]]; hl=len(sl)>=2 and L5[sl[-1]]>L5[sl[-2]]
    ll=len(sl)>=2 and L5[sl[-1]]<L5[sl[-2]]; lh=len(sh)>=2 and H5[sh[-1]]<H5[sh[-2]]
    micro=("HIGHER HIGHS + HIGHER LOWS = up micro" if hh and hl else
           "HIGHER HIGHS = up push"               if hh else
           "LOWER LOWS + LOWER HIGHS = down micro" if ll and lh else
           "LOWER LOWS = down push"                if ll else "mixed / coiling")
    print(f"\n  5m MICRO (live tape): px {C5[-1]:,.0f} · recent highs {[round(H5[i]) for i in sh]} · lows {[round(L5[i]) for i in sl]} -> {micro}")
    print(f"     RECONCILE (#49): do NOT call the up-path dead while 5m prints HIGHER HIGHS above the make-or-break,")
    print(f"     nor the down-path dead while it prints LOWER LOWS. The coarse-TF/analog lean must not override the live 5m.")
print("\nHOW TO USE: the zone is WHERE (Fib price) + WHEN (Fib time above); the top discriminators + their rate-of-change")
print("are WHETHER it holds or breaks (signals adjudicate). Backtest above = which signals actually called it.")
print("In-sample discovery: the discriminators owe bootstrap-CI + OOS + the forward gate before ADMITTED (#46).")
