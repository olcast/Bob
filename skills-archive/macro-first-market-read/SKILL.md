---
name: macro-first-market-read
description: Use for ANY market read, level call, trade idea, or scheduled market brief on Hyperliquid (BTC/ETH/SOL/HYPE, xyz:SP500, xyz:BRENTOIL, xyz:CL, xyz:GOLD, single names). Enforces news-and-inbox-before-price ordering, a mandatory disconfirming search, and an explicit confluence/divergence step. Triggers on any question about levels, entries, shorts, longs, liquidity, funding, or "what's the setup".
---

# Macro-first market read

## Why this exists

On 2026-07-26 a weekend read started from price and levels. It searched the web with
escalation-framed queries ("Hormuz", "Iran tension", "oil war premium"), got back only
escalation headlines, and confidently told the trader the war premium was "fully intact"
— about an hour before a US–Iran bombing pause gapped the market the other way.

Two things were available and unused:
1. The story was sitting **unread in the trader's own Gmail** (Bloomberg, subject
   "Albanese to press Trump on tariffs, US and Iran extend pause").
2. The **price was already telling the truth** — HL BRENTOIL had bled 90 → 88 → 86 for
   hours. That divergence was noticed and then rationalised away to fit the narrative.

Root cause: **confirmation bias**. Searching to confirm the existing thesis rather than
to break it. This skill makes the disconfirming pass structural, not optional.

## Non-negotiable order

Do not write a single price level until steps 1–3 are complete.

### 1. Inbox first

Gmail is a primary feed, not a fallback. Run it unprompted, every time.

    newer_than:1d {from:bloomberg.net from:bloomberg.com from:ft.com from:theinformation.com from:wsj.com from:reuters.com}

Read the macro ones: Bloomberg Morning Briefing (Asia/Europe/Americas), Five Things,
myFT Daily Digest, The Information Briefing. Quote the market-moving lines **verbatim** —
do not paraphrase a headline into a thesis.

`get_thread` output frequently exceeds the token limit and is auto-written to a file.
When that happens, extract with python/grep or hand the file to a `general-purpose`
subagent. Do not skip the email because it was large.

### 2. Disconfirming search — mandatory

Search for the **opposite** of the prevailing narrative, in neutral wording.

- Narrative is escalation → search de-escalation, pause, ceasefire, talks, off-ramp.
- Narrative is risk-off → search what would make it risk-on.
- Never use narrative-loaded query terms; they return narrative-confirming results.
- Neutral form: `"US Iran latest <date>"`, not `"Iran escalation oil supply risk"`.

Also sweep every time: Fed / FOMC rate pricing, CPI, the earnings calendar, and any
scheduled event inside 72h.

### 3. Cross-asset data

    POST https://api.hyperliquid.xyz/info
      {"type":"metaAndAssetCtxs"}                  # main dex
      {"type":"metaAndAssetCtxs","dex":"xyz"}      # HIP-3 builder dex
      {"type":"candleSnapshot","req":{"coin":"xyz:SP500","interval":"15m",
                                      "startTime":<ms>,"endTime":<ms>}}
      {"type":"l2Book","coin":"xyz:SP500"}

Funding APR = `float(ctx["funding"]) * 24 * 365 * 100`.
Negative APR = crowded shorts = squeeze fuel. Large positive = crowded longs.

Minimum coverage: SP500, BRENTOIL, CL, GOLD, SILVER, DXY, XLE, VIX, BTC, ETH, HYPE.
Commodities and FX are the macro tell; the equity index is the follower.

Two facts that have been got wrong before:
- **HL `xyz:BRENTOIL` trades roughly $10 BELOW real Brent.** Direction is readable, the
  absolute level is not. Never quote it as the world oil price.
- **The xyz oracle is live 24/7, including weekends.** It is NOT frozen to Friday's cash
  close and the ~1%/update clamp does not bind in practice. Liquidations run on weekends.

### 4. Confluence / divergence — the actual product

Answer all three, explicitly:

- **Where do news, price and positioning agree?** Confluence is what is tradeable.
- **Where do they disagree?** Divergence is the warning.
  **When price contradicts the narrative, the price is right and the narrative is stale.**
  Stop. Go find the news that explains the price. Do not explain the price away.
- **What single event or level flips the regime?** Name the tripwire out loud.

### 5. Output

Blunt and short — this trader skims. No wall of tables.

1. What changed (verbatim quotes)
2. The tape — only the levels that matter
3. Confluence vs divergence
4. The trade: bias, entry zone, invalidation, tripwire

**Never look up or comment on the trader's account or open positions.** Standing
instruction: "do not look at my account, waste of time" / "leave my position out, focus
on giving alpha." Seeing a position also biases the framing — that has happened before.

## Failure modes to self-check before sending

- Did I read the inbox, or did I assume it held nothing?
- Did my search wording presuppose the answer?
- Is there an asset moving against my thesis that I have explained away?
- Am I quoting a price from hours ago as if it were current?
- Am I arguing a direction because a position exists in that direction?
