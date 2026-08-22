# RAW FACTS PACKET — R5 — 2026-08-22 11:45 UTC
No thesis. No rails. No probability. Extract your own observations, then commit.

## Clock
- asOf 2026-08-22T11:45:35Z (orderflow) / 11:44:05Z (0a + packet)
- Weekend Saturday. xyz DARK / R-fiction live. BTC/ETH/SOL/HYPE = hard-stop venues (xyz clock no-op).
- 04–10 UTC distrust window is CLOSED (now 11 UTC).
- TOD (collector sample, NOT Hawkes): hour 11 |Δmark|/h 124.2 vs median 237.8, ratio 0.52. ticks=202.

## Event clock (72h)
- +4.3h CEX 8h funding stamp
- +20.3h Deribit BTC 23AUG26 (0DTE) OI=4007.5
- +44.3h Deribit BTC 24AUG26 weekly OI=2722.3
- +68.3h Deribit BTC 25AUG26 weekly OI=1601.9
- next macro: CPI (Aug 2026 data) in 480.8h
- Jackson Hole 27–29 Aug is OUTSIDE 72h
- No stamp inside 90m.

## Macro 0a live
- verdict VOID asOf 2026-08-22T11:44:05Z
- VOID Hyperliquid +4.25% mark 77.62
- VOID Solana +3.19% mark 93.39
- VOID Ether +2.10% mark 2,425
- STUBS (do not quote as prices): xyz:DXY, xyz:VIX
- BTC in 0a packet: 77,161 +0.38% (not a VOID mover at this stamp)

## Macro 0b/0c cache
- file data/macro_gate_last.md stamp 2026-08-22 09:14 CEST (07:14 UTC), age 4.5h FRESH (<8h)
- Cache 0a at 06:54Z was also VOID: HYPE +10.18% 80.322 / SOL +4.57% 94.382 / ETH +2.64% 2435.6 / BTC +2.49% 77518
- Cache named dated stories (headers/search, not inbox-as-proof):
  - BTC/ETH: Bessent Treasury buybacks $2bn → ≥$4bn/op from 9 Sep, longer-dated paper (Bloomberg 21 Aug; FT 21 Aug)
  - BTC/ETH: US spot ETFs +$2.61B five sessions, BTC +$1.92B (CoinSpectator 22 Aug)
  - HYPE: ATH $77.62 on 21 Aug (Coinbase); Trump 20 Aug “bring Hyperliquid to the US”; 18 Aug HPC + trade[XYZ] SEC IPOP letter
  - SOL: ETF inflows 3-week high + short-cover squeeze above MAs (CoinGape / CryptoNews.net 21 Aug)
  - Iran still live (Pezeshkian 21 Aug; Trump Hormuz “American territory” 22 Aug). Oil little changed — not the crypto 24h mover
- Inbox 36h @ 06:55 UTC: Iran president peace; Jackson Hole look-ahead; Economics Daily ‘Sell America’; Markets Daily debasement trade. No 22 Aug wire beyond Merryn/myFT.

## BTC tape / collector
- collector.py --once 11:42:06Z OK. addrbook=2166. last BTC market ts 1787398926305 mark 77160 oracle 77130 mid 77159.5 funding 1.25e-05 oi 36066.72 premium 0.000272 dayNtlVlm 4.772e9 impactBp 1.17
- analog sidecar 11:41:03Z px 77185 (fresh <6h)
- absorption_last.json 10:38Z STALE (>30m) — do not use. Live orderflow below replaces it.

## Positioning (oi_flow, excess vs dex baseline)
- BTC 77,161 +0.38% OI $2783m dOI -0.2% turn 1.71 exc +0.0% prem +4.5bp
- ETH 2,424 +2.09% OI $1827m dOI +1.6% turn 1.88 exc +0.0% prem +2.5bp — OI+ with price+ (new length)
- SOL 93.38 +3.17% OI $449m dOI -0.7% turn 1.85 exc +0.0% prem +5.0bp
- HYPE 77.66 +4.31% OI $1873m dOI +0.4% turn 0.95 exc +0.0% prem +2.2bp
- xyz:SP500 7,658 -0.26% OI $427m dOI n/a turn 0.34 exc +5.5% prem +2.0bp — prem inside ±4bp 64/72h; weekend DARK
- OI snapshot age 1.1h
- BTC turnover 1.71 = mid band (weight both tape and positioning)

