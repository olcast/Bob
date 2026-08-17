#!/usr/bin/env python3
"""Own-lines engine: pivot-based trendlines + horizontals + multi-TF confluence."""
import json, time, datetime, urllib.request, sys
API="https://api.hyperliquid.xyz/info"
def fetch(coin, interval, days):
    end=int(time.time()*1000); start=end-days*86400_000
    r=urllib.request.Request(API,data=json.dumps({"type":"candleSnapshot","req":{"coin":coin,"interval":interval,"startTime":start,"endTime":end}}).encode(),headers={"Content-Type":"application/json"})
    return sorted(json.load(urllib.request.urlopen(r,timeout=30)),key=lambda k:k["t"])
def pivots(H,L,k):
    ph=[i for i in range(k,len(H)-k) if H[i]==max(H[i-k:i+k+1])]
    pl=[i for i in range(k,len(L)-k) if L[i]==min(L[i-k:i+k+1])]
    return ph,pl
def atr(cd,n=14):
    trs=[max(float(c["h"])-float(c["l"]),abs(float(c["h"])-float(cd[i-1]["c"] if i else c["o"])),abs(float(c["l"])-float(cd[i-1]["c"] if i else c["o"]))) for i,c in enumerate(cd)]
    return sum(trs[-n:])/n
def lines(cd, side, piv, vals, tol, min_sep=3):
    """lines through pivot pairs; score by touches; reject if badly violated between/after anchors."""
    out=[]
    n=len(cd)
    for a in range(len(piv)):
        for b in range(a+1,len(piv)):
            i,j=piv[a],piv[b]
            if j-i<min_sep: continue
            m=(vals[j]-vals[i])/(j-i); c0=vals[i]-m*i
            viol=0; touches=0
            for x in range(i,n):
                lv=m*x+c0
                d=vals[x]-lv
                if side=="res" and d> tol*1.5: viol+=1
                if side=="sup" and d< -tol*1.5: viol+=1
                if abs(d)<=tol: touches+=1
            if viol> (n-i)*0.03: continue   # broken line
            if touches<3: continue
            out.append({"m":m,"c":c0,"t":touches,"i":i,"j":j,"now":m*(n-1)+c0})
    # dedup near-identical lines, keep best-touched
    out.sort(key=lambda l:-l["t"])
    kept=[]
    for l in out:
        if all(abs(l["now"]-k2["now"])>tol or abs(l["m"]-k2["m"])>abs(l["m"])*0.5+1e-9 for k2 in kept):
            kept.append(l)
    return kept[:4]
def tf_scan(coin, interval, days, k, label, weight):
    cd=fetch(coin,interval,days)
    if len(cd)<40: return None
    H=[float(c["h"]) for c in cd]; L=[float(c["l"]) for c in cd]
    A=atr(cd); tol=A*0.35
    ph,pl=pivots(H,L,k)
    res=lines(cd,"res",ph,H,tol); sup=lines(cd,"sup",pl,L,tol)
    mark=float(cd[-1]["c"])
    # horizontals: last untapped swing H/L
    hz=[]
    for i in ph[-8:]:
        if all(H[x]<H[i] for x in range(i+1,len(cd))): hz.append(("swingH",H[i]))
    for i in pl[-8:]:
        if all(L[x]>L[i] for x in range(i+1,len(cd))): hz.append(("swingL",L[i]))
    def bars_per_day(iv): return {"15m":96,"1h":24,"4h":6,"1d":1}[iv]
    objs=[]
    for l in sup: objs.append({"type":"TL-sup","tf":label,"now":l["now"],"slope_d":l["m"]*bars_per_day(interval),"touch":l["t"],"w":weight*l["t"]})
    for l in res: objs.append({"type":"TL-res","tf":label,"now":l["now"],"slope_d":l["m"]*bars_per_day(interval),"touch":l["t"],"w":weight*l["t"]})
    for t,v in hz: objs.append({"type":t,"tf":label,"now":v,"slope_d":0,"touch":1,"w":weight*2})
    return {"mark":mark,"objs":objs,"atr":A}
def confluence(all_objs, mark, tolpct=0.004, maxdist=0.15):
    all_objs=[o for o in all_objs if abs(o["now"]-mark)<=mark*maxdist]
    zones=[]
    objs=sorted(all_objs,key=lambda o:o["now"])
    used=[False]*len(objs)
    for i,o in enumerate(objs):
        if used[i]: continue
        grp=[o]; used[i]=True
        for j2 in range(i+1,len(objs)):
            if used[j2]: continue
            if abs(objs[j2]["now"]-o["now"])<=mark*tolpct: grp.append(objs[j2]); used[j2]=True
        if len(grp)>=2 or grp[0]["w"]>=8:
            lo=min(g["now"] for g in grp); hi=max(g["now"] for g in grp)
            zones.append({"lo":lo,"hi":hi,"score":sum(g["w"] for g in grp),
                          "n":len(grp),"tfs":sorted(set(g["tf"] for g in grp)),
                          "mix":sorted(set(g["type"] for g in grp))})
    return sorted(zones,key=lambda z:-z["score"])
def run(coin, plan):
    allo=[]; mark=None
    for interval,days,k,label,w in plan:
        r=tf_scan(coin,interval,days,k,label,w)
        if not r: continue
        mark=r["mark"]; allo+=r["objs"]
        for o in sorted(r["objs"],key=lambda o:-o["w"])[:4]:
            print(f"  [{label}] {o['type']:8s} now {o['now']:10.1f}  slope {o['slope_d']:+8.1f}/d  touches {o['touch']}")
    print(f"\n  == CONFLUENCE ZONES ({coin}, mark {mark:.1f}) ==")
    for z in confluence(allo,mark)[:7]:
        pos="ABOVE" if z["lo"]>mark else ("BELOW" if z["hi"]<mark else "AT")
        print(f"  {pos:5s} {z['lo']:.0f}-{z['hi']:.0f}  score {z['score']:.0f}  objects {z['n']} {z['mix']} TFs {z['tfs']}")
if __name__=="__main__":
    now=datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M UTC")
    for coin in sys.argv[1:] or ["xyz:SP500","BTC"]:
        print(f"\n===== {coin} — own-lines scan {now} =====")
        run(coin,[("15m",4,3,"15m",1),("1h",14,3,"1h",2),("4h",45,3,"4h",4),("1d",300,2,"1d",8)])
