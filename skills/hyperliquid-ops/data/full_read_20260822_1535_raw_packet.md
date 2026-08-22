# RAW FACTS PACKET — R5 — 2026-08-22 15:36 UTC
No thesis. No rails. No probability. Extract your own observations, then commit.

## Clock
- asOf 2026-08-22T15:35:33Z (orderflow) / 15:31:32Z (0a) / 15:31:31Z (collector)
- Weekend Saturday. xyz DARK / R-fiction live. BTC/ETH/SOL/HYPE = hard-stop venues (xyz clock no-op).
- 04–10 UTC distrust window is CLOSED (now 15 UTC).
- TOD (collector sample, NOT Hawkes): hour 15 UTC |Δmark|/h 265.8 vs sample median 234.0, ratio 1.14. ticks=207. status OK.

## Event clock (72h)
- +0.5h CEX 8h funding stamp (inside 90m)
- +16.5h Deribit BTC 23AUG26 (0DTE) OI=4159.6
- +40.5h Deribit BTC 24AUG26 weekly OI=2736.2
- +64.5h Deribit BTC 25AUG26 weekly OI=1581.1
- next macro: CPI (Aug 2026 data) in 477.0h
- Jackson Hole 27–29 Aug / Warsh keynote ~28 Aug is OUTSIDE 72h
- Clock note: same CVD/book is a different object inside 90m of a stamp. Funding stamp is inside 90m.

## Macro 0a live
- verdict CLEAR asOf 2026-08-22T15:31:32Z
- nothing ≥2.0% 24h at stamp
- STUBS (do not quote as prices): xyz:DXY 97.150, xyz:VIX 20.000
- live 0a marks @ 15:31:32Z:
  - Brent (HL basis ~-$10) 91.978 −0.15% fundAPR 5.5%
  - WTI 86.374 −0.06%
  - Gold 4605.800 +0.04%
  - Silver 68.893 −0.84%
  - Euro 1.169 +0.03%
  - Yen 159.060 +0.09%
  - S&P 500 7668.600 −0.08%
  - Nasdaq-ish 29229.000 −0.23%
  - Bitcoin 77049.000 −0.76% fundAPR 15.9%
  - Ether 2412.100 +0.54%
  - Solana 93.293 +1.80%
  - Hyperliquid 77.842 +1.63%

## Macro 0b/0c cache
- file data/macro_gate_last.md stamp 2026-08-22 17:32 CEST (15:32 UTC), age ~4m FRESH (<8h)
- Cache 0a at 15:32Z CLEAR — nothing ≥2% 24h
- Inbox 8h @ 15:32 UTC (headers only, 7 matching): Bloomberg Green / Opinion / Money / Pursuits / Businessweek / New Economy: Central Europe’s China gaze / Weekend ‘Everyone will have to fight’. No 22 Aug market-moving wire in allowlist.
- RSS/news check 8h (headline-only, not full index):
  - [15:06Z] Bloomberg Markets weekly news quiz
  - [14:23Z] Sanctions Target Iran’s Weakened Regional Network
  - [13:37Z] MI6 Veteran Warns Against Politicizing Intelligence
  - [13:31Z] FT: Russian ‘double-tap’ attack on Ukrainian shopping mall kills at least 16
  - [13:22Z] Canada Pushes Back as US Trade Talks Collapse
  - [13:11Z] Bond Market Tests Limits of Treasury Intervention
  - [12:03Z] The AI Spending Spree Comes With a Catch
- Neutral 0b web (this pass, not inbox-as-proof):
  - CNBC 21 Aug: Bitcoin around $77,000 Friday; weekly gain more than 20%
  - crypto.news / Blockonomi 22 Aug: US spot BTC+ETH ETFs +$2.61B five sessions; BTC +$1.92B
  - Yahoo 20 Aug: 12 US spot BTC ETFs +$600m that day
  - CNN 22 Aug: US preparing further economic sanctions on Tehran, details Monday
  - Al Jazeera 22 Aug: Trump “Strait of Hormuz as an American territory right now”; “not ready to make the right deal”
  - Jackson Hole 27–29 Aug; Warsh first keynote as Fed chair 28 Aug