## Wave script (enumerate only — script output, not a pick)
4h: last DOWN leg A 79,584 -> B 76,256 (leg $3,328) px 77,166
- Fib: .382 77,527 · .5 77,920 · .618 78,313 · .786 78,799
- price at +27% retrace (shallow, below .382)
- efficiency 0.73 trending · vol-exp -0.19 · cvd-slope +5048 · atr-compress 1.89
- FIB TIME: 5 bars since B (Fri 08-21 12:00, 20h ago) — AT 5-bar window

1h: last UP leg A 76,600 -> B 77,715 (leg $1,115) px 77,166
- Fib: .382 77,289 · .5 77,158 · .618 77,026 · .786 76,863
- price at +49% retrace — in/near zone
- efficiency 0.06 coil · vol-exp -0.70 · cvd-slope -6640 · atr-compress 1.65
- FIB TIME: 4 bars since B (Sat 08-22 07:00, 4h ago) — AT 5-bar window

5m micro: px 77,166 · recent highs [77396, 77428, 77225] · lows [77106, 76558, 76840] — mixed/coil

## Liqmap (collector row live, age 2.0m, STATUS OK, nPos=63 nAddr=150)
Mark 77,164
DOWN fire (long liq, in-band): 71,373 $4.6M (-7.5%) · 72,145 $107k (-6.5%) · 72,916 $948k (-5.5%)
UP fire (short liq, in-band): 77,932 $1.5M (+1.0%) · 79,089 $3k (+2.5%) · 79,861 $162k (+3.5%)
Forced path:
- if tag DOWN through 76,388 (-1.0%) long-liq $18k
- if tag DOWN through 76,003 (-1.5%) long-liq $627
- if tag UP through 77,932 (+1.0%) short-liq $1.5M
- if tag UP through 79,089 (+2.5%) short-liq $3k
Far 1× anchors outside ~8% not listed.

## Liq path (Δntl MIXES refill + address-book growth; falling ntl is the informative move)
status OK rows=8 nPos=63 nAddr=150 τ-to-half median=1.0h
- long 76388 ntl 18444 dNtl -157008 d2 -330400 n=8 τ½ 1.13
- short 77932 ntl 1,520,925 dNtl -61312 d2 -1,642,625 n=8 τ½ 0.13
- long 76003 ntl 627 dNtl +145 d2 +1723 n=8 τ½ 1.13
- long 75231 ntl 322111 dNtl -932447 d2 -1,220,672 n=7 τ½ 1.0
- short 79089 ntl 2598 dNtl -738 d2 +42110 n=8 τ½ 0.13
- long 74459 ntl 117 dNtl -23906 d2 -27903 n=3 τ½ 1.21
- short 79861 ntl 161565 dNtl -937066 d2 -2,020,615 n=8 τ½ 0.13
- long 74074 ntl 24096 dNtl +73 d2 -3924 n=3 τ OK

## Pulse
5m: px 77,157 · vol -45% fading · CVD +buy slope +195 · accel +767 · price UP → FADING/DIVERGING
1h: px 77,008 · vol -27% fading · CVD -sell slope -14733 · accel -9946 · price DOWN

## Occupancy (wick ≠ accept; last CLOSED 1h/4h only)
vs last-6 4h high 78,885
- 1h close 77,008 → BELOW
- 4h close 77,166 → BELOW

## Analog sidecar (11:41:03Z, n=164, refused=false)
px 77185 · eff 0.064 · range_pos 0.858 · atr_compression 1.652
leg1_up 43.9% · leg1_dn 56.1% · leg2_continue 26.8% · leg2_reverse 73.2%
in-sample overlapping 1h; directional not Brier.

## analog_markov
P(up first) 44% n=193 cell range/high-range/expanded-ATR
(n≥15 — not refused)

