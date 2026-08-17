# Hyperliquid info endpoint — quick reference

All requests: `POST https://api.hyperliquid.xyz/info` with
`Content-Type: application/json`. Public, no auth. Read-only.
Full docs: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint
(append `.md?ask=<question>` to any docs page URL to query it in natural language).

## Request types used by scripts/hl_ops.py

| type | body params | returns |
|---|---|---|
| `perpDexs` | — | list of perp dexes; first entry `null` = main dex, others are HIP-3 builder dexes (`{name, fullName, deployer, ...}`). Pass `dex` to clearinghouseState/meta calls to query them |
| `clearinghouseState` | `user`, `dex?` | perp account: `assetPositions[].position` (coin, szi, entryPx, liquidationPx, leverage, marginUsed, positionValue, unrealizedPnl, returnOnEquity, cumFunding), `marginSummary`, `withdrawable` |
| `metaAndAssetCtxs` | — | `[meta, ctxs]`; zip `meta.universe[i].name` with `ctxs[i]` (markPx, funding = hourly rate, openInterest, oraclePx, dayNtlVlm) |
| `userFunding` | `user`, `startTime` (ms), `endTime?` | funding ledger events: `delta.{coin, usdc, szi, fundingRate}`, `time`. Positive `usdc` = received |
| `userFillsByTime` | `user`, `startTime`, `endTime?` | fills: coin, px, sz, side, dir ("Open Long"…), closedPnl, fee, time, oid, hash. Max ~500/page — paginate with last `time`+1 |
| `userFills` | `user` | most recent ~2000 fills |
| `portfolio` | `user` | `[["day", {accountValueHistory, pnlHistory, vlm}], ["week",…], ["month",…], ["allTime",…]]`; histories are `[timestampMs, "value"]` pairs |

## Other useful read-only types (not wired into the script)

- `fundingHistory` (`coin`, `startTime`) — historical hourly funding rates per coin
- `predictedFundings` — predicted next funding across venues (HL vs Binance vs Bybit)
- `openOrders` / `frontendOpenOrders` (`user`) — resting orders
- `spotClearinghouseState` (`user`) — spot token balances
- `historicalOrders`, `orderStatus` (`user`, `oid`)
- `l2Book` (`coin`), `candleSnapshot` (`req: {coin, interval, startTime, endTime}`)

## Conventions

- All numbers arrive as strings — always cast.
- `szi` is signed position size: positive = long, negative = short.
- Funding is exchanged hourly; APR ≈ hourly rate × 24 × 365.
- Address must be the master or sub-account (42-char hex). Agent-wallet
  addresses silently return empty results.
- Testnet equivalent: `https://api.hyperliquid-testnet.xyz/info`.
