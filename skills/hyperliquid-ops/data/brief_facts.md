# BRIEF FACTS — shared venue-risk context (every originator reads BEFORE producing a call)

This file is the objective, non-directional fact sheet injected into EVERY originator's brief
(DeepSeek, Qwen, Grok) at the start of a round-robin firing. It is written by Charly (the
reconciler), not re-derived by the models.

**Read this first. It is CONTEXT, not a conclusion — it must not bias your direction.**
It exists so you calibrate correctly against the venue's real mechanics. Where a finding has
a *directional* implication, that is Charly's job (the reconcile layer), NOT yours — your job is
to produce your own independent read WITH these facts known.

**Root principle — immutability is DISCOVERY, not a freeze on truth (Olivier / VCP):** the desk
ledger is append-only and never erased, only AMENDED. What is true today may not be true tomorrow;
what happened still shapes the future, and that is discovery. When a prior read turns out wrong, we
amend it — we never delete it, because the *visible* contradiction between the old belief and the new
truth is the entire learning engine (MISS→LESSON→RULE only works if the MISS stays legible). No
ledger, no progress. Your job is NOT to reconcile with a past read — it is to give a clean,
independent read of TODAY's facts. Divergence from the past is information, not a conflict to smooth.

---

## 1. Venue mechanics (facts about HOW the market works, not WHAT will happen)

- **Hyperliquid perps**: BTC / ETH / SOL / HYPE are hard-stop venues. SP500 / Brent / Gold are
  **oracle-priced synthetic ("xyz") markets** whose underlying trades only during US hours.

- **R is FICTIONAL on xyz oracle markets during closed-underlying hours** (finding #1).
  The risk envelope (0.33R sizing, 80%-of-liquidation stop, 3-stops/5-days breaker) assumes a hard
  engine stop that works on BTC/ETH/SOL/HYPE — it BREAKS when SP500/Brent/Gold underlying is dark
  (nightly + weekends). Friday 22:00 CET card → weekend headline → Sunday re-open re-marks 3–4% →
  the stop fires into a ~$465M-OI thin book = 3–6× planned R on a call priced as "conservative."
  The breaker counts STOPS, not realized R.

- **Stops placed "beyond liquidity magnets"** (finding #4): the price paths that reach them are
  disproportionately CASCADE paths, so conditional-on-stop slippage runs well above average.
  A `1.33R` plan can realize `3R+` in a single wick. (This is a fact about stop placement physics,
  independent of direction.)

- **Narrative-vector caps are semantic, not statistical** (finding #3): "AI infra bid" / "ETF flows"
  / "macro liquidity easing" read as three distinct vectors but collapse to ONE correlated position
  (long crypto beta) in a liquidation cascade.

## 2. Base rates — read from disk, never from memory

- **`data/state.json`** = single source of truth for the LIVE call, entries, and base rates
  (`{rate, n, source}`). QUOTE every base rate from this file with its n/source. Do NOT recall
  rates from memory. (Provenance gate: any empirical rate without `{rate, n, source}` is rejected.)
- **`data/backtest_rates.json`** = the walk-forward backtester rates. Cap backtest reference to
  ONE line and treat it as in-sample, walk-forward-unvalidated — NEVER let a backtest number drive
  direction by itself.

## 3. Macro gate + cross-asset — already gathered, RE-DERIVE don't inherit

- **`data/macro_gate_resolved.md`** = the pre-resolved macro NAMED STORY (bond slump, Fed minutes,
  distrust window). READ THIS FILE for the story; do NOT fetch live email/news (trips the
  external-content security guard and zeroes the turn).
- **`data/cross_asset_snapshot.md`** = the RAW 24h breadth + lead-lag + correlation numbers.
  You must RE-DERIVE breadth/divergence from these raw numbers YOURSELF — do NOT inherit the
  reconciler's "risk-off short" label. The raw tape (BTC+SOL up, ETH/SPX/NDX down) can pull the
  OPPOSITE direction from the macro story; your job is to reconcile them independently, not to
  rubber-stamp a conclusion.

## 4. Live entry levels (fact, current window — update per state.json)

- MOVE 2 FLUSH entry = 15m close BELOW 63,930 (below prior low 63,938 + 64,000 magnet).
- soft-kill = 1h close > 64,050. hard-kill = 4h close > 64,580 (acceptance alone kills).
- MOVE 1 poke = NO ENTRY (observe only).

---

**Reminder:** these are facts. Produce your own independent read (levels, direction, p_up, named
death-price) knowing them — do not treat any fact as a directional conclusion. Independence is the
whole point; your value is your *uncorrelated* read, not agreement with the other desks.