- Morning cache (07:14 UTC, now superseded) had named stories: Bessent Treasury buybacks $2bn → ≥$4bn/op from 9 Sep; HYPE ATH $77.62 21 Aug; Trump 20 Aug “bring Hyperliquid to the US”

## BTC tape / collector
- collector.py --once 15:31:31Z OK. addrbook=2226. last BTC market ts 1787412691021 mark 77049 oracle 77001 mid 77048.5 funding 1.81648e-05 oi 35599.79414 premium 0.0006103817 dayNtlVlm 3.919e9 impactBp 0.13
- analog sidecar 15:35:00Z px 77144 FRESH (<6h)
- absorption_last.json 15:35:33Z FRESH (<30m)

## Positioning (oi_flow, excess vs dex baseline, snapshot 3.8h old)
Neutral funding baseline: main 10.95% APR, xyz 0.00% APR.
- BTC 77,152 −0.62% OI $2749.4m dOI −1.2% turn 1.43 exc +5.1% prem +6.6bp (3d prem +0.3)
  script note: OI −1.2% while price −0.62% — longs being closed out (script’s own label)
- ETH 2,414.8 +0.65% OI $1850.3m dOI +1.7% turn 1.64 exc +0.0% prem +2.4bp (3d +1.9)
  script note: OI +1.7% with price +0.65% — new length chasing
- SOL 93.543 +2.07% OI $453.4m dOI +0.8% turn 1.68 exc +0.0% prem +5.1bp (3d +2.8)
- HYPE 78.050 +1.91% OI $1897.1m dOI +0.8% turn 0.78 exc +0.0% prem +4.3bp (3d +6.2)
- BTC turnover 1.43 = mid band (weight both tape and positioning)

## HLP inventory (collector 15:31:31Z)
equity $188.0m apr 7.19% nChildVaults 7
inventory ntlUsd: BTC −0.0331 / $34.0k · ETH −0.709 / $80.7k · SOL −19.24 / $4.0k · HYPE −44.75 / $49.4k

## Wave script (enumerate only — script output, not a pick)
4h: last DOWN leg A 79,584 -> B 76,256 (leg $3,328) px 77,148
- Fib: .382 77,527 · .5 77,920 · .618 78,313 · .786 78,799
- price at +27% retrace (shallow, below .382)
- efficiency 0.72 trending · vol-exp −0.60 · cvd-slope −13752 · atr-compress 1.87
- FIB TIME: 6 bars since B (Fri 08-21 12:00, 24h ago) — AT 5-bar window (a turn is DUE per script)

1h: last UP leg A 76,600 -> B 77,715 (leg $1,115) px 77,152
- Fib: .382 77,289 · .5 77,158 · .618 77,026 · .786 76,863
- price at +50% retrace — in/near zone
- efficiency 0.01 coil · vol-exp −0.56 · cvd-slope −660 · atr-compress 1.42
- FIB TIME: 8 bars since B (Sat 08-22 07:00, 8h ago) — AT 8-bar window

