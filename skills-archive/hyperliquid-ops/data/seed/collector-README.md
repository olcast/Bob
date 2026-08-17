# HL-OPS forward collector — data sink

Durable store for the Hyperliquid forward-collector (VCP-ABLATION P2 layer). Each scheduled
run drops one append-only file `tick-YYYYMMDD-HHMM.jsonl`. Source: `hyperliquid-ops/scripts/collector.py`.
READ-ONLY collection — /info API only, never /exchange. Filled from 2026-08-15 onward.

## Row schema (one JSON object per line; `ts` = ms epoch UTC)
- **market**  — coin, mark, oracle, mid, funding, oi, premium, dayNtlVlm, impactBp
- **book**    — l2Book depth (bidDepth/askDepth at ±0.1/0.25/0.5/1% of mark) + top-3 bid/ask walls.
                NOTE: bands often equal — l2Book returns only 20 levels/side; for liquid coins all 20
                sit inside 0.1%. Valid top-of-book size sample; deeper resting size is not in the API.
- **hlp**     — Hyperliquid's OWN market-maker net inventory across its 7 child vaults (szi + ntlUsd per
                coin), equity, apr. Near-neutral by design; small net tilts + larger offsetting gross.
                The unique observable no CEX broadcasts.
- **liqmap**  — TRUE liquidation map from EXACT per-position liquidationPx (not a leverage estimate):
                downFuelUsd (forced sells below), upFuelUsd (forced buys above), fuelSkew, and the
                biggest long/short liq clusters [price, notionalUsd]. nPositions/nAddrScanned = coverage.
                CAVEAT: aggregates only harvested addresses (partial book); far-from-mark clusters (e.g. a
                3x-away level off a 1x position) inflate totals — FILTER by distance-to-mark at analysis time.
- **liqevent**— realized liquidations from tagged fills (px, sz, side, dir, closedPnl, method, markPx).

## Analysis
Concatenate all `tick-*.jsonl`, parse by `kind`. The point is the TIME SERIES — how HLP inventory,
fuel skew, and depth evolve, and whether price is drawn to / repelled by liq clusters (VCP-ABLATION T-B).
Coverage compounds only if the address book is also persisted (v2); v1 takes a rolling address sample
each run, so treat liqmap levels as sampled, not exhaustive — always read nPositions/nAddrScanned with them.