## Joint state (state_view, 1h)
D1 TREND 24h +0.52% |move| pctile 0.31 mid
D2 REGIME eff 0.06 pctile 0.16 RANGING
D3 BASIS +8.8bp pctile 0.9 PERP PREMIUM
D4 FUNDING +1.25e-05 /hr pctile 1.0 aligned=+1.3e-05
D5 FLOW volexp -0.70 / CVDslope -6640 · volexp pctile 0.03 QUIET
D6 PRICE-STRUCTURE setup none
D7 CROSS-VENUE mark_gap=4.23bp funding_gap=0.0% oi_share=43.0% LOCAL dislocation
D8 CARRY slope_1h→8h=0.0%ann BACKWARD-HEAVY contradiction=no
D9 JUMP J=0.255 vol=76.09%ann SMOOTH · JUMPINESS RISING
D10 OPTIONS SKEW BTC ATM=42.19% RR25d=4.76pp CALL SKEW P/C=0.557 · ETH ATM=62.08% RR25d=5.57pp CALL SKEW P/C=0.702
D11 OI-AGE BTC age=0.0h old+uw=0.005 fresh=0.984 · ETH fresh=1.0 · SOL fresh=1.0 · HYPE fresh=0.753
Relationships: trend×cvdslp r=0.47; basis×funding r=0.41; else |r|<0.2
No last-bar structure trigger.

## Contradiction
score -3 (agree 6 / contra 9 / miss 0) SPLIT
dims: price +0.31% 24h · cvd − -14733.4 6h · oi − -0.18% · basis +8.6bp · funding +0.125 1h bp · fuel − -0.401
pattern flagged: cover-rally (price↑ CVD↓ OI↓)
Do not average.

## Accel (12h, ticks=15)
mark last=77160 vel2=-65.51 px/h accel=+62.40 accelerating+
oi last=36066.7 vel2=+211.96 /h accel=+128.65 accelerating+
funding last=10.95 vel2=-0.77 APR-pct/h accel=-1.31 decelerating
premium last=2.72 vel2=-0.98 bp/h accel=-1.55 decelerating
cvd 1h-proxy slope6h=-14733.4 prev=-4787.3 accel=-9946.0 px6h=-1510.0
No stored IV history.

## Options path PROXY (NOT dealer GEX/vanna/charm)
BTC spot 77114.9 near 23AUG26 (0.84d)
MAX PAIN 69000 dist -10.52%
gamma-mass proxy near: call=1.0B put=629.2M callShare=0.615
vanna-mass proxy near: call=8.2M put=-13.9M [NOT dealer]
OI split: 0DTE 4007.5 · weekly 82311.5 · monthly+ 309543.3

## Order flow BTC 90s ending 11:45:35Z (prints=receipts)
Price 77171 → 77231 (+60)
Prints 305 · avg 0.051 · median 0.003 · max 1.397
Buy vol 14.04 · Sell vol 1.50
DELTA +12.54 (+80.7% of volume)
MIX HHI 0.0263 top1 0.09 whale 0.978 of vol (118 whale prints / 305)
Absorption: none this window
Resting book (intent, can be pulled): mid 77169.5 spread 1 · 0-5bp bid 25.85 ask 41.98 imb -0.24 ask-heavy
Largest prints all BUY 1.397/0.888/0.760/0.759 @ 77192–77199
Sample not a regime.

## Breadth / venue notes (cross_asset.py, live)
- last 24h: BTC +0.60% · ETH +2.34% CONFIRMS · SOL +3.48% CONFIRMS · HYPE +4.53% CONFIRMS · SPX -0.22% DIVERGES · NDX -0.61% DIVERGES
- breadth 3/5 confirm BTC 24h direction → ALIGNED (alts yes, xyz weekend DARK so SPX/NDX are not cash)
- 1h corr vs BTC: ETH 0.88 SOL 0.84 HYPE 0.57 SPX 0.46 NDX 0.47
- no usable cross-asset LEAD (doctrine #51) — breadth only
- Do not quote stubs. Do not fetch any wallet/book.
