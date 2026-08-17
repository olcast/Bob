# Liquidation-map capture (Coinglass, free tier, via browser) — P2 collector method

Coinglass returns the heatmap payload ENCRYPTED (`data:"<base64>"`, decrypted client-side),
and does not expose the chart lib globally. Capture the DECRYPTED matrix by hooking JSON.parse.

## Procedure (claude-in-chrome tools)
1. Navigate a tab to https://www.coinglass.com/pro/futures/LiquidationHeatMap (free tier OK; no login).
2. Install the hook (javascript_tool):
   ```js
   (()=>{ if(window.__jpInstalled){window.__jp=[];return;} window.__jp=[];
     const op=JSON.parse; JSON.parse=function(t){const r=op.apply(this,arguments);
       try{ if(typeof t==='string'&&t.length>2000){ window.__jpLast=r; } }catch(e){} return r;};
     window.__jpInstalled=true; })()
   ```
3. Force a refetch: click the circular REFRESH icon on the chart toolbar (or change timeframe/exchange
   dropdown). The refetch → decrypt → JSON.parse fires the hook.
4. Read `window.__jpLast`. Shape: { instrument, liq:[[xIdx,yIdx,valUSD],...], y:[price per row],
   prices:[[ts,o,h,l,c,vol],...], rangeHigh, rangeLow, updateTime, precision }.
5. Aggregate to a price profile:
   ```js
   (()=>{const d=window.__jpLast,{liq,y}=d;const p=new Float64Array(y.length);
     for(const e of liq){const yi=e[1],v=+e[2];if(yi>=0&&yi<y.length&&isFinite(v))p[yi]+=v;}
     const a=[];for(let i=0;i<y.length;i++)if(p[i]>0)a.push([+y[i],p[i]]);
     a.sort((x,z)=>z[1]-x[1]);return a.slice(0,20);})()
   ```
   Above current price = SHORT-liq (squeeze fuel); below = LONG-liq (drain targets).

## Windows / exchanges
Timeframe dropdown (default "24 hour") and exchange dropdown ("Binance BTC/USDT Perpetual") each trigger a
new fetch → new __jpLast. Sweep 24h/1M/... and Binance/OKX/Bybit by changing them and re-reading. All-exchange
aggregate + long windows may be Prime-gated on free tier.

## Caveats
Model-1 = leverage-ESTIMATED liquidation topology, cumulative intensity, NOT literal resting orders.
Single-exchange on free tier. Interactive-only (needs the browser + hook); no headless/cron path yet.
