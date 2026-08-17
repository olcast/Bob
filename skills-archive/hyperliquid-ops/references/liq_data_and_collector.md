# Liquidation data on Hyperliquid + the forward collector (verified 2026-08-15)

## What the info API actually exposes (probed, not assumed)

| endpoint | returns | history? | use |
|---|---|---|---|
| `clearinghouseState{user}` | open positions w/ **exact `liquidationPx`**, `szi`, leverage, uPnL | **NO** — live snapshot only | true liq-map (aggregate across addresses) |
| `userFillsByTime{user,startTime,endTime}` | fills, up to 2000/call, **`liquidation:{liquidatedUser,markPx,method}` tag** | **YES** per address | realized liq events (ground truth) |
| `recentTrades{coin}` | ~last 10 trades, **`users`=both counterparties** | shallow (~25s) | harvest address universe forward |
| `vaultDetails{vaultAddress}` | HLP equity/PnL history, APR, `relationship.childAddresses` | portfolio series | HLP inventory + equity |
| `metaAndAssetCtxs` | per-coin mark/oracle/mid, funding, OI, premium, dayNtlVlm, impactPxs | current | context row |
| `liquidations` / `trades` (bare) | — | — | **422, do not exist** |

HLP master `0xdfc24b077bc1425ad1dea75bcb6f8158e10df303` holds ~$187M equity; positions live in its **7 child vaults** (`relationship.data.childAddresses`) — sum their `clearinghouseState` for HLP's net book.

## The induction question — "can you induce liq levels from past orders?"

Three distinct objects; do not conflate them:

1. **Current liquidation LEVELS** → **EXACT and directly observable** (`clearinghouseState.liquidationPx`). Not "induced" — HL computes and publishes each position's real liq price. Aggregate → the true fuel map, strictly better than the Coinglass leverage-estimate. LIMIT: snapshot only, so **forward-collect-only** (no as-of-past-date form).
2. **Realized liquidation EVENTS** (where liqs actually fired, historically) → **fully reconstructable** from tagged fills. Harvest addresses (trades feed) → `userFillsByTime` → filter `liquidation != null`.
3. **Historical liquidation MAP** (levels as they stood at a past instant) → **not from any single call**; only by replaying the entire on-chain fill log to rebuild every position at each past moment (heavy, but possible — HL is fully on-chain).

The price-only shortcut (draw bands X% off price at assumed leverage) = **T-003, already REJECTED as null (#071)**. That is the bad kind of "induction." Don't revive it. You don't need it — objects (1) and (2) are handed to you directly. This is the concrete meaning of "HL is a mine of information Renaissance never had": the mine is real, it is **forward**, and it is ground truth.

## Collector (`scripts/collector.py`) — READ-ONLY, /info only

Appends timestamped JSONL rows (`data/collector.jsonl`), kinds:
`market` · `book` (l2Book depth bands + walls) · `hlp` (net MM inventory across child vaults + equity/APR) · `liqmap` (exact-liqPx TRUE map: up-fuel/down-fuel + clusters) · `liqevent` (realized tagged liqs).
Persistent `data/addressbook.json` compounds address coverage across runs; bounded per-tick sweep keeps runtime finite.

```
python3 collector.py --once                       # one snapshot (call each firing)
python3 collector.py --loop --interval 300        # daemon, 5-min cadence
python3 collector.py --once --cap 400 --liqevents # deeper sweep + realized liqs
```

### Known limits / honesty
- `book` depth bands beyond ~0.1% are often identical: l2Book returns only 20 levels/side, and for liquid coins all 20 sit inside 0.1% of mark. The number is still a valid top-of-book size snapshot; deeper resting size is simply not in the API.
- `liqmap` coverage = the addresses harvested so far, NOT 100% of the book. Cold start is thin (tens of addresses); it sharpens over runs. Largest positions dominate notional, so partial coverage is still informative — but report `nPositions`/`nAddrScanned` with every read, never imply full coverage.
- Far-from-mark liq clusters (e.g. a 3× away level from a 1× position) are real but not "fuel" in any near-term sense — filter by distance-to-mark at analysis time.
- **Persistence:** default write is local JSONL, which dies with an ephemeral session. To actually accumulate across scheduled firings, point the collector at a durable sink (Drive file / dedicated ledger) — wire this before relying on the series.
