---
name: hyperliquid-ops
description: Read-only trading-operations reporting and macro-first market scanning for Hyperliquid perpetuals — enforces an inbox-and-disconfirming-news pass BEFORE any price or level work, then cross-asset data, then an explicit confluence/divergence read; also covers position snapshots, realized/unrealized PnL, funding paid/received, recent fills, and market observations (movers, funding extremes, range position, cross-venue funding). Use this skill whenever the user mentions Hyperliquid, perp positions, funding rates, liquidation prices, trading PnL, fills, trade ideas, levels, entries, longs or shorts, liquidity, market setups, or asks things like "what's the setup", "anything interesting in the market", "is X a level", "what did funding cost me this week", or "give me my trading ops summary" — even if they don't name Hyperliquid explicitly, if their context is perp/DEX trading, reach for this skill.
---

# Hyperliquid Trading Ops

Produce a chat summary of the user's Hyperliquid trading operations using the
bundled fetch script. Everything here is **strictly read-only**: the script only
calls the public `info` endpoint. Never place, modify, or cancel orders, never
touch the `/exchange` endpoint, and never handle private keys — if the user asks
for trade execution, decline that part and explain this skill is reporting-only.

## THE READ — default procedure for EVERY read (run end-to-end, UNPROMPTED)

For any market read, level call, or trade idea, follow **references/THINKING-PROCESS.md** top to bottom by
default — do not wait to be walked through it step by step. Order (converged 2026-08-15, doctrine #50):

0. **Macro gate** (Step 0 below) — no level before CLEAR + a named catalyst.
1. **Wave structure across 5m/1h/4h — FIRST** (`wave_scenarios.py`): enumerate the Fib scenario-space + levels (reversal vs trendline-break). The frame, not a prediction — running it first is what makes CONFLUENCE visible (a liquidity pool sitting on a Fib level). It ENUMERATES both scenarios, never asserts one.
2. **Positions, not funding, in rate-of-change** (`oi_flow.py` + collector): OI/ΔOI, liq-map magnet (does it sit on a step-1 level?), HLP inventory, whale net. Funding is a *price*, secondary. Positions clear before events.
3. **Joint state** (`state_view.py`): all dimensions at once + the relationship matrix (don't double-count correlated lenses).
4. **Signals + rate-of-change adjudicate** R vs C at the level (volume/CVD → holds; accelerating efficiency → breaks/fake) — `pulse.py [level]` gives this call in ~2s (CONFIRMING vs FADING).
5. **Repro the state** (`analog.py`): the empirical base rate; when a leg is a coin flip, steps 1–2 break the tie, not a story.
6. **Commit** the **2 next most probable moves** — this stays the deliverable, always: each with entry-zone → target, mechanism, invalidation; an honest probability; the low-prob / high-significance tail; the make-or-break level. THEN, silently to the ledger only (never in the user-facing read), append a forward-judge tag — `SCORE {"ts":<now_ms>,"h":<hours>,"up":<up-target>,"dn":<down-break>,"p_up":<committed P(up before dn)>,"p_base":0.5}` — so the call (script + positioning + brainstorm) is graded by `calibration.py` without changing what the user sees.
7. **Continuity** — read the prior read (ledger / earlier in the conversation) and assess how the scenarios EVOLVED since (strengthened / weakened / invalidated / level-shifted, + the driver); the new call is a DELTA, not a restart. This is what lets grading + expectancy accumulate across reads.

Firewall throughout (mechanism > fit #46; trial-count as denominator; decorrelation #42; forward + stopping rule; Elliott admissible ONLY as falsifiable scenarios). Read-only — analysis, not orders; execution is Olivier's layer.

**The judge (Sunday retro): extract the ledger's SCORE tags → `calibration.py` → Brier vs baseline + calibration + kill-switch + SWEEP DIAGNOSTIC.** This is the desk's ONLY proof of edge, and it grades the COMMITTED call (script + positioning + live brainstorm), so the human conditioning is on the stand too. The user-facing output never changes — it is always the 2 next most probable moves; the scoring is silent behind it. **Then the DISCOVERY LOOP** (`discovery_loop.py` over the collected calls + `lessons.json`) proposes which candidate lessons earned promotion to doctrine and which rules to retire — it PROPOSES only; your SAVE of the skill is what propagates them to every agent, so all instances come to read the market alike (doctrine #54).

## Step 0 — Macro gate (MANDATORY, runs before any price work)

**Do not write a single price level until this is done.** This gate is not
optional and does not wait to be asked for.

Why it exists: on 2026-07-26 a read started from price and levels, searched the
web with escalation-framed queries ("Hormuz", "Iran tension", "oil war
premium"), got back only escalation-confirming headlines, and concluded the war
premium was "fully intact" — roughly an hour before a **US–Iran bombing pause**
gapped the market the other way. Two things were available and unused: the story
was sitting **unread in the user's own Gmail** (Bloomberg, subject *"Albanese to
press Trump on tariffs, US and Iran extend pause"*), and **HL BRENTOIL had
already bled 90 → 88 → 86 for hours** — that divergence was noticed and then
rationalised away to fit the thesis. Root cause: confirmation bias. Searching to
confirm rather than to break the thesis.

**0a. Run the pre-flight. It is a gate, not a formality.**

```bash
python3 scripts/macro_preflight.py --thesis "<the view you are about to argue>"
```

It prints a timestamped cross-asset snapshot, marks which xyz markets are dead
stubs rather than live prices, checks a handful of macro relationships, and
returns **VOID** or **CLEAR**.

> **The void rule.** If any macro asset has moved ≥2% in 24h, you are VOID:
> **no levels, no entries, no targets, no bias** until every flagged mover is
> matched to a **named, dated story** from step 0b or 0c. If a mover contradicts
> the view and nothing explains it, **the price is right and the view is wrong.**
> Start over. Do not write around it.

This exists because on 2026-07-26 HL BRENTOIL had bled 90 → 88 → 86 in plain
sight, the divergence was noticed, and it was rationalised away in prose. A
sentence of good intentions did not stop that. A verdict line does.

**0b. Disconfirming search — this is the discovery mechanism, do it first.**

Search for the **opposite** of the prevailing narrative, in neutral wording.

- Narrative is escalation → search de-escalation, pause, ceasefire, talks, off-ramp.
- Narrative is risk-off → search what would make it risk-on.
- Neutral form: `"US Iran latest <date>"`. Never `"Iran escalation oil supply risk"`.
  Narrative-loaded query terms return narrative-confirming results — that is the
  exact mechanism of the 2026-07-26 miss.

Sweep every time regardless of the day's story: Fed / FOMC rate pricing, CPI, the
earnings calendar, and any scheduled event inside 72h. Then use these searches to
fill in the VOID checklist from 0a.

**0c. Inbox — confirmation and depth, not discovery.**

```
newer_than:1d {from:bloomberg.net from:bloomberg.com from:ft.com from:theinformation.com from:wsj.com from:reuters.com}
```

Read the macro ones: Bloomberg Morning Briefing (Asia / Europe / Americas), Five
Things, myFT Daily Digest, The Information Briefing. Quote market-moving lines
**verbatim** — never paraphrase a headline into a thesis. `get_thread` output
often exceeds the token limit and is auto-written to a file; when that happens
extract it with python/grep or hand the file to a `general-purpose` subagent.
Do not skip an email because it was large.

**Know what this feed can and cannot do.** These are daily digests, so they lag
the wire by hours. On 2026-07-26 the Bloomberg email carrying the Iran pause
arrived at 00:32 CEST — *thirty minutes after the market had already gapped on
it.* The inbox is where the depth is (rate pricing, earnings estimates, the
detail behind a headline); the **search in 0b is what gets there in time**. Never
treat "the inbox had nothing" as evidence that nothing happened.

**0d. Session-gap catch-up.** This skill only runs when a session runs, so there
is no coverage between them. If the last exchange in this conversation is more
than ~6 hours old, or the conversation is new, widen 0b and 0c to cover the full
gap (`newer_than:2d`, and search the whole window) before anything else. The
2026-07-26 failure happened Saturday night — outside every brief window there was.

**0e. Confluence / divergence.** This is the product; the levels are the footnote.
Answer all three explicitly:

- **Where do news, price and positioning agree?** Confluence is what is tradeable.
- **Where do they disagree?** Divergence is the warning. When price contradicts
  the narrative, the price is right and the narrative is stale.
- **What single event or level flips the regime?** Name the tripwire out loud.

**0f. Freshness.** Every price quoted to the user carries the timestamp it was
pulled at. Nothing older than ~30 minutes is presented as current — re-run the
pre-flight instead. On 2026-07-26 a two-day-old oil quote was used to argue a
live thesis while the actual tape was three dollars lower.

**0g. Pick the right instrument for the venue, THEN read it.**

Run this first — it decides which of the two tools below is even worth running:

```bash
python3 scripts/oi_flow.py
```

The routing rule is turnover, `24h volume / open interest`:

- **Turnover under ~0.4 → positioning is the signal, the tape is noise.** The
  book is a place where people hold, not trade. `xyz:SP500` runs about **0.18**
  ($88M of daily volume against $477M of OI). A ninety-second window there is a
  handful of contracts. Read `oi_flow.py`, not the tape.
- **Turnover over ~2 → the tape carries information.** Run `orderflow.py`.
- **In between → run both and say which one you weighted.**

What `oi_flow.py` measures and why each one is not the obvious thing:

- **Neutral funding is not zero.** Hyperliquid funding is premium *plus* an
  interest-rate component, so a perfectly uncrowded market prints about
  **+10.95% APR on the main dex and +5.475% on xyz**. The script measures those
  baselines as the median of each dex's whole universe every run and reports only
  the **excess**. Reading raw funding as crowding labels every quiet market
  "crowded longs" — this was an actual bug in the first version of this script,
  caught by noticing that eight unrelated markets all printed the same number.
- **Premium, not funding rate, is the crowding measure.** Perp versus oracle in
  basis points, over a 3-day hourly history. Inside ±4bp is fair value; there is
  no crowd, and saying "neutral" is the correct answer rather than a failure to
  find something.
- **OI change against price direction.** OI up while price falls = new shorts
  being added (aggressive, builds squeeze fuel). OI down while price falls =
  longs being liquidated (capitulation, exhausts itself, late not early).
  This needs a prior snapshot; the script writes one to
  `~/.hyperliquid-ops/oi_state.json` and **says out loud when there isn't one
  yet** rather than implying a delta it cannot compute.
- **Books under $10M OI are suppressed entirely.** `xyz:XLE` prints −55% excess
  APR on $1.9M of OI. That is one participant, not a crowd.

Crowding is fuel, never direction. It sizes a move you already have a reason to
expect; crowded stays crowded for weeks.

**0h. Order flow — before any level is called "held", "rejected" or "defended".**

```bash
python3 scripts/orderflow.py --coin xyz:SP500 --secs 90
```

Requires `websockets` (`pip install websockets --break-system-packages`).
Read-only: public trades feed plus public `l2Book`. Never touches `/exchange`.

Know the difference between the three things that get confused for each other:

| what | source | what it actually is |
| --- | --- | --- |
| **Activity** | candle volume | how much traded. Says nothing about who was hitting. |
| **Intent** | `l2Book` depth | resting size. **Can be pulled at any moment.** Weakest evidence on the page. |
| **Flow** | websocket `trades` | aggressor-tagged prints. `"B"` = a buy lifting the offer, `"A"` = a sell hitting the bid. This is the only one that is flow. |

On 2026-07-27 a level was called "holding on a real bid" on the strength of two
resting book levels. It broke twenty minutes later, and the tape over that window
was 3:1 sell-side. Resting bids are a promise; prints are a receipt. Quote the receipt.

What to read out of the output, in order of value:

- **Delta / delta_pct** — net aggression. Above roughly ±30% of volume, one side
  is genuinely in control; below that it is a coin flip dressed up as a signal.
- **Divergence** — price higher with negative delta means the move is being sold
  into. Price lower with positive delta means the flush is being bought.
- **Sequence** — a price high printing *after* the CVD high is exhaustion. The
  buying peaked before the price did.
- **Absorption** — heavy one-sided volume with a below-median range means someone
  large is on the other side. At a level, absorption marks the turn, not the break.

**Sample-size honesty is mandatory and non-negotiable.** A window is a sample, not
a regime. State the print count and total contracts every single time, and say
plainly when they are too thin to act on. Overnight `xyz:*` markets routinely
trade under 50 contracts in 90 seconds — at that size a single 2.5-lot swings
delta from negative to positive and the "signal" is one participant. Re-run at
the level that matters and at the cash open (15:30 CEST) before sizing anything.
A dead tape is itself information: if nobody is trading, "rejection" is noise.

## Workflow

1. Run the fetcher (wallets come from `config.json` next to this file):

   ```bash
   python3 scripts/hl_ops.py all --days 7
   ```

   Subcommands when the user asks for one thing only: `positions`, `pnl`,
   `funding`, `fills`, `scan` (market context for idea generation).
   `--days N` widens the funding/fills window. `--address 0x...` overrides
   the configured wallets for one-off lookups.

   Note the House rules below: by default the user does **not** want their
   account or positions fetched or discussed. Unless they asked in this message,
   skip straight to `scan` and the market read.

   The other two scripts are read-only, wallet-free and safe to run any time:

   - `scripts/macro_preflight.py` (Step 0a) — cross-asset gate. Required before
     any level call. `--thesis "..."` records the view being tested; `--threshold`
     defaults to 2.0%; `--json` for raw.
   - `scripts/oi_flow.py` (Step 0g) — OI, funding drift, premium, turnover
     routing. Run before the tape; on low-turnover venues it replaces it.
     `--coins`, `--days`, `--state`, `--no-save`, `--json`.
   - `scripts/orderflow.py` (Step 0h) — aggressor-tagged tape, CVD, divergence
     and absorption. Required before calling any level held, rejected or defended,
     but only meaningful where turnover says the tape is real.
     `--coin`, `--secs`, `--bucket`, `--json`. Needs the `websockets` package.

2. Format the JSON output into the report below. Don't dump raw JSON at the
   user; they want an ops summary they can scan in ten seconds.

## Report structure

Use this shape (drop sections the user didn't ask for):

```
## Hyperliquid ops — [wallet name] ([short address]) — [date]

**Account**: $X account value · $Y notional · Z% margin used · $W withdrawable

### Positions
| Coin | Side | Size | Entry | Mark | Liq px | Lev | uPnL | Funding APR |
(one row per position; bold or flag anything within 15% of liquidation)

### PnL
Day / week / month / all-time PnL; realized (net of fees) vs unrealized split.

### Funding (last N days)
Net funding $ and the coins that drove it (paid vs received).

### Fills (last N days)
Count, volume, fees, and the handful of most recent fills if relevant.

### Flags
Only if warranted: positions near liquidation, funding bleeding faster than
PnL accrues, unusually high fees vs volume, concentration in one coin.
```

The Flags section is where you earn your keep — apply judgment, don't just
restate numbers. Distance to liquidation matters more when leverage is high;
negative funding on a large short is income, on a large long it's a bleed.

## Idea generation (`scan`)

When the user asks for trade ideas, setups, or "what's interesting", run
`scan`. It returns the current book plus objective market context: top coins
by volume, biggest 24h movers, funding-rate extremes, where each held coin
sits in its 7-day range, and predicted funding across venues.

Present **observations, not trade calls**. For anything you surface, give the
data on both sides and what would invalidate it. The format that works:

```
### Market observations — [date]

**What changed** (from Step 0a/0b — verbatim quotes from the inbox and the
disconfirming search; if nothing changed, say so explicitly).

**Confluence / divergence**: where news, price and positioning agree; where they
disagree; and the single tripwire that flips the regime.

**Fuel** (from Step 0g): excess funding over the dex baseline, mean premium in
bp, OI change and its direction against price. Name which side is crowded, or
say **neutral** — "no crowd to squeeze" is a real answer, not a missing one.
State the turnover so it is clear whether the tape or the positioning was
weighted, and never present venue-local OI as information about the underlying.

**Your book first**: [ONLY if the user asked about their positions in this
message — see House rules; by default skip this line entirely. When asked: 1-2
lines, existing risk dominates any new idea, flag anything near liquidation.]

**Notable conditions** (2-4, only if the data warrants):
- [Coin]: [observation — e.g. funding at +45% APR while price is flat near its
  7d low; shorts are being paid to wait]. Case for: … Case against: …
  Invalidation: [level/condition].

**Not notable today**: [what you checked that showed nothing — this is signal
too.]
```

Rules that matter here:

- "There's always a trade" is a hypothesis the data must earn, not an
  assumption. If nothing clears the bar, say **"nothing compelling today"**
  plainly — chasing marginal setups on leverage is how accounts die, and a
  scan that always produces ideas is indistinguishable from noise.
- Never state or imply the user *should* enter a position. Frame everything
  as what the data shows; sizing, direction, and timing are theirs. End the
  section with: *Data-driven observations, not financial advice.*
- Weigh new ideas against existing exposure: adding correlated risk to a
  stressed book is a worse idea than the setup is good.
- Never execute anything. Reporting and observation only, as everywhere in
  this skill.


## Hybrid scan (focused universe)

`config.json` contains a `watchlist` — the user's focused trading universe.
When the user asks for a scan, trade ideas, or "what's interesting", run two
layers:

1. **Focused layer (primary)**: for each watchlist coin, fetch 4h candles
   (~30 days) from the public `candleSnapshot` info endpoint and compute:
   30d volume profile (POC / VAH / VAL, 70% value area), position in 7d and
   30d range, 7d/30d momentum, distance from 20-period MA, and current
   funding APR from `metaAndAssetCtxs` (xyz:* coins live on the `xyz` dex —
   pass `"dex": "xyz"`; `candleSnapshot`, by contrast, takes the plain coin
   name like `"xyz:SP500"` with **no** dex param — verified 2026-07-12). Surface only conditions the data earns: price at
   value-area edges, S/R flips, momentum extremes, funding vs price
   divergences. Present case for / case against / invalidation for each.
2. **Broad layer (backdrop)**: the all-market funding-extremes and movers
   screen from `scan`, as one or two lines of context. Never promote a
   broad-screen name to an idea unless its daily volume exceeds $5M.

The watchlist is ~4 correlated risk clusters (equity: SP500/XYZ100/TSLA/
AAPL/SPCX; crypto: BTC/ETH/HYPE; gold; oil; ZEC idiosyncratic) — flag when
multiple observations are the same cluster bet, especially against existing
positions. Levels analysis (volume profile, swings, fibs) is mechanical and
encouraged; Elliott Wave counts are permitted as explicitly-labeled
brainstorming with alternative counts, never as single-count certainty.

## Game layer (positioning & pain trades)

A trade is against other people, not against the news. Whenever producing a
scan, observations, or ideas, add a positioning read built from the data you
already fetched:

- **Crowding taxonomy** (funding x OI x price direction): OI up + price up +
  funding rising = levered longs crowding in (squeeze fuel both directions);
  price down while funding stays positive and OI holds = trapped longs,
  bounces get sold; a sharp move with OI falling = liquidation flush, often
  near exhaustion; funding beyond ~0.05%/8h = the crowded side pays carry —
  time favors the other side even at flat price. The scan's cross-venue
  predicted fundings are a cross-check: divergence between venues means the
  crowding is venue-specific and arbable, convergence means it's systemic.
- **Funding signal validity (xyz caveat)**: HL funding is premium-vs-oracle.
  On xyz perps outside underlying market hours, Hyperliquid is the only open venue,
  so its flow is a thin, unrepresentative slice of true global positioning
  (xyz:SP500 OI is a rounding error next to the CME complex). Treat xyz
  funding as a carry cost always, but as a positioning signal only when the
  underlying market is open, the sign has persisted for hours, and OI moves
  confirm. Crypto funding can be cross-checked across venues via the scan's
  predicted fundings; xyz funding cannot on weekends — say so rather than
  over-reading it.
- **The xyz oracle is LIVE 24/7 — it is NOT frozen to the last cash close.**
  Verified 2026-07-26: across the full weekend the `xyz:SP500` oracle tracked
  the perp within ~5 points (mark 7456.3 / oracle 7451.0) and rose ~40 points
  from Friday's 7,405 cash close to 7,451. The ~1%-per-update clamp (~74 pts at
  these levels) never binds in practice. **Consequences: liquidations run
  normally on weekends and holidays**, whoever walks the perp also walks the
  oracle, and weekend funding is a real premium-vs-live-oracle number rather
  than a stale-reference artifact. Any reasoning that assumes a frozen weekend
  oracle — "stops can be run but liqs can't", "the gap is mechanical" — is
  wrong; do not reuse it.
- **`xyz:BRENTOIL` trades roughly $10 BELOW real Brent** (HL ~87–88 while the
  physical benchmark was ~98). Direction and rate-of-change are readable; the
  absolute level is not. Never quote it to the user as the world oil price —
  cross-check the real benchmark by web search before making a level claim
  about oil. `xyz:CL` (WTI) carries its own basis; treat it the same way.
- **Globex reopens at weekend fair value ≈ the perp**, not at Friday's cash
  close. There is no mechanical gap to trade at the Sunday reopen; the move
  comes from post-open real flow. Do not size a trade around an expected
  reopen gap.
- **Real-money positioning (equity/index names)**: HL funding is NOT a
  positioning signal for xyz:SP500/XYZ100/TSLA/AAPL/NVDA/META/MU/SPCX — a thin,
  oracle-referenced venue whose OI is a rounding error next to the CME complex —
  so treat it as carry cost only. For these names, get the real-money read via
  web search instead: CFTC COT lean (asset-manager net long vs leveraged-fund
  short, plus where each sits in its historical range), SPX dealer-gamma / GEX
  regime (the gamma flip level, call and put walls), CBOE put/call, and the CNN
  Fear & Greed index. Negative gamma means dealers amplify moves, so surprises
  overshoot; positive gamma means they dampen. This real-money read overrides any
  HL-funding positioning inference for these names — when they conflict, trust
  COT and dealer gamma, not the perp's funding.
- **Priced-in test**: weigh the dominant narrative's age against the move
  already made. Day-3 headlines of a story move less than day-1; the
  asymmetric headline is the reversal of the story everyone now holds.
- **Pain trade**: state "the move that hurts the most positioned money is X"
  for the dominant driver and for any cluster where the user has exposure.
  Surprises overshoot in the pain direction.
- **Forced flows beat opinions**: liquidation proximity (the user's own book
  first), CME weekend/holiday gap reopens, token unlocks, options expiry and
  rebalance dates, thin weekend books. Name who must transact, and when.
- **Event odds vs price**: for binary catalysts (CPI, Fed, geopolitical
  deadlines) check prediction-market odds (Polymarket, Kalshi), CME FedWatch
  and the Crypto Fear & Greed index via web search (their APIs are typically
  blocked by the sandbox allowlist). The tradeable thing is the gap between
  event odds and what price implies — never the odds alone.
- **Schelling points**: round numbers and prior extremes coordinate stops and
  defenses — expect magnet and stop-raid behavior; suggest invalidation
  levels just beyond them, not exactly on them.
- **Sentiment texture**: an optional web-search pass over X/crypto-Twitter
  and financial media for euphoria/panic language. Sentiment confirms
  crowding; it never generates an observation alone.

In observations and ideas, label each setup **JOIN** (an uncrowded trend with
acceptable carry) or **FADE** (a crowded, levered, negative-carry extreme —
fades require a price trigger, never sentiment alone), and include an
"Other side:" line naming who is positioned against it and what forces them
out (funding bleed, liq cluster, unlock, data print). Contrarianism must be
earned by positioning data, not assumed.

## House rules (standing user preferences — these override the defaults above)

- **Do not fetch, report on, or reason about the user's account or open
  positions unless they explicitly ask in that message.** Standing instruction,
  stated repeatedly: *"do not look at my account, waste of time"* and *"leave my
  position out, focus on giving alpha."* This overrides the "Your book first"
  line in the observations format and the Account/Positions/PnL sections of the
  report — skip them by default and lead with the market read.
- **Seeing a position biases the framing.** On 2026-07-26 the read flipped
  direction within one message of a position being disclosed, and the user
  caught it: *"why do you switch now that you saw my position."* If a position
  is disclosed anyway, state the market view **before** acknowledging it, and do
  not let distance-to-liquidation reweight the probabilities. Write the view you
  would have written blind.
- **The protective flip is the banned move (read ⊥ holdability).** A position's
  distance to liquidation is a *holdability* fact, never evidence the read is
  wrong — the two are orthogonal. When a bad entry puts liquidation close, the
  desk must NOT flip, soften, or invert a correct scenario to rescue the book:
  liquidation risk is solved by the position (trim / exit / re-enter / size
  down), never by moving the view. Flipping a correct read converts a bounded
  entry error into an unbounded reversal loss — you go from "right but badly
  sized" to "wrong and paid to get there." This is the fossil of the AUG-11
  loss: right scenario, bad entry, desk spooked by the close liquidation and
  flipped a correct read; the machine's own risk-anxiety about the book, not the
  market, was the trick. The machine speaks only to direction; holdability is
  the trader's book call, and the machine never issues the flip.
- **Be blunt and short — the user skims.** No wall of tables, no restating every
  asset. Lead with what changed, then only the levels that matter, then the
  divergence, then the trade with its invalidation and tripwire.
- The "not financial advice" framing and the never-execute rule still stand;
  keep them terse rather than repeating disclaimers at length.

## Self-check before sending

Run this list every time. Each item is a failure that has actually happened.

- Did I run `macro_preflight.py`, and if it returned VOID, is **every** flagged
  mover matched to a named, dated story? An unexplained mover means no levels.
- Did my search wording presuppose the answer I wanted?
- Did I read the inbox — and did I avoid treating an empty inbox as proof that
  nothing happened?
- Is there an asset moving **against** my thesis that I have explained away?
- Does every price I quote carry a timestamp, and is it under ~30 minutes old?
- Am I quoting a stub market (`xyz:VIX`, `xyz:DXY`, and the others the pre-flight
  flags) as if it were a live price?
- Am I assuming a frozen weekend oracle, a mechanical reopen gap, or quoting
  `xyz:BRENTOIL` as the real oil price?
- Am I arguing a direction because a position exists in that direction?
- Did I call a level held, rejected or defended? If so, did I run `orderflow.py`
  first — or am I reading resting book size and candle volume and calling it flow?
- Did I state the print count and contract total behind every flow claim, and say
  out loud when the sample is too thin to act on?
- Did I check turnover before reading the tape, or did I read a 90-second window
  on a 0.18-turnover book and present it as a signal?
- Am I calling something "crowded" off a raw funding rate instead of the excess
  over the dex baseline and the premium in bp?
- Am I presenting HL open interest or HL flow as information about the underlying
  index? It is venue-local positioning. `xyz:SP500` does $88M against ES's
  hundreds of billions.
- Did I claim an OI change without a prior snapshot to measure it against?
- If this session follows a gap of more than a few hours, did I widen the sweep
  to cover the gap rather than just the last day?

## Interpreting fields

- `szi` sign gives the side; the script already converts to LONG/SHORT.
- `fundingSinceOpenUsd` is signed from the user's perspective: positive =
  received since the position opened.
- `currentFundingAprPct` annualizes the hourly rate (×24×365). Longs **pay**
  when funding is positive; shorts receive.
- The raw `funding` field in `metaAndAssetCtxs` is the **hourly** rate: ×8
  gives the 8h rate shown in the Hyperliquid UI, ×24×365 the APR. 24h change
  = `markPx`/`prevDayPx` − 1. (Verified against the live UI 2026-07-12.)
- `returnOnEquity` is on isolated margin for isolated positions.
- Portfolio `pnlUsd` per period comes from the exchange's own history and
  includes both realized and unrealized.

## Pitfalls

- **Positions can live on HIP-3 builder dexes** (coin names like `xyz:SP500`),
  not just Hyperliquid's main perp dex. The script sweeps every dex
  automatically and tags each position with its `dex`; per-dex account values
  are in `perDex`. If the user mentions a position you don't see, don't assume
  it's closed — check the `perDex` list first.
- **Agent wallet addresses return empty data.** If everything comes back empty
  for an address the user insists is active, they likely gave an API/agent
  wallet. Ask for the master or sub-account address instead.
- Time-ranged queries return at most ~500 rows; the script paginates fills
  automatically, but very active accounts over long windows may take a while —
  keep `--days` modest unless asked.
- If the script errors with "cannot reach api.hyperliquid.xyz", the sandbox
  blocks the domain; tell the user to allow it in network settings rather than
  attempting another fetch route. As a read-only fallback for market data,
  Claude in Chrome browser tools on https://app.hyperliquid.xyz/trade work
  (the markets dropdown lists price / 24h change / 8h funding / volume / OI);
  note the embedded TradingView chart canvas does not render in screenshots —
  use hyperdash.com chart panes if a visual chart is needed.
- The S&P 500 index perp is `xyz:SP500` — `xyz:US500` does not exist on the
  API even though some UIs label the market "US500".
- **Several xyz markets are dead stubs, not live prices.** They sit at a
  constant with 0% 24h change, zero funding and no flow — as of 2026-07-27 that
  includes `xyz:VIX` (pinned at 20.000), `xyz:DXY` (97.150), `xyz:URANIUM`,
  `xyz:ALUMINIUM`, `xyz:CORN`, `xyz:WHEAT`, `xyz:TTF`, `xyz:NIFTY`, `xyz:IBOV`
  and `xyz:GEV`. Quoting "VIX at 20" or "the dollar is flat" from these is
  fabricating a market read. `macro_preflight.py` flags them automatically; get
  the volatility read from options/news and the dollar read from `xyz:EUR` and
  `xyz:JPY` instead.
- For deeper API details (spot balances, order status, historical funding
  rates per coin), read `references/api.md`.

## Swing desk — DOCTRINE v2.3 (adopted 2026-08-08 after external review; supersedes conflicting defaults above)

This user runs a scheduled "swing desk" (5 firings: EU open light, US cash open full, US close light, weekend full + Sunday retro, on-demand). All are hardened (2026-08-13): version-check + append-only write discipline before any ledger write; attribution hygiene per rule #059. ANY interactive session doing market work follows the same doctrine:

1. **Ledger first, always.** Gmail draft "HL-OPS CALLS LEDGER" (fallback: Google Drive doc, same title, latest modifiedTime). Its RULES block is binding: grade resolved OPEN calls before any new analysis (timestamp + price, MAE/MFE from candles, R-multiple, time-to-resolution; running expectancy after costs is the headline metric, plus calibration by source). Append-only. No-trades are calls. Misses get LESSON lines.
2. **Two scenarios max** per instrument: PRIMARY + one ALTERNATE, each with own probability and invalidation. Primary invalidation = MISS even if the alternate then plays. EW/fib are context only, never the trigger; tag [EW-Context] vs [Structural-Only] (A/B tested in ledger).
3. **Call schema:** structural trigger | structural invalidation (never fitted to leverage; must exceed ~1.5x ATR14 noise) | probability % | horizon/TTT | one-line null hypothesis | abandon-tell | T1 + runner (stop to entry at T1, runner to next confluence) | leverage supported = risk budget / stop distance (say when 50x doesn't fit; never tighten a stop to fit leverage) | VIX regime tag + session tag | [Sentiment State] (free sources) | flags: ONE-BETA-TRADE (same-direction SP500/BTC/HYPE, 30d corr >0.8, vs last OLIVIER-EXPOSURE declaration), UNHOLDABLE (sub-1% stop into weekend/thin window).
4. **Blind audit before logging any new call:** spawn one subagent given ONLY the structured packet (no narrative); it returns its own P(direction), base-rate comment, top 3 reasons NOT to trade, alt invalidation. Log SELF-AUDIT; |ΔP| > 20pp = CONTESTED, lowest conviction. EXT-AUDIT lane = external model reviews couriered by the user.
5. **VENUE-STATE rule:** HL funding/OI/premium is venue state, never macro positioning. Cross-check (put-call/COT/GEX for indices via Alpha Vantage; cross-venue funding for crypto) before directional weight; otherwise advisory. HL funding may inform entry timing/carry.
6. **Macro-gate tightening:** a mover's matched story must PRE-DATE or co-time the move; multiple candidates = log ambiguity, don't assert causation.
7. **Alpha Vantage over web search** for market facts: real VIX (regime), cash SPX/SPY, real Brent/WTI (HL basis), SPY put/call term structure, calendars.
8. **User lanes:** OLIVIER-INPUT (his reads, scored), OLIVIER-DISSENT (scored), OLIVIER-EXPOSURE (self-declared clusters; stale after 7d — ask). US-close firing only: fills-based execution scoring AFTER views are final (fills only — positions/account/PnL remain off-limits per house rules).
9. **Weekly retro** (Sunday firing): metrics, lessons, up to 3 PENDING-APPROVAL process changes. Monthly: package updated skill for the user to save.
10. **Token discipline:** prefer structured tools over search; light firings deliver deltas ("No change. Nothing armed." is complete); never restate unchanged analysis.

Standing macro count (challenge every session, never assume): equities in a topping process → joint risk decline → crypto bottoms first, BTC survivor.


## Own-lines engine (added v2.4, 2026-08-08)

`scripts/structure.py [COIN ...]` computes the desk's OWN technical structure from raw candles — never rely on user-supplied chart drawings as primary input (treat screenshots as cross-checks only). Per coin it scans 15m/1h/4h/1d: fractal pivots, trendlines through pivot pairs scored by touch count (broken lines rejected), untapped swing highs/lows, then clusters everything into ranked multi-timeframe CONFLUENCE ZONES (objects >15% from mark filtered as ancient-anchor artifacts). FULL firings run it for the instruments in play and quote its zones alongside volume-profile levels; where an engine zone and a POC/VA level stack, that is first-class confluence. Lines are recomputed fresh every run — no stale hand-drawn anchors.


## Doctrine v3.2 — state estimation, coherence & the research firewall (2026-08-13; ledger #063–#064; PROPOSED items pending Sunday retro)

**Governing frame.** Do not predict the noisy surface; estimate the state underneath it, then test whether that state makes the next transition conditionally predictable. A read's product is: (1) a state estimate across the nine observation families — structure, macro, positioning, flow, liquidity, time, sentiment, operator incentives, crowd belief (families feeding one estimate, not nine equal weights); (2) which transitions just became more probable, tested across horizons (noise dominates some Δ, structure others); (3) what proves it wrong. First estimate the state. Then test the transition. Then remember the result.

1. **State coherence replaces "manipulation" talk.** Deception, operationally = the measured probability that current price action is inducing positioning opposite to the subsequent path. Detect it as INCOHERENCE between families (price up but spot not leading; story says fear but positioning never left; break lands in the operator-preferred hour) — never assert who caused it. The "operator" is a game-theoretic model, not a claimed fact. An incoherent state → deception grade up → quarantine / no view. No-view is a first-class output.
2. **Deception base rates (145d, n=189 level-breaks; ledger #053–#055; quote with n, "directional").** Low-breaks: 66% traps overall — 92% uptrend / 64% range / 53% downtrend. High-breaks: 76% fake in range, 59% once markup confirms. Traps reclaim fast (median 10 min; 60 min is the definition cutoff, not a finding). Real breaks average −3.6% vs a trap's −2.0% — frequency comforts, magnitude kills. Sweeps precede ~70% of squeezes (they mint shorts, not spend them). Repeated sweeps decay 50%→38% (R-044, CANDIDATE). Sequence: immediate trap history added no measurable predictive information under the tested specification — a bounded claim, never "the market has no memory."
3. **Research firewall (R4).** DISCOVERY (anything may be tested, no live influence) → CANDIDATE (frozen, pre-specified test) → ADMITTED (blind-validated on data untouched during discovery) → only then live conviction. The trial log records every test including discards; the trial count is the denominator of any significance claim. Overnight findings are CANDIDATE by default — never trade a same-night discovery's conviction at the next open.
4. **Blind-audit fact firewall (R5, supersedes v2.3 §4 packet definition where they conflict).** Audit packets contain raw exchange facts only — no thesis, no trap-scores, no deception grades, no derived features, no narrative, no trader opinion. The auditor extracts its own observations first, then derives its own probability; comparison only after both are committed.
5. **Narrative-capture metrics (R6).** Per contested view log P0 (before trader input), P1 (after input, no new data), P2 (after next primary data). Narrative elasticity |P1−P0| vs evidence elasticity |P2−P1|; NE large + EE small = co-narration flag. A stance change without new primary data is itself a logged event.
6. **Bounded claims (R7).** Label every empirical statement OBSERVED / INFERRED / HYPOTHESIS / SPEC. Banned words for desk claims: proves, always, zero memory, engineered, "institutional operators" as fact. Instruments carry maturity labels: trap-score INPUTS MEASURED / WEIGHTS UNFITTED · blow-ratio FIRST OBS (n=1, $87M ≈ 350 pts, calibration unproven) · trick-EV SPEC · deception meter SPEC · time-as-weapon PARTIAL (time-tells measured, raid proxy spec). Nothing enters live weighting without demonstrated out-of-sample value.
7. **Added instruments (game layer).** Trap-score factors: event proximity, positioning (dOI + funding), hour-class, volume character, spot-vs-perp lead, structure freshness. Lead–lag clocks: who moved first is a tell (price before news = someone knew; story before flow = someone is selling you something). Pattern-of-life: activity peaks 13–15 UTC; ~01:00 UTC Asia burst hour; **04–10 UTC EU morning is a statistical distrust window — no conviction upgrades from moves inside it.** Time-as-weapon: price-raids harvest stops fast, time-raids harvest capitulation slowly (boredom exits, funding bleed, OI decay).
8. **Rejected with reasons (do not re-adopt without new evidence).** DSR≥0.95 hard admission gate (false precision at current N — use the strongest appropriate statistical method per hypothesis; tools, not truths). Automated server-side stop deployment (violates the read-only constitution; monitors summon, the trader decides). Persona-framed auditing (independence comes from information separation, not role-play). Multi-agent debate as default (correlated errors, consensus theater). External reviews receive the same verification as market claims — a reviewer fabricating statistics is an external-lane calibration event (ledger #063).
9. **Hand-off rule.** The ledger holds thesis state; the trader holds book state. When a thesis a disclosed position leans on transitions to DEAD, saying so immediately is the highest-priority output of any session or firing.
10. **Live vision.** While an interactive session is alive, arm a standing monitor on the ledger's own armed levels (crossing-triggered, ~20s poll, hysteresis re-arm; expect ~30-min re-arm cycles). Between sessions the firing cadence is the coverage net — never imply continuous vision that does not exist.


## Doctrine v3.3 delta — research session 2026-08-13 (ledger #066)

11. **Trap-score first measured factor ordering (T-001, DISCOVERY — CANDIDATE-PENDING, do not use for live conviction yet).** On 93 low-break events (12h-reclaim spec; differs from #053's 60-min spec — the LIFTS are the finding, not the levels): sweep DEPTH dominates — shallow sweeps (<0.24% beyond the level) trapped 46/46 under this spec, in every regime; deep sweeps 64%. Quiet breaks (range-expansion below median) trap 91% vs 72% loud. Ordering: depth >> volume-character >> regime > hour-class. Mechanism HYPOTHESIS: shallow+quiet pokes are probes/stop-harvests; deep+loud breaks carry participation. Requires re-test on the original spec + blind validation before any weight goes live — a 100% cell on n=46 is exactly what the firewall exists for.
12. **Deception Meter v0 (pre-registered #066, thresholds frozen until N≥30 readings).** Four binary components, sum /4: (1) sentiment extreme — Fear&Greed ≤20 or ≥80; (2) funding stress — |excess APR|>15% or |premium|>15bp sustained 24h; (3) breadth divergence — BTC move unconfirmed by majority of ETH/SOL/HYPE; (4) analyst unanimity in inbox digests (verbatim-quote test). Log a reading every full firing; revise thresholds once at N≥30, then freeze again.
13. **D7 forward-collection duty (binding).** Full firings and the dedicated D7 collector (scheduled 12:00 & 20:00 UTC) log per armed ledger level: l2Book resting depth (bid/ask, ±0.3% of level), pool estimates beyond it, and realized displacement per $M when a level breaks — accruing the blow-ratio / trick-EV calibration sample from n=1 forward. Rationale: depth-at-level cannot be fetched retroactively; the sample only exists if we record it.


## Doctrine v3.4 delta — hostile-review triage (2026-08-13, ledger #068)

14. **Registered architecture kill condition (the desk's falsifier).** IF, across ≥500 verified OUT-OF-SAMPLE level-break events spanning at least one regime shift, state-conditioned expectancy after the standing cost model and FDR control is ≤ 0, THEN the deception-edge thesis is DEAD — the desk stands down as a trading-signal generator and survives only as process tooling. Progress toward this is reported at every Sunday retro.
15. **Standing cost model.** All expectancy math from 13 Aug 2026 onward is quoted AFTER a ~25bp round-trip friction haircut (taker fees ~9bp + spread 2–8bp + impact 5–15bp in volatile windows). No un-haircut expectancy may be presented. Context: desk horizons target 200–400bp swings; the haircut matters but does not invert them a priori — it must be measured.
16. **Microstructure null for the operator model.** The null hypothesis for every "deception" pattern is classical LOB mechanics: adverse selection, inventory unwind, quote-pulling. The deception grade graduates only by outperforming that null out-of-sample — not by beating an unconditional baseline. Grades/meters graduate only with proper-scoring-rule evidence (Brier or log-loss + reliability by grade bin), never hit-rate anecdotes.
17. **Validation hygiene (amendments to R4/T-001/R-044).** (a) T-001 depth threshold is pre-registered FIXED at 0.24%, tested on the original #053 60-min spec on held-out data — median-split-after-seeing-data is ex-post selection and may not recur. (b) Validation partitions must span at least one regime change; a subsequent same-regime window is NOT independent. (c) N≥50/lane is the PROCESS freeze-lift only, explicitly not an edge-significance threshold — edge claims need hundreds of events across regimes. (d) R-044 (sweep decay) requires ~hundreds per group for power (Fisher p≈0.43 at n≈30) — it stays CANDIDATE indefinitely on single-venue BTC data; extension path is cross-asset/cross-venue accrual. (e) The 70% sweep→squeeze figure requires a control: measure P(squeeze|sweep) and the base rate of comparable moves preceded by local-extreme breaks before it is quoted as more than sequence description.
18. **Enforcement countability.** Sunday retros publish counts: blind audits run / CONTESTED flagged / contested actually sized-down / rules frozen vs admitted / trials logged vs discarded. Claims of discipline are numbers like everything else.
19. **Hostile-review rebuttal file (do not relitigate without new evidence):** df=−261 assumes a fitted 450-parameter joint model that is never fitted (base rates are 1–2 way marginal splits; weights frozen). Regime labels use SMA state AT event time — no look-ahead. Latency attacks price a microsecond scalper; the mechanical sweep-scalp was killed in-house (R-042, EV≈0). Reviewer-invented quantities (Gemini's CIs/#00471, hostile review's SDT d′ inputs) are external-lane calibration events — external reviews get the same verification as market claims.

20. **Prediction vs state estimation — the resolved tension (2026-08-13).** The desk does not abandon prediction; it distrusts UNCONDITIONAL prediction. Three layers: (1) estimate the state; (2) generate ≤2 scenarios with probabilities over explicit horizons; (3) the TRADER takes the highest-probability actionable scenario — probability × payoff × invalidation is his decision, never the machine's. Recursion exists to sharpen those probabilities: state → hypothesis → evidence → probability update → new state estimate. When the system predicts accurately, keep the prediction (and grade it); when it cannot, keep the state estimate (and say so). State estimation is the architecture; prediction is the reward function. The research firewall's purpose restated: not proving prediction impossible — discovering where it becomes conditionally possible.

21. **Market-maker mechanics & the leverage-cascade hypothesis (2026-08-13, HYPOTHESIS layer).** The trap shape is producible WITHOUT intent by standard MM mechanics: quote-pulling at obvious levels (adverse-selection defense) → thin book → small aggression "breaks" it → stops fire into vacuum → MMs re-enter at edge, absorb forced flow → unwind = reclaim. This is the microstructure null (§16) stated as mechanism — and it concedes the trap is structural and harvests the positioned, which is all the desk needs. LEVERAGE-COHORT TOPOLOGY: leverage tiers map to timeframes via liquidation distance (≈40x dies 1–2% from entry = intraday sweeps; ≈20x at 3–5% = hourly/daily; ≈10x at 8–10% = weekly). Sequencing hypothesis: each harvest MINTS the next tier's fuel (swept cohort re-enters at worse prices with fresh stops + next band's untouched liqs). "Market finds the max-fooling sequence" = SELECTION not intention: max-harvest paths pay liquidity providers most, so aggregate inventory optimization drifts price toward them; the visible stop/liq topology is the coordinator. REGISTERED-PENDING HYPOTHESES: H-1 sweep depths cluster at recent-cohort liquidation radii; H-2 after an intraday sweep the next-larger liq band GROWS (dOI at worse prices) before the larger move — test with D7 depth series; H-3 realized direction correlates with the larger harvestable pool (Trick-EV's formal test); H-4 Hyperliquid HLP vault = PUBLIC MM inventory (unique observable; candidate tenth observation family — inventory swing through trap-reclaim cycles). All HYPOTHESIS until the forward collection accrues; none touches live conviction (D4).


## Doctrine v3.5 delta — the protective-flip ban (ledger #069; RATIFIED #070, 2026-08-13 — STANDING DOCTRINE)

22. **Read ⊥ holdability; the protective flip is banned (binding on every session and firing).** A position's distance to liquidation is a *holdability* fact, never evidence the read is wrong — the two axes are orthogonal. The desk must NEVER flip, soften, or invert a correct scenario to rescue a book near liquidation; liquidation risk is a position problem (trim / exit / re-enter / size down), solved by the trader, never by moving the view. Flipping a correct read converts a bounded entry error into an unbounded reversal loss ("right but badly sized" → "wrong and paid to get there"). Origin (ledger, AUG-11 loss): right scenario + bad entry → desk spooked by the close liquidation → flipped a correct read → loss. The trick was the machine's own risk-anxiety about the trader's book, not a market deception — so this is a governance rule, NOT a new deception instrument; do not build machinery for it. Corollary to §9 (hand-off) and the house-rules blind-view discipline: the machine speaks only to direction and never issues the flip.


## Doctrine v3.6 delta — T-002/T-003 backtest results (ledger #071, 2026-08-13)

23. **Sweep-depth → reclaim: regime-spanning OOS cleared (T-002 Test B; CANDIDATE, NOT admitted).** Pre-registered, 0.24% depth threshold fixed a priori, on 833d of BTC/ETH/SOL 4h; held-out 2nd half spanning a bull→bear regime change: shallow sweeps (<0.24% beyond the level) reclaim **84.9%** (Wilson 81–88, n=337) vs deep (≥0.24%) **60.4%** (58–63, n=1284), non-overlapping. This clears the #068 A5 regime-spanning bar for the T-001 depth factor — the desk's strongest candidate. USE: cite the shallow-sweep→reclaim base rate as CANDIDATE-maturity **context** in reads (labelled: ~85% shallow / ~60% deep; effect attenuates on 4h vs 1h's 92/73 — always quote the timeframe), NEVER as live conviction or a trade trigger. REMAINING FOR ADMISSION: proper-scoring evidence (Brier/log-loss + reliability by bin, A4), out-performance of the microstructure null (A6), and larger cross-asset/venue N. Still DISCOVERY→CANDIDATE; nothing here touches live sizing (D4).

24. **Pain-radii / leverage-cohort / wave-clustering: REJECTED in price-observable form (T-002 Test A + T-003, 0/4 tests).** Sweep-continuation magnitudes AND swing-leg magnitudes show NO clustering at the 2/5/10/20% liquidation radii (concentration ratio ≈1.05, matching a non-sweep control; distribution is smooth exponential with no peaks). The clean price form of the fractal-harvest / leverage-clock story is DEAD. Interpretation (trader note, adopted): leverage is DYNAMIC — margin top-ups, cross-margin portfolio liq, mid-trade leverage changes and partial closes smear the static 1/L radius — which explains the null but does not rescue it. If the mechanism is real it is ORDER-BOOK-LEVEL (depth / liq-map, D7 forward-only), not price-clustering. DO NOT build price-based leverage-cluster instruments and do not re-run this clustering family without new (order-book) data; the leverage-clock and EW/fib overlays remain CONTEXT / labelled brainstorming only (never a single-count predictive engine), per the watchlist Elliott-Wave rule.


## Doctrine v3.7 delta — latent fuel & the denied-exit-liquidity squeeze (2026-08-13, OLIVIER-INPUT adopted; ledger #072)

25. **Latent fuel: "funding neutral = no fuel" is TOO STRONG (positioning-read refinement + game layer).** HL funding/OI see only crowded PERP leverage — NOT latent fuel: cash-on-sidelines waiting for the dip, cross-venue shorts, the crowd's flush-lean. A squeeze CAN fire from neutral funding when the expected sweep does NOT come and flush-waiters / offside shorts are denied their exit liquidity and forced to chase — the "denied-exit-liquidity" squeeze. This is the mechanism behind the grind-up pain trade (the no-sweep third path). The mechanism is HYPOTHESIS / interpretation — latent fuel is UNOBSERVABLE by construction; never claim it as measured. Amends the oi_flow "nothing crowded = no setup" line: it is correct for PERP-leverage crowding — phrase it as "no perp fuel; latent fuel not visible here," never a flat "no fuel."
    DISCIPLINE (governance, binding): (a) TELL, because the fuel is invisible — NEVER invoke "trapped shorts / denied liquidity" to justify an up-move absent the observable signature: the squeeze fires as an IMPULSIVE break through resistance (acceleration, no retrace); a choppy rejection means no fuel, just rotation. (b) DEATH-PRICE GUARD (co-narration instance, ties D5 + #22): if BOTH the sweep-path (shallow reclaim ~85%, rule #23) AND the no-sweep-path (trapped flush-waiters) read bullish, the thesis has NO death-price and is FORBIDDEN — a thesis where every path is up is a hope, not a trade. Name the down explicitly: a deep break that ACCEPTS below the invalidation, OR repeated fade at resistance with no chase. Every multi-path thesis must survive the "what makes this DOWN?" test before it is voiced.


## Doctrine v3.8 delta — trendline break+retest watch, liquidation-map picture (P2), VCP-ABLATION experiment (2026-08-15; OLIVIER-INPUT session)

26. **STANDING WATCH — trendline break + retest ("backtest"), both directions (binding on every read and firing).** Always scan for breaks of the desk's own trendlines (structure.py TL-res/TL-sup objects, scored by touch count) AND their RETEST: price breaks a line, returns to it, the retest holds = entry — long on an up-break, short on a down-break. This is target T-A generalized to DIAGONAL levels; the retest-hold is the diagonal analog of the #23 reclaim. Report any in-progress break+retest in every read: direction, the line (touch count), the retest level. SFP (swing-failure) and horizontal reclaim are the SAME event family — a level is swept/broken and the only question is reclaim-vs-continue. Apply standard discipline (distrust-window, weekend-thin, turnover, no "held/rejected" without flow).

27. **LIQUIDATION-MAP PICTURE = observation family / ablation layer P2 (NEW data source).** Source: Coinglass liquidation heatmap, free tier, via the user's browser (procedure in references/liqmap_capture.md). READ: aggregate the decrypted liq matrix into a price profile; bands ABOVE price = SHORT liquidations (up-squeeze fuel / magnets), bands BELOW = LONG liquidations (downside drain targets). Use it to CONFIRM or KILL a magnet/SFP thesis. Verified 2026-08-15: it confirmed a short-liq shelf 63.29–63.65k (Olivier's "63,500" = the 63,515 band, shelf center), reversal drain at the long-liq pool 62.0–62.4k. CAVEATS (bounded claims, D3): single-exchange (Binance) + 24h + Model-1 = leverage-ESTIMATED, cumulative-over-window intensity, NOT literal resting orders; free tier ≠ all-exchange aggregate; it does NOT replace HL positioning — it is venue-estimated leverage topology, a new picture, not ground truth.
    **AUTOMATION CAVEAT (honest):** liq-map capture needs an INTERACTIVE browser session (extension + JSON.parse decrypt hook). Scheduled/headless firings likely have NO browser, so P2 forward-collection is INTERACTIVE-ONLY until a headless path (server-side decrypt, or a local script the user runs) is built. Never claim the cron collects it.

28. **VCP-ABLATION-001 (sealed pre-registration 2026-08-15, sha256 344cbad6…).** Standing experiment: does adding "pictures" (nested layers P0 price → P1 positioning → P2 liq-maps → P3 cross-venue → P4 time → P5 macro) LOWER out-of-sample log-loss on sealed labels, per layer, on regime-spanning held-out data, trial-count as denominator? Targets: T-A reclaim-vs-continue (primary), T-B liq-magnet, T-C cascade-vs-fizzle. P0/P1 backtest on history now; P2 forward-collection-only (started 2026-08-15). Firewall DISCOVERY→CANDIDATE→ADMITTED; nothing live until blind-validated. This is the empirical spine of "more pictures = better prediction?" — it may CONFIRM or REJECT; both are logged. Full spec: references/VCP-ABLATION-001.md (+ .seal.txt).

29. **OPEN OLIVIER-INPUT call (2026-08-15, for grading).** BTC: backtest of the descending trendline pushes into the 63.29–63.65k short-liq shelf → SFP reversal down toward 62.4k then 62.0k. Invalidation: hourly acceptance >63.65k (no fail) OR direct break <62.8k (no push-up leg). Weekend/distrust-window → scenario, not a sized call. Grade on resolution: map-confirmed version vs eyeball version.


## Doctrine v3.9 delta — Elliott-Wave as a live multi-timeframe SCENARIO TREE (2026-08-15; OLIVIER-INPUT session)

30. **STANDING: maintain a multi-timeframe EW scenario TREE in every read and FULL firing.** Not a single count — a probability-weighted set of scenarios across timeframes, each with a HARD INVALIDATION, re-weighted by every move. This operationalizes #20/D1 (estimate state → scenarios with probabilities over horizons → update on evidence) for wave structure. GUARDRAILS — what keeps it edge, not astrology:
    (a) **≥2 counts, ALWAYS.** Single-count certainty is the banned failure mode (watchlist EW rule). Primary + ≥1 alternate, each with a rough probability.
    (b) **Every count carries an invalidation PRICE — that price IS the update rule.** A move does not "surprise" the tree; it crosses an invalidation and re-weights it. State each count's kill-level explicitly.
    (c) **EW is CONTEXT, never the trigger.** It must agree with the mechanical read (structure.py levels / liq-map / positioning / forced flows); on conflict, the MECHANICAL wins. Prefer counts whose pivots COINCIDE with real levels (a liq shelf, a pool, a POC) — a wave label with no mechanical level under it is noise.
    (d) **Label HYPOTHESIS; no false precision.** The product is "what invalidates this + which scenario just gained probability," NOT "what happens next." Report compactly: Count A (prob, invalidation), Count B (prob, invalidation), and the shared pivot that discriminates them.
    SCAR (do not forget): the PREDICTIVE form of wave structure was tested and REJECTED — T-003 "waves × timeframes × leverage clusters" failed 0/4 in price-observable form (#071). EW earns its place ONLY as scenario-organizing scaffolding with hard invalidations and a fast "you're wrong here" signal — NEVER as a source of edge. The edge is mechanical (liq-map, positioning, forced flows); EW is the frame that tells you WHEN a scenario died and which one is now live.
    EXAMPLE (2026-08-15 BTC ~63.0k, post-#050-A break): A — corrective decline near exhaustion (~55%), finishing near the 62.0–62.5k long-liq pool; trendline break+backtest into the 63.3–63.65k short-liq shelf = counter-trend bounce; inval acceptance <~61.9k. B — impulsive decline, more to go (~45%); 62.0–62.5k a pause; rallies into 63.3–63.65k are counter-trend to sell; inval acceptance >~63.65k. Both route through the same liq-map levels; the 63.3–63.65k shelf is the discriminating pivot.


## Doctrine v3.10 delta — measurement discipline + trendline-reclaim null (2026-08-15; OLIVIER-INPUT session, DISCOVERY)

31. **VOLUME IS RELATIVE — judge vs the weekend/hour baseline, never absolute (binding on every flow/tape read).** Measured 2026-08-15: weekend 5m volume runs ~34% of weekday; a print that looks like "dust" in absolute terms can sit at the ~80th percentile for a weekend morning. Never dismiss weekend / off-hours flow as noise without the percentile. The orderflow sample-size honesty (#0h) still holds — but "thin" is a percentile claim against the RIGHT baseline, not an absolute-BTC claim. This corrects an actual error this session (a real buy-flip at ~80th-%ile weekend volume was miscalled "dust").

32. **TREND-LINE RECLAIM IS NOT A STANDALONE TRIGGER (trial T-004, DISCOVERY/in-sample — do NOT use for live conviction).** Backtested walk-forward with the desk's OWN lines (last two confirmed descending pivot highs, structure.py logic; pivots known only at p+k, no look-ahead), 5m/15m/1h/4h, +0.8% target vs reclaim-fail stop (line −0.2%), 25bp round-trip cost, vs unconditional drift (scripts/backtest_reclaim.py, backtest_confluence.py):
    - Naked descending-trendline reclaims are **null-to-negative after costs** on every timeframe; they do not beat the do-nothing drift baseline.
    - **"Confirm earlier" is worse, not better:** EARLY (impulsive reclaim) carries a 55–57% false-start rate and is ≤ STRICT (hold-above-2-bars). Waiting marginally beats rushing; neither is profitable.
    - **Multi-TF line×line confluence raises HIT-RATE modestly (41>37, 46>31, 50>40) but NOT expectancy** — confluent reclaims fail with fatter tails, so the accuracy edge dies in the mean. Confluence buys accuracy, not expectancy.
    - Companion null: bullish RSI-divergence at a fractal low → +2h median +0.12% (marginal, pre-cost). Eyeballed chart-TA triggers do not carry edge after costs in-sample.
    CONSEQUENCE: a reclaim / trendline-confluence is CONTEXT (a scenario discriminator per #30), NEVER a standalone long trigger. The untested, forward-only question is **reclaim × LIQUIDITY (P2 liq-map shelf)** — liquidity-confluence, not line-confluence — which is where the live thesis lives and what P2 collection exists to grade. Status DISCOVERY/in-sample, single venue+asset, one pre-specified spec; needs blind + regime-split + proper-scoring (R4/A5/A6) before any live weight.


## Doctrine v3.11 delta — post-impulse reclaim underperforms (T-004b, 2026-08-15, DISCOVERY)

33. **POST-IMPULSE RECLAIM = CHASE / EXHAUSTION — it UNDERPERFORMS (T-004b, extends #32; DISCOVERY/in-sample).** Conditioning a descending-trendline reclaim on a PRIOR strong impulse off the lower shelf (≥0.8% up from the shelf + a >1.2x ATR bullish candle in the run-up) makes it WORSE, not better: 1h impulse-preceded mean −0.66% (median −0.55%) vs flat-preceded −0.03% (median +0.50%); 4h −1.37% (median −1.12%) vs −0.00% (median +0.03%). ~1% separation, same sign both timeframes. MECHANISM (interpretation): the impulse already spent the fuel — by the reclaim you are buying late, into exhaustion; the clean thrust that makes the setup LOOK likely is exactly what marks it a worse long. Counterintuitive, and it contradicted a live OLIVIER-INPUT read (which was factually correct that the impulse happened — 08-14 15Z, +1.5x ATR off 62,523 — but wrong on its bullish implication). This says the LONG has negative edge; it does NOT greenlight a short. Caveats: modest n (39–46 in the impulse bucket), one pre-specified definition, in-sample, single venue/asset; needs blind + regime-split. Untested frontier: impulse × LIQUIDITY (P2 liq-map shelf), which may interact differently.


## Doctrine v3.12 delta — HL exposes GROUND-TRUTH liquidation data; line-relative excursion (2026-08-15; OLIVIER-INPUT session, DISCOVERY)

34. **HYPERLIQUID PUBLISHES EXACT LIQUIDATION LEVELS AND EVENTS — the TRUE liq-map supersedes the Coinglass ESTIMATE (verified 2026-08-15).** Probed the info API directly. Three distinct objects, do not conflate:
    (a) **Current liquidation LEVELS — EXACT, not induced.** `clearinghouseState(user)` returns every open position with HL's own computed `liquidationPx` (+ signed size `szi`, leverage). Aggregate liqPx×notional across addresses → the REAL fuel map (long liqs = forced SELL below = down-fuel; short liqs = forced BUY above = up-fuel). This is what Coinglass only *estimates* (their Model-1 = leverage-guess off price). We can build it exactly. LIMIT: it is a LIVE snapshot — no historical/time-parameterized form exists, so the map is **forward-collect-only** (must be stored from now; can't be pulled as-of a past date).
    (b) **Realized liquidation EVENTS — fully reconstructable, historically.** Every liquidation is a public tagged fill: `userFillsByTime(user,…)` returns fills carrying `liquidation:{liquidatedUser,markPx,method}` (exact px/sz/time/victim). Address universe is harvestable from the public `recentTrades` feed (`users` field exposes both counterparties per trade). So historical liquidation *events* ARE buildable; coverage compounds as the address book grows.
    (c) **Answer to "can you induce liq levels from PAST orders?" — verdict:** the price-only leverage-band reconstruction (guess bands X% off price at assumed leverage) is exactly **T-003, already REJECTED as null (#071)** — that is "inducing" in the bad sense, do not revive it. You do not need it: HL hands you exact *current* levels (a) and exact *past events* (b) directly. The only thing genuinely unavailable via any single call is the *historical MAP* (levels as they stood at a past instant) — obtainable only by replaying the full on-chain fill log to rebuild every position at each past moment (heavy, but possible since HL is fully on-chain). CONSEQUENCE: stop treating liq-levels as something to model; they are something to OBSERVE and STORE. This is the concrete form of "HL is a mine of information Renaissance never had" (OLIVIER-INPUT) — the mine is real but FORWARD, and it is ground truth, not estimate.
    (d) **FORWARD COLLECTOR built (`scripts/collector.py`, READ-ONLY /info only).** Appends timestamped JSONL: `market` (mark/funding/OI/premium/impact), `book` (l2Book depth bands + walls), `hlp` (Hyperliquid's own market-maker NET inventory across its 7 child vaults + equity/APR — the unique observable), `liqmap` (the exact-liqPx TRUE map, up/down fuel + clusters), `liqevent` (realized tagged liqs). Persistent `addressbook.json` compounds coverage across runs; bounded per-tick sweep. This is the P2 layer of VCP-ABLATION-001 filling from today, upgraded from Coinglass-estimate to HL-ground-truth. NB: persistence across the ephemeral firing sessions requires a durable sink (Drive/ledger) — collector writes local JSONL by default; wire the sink before relying on accumulation.

35. **LINE-RELATIVE EXCURSION — the right lens on "does the trendline break travel?" (trial T-004c, OLIVIER framing, DISCOVERY/in-sample; `scripts/backtest_lineexc.py`).** Per OLIVIER-INPUT: don't grade a trendline event by fixed-time return — grade by how far price runs PAST the line before it REVERSES (closes back through the line = round-trip), measured UP (reclaim of descending resistance) and DOWN (breakdown of ascending support). Walk-forward, own-lines, no look-ahead, BTC, target scale +0.5%. Result:
    - **Excursion scales with timeframe and cleanly gates tradability.** Median peak-past-line: 15m UP +0.23% / DOWN +0.27% (BELOW the 0.5% target → sub-hour line-crosses are noise); **1h UP +0.91% (67% reach +0.5%, OOS train +1.12/test +0.83) / DOWN +0.50%**; 4h UP +1.39% / DOWN +1.57% (both clear). This independently REPRODUCES "the edge lives at ~1h, not sub-hour" (#32, backtest_sweep) and EXPLAINS it: sub-hour reclaims simply don't travel far enough past the line before round-tripping. "Magnitude kills" made geometric.
    - **Round-trip ~50% at every TF** → the line-cross alone is a coin-flip on persistence; the signal is entirely in the MAGNITUDE distribution (the winners run 0.9–1.6% at 1h/4h), never the hit-rate. Same lesson as #32/T-004b and the shallow-reclaim excursion work: reward is in the tail, a tight −0.3% chase-stop gets shaken out before the run; a wider stop / partial-target / dip-entry is required to capture it.
    - **UP/DOWN excursion asymmetry is itself a live regime read.** At 1h over 208d, UP excursions ran **1.82× DOWN** (net-bullish drift epoch); 4h ~symmetric (0.89×). Tracking current up-excursion vs down-excursion is a directional-bias gauge — a byproduct signal worth logging. Status DISCOVERY/in-sample, single venue/asset; does NOT resurrect T-004 as a mechanical bracket trade (round-trip 50% + tight stop still loses) — it sharpens WHY and adds the asymmetry gauge. Frontier: excursion conditioned on the P2 liq-map shelf ahead (does price run further when a liq cluster sits in the excursion path?).


## Doctrine v3.13 delta — the combiner / ensemble layer (VCP-COMBINER-001 sealed, 2026-08-15; OLIVIER-INPUT session)

36. **THE EDGE IS THE ENSEMBLE, NOT THE SIGNAL — combiner method SEALED (VCP-COMBINER-001, sha256 14a75ca3…; references/VCP-COMBINER-001.md).** Take from RenTec/Numerai the METHOD, never a magic signal: many weak, decorrelated, cost-surviving edges, blind-validated, regime-tested, ensembled. Combined IR ≈ IR_single × √(N_independent) → the object to maximise is the number of genuinely INDEPENDENT admitted net-of-cost bets, not any one signal's cleverness. This sits one level ABOVE VCP-ABLATION-001: the ablation grades FEATURES (does each picture lower OOS log-loss); the combiner grades COMBINATIONS (does each admitted signal add ensemble value net of AGGREGATE cost). Frozen decision rules (pre-committed so the combiner can't be reverse-fit to flatter a favoured signal):
    (a) **Admission gate** — a signal carries weight ONLY when ADMITTED (blind OOS, regime-spanning A5, proper-scored A4, beats microstructure null A6), net-positive after real ~5bp cost on its own turnover (A7), emitting a CONTINUOUS CALIBRATED output (prob or z, isotonic/Platt), with a documented decorrelation profile. DISCOVERY/CANDIDATE = logged, never weighted.
    (b) **Decorrelation is the whole point** — |ρ|≥0.7 (outputs or PnL) = ONE cluster, one signal's weight; new signals orthogonalised against existing span (only incremental info earns weight); report effective independent-bet count (1/Σw²), not raw signal count.
    (c) **Weighting ladder, promote only on OOS evidence** — T0 equal-weight (robust default, beats "optimised" at small N) → T1 risk-parity → T2 shrunk-IR (Ledoit-Wolf) → T3 meta-learner (only at N≥hundreds spanning ≥2 regimes). A tier is adopted only if it beats the tier below OOS after cost. The combiner is firewalled like any signal.
    (d) **Cost charged on the AGGREGATE** — co-directional signals don't pay double; a signal is scored on incremental cost-adjusted contribution (marginal IR after its added turnover), which can differ from its standalone edge.
    (e) **Conviction → size** — combiner emits a VIEW (calibrated conviction); trader sizes via vol-target / fractional-Kelly (≤¼, capped), never full Kelly; read⊥holdability (#22) — combiner never orders, never flips to rescue.
    (f) **Decay & scheduled re-fit** — weight→0 when a signal stops beating its null (benched, not deleted); re-fit on a fixed schedule under the firewall, NEVER continuously; each re-fit is a logged trial.
    CURRENT STATE (honest): ADMITTED = 0; best CANDIDATE = 1h shallow-sweep→reclaim (excursion-graded, needs blind+regime+proper-score+null); P2 liq-map/HLP accruing, not yet gradeable. So the combiner is EQUAL-WEIGHT-OF-ONE (i.e. the single signal) until a SECOND decorrelated admitted edge exists. ACTIVATION TRIGGER: ≥2 admitted, decorrelated, cost-surviving signals on the same target. Success criterion for the combiner itself: OOS + regime-spanning + after aggregate cost, it must beat (a) the best single signal, (b) equal-weight, (c) the microstructure null, on proper score AND realised expectancy — else it stands down to equal-weight or to the single best signal. Nothing adopted on in-sample improvement.


## Doctrine v3.14 delta — per-asset discipline + discovery sweep null + admission checklist (2026-08-15; OLIVIER-INPUT session, DISCOVERY)

37. **PER-ASSET, NEVER POOLED (binding on ALL backtests/discovery) + the discovery sweep came back NULL + shallow-reclaim admission gate (scripts/discovery_sweep.py, funding_sweep.py, references/ADMISSION-shallow-reclaim.md).**
    (a) **NO POOLING RULE (OLIVIER-INPUT, binding):** BTC trades differently from ETH/SOL/HYPE — never pool coins into one sample; grade every signal PER-ASSET. A signal admitted on BTC is a BTC signal; other coins are separate questions (and separate, possibly-decorrelated, signals for the combiner). Pooling assets with different dynamics manufactures fake edges. RETRO-FLAG: T-002/T-003 (#071) POOLED BTC/ETH/SOL — the only pooled-POSITIVE there (depth→reclaim Test B, 84.9%) is now SUPERSEDED by the BTC-only excursion/SFP reconfirm (below); the pooled-NEGATIVES (pain-radii, wave-leverage clustering) stay null and a BTC-only rebuild is low-priority (pooling more data helps find edges, so pooled-null ≈ BTC-null). Also flag: the D7 collector and forward collector are already PER-ASSET (per-coin rows, no cross-coin pooling of any signal) — compliant.
    (b) **DISCOVERY SWEEP = 30 BTC-only trials, 0 survivors (T-005 price battery + T-006 positioning).** Uniform excursion grading at +0.5%/−0.3%/5bp vs matched random control, OOS train/test split, trial-count as denominator. T-005 (price, 27 cells across 1h/2h/4h): mean-reversion (overext z>2, 4-consec fade), momentum (NR7, Donchian20), large-range follow/fade, vol-spike cont/fade, inside-bar — ALL net-negative after 5bp, none beats random OOS-consistently (best vsRAND +0.061% fails OOS). T-006 (positioning, funding_sweep.py, 180d paginated fundingHistory): funding-extreme fade/follow + premium-extreme fade — all null/≤random on BTC (BTC funding is pinned/efficient; extremes are an alt phenomenon). CONSEQUENCE: the naive pattern zoo is null after costs on BTC — exactly the RenTec reality (real edges are rare/weak); the firewall correctly ADMITTED NOTHING. Median MFE was fine (+0.3–0.6%) but only 37–59% reached +0.5% before the −0.3% stop — vs the reclaim candidate's 85% — which is precisely why that one is distinctive. LESSON (harness hygiene): cost units — 5bp = 0.0005 fraction, NOT 0.05; a factor-100 cost bug made everything read ≈−5% until caught (the vsRAND control cancels it, which is why the null conclusion held regardless — always keep a control that cancels systematic harness errors).
    (c) **SHALLOW-SWEEP→RECLAIM reconfirmed BTC-only + ADMISSION CHECKLIST written.** n=93, median MFE +1.09%, reached +0.5% in 85% (OOS-stable train=test=85%), median MAE −1.42%. The +0.5%/−0.3% mechanical bracket is ≈breakeven-negative (−0.023%/tr) because the −0.3% stop sits INSIDE the −1.42% noise (only 12% never breach it). The edge is the EXCURSION, not the tight chase. references/ADMISSION-shallow-reclaim.md pre-registers the tradeable spec (structural/~1×ATR stop OUTSIDE the noise, partial +0.5% + runner to +1%, or dip-entry) and the CANDIDATE→ADMITTED gate: A7 costs-first (>0 after 5bp OOS, stress 25bp) · A5 regime-spanning (per-regime) · A4 proper scoring (log-loss/Brier/reliability, not hit-rate) · A6 beat the microstructure null (reclaim-confirmation must add over any-bounce-off-a-swept-level) · R5 blind audit (|ΔP|>20pp=CONTESTED) · A2 power (n=93 < hundreds; extend within-BTC-across-time, not across assets) · decorrelation before ensembling. Frontier for edge #2 (forward-only): reclaim × P2 liq-map/HLP — does an approaching liq-cluster explain WHICH reclaims run.


## Doctrine v3.15 delta — admission test: shallow-reclaim NOT admitted (trial T-007, 2026-08-15, DISCOVERY)

38. **ADMISSION TEST — shallow-sweep→reclaim is NOT ADMITTED; stays CANDIDATE (trial T-007; scripts/admission_test.py; BTC-only, brackets chosen on TRAIN, TEST reported once; A6 microstructure null + base-rate null + A5 regime split + A4 proper scoring; trial-count = 8 brackets × 2 TF).**
    - **1h = FAIL.** Train-chosen bracket (reclaim stop-2.0%) → TEST −0.034%/tr (negative after 5bp). Decisive: the reclaim does NOT beat the **A6 microstructure null** — "swept-no-reclaim" scored +0.151% vs the reclaim's lower net, so the reclaim adds **−0.105% vs the null**; and A4 proper scoring shows **no calibrated info** (signal logloss 0.444 ≈ base 0.443). CONSEQUENCE: on 1h the "reclaim" is just *a bounce off a swept low* — the confirmation is worthless. BENCHED on 1h.
    - **4h = MARGINAL first-pass PASS, via DIP-ENTRY@level → +1.0% target only.** TEST **+0.105%/tr at 5bp**, beats the A6 null (+0.049%) and base (+0.392%), and **ADDS calibrated info** (A4 logloss 0.685 < base 0.851; signal p=0.45 vs base 0.18). FOUR RED FLAGS keep it CANDIDATE, not ADMITTED: (i) **regime-concentrated** — UP −0.031 / DOWN +0.268, i.e. works only in downtrends (fails A5 "not one-regime"); (ii) **dies at 25bp** (net25 −0.084) → survives only at the real ~5bp, thin safety margin; (iii) **n=62** after the dip-fill filter (< hundreds, A2 power); (iv) **TRAIN-chosen** → needs a pre-registered BLIND run before any weight.
    - **CROSS-TF THREAD:** the **dip-entry** (wait for the −1.42% MAE heat, buy the retrace to the reclaimed level, ride to +1.0%) is the ONLY variant with life on BOTH TFs (1h TEST +0.130, 4h TEST +0.105) — consistent with the excursion thesis (the −1.42% median MAE is the ENTRY, not the stop; the −0.3% and reclaim-close chase are dead on both TFs). But eyeballing consistency across TFs = multiple comparison → SUGGESTIVE, not proven.
    - **VERDICT:** shallow-reclaim NOT ADMITTED; combiner still 0 admitted (equal-weight-of-nothing). The reclaim-close chase is dead; the **4h dip-entry@level → +1.0%** is the single spec worth freezing for a pre-registered, regime-balanced BLIND run with more N. Discipline held — the harness surfaced a marginal candidate and named its four weaknesses rather than declaring an edge. Next: freeze that one spec, blind-validate regime-balanced; and let the P2 collector accrue so reclaim × liq-cluster can be tested as the decorrelated edge #2.


## Doctrine v3.16 delta — NO-RULES discovery surfaces real predictive content; the fixed bracket was the blindfold (trial T-008, 2026-08-15; OLIVIER-INPUT HIT)

39. **DISCOVERY MUST NOT BE STOPPED/INVALIDATED BY TRADING RULES (OLIVIER-INPUT, binding) — and doing so surfaces genuine predictive content the bracket hid (scripts/discovery_excursion.py; BTC-only).** OLIVIER: a stop is exactly what invalidates a pattern that would have worked; costs are the trader's layer; discovery must measure raw predictive content, not a mechanical trade. Re-ran the whole battery in PURE-CONTENT space — NO stop, NO cost, NO bracket — measuring directional forward return d·(C[i+h]/C[i]−1) vs a matched random control + MFE/MAE + reach, OOS split, on 5m/15m/1h/4h. This RECONCILES the earlier "30 trials, 0 survivors" (#37): that was under trading rules; **content exists rule-free.** The random control is NOT a rule that can invalidate — it is the definition of "is there information."
    - **STANDOUT — vol-spike FADE:** fading the direction of a ~3× volume-spike bar predicts reversal, flagged CONTENT on **5m/15m/1h** (fwd-return edge vs random +0.07 / +0.22 / +0.20%), **OOS-positive on all three**; its mirror (CONT/follow) is symmetrically NEGATIVE. Cross-TF consistency ⇒ unlikely to be chance. A real weak mean-reversion edge the fixed bracket completely hid (the reversal excursion is there; a tight stop got hit first).
    - **shallow-sweep→reclaim (the live thesis):** CONTENT on **15m** (edge +0.119, OOS +0.24/+0.04) and **4h** (+0.180, OOS +0.54/+0.24), OOS-positive — but **NOT 1h** (fails; explains the earlier 1h bracket FAIL, #38). The reclaim is real on the *right* timeframes; 1h was the wrong lens.
    - **MR 4-consec fade:** CONTENT on 5m + 1h (fade on short TFs), reverses sign on 4h.
    - **PATTERNS ARE TIMEFRAME-SPECIFIC** — signs flip across TFs (e.g. large-range fades on 5m/1h, continues on 4h; overext continues on 1h). Corollary to #37a: don't pool timeframes any more than you pool assets; each TF is its own regime.
    - **CAVEATS (firewall still applies, one level up):** in-sample OOS-SPLIT only (needs a true pre-registered BLIND run); trial count 8×4 = 32 (single-TF flags include multiple-comparison noise — trust only CROSS-TF-consistent ones: vol-spike-fade, reclaim-15m/4h); CONTENT = predicts DIRECTION, not automatic profit — but at OLIVIER's ~0 execution cost, a +0.1–0.2%/event directional edge is harvestable (his layer, separate). These are the combiner's FIRST candidate weak edges: **vol-spike-fade** and **reclaim-15m/4h** are mechanically different (volume-climax reversal vs shallow-sweep reversal) → likely DECORRELATED → the ensemble's first two members, pending a decorrelation check (COMBINER §4) + blind validation. OLIVIER-INPUT: **HIT** — the no-rules reframing was correct and productive; it moved the desk from 0 candidates to 2.


## Doctrine v3.17 delta — thesis test: reversals (poke-the-other-way) + trendline REJECT-for-continuation (trial T-009, 2026-08-15; OLIVIER-INPUT HIT)

40. **OLIVIER THESIS TESTED & SUPPORTED (no stops · reversals off pokes · trendline rebreak/reject for continuation) — scripts/thesis_test.py, BTC-only, pure content (no stop/cost/bracket), both directions, vs random, OOS, 5m/15m/1h/4h. Two honest refinements:**
    - **REVERSAL ("BTC rarely makes a big move without first poking the other way") is REAL but LONG-BIASED.** poke-low→reclaim (LONG) has content on **15m** (edge +0.148, OOS +0.24/+0.04) and **4h** (+0.158, +0.54/+0.24); the SHORT mirror poke-high→reject does **NOT** (null/negative everywhere clean). Interpretation: BTC's structural up-drift → down-pokes get bought, up-pokes don't symmetrically reverse. **Buy the down-poke; don't reflexively short the up-poke.**
    - **CONTINUATION winner is the REJECT, not the rebreak.** resTL-**REJECT**→SHORT (price tags a descending-resistance line and closes back below → down continues) has **strong OOS-stable content on 1h** (edge +0.371, OOS +0.23/+0.16). The break+retest "rebreak" continuations are null-to-**ANTI-predictive** — descending-res breaks tend to FAIL (trap/deception theme, #072): "break+retest long" loses (−0.093), "reject short" wins. So **fade the line touch; don't chase the rebreak.** (The CONTENT flag catches signed content incl. inverse — a negative flag means the signal predicts the OPPOSITE, i.e. its inverse is the edge.)
    - **The desk now has ~3 candidate WEAK edges, all in OLIVIER's reversal/reject family:** (a) **vol-spike-FADE** (climax reversal, 5m/15m/1h, #39); (b) **poke-low→reclaim LONG** (sweep reversal, 15m/4h); (c) **resTL-reject SHORT** (line-rejection continuation, 1h). Mechanically different + different directions → likely DECORRELATED → the combiner's first candidate members (0 → 3 in one session, by removing the stop from discovery).
    - **CAVEATS (firewall, one level up):** in-sample OOS-SPLIT only (needs pre-registered BLIND / forward); trial count now ~56 cells across the two harnesses → multiple comparison is real, so trust only cross-TF/method-consistent flags and DOWN-WEIGHT single-TF & the noisy small-n 4h (random-control values there swing wildly, e.g. +0.89). CONTENT = predicts DIRECTION, not proven profit — but at ~0 cost + reversal execution (scale-in, no stop) it is harvestable. **NEXT:** freeze these 3 specs → pre-registered BLIND validation → pairwise DECORRELATION (COMBINER §4) → survivors are the ensemble's first members. OLIVIER-INPUT: **HIT.**


## Doctrine v3.18 delta — the leverage-washing-machine model, tested & confirmed (2026-08-15; OLIVIER-INPUT HIT)

41. **THE LEVERAGE-WASHING-MACHINE MODEL (OLIVIER, tested & largely CONFIRMED; scripts/market_structure.py; BTC-only). "BTC ranges until it trends, comes back for it after, and kills faraway leverage via funding while trending."** Three measurable claims, all supported with honest nuance — and together they EXPLAIN why the desk's edges are reversal-shaped:
    - **(1) Ranges / mean-reverts.** Variance ratio VR<1 at EVERY horizon and FALLING with horizon (1h VR2=0.99→VR48=0.93; 4h 0.98→0.90). BTC is mildly MEAN-REVERTING intraday→weekly, more so the longer the horizon. Ranging/reversion is the dominant regime; strong directional trends are the rarer / longer-horizon exception (no VR>1 in the tested window). This is WHY discovery found REVERSAL content and null momentum (#39/#40) — the market structure itself is reversion.
    - **(2) Comes back for it.** After a trend leg, median retracement over the next equal window = 20–37% (1h 3%-legs: up 37% / down 27% — up-legs retrace MORE, the up-bias again). Partial revisit confirmed (not a full round-trip); same story as the falling VR.
    - **(3) Funding bleeds the counter-trend crowd.** As trailing-trend strength rises Q1→Q5, trend-ALIGNED funding flips +1.8e-7 → −1.07e-6 and |funding| rises (8.6→9.6e-6/hr): during strong trends the OFFSIDE (counter-trend) leverage pays and is bled slowly by funding — the "faraway" leverage whose price-liq never gets hit. Magnitudes SMALL (~4%/yr scale) = a slow grind, consistent with "kills faraway leverage over time," not a fast liq.
    - **SYNTHESIS (the model unifies the desk):** a reversion machine ⇒ FADE setups (reversal off pokes, reject at lines) carry the edge and momentum/breakout mostly don't (matches #39/#40); "comes back for it" ⇒ fade trend-leg exhaustion toward the retrace; the funding-bleed is the TELL for trend maturity ⇒ the collector's positioning/funding (P2) is exactly where a *decorrelated* "trend-exhaustion reversal" edge should live (counter-trend crowd fully bled → snap-back). This is the candidate edge #4 and the reason the forward collector matters. NUANCES (honest): reversion is MILD (VR 0.90–0.99), retrace PARTIAL (~⅓), funding-bleed SLOW/small. Descriptive structure, in-sample, not a trade. OLIVIER-INPUT: **HIT** — coherent, data-supported, and it explains the *shape* of every edge found today.


## Doctrine v3.19 delta — ensemble/decorrelation: 4 candidates → 2 robust; don't ensemble null edges (trial T-010, 2026-08-15)

42. **THE COMBINER'S FIRST REAL EVALUATION — bootstrap-CI + walk-forward culls 2 of 4 candidates; decorrelation is real; equal-weighting nulls HURTS (scripts/edge_ensemble.py; BTC-only, no stop/cost; VCP-COMBINER-001).** Took the 4 candidate edges past the discovery train/test split to stricter robustness (bootstrap 90% CI + 4-fold walk-forward):
    - **ROBUST survivors (2):** **E2 resTL-REJECT short (1h)** — walk-forward 4/4 folds positive, mean +0.169%, CI90 [−0.036,+0.394] (clips 0 but fully sign-stable); **E4 poke-low→reclaim (15m native)** — mean +0.127%, CI90 **[+0.040,+0.218] EXCLUDES 0.**
    - **NOT-robust here (2, culled):** **E1 vol-spike-FADE (1h)** — CI spans 0, walk-forward unstable [−1,1,1,−1] (may still hold on 5m/15m where discovery was stronger — unproven, not dead); **E3 fade-strong-trend (1h)** — CI spans 0, unstable (the retracement is real per #41 but too partial/noisy for a mechanical directional edge). Bootstrap CI + walk-forward correctly caught discovery over-optimism — the firewall one level up.
    - **DECORRELATION is EXCELLENT:** pairwise daily-PnL corr avg **−0.12** (E2×E3 −0.50, E1×E2 −0.15, E1×E3 +0.29) → effective independent bets **N_eff = 3.0 of 3**. The edges are genuinely independent (even negatively correlated) — exactly what an ensemble wants.
    - **KEY LESSON (empirically vindicates COMBINER §2 admission gate):** equal-weighting all 4 HURT — ensemble daily-Sharpe (+0.04) < best-single (+0.10) — because 2 edges are individually null and averaging a real edge with nulls DILUTES it. **Weight ONLY admitted (robust) edges; never equal-weight raw discovery candidates.** This is the admission gate proven with data, not asserted.
    - **CONSEQUENCE:** the real ensemble is the 2 robust survivors **E2 (resTL-reject) + E4 (poke-reclaim)** — next: a pre-registered FORWARD (true-blind) run of both (collector accrues it) + measure E2×E4 decorrelation (different clocks), then weight ONLY the pair. Caveats: weak edges (daily-Sharpe ~0.1 — expected, RenTec-weak), content ≠ tradeable-PnL (Sharpe a rough proxy), in-sample-OOS not true blind. Nothing ADMITTED yet.


## Doctrine v3.20 delta — think like the MM/whale: PATH not direction; reversals harvest liquidity the move built (trial T-011, 2026-08-15; OLIVIER-INPUT HIT)

43. **THE MARKET ENGINEERS PATH, NOT DIRECTION — reversals are liquidity-grab footprints, strongest where liquidity was just built (OLIVIER lens; scripts/mm_regime.py; BTC-only).** Model (OLIVIER): the house MM (HLP, which literally performs liquidations) + whales look to FILL THE MOST volume, and LIQUIDATIONS PAY → price is pushed to where it can fill size + trigger liqs. They don't set overall DIRECTION (exogenous / informed flow) but they engineer the PATH — the sweeps, pokes, reversals — to get there; **SFPs / liquidity grabs are how whales fill SIZE at good prices** (poke below a swing low → trigger stops/liqs = forced sellers → whale absorbs the liquidity → price reverses up).
    - **Our edges ARE those footprints:** poke-low→reclaim (E4) = a whale filling long via a liquidity grab; vol-spike-FADE = climax absorption; resTL-reject = level defense. That is WHY every edge found is reversal-shaped and weak-directional — **they predict the PATH, not the direction.** Corollary: grade by excursion/reversal, never fixed-direction; direction is someone else's (macro) job.
    - **EMPIRICAL (mm_regime.py) — and it corrected the naive filter:** the reversal edges are STRONGER after a trailing directional move than in a dead range — E2 resTL-reject TREND +0.240% vs RANGE +0.097%; E4 poke-reclaim TREND +0.206% vs RANGE +0.049%. So "MM fades noise in the quiet range" is WRONG; the truth is **the move BUILDS the offside leverage/stops, and the SFP/reversal HARVESTS it.** No fresh move → less liquidity to grab → weaker edge. Ties #41 "comes back for it": the trend leg is the fuel, the reversal is the harvest. FILTER FOR "liquidity was just built," not "quiet range."
    - **THE FORWARD EDGE this points to:** condition the SFP/reclaim on a REAL liquidity cluster being grabbed — the collector's true liq-map (exact liqPx) + HLP inventory read directly where the house is exposed and where the fills/liqs sit. That is the whale-fill DETECTOR = the decorrelated positioning edge the collector is accruing from today. OLIVIER-INPUT: **HIT** — reframes the target (path, not direction) and the condition (liquidity-built, not quiet-range).


## Doctrine v3.21 delta — spot vs perp: no lead-lag, but perp-premium-fade is a positioning edge; profiling scoped forward (trial T-012, 2026-08-15; OLIVIER-INPUT)

44. **SPOT vs PERP (HL only, BTC; perp 'BTC' vs spot '@142' UBTC/USDC; scripts/spot_perp.py). Backtestable slice done; CVD + trader-profiling scoped FORWARD.** Over 4801×1h overlap:
    - **BASIS tight:** mean +0.2bp, sd 6.3bp, range −101/+19 — perp occasionally CRATERS below spot on flushes but rarely spikes above (down-flushes sharper; consistent with the washing-machine's downside pokes).
    - **LEAD-LAG null at 1h:** spot↔perp return cross-correlations are symmetric and ~0 (arbitrage keeps them coupled; any real lead-lag is sub-second, not tradeable at OLIVIER's TF). Honest null — no spot-leads-perp edge on the hourly.
    - **BASIS-DIVERGENCE = a positioning fade:** perp-PREMIUM decile → fwd 6h **−0.42% vs random +0.63%** (≈ −1.05% relative underperformance) = **fade the perp premium (short crowded perp longs relative to spot).** The DISCOUNT/long side is null (asymmetric — same up-bias theme as the price reversals). This is a POSITIONING signal, mechanically DIFFERENT from the price-pattern reversals ⇒ plausibly the decorrelated **candidate edge #5**; DISCOVERY/in-sample (one decile, no OOS yet) — owes the full gate.
    - **FORWARD-ONLY (scoped to the collector, NOT backtestable):** (i) CVD / aggressor flow — the historical trade tape is shallow (recentTrades ~10); orderflow.py collects it live; add to the collector. (ii) TRADER-PROFILING by address/size — userFillsByTime carries `closedPnl` per fill, so addresses can be ranked into winner/loser cohorts and the CONTRARIAN buy-high/sell-low losers isolated to FADE (their aggregate flow = a contrarian indicator). The collector's compounding address book is the substrate; this is the deepest use of HL per-address transparency ('the mine Renaissance never had') and the natural home of the decorrelated positioning edges. OLIVIER-INPUT: HIT — opens a whole positioning family (perp-premium fade now; CVD + loser-cohort fade forward).


## Doctrine v3.22 delta — CROSS-LENS: the signal lives at price-reversal × positioning-extreme (trial T-013, 2026-08-15; OLIVIER-INPUT HIT — the capstone)

45. **HUNT THE SIGNAL AT THE INTERSECTIONS ('like a bug' — isolate the exact conditions): the perp↔spot BASIS is the master conditioner that turns weak price-reversals into real signals (scripts/cross_lens.py; BTC 1h, no stop/cost; DISCOVERY/in-sample).** Conditioned each reversal edge on the other lenses (recent-move, trend-direction, perp-spot basis, funding). The finding is coherent across ALL three edges:
    - **E2 resTL-reject short:** ALL +0.181% → × perp-PREMIUM (longs crowded) **+0.606% (3.3×, CONFLUENCE)**; × perp-DISCOUNT +0.065% (killed, CONTRADICTION). Fade the resistance-reject when perp longs are crowded — not otherwise.
    - **E4 poke-reclaim long** (weak on 1h alone, −0.130%): × perp-DISCOUNT (shorts crowded) **+0.073% — FLIPS POSITIVE (CONFLUENCE)**; × perp-PREMIUM −0.249% (CONTRADICTION). Positioning RESCUES the 1h poke-reclaim.
    - **E1 vol-spike-fade** (~0 alone): × aligned perp-dislocation **+0.203% (CONFLUENCE).**
    - **INTERPRETATION (unifies the session):** the reversal HARVESTS offside leverage (#41/#43), so it fires reliably exactly when POSITIONING confirms the offside crowd is trapped — price says "reversal setup," the basis says "and the crowd is on the wrong side." Price alone = weak; **price × positioning = the signal.** This is the combiner as CONDITIONING (interaction), which beats averaging. Decorrelation matrix confirms the lenses are independent (E4×E5 −0.33, E2×E4 −0.24, mostly low/negative) — so the interaction is real information, not one lens counted twice.
    - **CAVEATS:** confluence cells have small n (19–57), several conditioners tested (multiple comparison), in-sample — owes bootstrap-CI on the cells + OOS + forward. BUT the CROSS-EDGE CONSISTENCY (positioning-confluence sharpens all three; the contradiction kills all three) is strong evidence it is real, not noise. **NEXT SPEC to freeze + blind-validate: "price-reversal × perp-spot-basis confluence"** — reject-short only at a perp premium, poke-long only at a perp discount, vol-fade only aligned. OLIVIER-INPUT: **HIT** — "hunt at the intersections" found the actual edge; the desk's thesis is now one concrete, testable, decorrelated signal family.


## Doctrine v3.23 delta — lead-lag confirms the basis LEADS; volume adds nothing; and the ELLIOTT-WAVE TRAP (the governing law of the whole program) (trial T-014, 2026-08-15; OLIVIER-INPUT HIT — the epistemics capstone)

46. **"THERE IS AN INFINITE NUMBER OF SIGNAL COMBINATIONS ACROSS BOTH VENUES (perp+spot), AND ALL SIGNALS LEAD TO AN ELLIOTT-WAVE SCENARIO" (OLIVIER — the governing epistemological law; it OUTRANKS every edge in this doctrine).** Two empirical results this trial, then the law they illustrate:
    - **LEAD-LAG — the basis LEADS the reversal (causality passes; #45 upgraded from "coincident?" to "leading").** The price-reversal × perp-PREMIUM confluence (E2) is STABLE across basis lags: lag 0h +0.606%, −3h +0.497%, −6h +0.728%, −12h +0.529% — the positioning extreme PRECEDES the price reversal; it is not a same-bar artifact. And price does NOT lead the basis (corr(prior return, current basis) = +0.000 / −0.056 / −0.109 ≈ 0). So the conditioner is USABLE (known before the reversal fires), not a tautology. This is the "does the signal lead price or price lead the signal" check OLIVIER demanded — and for the capstone signal, the SIGNAL (basis) leads.
    - **VOLUME adds nothing — LEVEL null, CHANGE null-ish; a live Elliott-trap specimen (scripts/vol_change.py).** Volume LEVEL (high/quiet/rising) did not sharpen E2/E4 (all ~edge-alone). Volume CHANGE (expansion/contraction/acceleration) + candle-CVD-proxy: the "confluence" cells are INCONSISTENT across edges (contraction helps the short +0.386 but expansion helps the long +0.120; CVD-'diverge' helps both while CVD-'confirm' HURTS E4 −0.253) and sit on THINNING n (15–48). No mechanism-consistent story survives across both edges — which is exactly what an over-conditioned search manufactures by chance. VERDICT: raw volume / its changes are NOT a confluence lens for these edges — drop it. (True aggressor CVD / per-address flow is a DIFFERENT object, forward-only via the collector, not this candle proxy.)
    - **THE LAW (why those two bullets matter more than any single cell):** infinite signal combinations across perp+spot = infinite degrees of freedom; with enough of them you can ALWAYS fit a flexible post-hoc narrative — Elliott wave is the archetype (relabel the count and it "explains" any path while predicting nothing out-of-sample). Our own washing-machine / MM-path model (range → impulse → "comes back for it" → continue; #41/#43) IS an Elliott-SHAPED path. The ONLY things that separate a model from an Elliott count — i.e. the only defenses against the infinite-combination trap — are: **(1) MECHANISM** — an economic prior (leverage liquidated, funding bleeds the offside, MM fills size via SFP, crowd trapped by positioning) specified BEFORE the fit, that constrains the search; a combo with no mechanism IS an Elliott count. **(2) FORWARD / BLIND FALSIFICATION** — the only honest judge; in-sample fit is near-worthless because the infinite space guarantees a good fit. **(3) TRIAL-COUNT AS DENOMINATOR** — every combination tested is a coin flip (~14 trials + dozens of conditioning cells this session) → discount single-cell "significance" hard, trust ONLY cross-edge / cross-TF / cross-lag CONSISTENCY. **(4) DECORRELATION / N_eff** — infinite combos are mostly the SAME bet relabeled; redundant "confirmations" are not confirmations (#42). **(5) A STOPPING RULE** — you cannot out-search an infinite space; freeze a small mechanism-backed set and STOP.
    - **CONSEQUENCE — the in-sample discovery program has reached its stopping point.** Exactly ONE finding carries a mechanism AND a passed causality check AND cross-edge consistency: **price-reversal × perp-spot-basis-extreme (basis leads).** That is what to FREEZE and pre-register for a forward/blind run (references/PREREG-reversal-x-basis.md) — NOT another combination. Every further in-sample lens from here (volume was the clean test case, and it failed) has falling odds of being real and rising odds of being an Elliott count. **STOP mining; go forward.** OLIVIER-INPUT: **HIT** — the sharpest guardrail of the whole build; it is now doctrine that the answer to "infinite combinations, all Elliott" is mechanism + forward + trial-count + decorrelation + a stopping rule, and that the desk STOPS here and lets time be the judge.


## Doctrine v3.24 delta — the holism resolution: SEE ALL DIMENSIONS AT ONCE (joint state); the relationship matrix is what makes it not-Elliott (2026-08-15; OLIVIER-INPUT HIT)

47. **"YOU ALWAYS HAVE TO SEE ALL DIMENSIONS AT THE SAME TIME, THEIR RELATIONSHIPS" (OLIVIER) — the corrective that COMPLETES #46. Reducing to one univariate pre-registered signal is NOT the whole answer to the infinite-combination trap; holding the JOINT STATE is (scripts/state_view.py).** Tension resolved: testing dimensions one pair at a time and cherry-picking = the Elliott trap (#46). Reading them ALL AT ONCE as a single state vector — WITH their relationship structure, a mechanism, and a forward test — is the DISCIPLINED form of the same holism, and it is exactly how the desk operates (macro-first, confluence/divergence). The signal is a REGION of the joint state, never a dimension in isolation.
    - **The state vector (BTC 1h, one screen):** D1 trend/impulse; D2 regime (efficiency ratio, trend vs range); D3 positioning (perp-spot basis, trailing pctile); D4 funding (+ trend-aligned bleed); D5 flow (volume-expansion + candle-CVD slope); D6 price-structure trigger (poke-reclaim / resTL-reject). Read together; the pre-registered price×basis region (#45 / PREREG-reversal-x-basis.md) is ONE configuration of this vector.
    - **THE RELATIONSHIP MATRIX IS THE ANTI-ELLIOTT DEVICE — it exposes which "dimensions" are the same bet.** Live co-movement (200d): **basis ↔ funding = +0.41** (perp-premium and positive funding are ~40% the SAME "longs crowded" read — do NOT count them as two independent confirmations); **cvd-proxy ↔ trend = +0.45** (the candle-CVD slope is ~45% just trend relabeled → not independent info → corroborates the volume-null #46; drop it). Everything else |r| < 0.22 → genuinely independent axes: trend, regime, positioning(basis), volume-expansion, price-structure. So of the many "signals," the independent AXES are FEW (the N_eff lesson #42, now at the dimension level). Seeing all dimensions at once + their relationships is precisely what stops infinite combinations from masquerading as infinite evidence.
    - **OPERATING RULE:** read the six rows JOINTLY every time (never one lens alone); use the relationship matrix to avoid double-counting correlated dimensions; the confluence read arms a pre-registered REGION only when INDEPENDENT axes agree (price-structure + positioning, with funding/regime as context, flow mostly redundant). state_view.py is the desk's on-demand "all dimensions at once" read; the collector accrues the forward tape that judges the armed regions. **Holism and the stopping rule are NOT in conflict: FREEZE the region to test forward (#46), but always READ the whole state (#47).** OLIVIER-INPUT: **HIT.**


## Doctrine v3.25 delta — answering "what's next": REPRO the current state (analog path), don't narrate it (trial T-015, 2026-08-15; OLIVIER-INPUT HIT)

48. **"THINK OF THE SIGNAL LIKE A BUG" APPLIED TO A LIVE FORECAST — to answer "BTC next 2 moves," REPRODUCE the current state and read the empirical forward path; never hand-label one (scripts/analog.py + scripts/scenarios.py). The disciplined replacement for an Elliott count (#46): ONE conditioning (today's fingerprint), no scan, no wave-labelling.**
    - **Method:** fingerprint NOW across the desk's dimensions — regime (efficiency ratio), volatility (ATR-compression), range-position — pull every historical 1h bar matching it, and measure the forward $K-leg path (which $K move comes FIRST; whether the 2nd $K CONTINUES or REVERSES). analog.py does the repro; scenarios.py maps it onto real structural levels with mechanism + explicit invalidation + a conviction guardrail that DOWNGRADES when positioning is neutral / the tape is coiled.
    - **LIVE READ 2026-08-15 14:00 UTC (BTC 63,015; gate CLEAR; oi_flow: BTC premium neutral −4.4bp = no crowd; catalyst = FOMC minutes + Jackson Hole next week):** state = deep coil (efficiency 0.22, range-pos 17%, ATR only 0.22× median = extreme compression). n=191 analogs → **LEG-1 direction 49% up / 51% down — a COIN FLIP** (median 3h to the first $300 move); **LEG-2 55% REVERSE / 45% continue** (58% reverse after a down-leg, 53% after an up-leg). So the first $300 is fast and directionally unpredictable in this state; the second $300 mildly favours rotating back (washing-machine #41), more so after a down-poke (long-bias #40). Modal path = poke → rotate; conviction LOW on leg-1 direction, MILD on the rotation; the real directional move waits on the catalyst.
    - **THE INTEGRITY POINT (the session's thesis made concrete):** the honest output here is "leg-1 direction is a coin flip — don't pay for it." An extreme coil has no directional edge, and SAYING SO is the anti-Elliott discipline in action — a wave count would have manufactured a confident direction from the same chart. The edge is not in the direction; it is in (a) the SPEED/size (compression → a fast ~$300 resolution) and (b) the mild leg-2 rotation — both measured, both weak, both honest. OLIVIER-INPUT: **HIT** — "do whatever it takes, think of a bug" → repro beats narration; the desk now answers "what's next" empirically and refuses to fake conviction.


## Doctrine v3.26 delta — Elliott made FALSIFIABLE (wave scenarios + signal/RoC adjudication) + a live multi-TF concession (trial T-016, 2026-08-15; OLIVIER-INPUT HIT)

49. **ELLIOTT, RECONCILED WITH THE FIREWALL (OLIVIER): use the swing structure ACROSS TIMEFRAMES to ENUMERATE the scenario space + the LEVELS (where a reversal / trendline-break can happen = Fib retrace zones off each completed leg), then let SIGNALS + their RATE-OF-CHANGE ADJUDICATE which scenario resolves, and BACKTEST which signals actually called it (scripts/wave_scenarios.py). Elliott stops being unfalsifiable the instant the competing scenarios are concrete levels and forward data adjudicates — this SATISFIES #46, it does not violate it.**
    - **Backtest (BTC, in-sample): at the 0.5 retrace of a completed leg, R (trend resumes) vs C (break/reversal) is ~52/48 (near coin flip); the DISCRIMINATORS are weak (|r| ≤ 0.11) but real and RATE-OF-CHANGE-led** — Δefficiency (d_eff) is the #1 discriminator on 1h and top-3 on 4h (efficiency ACCELERATING into the zone → it BREAKS); volume-expansion + CVD (buying) at the zone → it HOLDS (bounce). Some signs flip across TF (atr_compress) = honest, no universal tell. Validates "think in rate of change": a signal's VELOCITY discriminates better than its level.
    - **LIVE CONCESSION 2026-08-15 (OLIVIER right, my down-first call wrong on the immediate leg):** I called down-first off a 1h view + a THIN 46-address liq-map. OLIVIER read UP-first off the 5m (higher lows from 62,890, base/trendline retest held) + a fresh-liquidity magnet at 63,500 + Friday's impulse from 62,523. Data confirms his structure (Fri low 62,523, +$507 impulse, 5m higher lows). And the wave tool INDEPENDENTLY confirms the magnet: the 4h up-leg (62,237→65,475) puts its **0.618 retrace at 63,474 ≈ his 63,500** — the Fib level and the liquidity pool COINCIDE. Both 1h and 4h sit on the **0.786 make-or-break at ~63,000**; holding it (5m says it is) keeps the up-path alive to 63,474/63,500, then per "BTC's first impulse is often a fake" that grab likely reverses — UNLESS it reclaims/holds >63,474, which resumes the 4h wave toward 65,475.
    - **TWO CONCRETE FIXES this exposed:** (1) go MULTI-TF including 5m — a single-TF statistical lean misses live microstructure (the 5m higher-low); (2) the liq-map needs a WIDER addressbook — 46 addresses missed the 63,500 pool, so the collector must compound more addresses (recentTrades `users` + liq events) before its fuel-skew is trustworthy. OLIVIER-INPUT: **HIT** — the disagreement was correct and upgraded BOTH the method (Elliott-as-scenario-space + RoC adjudication) and the tooling (5m + wider liq-map).


## Doctrine v3.27 — THE READ promoted to the standing thinking process (canonical, 2026-08-15; OLIVIER)

50. **THE READ IS NOW THE DEFAULT PROCESS FOR EVERY MARKET READ — run end-to-end, unprompted (references/THINKING-PROCESS.md; surfaced at the top of this SKILL). OLIVIER: "updated the thinking process for everything… so next time you come with it without me prompting."** The exact sequence converged today, ordered: (0) macro gate — no level before CLEAR + named catalyst; (1) **WAVE STRUCTURE across 5m/1h/4h FIRST** — enumerate the Fib scenario-space + levels (reversal vs trendline-break); the frame that makes confluence visible, enumerating BOTH scenarios, never asserting one; (2) **POSITIONS not funding, in rate-of-change** — OI/ΔOI, liq-map magnet mapped onto step-1's levels, HLP inventory, whale net; funding is a price, secondary; positions clear before events; (3) **JOINT STATE** — all dimensions at once + relationship matrix; (4) **SIGNALS + RATE-OF-CHANGE adjudicate** R vs C; (5) **REPRO** (analog) for the base rate; (6) **COMMIT** a best call, honest probability, weight the low-prob/high-significance tail, state the make-or-break. Firewall throughout (#46 mechanism>fit, trial-count, #42 decorrelation, forward+stopping-rule; Elliott only as falsifiable scenarios). **"Was the key to run Elliott first?" — yes, but as the ENUMERATOR/frame, not the predictor:** it turns an infinite chart into a few falsifiable levels + a binary (hold vs break) and makes liquidity-on-Fib confluence detectable; positions + signals + base-rate do the picking. The method is the product; the level is the footnote. OLIVIER-INPUT: **HIT — promoted to standing doctrine.**


## Doctrine v3.28 delta — cross-asset: NO tradeable lead, but correlation/beta/BREADTH is the lens (trial T-017, 2026-08-15; OLIVIER)

51. **CROSS-ASSET (BTC/ETH/SOL/HYPE + xyz:SP500/xyz:XYZ100) — per-asset, NEVER pooled (#37a); the RELATIONSHIPS are the product (scripts/cross_asset.py). Honest result: NO tradeable LEAD, but correlation + beta + BREADTH ARE a real confluence/divergence lens.**
    - **NO LEAD (null, and expected):** cross-return lead-lag vs BTC is ~0 at 1h AND 4h (all |corr| ≤ 0.07; "who-leads" flickers are noise) — arbitrage keeps the complex synced; same lesson as spot↔perp (#44). Do NOT expect an alt or an equity index to lead BTC on a tradeable clock.
    - **WHAT IS REAL — the structure:** crypto majors are ONE risk complex (BTC–ETH 0.89, BTC–SOL 0.85); **HYPE is semi-independent** (0.59 — its own token dynamics); **equities are a SEPARATE cluster** (SPX–NDX 0.89) moderately linked to BTC (~0.50). Betas: alts amplify BTC ~1.2× (ETH 1.18 / SOL 1.22 / HYPE 1.27); BTC's beta to equities is LOW (SPX 0.20 / NDX 0.30 — BTC's own vol dominates, so an equity wobble is a small BTC input).
    - **THE USABLE LENS = BREADTH (confluence / divergence), not lead.** A BTC call GAINS conviction when the complex CONFIRMS (alts + equities aligned) and LOSES it on DIVERGENCE (BTC up but equities / alts not confirming = the #37a breadth warning). Feeds THE READ as a cross-asset confluence check at step 6, never as a leading signal. Live 2026-08-15: 4/5 confirm BTC's +0.21% 24h → ALIGNED (HYPE +1.95%, leading on beta). xyz indices are masked to active/trading bars (off-hours = stub). DISCOVERY / in-sample. OLIVIER-INPUT: cross-asset opened — and it correctly resolved to breadth, not lead.


## Doctrine v3.29 delta — first LIVE firing audit: two real gaps fixed (5m-blindness + ledger-compaction awareness) (2026-08-15; OLIVIER)

52. **FIRST LIVE ON-DEMAND FIRING (#079) AUDITED — it passed the hard parts (macro-gate VOID caught + resolved via #51, Fib-time, continuity/evolution, honest grade, clean append-only ledger write v3.2.14 → v3.2.15 with #077/#078 preserved) but exposed TWO real gaps, now fixed:**
    - **5m-BLINDNESS (the important one):** the firing called the up-path "near-dead / lean down 52%" while BTC was printing **5m HIGHER HIGHS above the make-or-break** (OLIVIER caught it live: "we were doing higher highs above 63"). Root cause: `wave_scenarios.py`'s CURRENT READ only printed 4h + 1h — it never surfaced the 5m micro-structure THE READ step 1 demands. FIX: wave_scenarios now prints the **5m micro (HH/HL sequence)** with an explicit RECONCILE rule — *do NOT call a path dead against the live 5m* (#49, same lesson as the 63.5k-magnet miss). Verified live: 5m = higher highs + higher lows, price holding > 63,013 → the up-path was ALIVE; the firing's down-lean was premature.
    - **LEDGER-COMPACTION AWARENESS:** the live ledger is compacted (lineage + #077-onward + archive pointer). #079 respected the note, but the D7 collector still carried an "if it looks truncated DO NOT WRITE" rule that could misread compaction as damage and refuse to write. FIX: D7 trigger rewritten **compaction-aware** (and BTC-only) — the short length / missing #001–#076 is intentional, append normally, never rebuild; abort only if the version stamp is absent or the write fails.
    - **3 firing-output polish rules:** reconcile the committed lean with the analog base rate (if overriding a 52/48, say *why*); always print the cross-asset **breadth tally**; never cite prediction-market pages as sources. OLIVIER-INPUT: the live-fire audit proved the process works AND self-corrected two genuine gaps on its first real run.


## Doctrine v3.30 delta — THE AUDIT: full-stack peer review; the desk is a DISCIPLINE framework, the alpha thesis is FROZEN (2026-08-15; OLIVIER commissioned)

53. **FULL-STACK ADVERSARIAL PEER REVIEW (code + statistics + process-aware method review). Verdict: this is a genuine DISCIPLINE / RISK-CONTROL framework, NOT a demonstrated alpha engine. The reversal-excursion thesis is FROZEN, not carried as a live belief.**
    - **KEEP (real value at zero alpha):** the macro gate (Step 0, the dated fix for the 2026-07-26 miss); coin-flip honesty (#48); N_eff/decorrelation (#42); weight-only-admitted; read⊥holdability; the read-only constitution. Run the desk as bias-control + level/timing + honest scorekeeping. That IS the product.
    - **DEMOTE #39–#52 from "content/robust/confirmed" to "UNVALIDATED HYPOTHESIS, likely noise":** the "OOS" was a sign-stability check auto-passed by drift (a signal AND its mirror both flagged CONTENT); the 0.03% bar ≈ 0.2σ → 16/32 cells "passed" incl. losers; MFE / "85% reach +0.5%" measures BTC volatility not edge (and discovery_excursion computes the control MFE/MAE then never prints it — the refutation was hidden); the one CI-excludes-0 edge (E4) is best-of-32, IID-bootstrapped on ~50%-overlapping events, in-sample; cross_lens SCANS conditioners and keeps separators, and basis↔funding=+0.41 makes the "confluence" collinear with what the edges harvest = near-tautology. At ZERO cost + excursion frame it STILL fails: |MAE|1.42% ≥ MFE 1.09%, 88% breach −0.3%, no-stop ⇒ non-positive excursion expectancy; the reclaim FAILS its own microstructure null (−0.105% vs swept-no-reclaim; #38 BENCHED-on-1h).
    - **THE MISSING FIREWALL LEVEL (#46, one level up — the deepest finding):** the stopping rule stops mining WITHIN a signal but nothing retires the THESIS. reclaim → dip-entry → reclaim×liqmap → reclaim×basis are all "reversals harvest offside leverage"; no finite sequence of failed specs can kill it, so the infinite-combination trap reappears at the PROGRAM level, uncovered. **NEW BINDING RULE: the reversal-excursion thesis is FROZEN. It gets exactly ONE correctly-specified forward test — graded on EXCURSION with a FROZEN EXIT model (not the fixed-direction return the sealed PREREG wrongly grades), vs the swept-no-reclaim null, at pre-committed power. Fail ⇒ the thesis is RETIRED: no new conditioner/timeframe/variant. Until it concludes, NO edge is claimed and the discovery scripts' PASS/CONTENT/"paying"/"robust" prints are NOT trustworthy (broken methodology per audit).**
    - **CODE BUGS fixed (live pipeline):** oi_flow OI-change was on notional (a price move fabricated "flow") → units; state_view "ARMED" read setup[n-1] (always 0, dead) → last closed bar; scenarios `[:0]` killed nearest-resistance → fixed; entry/check silently used price 0 on API failure → fail loud; edge_ensemble printed "decorrelation is paying" unconditionally → made conditional. (discovery_excursion's hidden control-MFE and the PREREG-grades-the-wrong-object are left as-is — the discovery layer is frozen pending a correct rebuild, not patched piecemeal.)
    - **NET:** worth running as a discipline; the alpha is undemonstrated and was structurally at risk of being unfalsifiable. STOP building variants; use the framework for risk-control; let ONE correct excursion-graded forward test (with a program-level kill-switch) be the only thing that can ever promote or retire the thesis. OLIVIER-INPUT: commissioned the review — and its value is exactly this reckoning.


## Doctrine v3.31 delta — THE DISCOVERY LOOP: self-improvement without self-overfitting; the program-level firewall #53 asked for (2026-08-15; OLIVIER — "make instances and other agents think like you")

54. **THE DISCOVERY LOOP — how one agent's learning becomes every agent's, safely.** #53's deepest finding was that nothing retires the THESIS, so the infinite-combination trap could reappear at the program level. This installs the missing firewall as a *governed* loop — and it is the answer to "make all instances think alike": lessons propagate through the shared skill, never by any agent rewriting itself.
    - **Three gates.** CAPTURE — candidate lessons are logged as NEW `lesson-YYYYMMDD-HHMM.json` files in the Drive folder `12xPcwVMMXfk3mqCxGSN-hBBeLKI4NNoG` (create-new-file / never-modify, like `call-*.json`; the seed `lessons.json` is the registry + candidate schema, merged in at the retro). PROMOTE — a candidate becomes doctrine ONLY after it holds up FORWARD across the bar (default **5 supporting calls**), auto-checked by `discovery_loop.py`; never because one call "taught" us something. RETIRE — promoted doctrine is demoted when its forward guard trips (the arm #53 said was missing).
    - **Runs at the Sunday retro:** `calibration.py` (grade the committed calls) → `discovery_loop.py` (propose promotions/retirements from the resolved calls + lessons.json). It **PROPOSES only — never auto-edits the skill.** Only OLIVIER SAVING the skill propagates a change to every agent. That human save-step is the safety catch, and the reason self-improvement here cannot run away.
    - **Mission one is untouched.** The loop tunes the METHOD's priors, never the deliverable: the user-facing output stays *the 2 next most probable moves*; read-only; BTC-only (#37a). Precision improves without compromising the mission.
    - **SCOPE GUARD — governs everything EXCEPT the frozen thesis.** The reversal-excursion thesis stays frozen under its own one-shot kill-switch (#53). The loop may promote METHOD / STANCE / bias-control lessons; it may NOT resurrect, re-condition, or variant the frozen alpha thesis — that has exactly one correct forward test, not a discovery-loop promotion. So no rule (including any future thesis) can become unfalsifiable again.
    - Seeded with **candidate L1**: *in discovery the invalidation is a SCORING line, not a stop — commit it BELOW the liquidity pool.* Evidence already on file: the collector liq-map (tick-20260815-1818) showed a BTC long-liq cluster ~62,430 sitting BELOW call #1's dn=62,600 — the wrong-sided break that motivated the lesson. On trial via the swept-then-right rate (`calibration.py` SWEEP DIAGNOSTIC); promotes at ≥40% over ≥5 wrong calls.
    - **CAPTURE DUTY — every agent looks for improvement signals (OLIVIER 2026-08-15).** The GOAL every firing serves: make the committed calls better — sharper reads, better-calibrated probabilities, tighter discipline — on the way to proving or honestly killing the edge. So on EVERY firing, as a closing step (THE READ step 8), ask: *did this run reveal a testable improvement to the METHOD?* If yes, append ONE candidate as a NEW file `lesson-YYYYMMDD-HHMM.json` to the Drive folder. A candidate is ADMISSIBLE only if it is (1) FALSIFIABLE — names its `metric` + forward test + promotion `bar`; (2) OBSERVATION-BACKED — tied to a specific resolved call or miss *this run*, not a vibe; (3) NOT A DUPLICATE of an existing lesson/doctrine; (4) METHOD / STANCE / bias-control SCOPE ONLY — it may NEVER re-open, re-condition, or variant the frozen alpha thesis (#53 scope guard). No forward test ⇒ not a candidate. **The default is an honest null: most firings add nothing, and that is correct** — a flood of vibes IS the overfitting trap, and capture is only safe because candidates are INERT until they survive the bar AND Olivier saves the skill. Distributed capture, centralised weekly governance.

55. **THE LIQUIDITY LENS — the reading stance to inherit (the "think like me" content).** A STANCE / bias-control tool (same family as the macro gate and coin-flip honesty that #53 says to KEEP), adopted now — NOT an edge claim; the frozen thesis stays frozen.
    - **Price is liquidity-seeking.** It moves toward the pools (stops / liq-clusters / round numbers), not away from them; the "magnet" is a magnet BECAUSE liquidity rests there. Every armed level names its pool — from wave pivots + the collector liq-map (`longLiqClusters`/`shortLiqClusters`, fuel-skew) + round numbers.
    - **The invalidation is a scoring line, not a stop.** In discovery there are no stops (cost-free, stop-free by doctrine), so commit the break-line BELOW the pool. A hunt that wicks the pool and reverses to target then scores as the correct call it was. (Operationalised as candidate L1.)
    - **Anticipate the hunt; don't hallucinate the hand.** We read snapshots (OI, funding, premium, HLP, liq-map), not resting or spoofed book size. The one tell that can't be faked is sustained ACCEPTANCE — weight the hold over the touch. A volume pop, an OI build, a first reclaim can all be manufactured, so confluence must span things hard to fake at once.
    - **The market maker is observable here.** HLP inventory (collector `hlp` block) is the closest thing to the house's book — flat much of the time, but when it leans, read it before committing.


## Doctrine v3.32 delta — the incentive structure: reward the objective, not activity (2026-08-15; OLIVIER)

56. **INCENTIVE STRUCTURE — the ONLY thing ever rewarded is THE OBJECTIVE: get the next 2 moves right, as precisely as possible, sharper as we get closer.** (OLIVIER, 2026-08-15.) Everything the loop does serves that terminal metric and nothing else.
    - **The objective, stated.** Not "log improvements," not "be active" — the 2 next moves, correct and PRECISE, with precision TIGHTENING as the move nears (the continuity mandate, THE READ step 7: each firing's call is sharper than the last as time/price approach). Measured today by calibration/Brier on the committed p_up + the swept-rate; to be sharpened toward true level/timing precision as the sample grows (candidate L2).
    - **Selection, not motivation (anti-Goodhart).** Agents are stateless across firings, so there is no agent-level reward and there must not be: reward "improvements found" and a stateless agent optimises for LOGGING candidates (productivity theatre), not for better moves — Goodhart, the overfitting trap wearing a comp plan. The incentive is evolutionary: forward validation PROMOTES what works (it wins by becoming doctrine every agent inherits) and RETIRES what doesn't. Winners propagate; no wanting required.
    - **Credit is outcome-based.** A lesson earns credit only if it was PROMOTED and then the terminal metric improved vs the lesson's promotion-baseline — never for being logged, never even for promotion if the moves didn't get more precise. On promotion, stamp the current calibration (Brier, swept-rate) as the lesson's baseline; credit = the improvement measured ≥N calls later. Instrument now, credit later.
    - **Asymmetry that kills spam.** An honest null (adding nothing) is FREE and correct; a bad candidate costs MORE than silence — it spends the bar's attention and risks a bad promotion. So more-candidates is NOT better; a source that logs junk earns a WORSE average, not a fuller one.
    - **The scoreboard is for the human, not the agent.** `discovery_loop.py` prints a per-source contribution readout for OLIVIER's governance — which firings / inputs produce lessons that actually pan out (the same "score by source" discipline the desk already applies to CALLS, extended to LESSONS). It is NEVER fed back to agents as a target; statelessness is the safety here — an agent cannot chase a score it cannot remember.
    - **The real incentive-holder is Olivier.** The desk improves because he grades it and gates promotions with his SAVE. Keep the single rewarded thing = the 2-moves objective and incentives stay pointed at truth; add any intermediate reward and they drift.


## Doctrine v3.33 delta — healthy competition between co-desks (Claude vs Grok) (2026-08-16; OLIVIER)

57. **CO-DESK COMPETITION — two desks (Claude + Grok, on a shared Drive ledger) compete on CALIBRATION only, never on volume / confidence / being different. Extends #56 to two sources; the prize is earned trust-by-regime, not a gameable reward.**
    - **Same metric as #56.** The contest is forward Brier / calibration on committed calls (`by:Claude` vs `by:Grok`), graded by the shared calibration over the same `call-*.json` store. Better calibration wins. Nothing else scores — not call count, not confidence, not disagreement. Produced by **`leaderboard.py`** (per-desk Brier + skill, REGIME-conditioned — trend/range, high/low-vol, weekend/weekday — with echo-discount + CONTESTED detection); run at the Sunday retro after `calibration.py` and `discovery_loop.py`.
    - **Commit BLIND (independence is the asset).** Each desk commits its 2-move call WITHOUT reading the other's OPEN call for that setup — only the shared PRIOR resolved calls + its own lineage. If they anchor to each other, the decorrelation that justifies running two desks collapses into one echoed view. Near-identical calls (same up/dn/p_up) are DISCOUNTED as non-independent — an echo is not a second vote.
    - **Self-sufficient, never dependent (+ reconcile if available).** Each desk ALWAYS completes a full standalone read from data + its own lineage — the co-desk being absent, slow, or wrong never blocks it; neither depends on the other to produce its own call, in either direction. The SCORED call is the independent, blind-committed one. THEN, if the co-desk's work is available, reconcile: take its new FACTS into consideration (a catalyst, a level, a datum missed) and update transparently — but never borrow its direction/probability (herding ≠ consideration); same-facts disagreement stays CONTESTED, not copied. Absent the co-desk, the call stands complete. This keeps the system robust (either desk alone is a whole desk) and decorrelated (the scored votes are independent).
    - **Proper scoring is the anti-bravado.** Brier / log-loss punish overconfidence automatically (0.90-wrong ≫ 0.60-wrong in cost), so no desk can win by being bold — only by being calibrated. Built-in defence against a confidence arms race.
    - **Abstention is free.** A desk may log "no call" on a coin-flip / no-edge setup: no penalty, no credit for the round it sat out. A sniper beats a machine gun. Abstention rate is a quality signal, not a demerit.
    - **Complementarity, not a single champion.** The leaderboard is REGIME-CONDITIONED (trend vs range, high-vol vs low-vol, weekend, catalyst). The output is "which desk to trust WHEN" — Grok's edge is the social / real-time-X regime, Claude's is structure / positioning. The system's value is coverage, not a winner.
    - **Divergence = a CONTESTED flag for OLIVIER, worth nothing to the desks.** When the two calls materially disagree (opposite direction, or p_up gap ≥ ~0.15), flag CONTESTED — the highest-information moments; track how they resolve (does one desk own the disagreements, in which regime?). Neither desk earns points for disagreeing.
    - **Human-gated, no self-reward (the #56 firewall holds).** The leaderboard is OLIVIER's governance readout — it sets his weighting and feeds the loop (the winner's DISTINCTIVE lessons become candidate doctrine for both, via `doctrine.json`). It is never fed back to a desk as a target; statelessness is the safeguard. No "winner" is declared until n ≥ ~20–30 resolved per regime — until then, accumulating.


## Doctrine v3.34 delta — loss post-mortems (2026-08-16; OLIVIER)

58. **LOSS POST-MORTEM — when a call resolves WRONG, diagnose why (both desks; a loss is the richest lesson source, if it isn't rationalised).**
    - **Variance vs error, FIRST.** An honest 58% call that lost is the 42% — that is variance, not a mistake. Do NOT manufacture a cause; fitting a story to every loss is hindsight bias = overfitting. Dig only when there is a genuine, identifiable process failure. Calling variance "variance" is the discipline, not a dodge.
    - **Attribute to ONE category** when it IS a process error: (a) INVALIDATION placement — `dn` above the pool, swept-then-right (the SWEEP DIAGNOSTIC auto-flags this, L1); (b) MISSED / under-weighted CATALYST (macro-gate); (c) POSITIONING misread (funding / OI / liq / HLP); (d) FAKEABLE SIGNAL trusted (a touch without acceptance, thin volume); (e) REGIME misclassification; (f) WAVE / LEVEL error.
    - **Feeds the loop.** A real, testable, plausibly-recurring cause → a candidate `lesson-*.json`; a one-off / variance → one line, no lesson. Aggregated at the retro by the `by` field, per-desk loss-cause clusters show WHERE each desk systematically fails — the sharpest input to the leaderboard's "trust who, when" (#57) and to the swept-then-right rate (calibration).
    - Read-only analysis; human-gated like every other lesson. The post-mortem hunts for OUR error honestly — and equally refuses to invent one.


## Doctrine v3.35 delta — model-mix cost audit; distinct-capability additions (game-theory red-team, ledger-coherence, call evolution) — never more voters (2026-08-17; OLIVIER)

59. **MODEL-MIX AUDIT (2026-08-17): each model earns its place by DISTINCT CAPABILITY, never by adding another vote on the same question — #8's ban on multi-agent-debate-as-default stays binding.** Reviewed the full automation stack's model assignments against cost and fit:
    - **Routing by task, not by default:** `hlops-collector` (72 runs/day, pure script execution + row-count report — zero judgment) and the orchestration layer of `hlops-contested-flag` (48 runs/day, freshness-check + spawn + compare glue-code) moved from Sonnet-5 ($3/$15) to **Haiku 4.5** ($1/$5) — ~65% cheaper on the two highest-frequency jobs, zero loss of analytical quality since neither job does judgment work. Sonnet-5 stays on the main interactive session and the weekly Sunday retro (real reasoning, low frequency — cost delta is trivial there).
    - **Two genuinely NEW capabilities added, each closing a real gap — not duplicate forecasts:**
      (a) **GAME-THEORY RED-TEAM (GPT-5.1, `scripts/redteam_packet.py`).** Given the ACTUAL call (not blind, unlike the Grok audit — game-theory reasoning needs the thesis to argue against it), answers five fixed questions: who is positioned on the other side, what forces them out, the explicit pain trade, the market's best incentive-structure reason to prove the call wrong, and whether a forced flow dominates regardless of belief. This operationalizes the desk's own "Game layer" section (crowding taxonomy, pain trades, forced flows) as an adversarial second-mind check instead of the same model reasoning about it inline — a distinct lens, not a second p_up.
      (b) **LEDGER-COHERENCE AUDIT (Gemini 3 Pro, 1M-token context, `scripts/coherence_packet.py`).** Ingests the FULL doctrine (this file) + full ledger history + lessons.json + doctrine.json state and checks a new call against all of it: does it contradict a binding numbered rule (e.g. #22 protective-flip ban, #2 two-scenarios-max, #25b death-price guard)? Does it repeat a pattern already tested and killed (e.g. #24's rejected pain-radii clustering, #8's rejected DSR gate)? Does it ignore a logged lesson? Nobody previously re-read the entire ledger before grading a call — this is a memory/consistency check, explicitly NOT a forecast (the packet instructs the model not to offer its own p_up).
      Both wired into `hlops-contested-flag` alongside the existing Grok-4.6 blind audit — three distinct checks per fresh call (blind statistical audit / adversarial game-theory / doctrinal memory), pinging Olivier only on an actual finding from any of the three, silent otherwise. **REJECTED:** Claude Fable 5 ($10/$50/M, "Mythos-class" general knowledge-work model) — no distinguishing capability for this stack over the existing tier, would be a fourth expensive vote = consensus theater by another name.
    - **CALL EVOLUTION TRACKING (`scripts/call_evolve.py`, cron `hlops-call-evolve`, every 15min) — operationalizes #7 (continuity: assess how scenarios evolved) and #30 (an EW count's invalidation price IS the update rule) as a PERSISTED, append-only log instead of a one-off read.** For every OPEN call in `calls.json`, mechanically tracks: elapsed time vs. horizon, price's position within the call's own up/dn range (never a new level pick), and the live `pulse.py` flow verdict at the nearest timeframe. Classifies `conviction_delta` as STRENGTHENED / WEAKENED / UNCHANGED / RESOLVED / EXPIRED / **CONTESTED_INTERNAL** (the new, most important state: mechanical distance says the call is winning while live flow is FADING/DIVERGING — the fake-move signature, #4 pulse.py's own verdict — surfaced explicitly rather than let a closing distance alone read as rising conviction). **Never overwrites the original committed `p_up`/`up`/`dn`** — calibration.py still grades the frozen original commit; this is a diagnostic overlay, not a re-forecast. First live run caught exactly this: both open calls (2026-08-17) sat 84–97% of the way to their up-targets by distance while 1h flow read FADING/DIVERGING — flagged CONTESTED_INTERNAL rather than reported as growing confidence.
    - **Cost-unconstrained mandate (2026-08-17, standing) stays governed by capability-fit, not blanket spend.** Olivier's "use as many models as needed, cost is not the constraint" (carried from the CO-CALL session) does not mean maximize model count — it means do not let cost block a model that earns its place. #8's anti-consensus-theater rule is the actual gate on HOW MANY, not budget.

## Amendment — "2 next most probable moves" is a PATH, not a FORK (2026-08-17, Olivier correction)

THE READ step 6 says: "Commit the 2 next most probable moves." This has been getting delivered as
two competing alternatives for the SAME instant (a fork: "either it fades down, or it holds and
goes up"). That is wrong. Olivier's correction, verbatim in spirit: "the next 2 moves means for
example 'goes to X and reject toward Y', not [two] alternate[s]. Then those 2 scenarios can have
alternates."

**Correct structure: a SEQUENTIAL PATH.**
- **Move 1** = where price goes FIRST (the nearer-term leg).
- **Move 2** = what happens AFTER Move 1 plays out (conditional on Move 1 resolving) — the next leg,
  not a parallel possibility for right now.
- Example: "Move 1: pushes into 63,860 resistance. Move 2: rejects there, toward 62,600." Move 2 is
  downstream of Move 1, not a competing bet against it.

**Each move in that path may still carry its own primary/alternate sub-case** — e.g. Move 1's
primary is "pushes into 63,860 and rejects" with an alternate "stalls earlier at 63,400 and rejects
from there"; Move 2 can likewise branch depending on which Move-1 sub-case actually fired. This is
where probability and alternates belong — WITHIN each sequential leg, not as two competing readings
of the current instant.

**Format going forward, every BTC (and other coin) read:**
```
Move 1 (near-term, prob%): [level/zone] → [what happens there: rejects/breaks/holds]
   invalidation: [price]
   (alt, if warranted): [alternate sub-case for this same leg]
Move 2 (conditional on Move 1, prob%): [level/zone] → [what happens there]
   invalidation: [price]
   (alt, if warranted): [alternate sub-case for this same leg]
Tripwire: [the one or two prices that actually decide which path is live]
```

**Why this matters mechanically:** a fork framing ("Move 1: down. Move 2 (alternate): up.") hides
the fact that these are usually NOT symmetric probability bets on the same instant — real market
structure moves in sequence (sweep → reclaim → continuation, or break → retest → next leg). Framing
the deliverable as sequential forces the read to state the MECHANISM connecting the two legs (what
has to happen at Move 1 for Move 2 to even become live), which is more honest and more falsifiable
than two disconnected alternatives.

**Interaction with SCORE tagging (THE READ step 6's ledger tag):** the silent SCORE tag still grades
a single up/dn/p_up pair per horizon — that discipline is unchanged. This amendment is about how the
human-facing narrative is STRUCTURED (sequential path with sub-alternates), not about adding more
SCORE tags. If Move 1 and Move 2 sit on genuinely different horizons, tag each with its own
horizon/call-family in the ledger per doctrine #085 (horizon-scope discipline) so a near-term Move 1
and a downstream Move 2 don't read as contradicting some other open call at a different horizon.

**Self-check addition:** before sending a "next 2 moves" read, ask — is Move 2 something that can
only happen AFTER Move 1 resolves (sequential, correct), or is it something that could happen instead
of Move 1 right now (a fork, wrong structure)? If it's the latter, restructure before sending.

## Amendment — "ON THE LINE" DISCIPLINE: mandatory exhaustion-vs-continuation check near any live level (2026-08-17, Olivier)

**Trigger condition:** price sits within ~0.3-0.5% of ANY of the following for a live/OPEN call:
- the tripwire level
- a named Move 1 / Move 2 target or shelf (e.g. the 62,499-62,730 confluence zone)
- the stated invalidation price

When any of these is true, this is "on the line" — the moment that actually decides the read, not
just another status update.

**Mandatory action when on the line:** before restating the standing call or answering a status
question, run the live discriminator check:
```bash
python3 scripts/pulse.py <COIN>
python3 scripts/oi_flow.py --coins <COIN>
```
and explicitly classify the moment as one of:
- **EXHAUSTION** (favors reversal / the level holds): volume fading or decelerating on the timeframe(s)
  pushing into the level, CVD diverging from price, no fresh positioning crowd (OI flat/falling,
  funding/premium inside fair-value band).
- **CONTINUATION / GENUINE PUSH** (favors the level breaking): volume expanding AND accelerating,
  CVD moving WITH price, and/or OI building in the direction of the push (a real crowd forming, not
  just price drifting).
- **AMBIGUOUS** (say so plainly, do not force a verdict): signals disagree across timeframes or data
  is too thin to call — state this rather than picking a side to sound decisive.

**Why this is separate from the ordinary pulse call:** THE READ step 4 already uses pulse.py to
adjudicate R-vs-C when BUILDING a fresh call. This amendment is about RE-RUNNING that same
discriminator specifically at the moment an EXISTING call's own level is actually being approached —
so the check happens at the highest-information instant, not just once at commit time and then
never again until resolution.

**Output requirement:** when reporting on a call that is on the line, lead with the
EXHAUSTION/CONTINUATION/AMBIGUOUS verdict and the specific evidence (vol %, accel, CVD slope, OI/funding
state) — not just a restatement of the price level and probability. This is what makes "is X becoming
a real move or a fake" answerable in the moment, not only after the fact via calibration.py.

**Interaction with existing automation:** `hlops-call-evolve` (15min cron) already tracks distance-to-target
and flags CONTESTED_INTERNAL when mechanical distance and pulse.py flow disagree. This amendment makes
the SAME discriminator discipline mandatory in live chat/manual reads too, not just the automated
tracker — so a human asking "is it exhaustion or the opposite" always gets the mechanical check, not
a narrative guess.
