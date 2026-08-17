#!/usr/bin/env python3
"""CROSS-ASSET LEAD-LAG & BREADTH (OLIVIER) — per-asset, NEVER pooled (#37a); then the RELATIONSHIPS between
them. Universe: BTC, ETH, SOL, HYPE (crypto, 24/7) + xyz:SP500 (SPX) + xyz:XYZ100 (NDX) — HL's equity-index
perps, to test whether EQUITY RISK leads BTC. Each asset is read on its OWN; this layer asks four things:
(1) which move together — correlation; (2) does any asset LEAD BTC — cross-corr at lags = a usable BTC
predictor; (3) each alt's BETA to BTC; (4) does cross-asset BREADTH confirm or DIVERGE from BTC's move
(divergence = the warning, per #37a's breadth check). The xyz indices trade only US hours, so their
off-hours bars are STUBS — a flat (unchanged) bar is masked out as 'not trading'. HL only, no stop/cost,
read vs the honest nulls. DISCOVERY / in-sample — owes the firewall. This is NOT signal-pooling: every asset
keeps its own identity; we measure the edges BETWEEN them."""
import json,urllib.request,time,statistics,math
API="https://api.hyperliquid.xyz/info"
ASSETS=[("BTC","BTC"),("ETH","ETH"),("SOL","SOL"),("HYPE","HYPE"),("xyz:SP500","SPX"),("xyz:XYZ100","NDX")]
XYZ={"SPX","NDX"}; TFMS={'1h':3600000,'4h':14400000}
def post(b):
    try:
        r=urllib.request.Request(API,data=json.dumps(b).encode(),headers={"Content-Type":"application/json"});return json.load(urllib.request.urlopen(r,timeout=60))
    except Exception:return None
def candles(coin,iv,days):
    step=TFMS[iv];end=int(time.time()*1000);cur=end-int(days*86400_000);seen={}
    while cur<end:
        d=post({"type":"candleSnapshot","req":{"coin":coin,"interval":iv,"startTime":cur,"endTime":min(cur+4800*step,end)}}) or []
        if not d:cur+=4800*step;continue
        for c in d:seen[int(c['t'])]=float(c['c'])
        cur=max(int(c['t']) for c in d)+step
    return seen
def build(iv,days):
    raw={lab:candles(api,iv,days) for api,lab in ASSETS}
    common=sorted(set.intersection(*[set(raw[lab]) for _,lab in ASSETS])) if all(raw[lab] for _,lab in ASSETS) else []
    px={lab:[raw[lab][t] for t in common] for _,lab in ASSETS}
    R={}
    for _,lab in ASSETS:
        p=px[lab]; r=[None]*len(common)
        for i in range(1,len(p)):
            ch=p[i]/p[i-1]-1
            r[i]=None if (lab in XYZ and ch==0.0) else ch   # xyz flat bar = closed/stub -> mask
        R[lab]=r
    return common,px,R
def corr(a,b):
    xs=[(a[i],b[i]) for i in range(min(len(a),len(b))) if a[i] is not None and b[i] is not None]
    if len(xs)<30: return None
    A=[x[0] for x in xs];B=[x[1] for x in xs];m=len(xs);ma=sum(A)/m;mb=sum(B)/m
    va=math.sqrt(sum((x-ma)**2 for x in A));vb=math.sqrt(sum((x-mb)**2 for x in B))
    return (sum((A[i]-ma)*(B[i]-mb) for i in range(m))/(va*vb)) if va>0 and vb>0 else 0.0
def lead(a,b,L): return corr(a[:-L],b[L:])   # corr(a[t-L], b[t]) -> does a LEAD b?
labels=[lab for _,lab in ASSETS]

for iv,days in [('1h',180),('4h',300)]:
    common,px,R=build(iv,days)
    if not common: print(f"===== {iv}: no common history (xyz gap) ====="); continue
    print(f"===== {iv} — {len(common)} common bars (xyz masked to active/trading bars) =====")
    M={(a,b):corr(R[a],R[b]) for a in labels for b in labels}
    print("  corr(returns):     "+"  ".join(f"{l:>5}" for l in labels))
    for a in labels:
        print(f"    {a:5s} "+"  ".join((f"{M[(a,b)]:>5.2f}" if M[(a,b)] is not None else "   . ") for b in labels))
    print("  LEAD-LAG vs BTC (X-leads-BTC / BTC-leads-X at lag -> who):")
    for l in labels:
        if l=="BTC": continue
        row=[]
        for L in ([1,2,3] if iv=='1h' else [1,2]):
            xl=lead(R[l],R["BTC"],L); bx=lead(R["BTC"],R[l],L)
            if xl is None or bx is None: row.append(f"L{L}: ."); continue
            who="X" if xl>bx+0.02 else ("BTC" if bx>xl+0.02 else "~")
            row.append(f"L{L} {xl:+.2f}/{bx:+.2f}->{who}")
        pr=[(R[l][i],R["BTC"][i]) for i in range(len(common)) if R[l][i] is not None and R["BTC"][i] is not None]
        den=sum(y*y for _,y in pr); beta=(sum(x*y for x,y in pr)/den) if den>0 else float('nan')
        print(f"    {l:5s} beta~{beta:4.2f}  "+"   ".join(row))
    print()

# ---- CURRENT: 24h returns + breadth vs BTC ----
common,px,R=build('1h',20)
print("===== CURRENT cross-asset (last 24h % + breadth vs BTC) =====")
last={l:((px[l][-1]/px[l][-25]-1)*100 if len(px[l])>25 else float('nan')) for l in labels}
btc=last["BTC"]
for l in labels:
    conf="" if l=="BTC" else ("CONFIRMS" if (last[l]>0)==(btc>0) else "DIVERGES")
    print(f"    {l:5s} 24h {last[l]:+.2f}%   {conf}")
agree=sum(1 for l in labels if l!="BTC" and (last[l]>0)==(btc>0))
print(f"  breadth: {agree}/{len(labels)-1} confirm BTC's 24h direction -> {'ALIGNED' if agree>=3 else 'DIVERGENT (warning)'}")
print("\nRead: an asset that LEADS BTC (X > BTC at a lag) is a usable BTC predictor; BREADTH divergence (alts /")
print("equities not confirming BTC) is the #37a cross-asset warning. Per-asset, never pooled. DISCOVERY/in-sample —")
print("owes bootstrap-CI + OOS + forward before ADMITTED. Feeds THE READ as a cross-asset confluence/divergence lens.")
