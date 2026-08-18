# MEMORY.md — Charly's long-term memory

## Who Olivier is (from Claude export, 2026-08-18)

- **Name:** Olivier ("Olive") Ludovic Castagne — `ol.castagne@gmail.com`.
- **Background:** retired global-macro portfolio manager, ~30 years, ex-hedge-fund.
- **Now:** trades crypto perpetuals **manually** on Hyperliquid — BTC/ETH/SOL/HYPE + oracle-priced synthetic markets (SP500/Brent/Gold, "xyz").
- **Timezone:** Europe/Madrid (ES). Devices: iPhone + Mac (macOS 10.15.7).

## His trading desk architecture (v2.6.4 — frozen until 50 calls grade)

This is *more* advanced than the workspace `hyperliquid-ops` skill currently reflects. The full stack includes:
- **Macro gate first** — no price/level work until every ±2% cross-asset mover is matched to a named story PRE-DATING the move; mandatory disconfirming search.
- **Venue-state analysis, structural confluence** (pivot trendlines, volume profiles, raid-pool maps), options term structure, Elliott wave context.
- **Append-only versioned ledger.**
- **Low-N statistical regime** — first 100 graded calls: flat 0.33R sizing, 80%-of-liquidation stop rule, 3-stops/5-days breaker, strict caps + holdouts.
- **Adversarial audit layer** — blind agents + echo-chamber detector, weekly retros (expectancy, Brier).
- **Pre-registered forecasting table** — CO-CALL vs DESK-SOLO, PM Brier vs desk Brier, CONTESTED vs AGREED expectancy, holdout at N=50, EW-Context vs Structural-Only.

## Standing safety findings (his own prior reviews — re-flag, don't rediscover)

1. **R is fictional on xyz oracle markets during closed-underlying hours.** The whole risk envelope (0.33R sizing, 80%-liq stop, breaker) assumes a hard engine stop that works on BTC/ETH/SOL/HYPE but *breaks* when SP500/Brent/Gold underlying is dark (nightly/weekend). Friday 22:00 CET card → weekend headline → Sunday re-open re-marks 3–4% → stop fires into ~$465M-OI thin book = 3–6× planned R on a "conservative" call. The breaker counts *stops*, not realized R.
2. **Bounded independence in the audit layer** — two frontier models, three rounds each, *same model family* = correlated errors. **Directly relevant to the DeepSeek-produces/Qwen-challenges cross-check I built:** both are Chinese frontier families; a shared market-structure blind spot won't be caught.
3. **Narrative-vector caps are semantic, not statistical** — "AI infra bid / ETF flows / macro liquidity easing" are three vectors but collapse to one correlated position (long crypto beta) in a liquidation cascade.
4. **Stops placed "beyond liquidity magnets"** → the price paths that reach them are disproportionately *cascade* paths, so conditional-on-stop slippage is well above average. `1.33R` planned can realize `3R+` in one wick.

## Model / provider lineup (see TOOLS.md + SOP-RECURSIVE.md §1 for the standing hygiene rule)

- **DeepSeek `deepseek-v4-pro`** = producer (flagship, direct-pay).
- **Qwen `qwen3.8-max`** = challenger (1M ctx, direct-pay DashScope intl).
- **Kimi `kimi-k3`** = unreliable third (concurrency=1, 128k ctx overflows on full reviews).
- **Vision:** `qwen3-vl-max` wired (pending gateway restart).
- **Always re-resolve the current flagship model id per provider before use** (§1 of SOP) — we've been burned twice (`kimi-k2`→`k3`, `deepseek-chat`→`v4-pro`).

## Standing cross-check discipline

Produce with one model, independently challenge with a second, reconcile. Do NOT trust a single model's blind spot (2026-07-26 confirmation-bias miss is the cautionary tale). Bounded-independence caveat above applies.