5m micro: px 77,144 · recent highs [77200, 77200, 77149] · lows [77155, 77002, 76976] -> LOWER LOWS + LOWER HIGHS = down micro
RECONCILE (#49): do NOT call the up-path dead while 5m prints HIGHER HIGHS above the make-or-break, nor the down-path dead while it prints LOWER LOWS.

## Liqmap (collector row live, age 2m at 15:31:31Z, STATUS OK, nPos=46 nAddr=150)
Mark 77,152
NEAR MARK (±8%):
- long 72,426 −6.1% $24k DOWN-fuel Δvs prior −4,648,828
- long 76,278 −1.1% $4k DOWN-fuel Δvs prior −194,525
- short 78,205 +1.4% $33k UP-fuel Δvs prior −4
- short 80,131 +3.9% $12k UP-fuel Δvs prior −582,074
- short 80,516 +4.4% $309k UP-fuel Δvs prior −530,290
Forced path:
- if tag DOWN through 76,278 (−1.1%) long-liq $4k
- if tag DOWN through 72,426 (−6.1%) long-liq $24k
- if tag UP through 78,205 (+1.4%) short-liq $33k
- if tag UP through 80,131 (+3.9%) short-liq $12k
Dropped 22 ancient far anchors (not live fuel). Sample nPos=46 / nAddr=150, not the whole book.

## Liq path (Δntl MIXES refill + address-book growth; falling ntl is the informative move)
status OK rows=8 nPos=46 nAddr=150 τ-to-half median=1.21h (n_halved=5)
- long 76278 ntl 3741 dNtl −194525 d2 −209856 n=8 τ½ 1.21
- short 78205 ntl 32801 dNtl −4 d2 −21186 n=8 τ½ 2.51
- short 80131 ntl 12076 dNtl −582074 d2 +32897 n=8 τ½ 0.51
- short 80516 ntl 309234 dNtl −530290 d2 −1,090,999 n=3 τ½ 1.52
- long 72426 ntl 24141 dNtl −4,648,828 d2 −8,371,182 n=8 τ½ 0.51

## Pulse (15:34–15:35Z)
5m: px 77,036 · vol −67% fading · CVD +buy slope +123 · accel +156 · price DOWN → FADING/DIVERGING
1h: px 77,053 · vol −43% fading · CVD −sell slope −4379 · accel +5073 · price DOWN → FADING/DIVERGING
Targets checked: 77,158 / 78,205 / 76,278 — same pulse state at this stamp (not at-magnet yet).

## Occupancy (wick ≠ accept; last CLOSED 1h/4h only)
coil 12h ±25bp of mark: 40.3% (58/144 5m closes)
5m closes ≥ last-6 4h high 78885: 0.0% (0/144)
ACCEPT vs last-6 4h high 78885.0
- 1h close 77053.0 @ 2026-08-22 14:00 UTC → BELOW
- 4h close 77163.0 @ 2026-08-22 08:00 UTC → BELOW

## Analog sidecar (15:35:00Z, n=263, refused=false)
px 77144 · eff 0.016 · range_pos 0.856 · atr_compression 1.421
leg1_up 44.5% · leg1_dn 55.5% · leg2_continue 28.5% · leg2_reverse 71.5%
after UP leg1: continue 32% / reverse 68% (n=117)
after DOWN leg1: continue 26% / reverse 74% (n=146)
in-sample overlapping 1h; directional not Brier. K=$300 legs. median time to leg1 1h.

## analog_markov
cell [range/high-range/expanded-ATR] n=193
P(up first | cell) 44% · P(down first) 56%
P(continue | cell) 30% n=193
P(next cell): 76% stay same cell (n=155)
(n≥15 — not refused)

## Joint state (state_view, 1h, bar 4800)
D1 TREND 24h −0.12% |move| pctile 0.08 LOW/extreme
D2 REGIME eff 0.01 pctile 0.04 RANGING
D3 BASIS +7.8bp pctile 0.83 PERP PREMIUM
D4 FUNDING +1.39e-05 /hr pctile 1.0 aligned=−1.4e-05
D5 FLOW volexp −0.56 / CVDslope −660 · volexp pctile 0.13 QUIET
D6 PRICE-STRUCTURE setup none
D7 CROSS-VENUE mark_gap=6.61bp funding_gap=5.0403% oi_share=42.41% GLOBAL/systemic (mark+funding same sign)
D8 CARRY slope_1h→8h=−5.0403%ann FRONT-LOADED (near carry > distant — crowd flipping fast, flush candidate) contradiction=no
D9 JUMP J=0.251 vol=75.81%ann SMOOTH · JUMPINESS RISING
D10 OPTIONS SKEW BTC ATM=36.44% RR25d=−2.03pp PUT SKEW P/C=0.593 · ETH ATM=58.96% RR25d=+8.37pp CALL SKEW P/C=0.697
D11 OI-AGE BTC age=0.0h old+uw=0.003 fresh=0.997 · ETH fresh=1.0 · SOL fresh=0.951 · HYPE old+uw=0.258 fresh=0.723
Relationships: trend×cvdslp r=0.47; basis×funding r=0.42; else |r|<0.2
No last-bar structure trigger.

## Contradiction
score −2 (agree 4 / contra 6 / miss 5) SPLIT
dims: price −0.24% 24h · cvd − −4379.1 6h · oi · +0.03% · basis +9.5bp · funding +0.182 1h bp · fuel +0.854 liqmap skew
pairs: price×basis− price×funding− price×fuel− cvd×basis− cvd×funding− cvd×fuel−
pattern flagged: trapped-longs (price↓ funding+)
Do not average.

## Accel (12h, ticks=16)
mark last=77049.0 vel2=+15.11 px/h accel=+245.22 accelerating+
oi last=35599.8 vel2=−106.66 /h accel=−448.19 accelerating−
funding last=15.9124 vel2=+0.99 APR-pct/h accel=+1.53 accelerating+
premium last=6.1038 vel2=+0.44 bp/h accel=+0.74 accelerating+
cvd 1h-proxy slope6h=−4379.1 prev=−9452.3 accel=+5073.2 px6h=−191.0
No stored IV history. Candle-CVD accel ≠ true aggressor CVD.

## Options path PROXY (NOT dealer GEX/vanna/charm)
BTC spot 77067.1 near 23AUG26 (0.68d)
MAX PAIN 70000 dist −9.17%
gamma-mass proxy near: call=1.1B put=793.1M callShare=0.576
vanna-mass proxy near: call=12.6M put=−16.0M [NOT dealer]
OI split: 0DTE 4170.7 · weekly 82098.7 · monthly+ 310136.5

## Order flow BTC 90s ending 15:35:33Z (prints=receipts)
Price 77153 → 77153 (+0)
Prints 243 · avg 0.046 · median 0.002 · max 0.921
Buy vol 2.80 · Sell vol 8.39
DELTA −5.59 (−50.0% of volume)
MIX HHI 0.0303 top1 0.082 whale 0.986 of vol (95 whale prints / 243)
Absorption: present=false this window
Resting book (intent, can be pulled): mid 77152.5 spread 1 · 0-5bp bid 44.68 ask 38.52 imb +0.07 balanced
bid walls: (77152, 5.32) (77137, 5.21) (77138, 5.15)
ask walls: (77153, 11.22) (77172, 4.81) (77169, 2.79)
Largest: SELL 0.921 @ 77149 · BUY 0.699 @ 77153 · SELL 0.636 / 0.543 / 0.519
Script signal: BEARISH DIVERGENCE — price flat/higher over window, net delta negative.
Sample not a regime. n=243 prints / 11.18 contracts.

## Own-lines (structure.py 15:35Z, mark 77137)
CONFLUENCE ZONES:
- ABOVE 79202–79428 score 180 objects 3 TL-res TFs 1h/4h
- ABOVE 80095 score 128 TL-res 4h
- ABOVE 78874–78943 score 36 TL-res + swingH 15m/1h/4h
- ABOVE 79584–79717 score 34 TL-res + swingH 1h/4h
- ABOVE 77411–77715 score 17 TL-res + swingH 15m/1h
- BELOW 76256–76558 score 10 swingL 15m/1h
Daily TL-sup cluster ~62.3–63.6k is far; 15m/1h/4h TL-sup prints are ancient-anchor range vs mark.

## Sentiment
Fear&Greed 71 [Greed] Δ−1 · extreme=false · source alternative.me

## Breadth / venue notes (cross_asset.py, live)
- last 24h: BTC −0.13% · ETH +0.92% DIVERGES · SOL +2.40% DIVERGES · HYPE +1.94% DIVERGES · SPX −0.24% CONFIRMS · NDX −0.47% CONFIRMS
- breadth 2/5 confirm BTC 24h direction → DIVERGENT (warning)
- 1h corr vs BTC: ETH 0.88 SOL 0.84 HYPE 0.57 SPX 0.46 NDX 0.47
- no usable cross-asset LEAD (doctrine #51) — breadth only
- xyz weekend DARK so SPX/NDX are not cash
- Do not quote stubs. Do not fetch any wallet/book.

## Commit format required
Return ONLY:
1. Two moves labeled MOVE 1 / MOVE 2. Each: mechanism one line; ENTRY / EXIT / INVALIDATION / ENGINE STOP / RE-ENTRY / REVERSE as exact prices.
2. Honest p for MOVE 1 (0–100). p_up = P(up-target before down-break) on your levels.
3. Top 3 reasons NOT to trade.
4. Alt invalidation (one price).
5. Make-or-break level.
6. Low-prob / high-significance tail (one line).
No narrative essay. No inherited rails. 40x convention: ENTRY = 15m close beyond the line; fast kill = 15m close the other way; confirm kill = 1h close; engine stop = 0.4–0.8% hard price.
If mid-range, say WAIT / FLAT and still name the two rail-tagged moves.
