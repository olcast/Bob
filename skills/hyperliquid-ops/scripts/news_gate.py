#!/usr/bin/env python3
"""
NEWS DIVERGENCE GATE — "does the wire contradict the tape?"

Read-only. No order mutation, no forecasting. Pulls free financial/crypto RSS
headlines (Coindesk, CoinTelegraph, BBC Business, MarketWatch), extracts the named
coin/topic + tone, and flags only DIVERGENCE candidates — where a headline's
directional implication could contradict current positioning/flow.

Per Olivier's standing rule: NEWS IS A GATE, NOT A SIGNAL. This script surfaces
*divergence checks*, never calls. It does not grade, does not store in calls.json,
does not touch doctrine. Output is a durable JSONL log + a human-readable summary.

stdlib only (xml.etree + urllib) — survives without pip. No feedparser dependency.
"""

import json
import time
import urllib.request
import xml.etree.ElementTree as ET

FEEDS = [
    ("coindesk",     "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    ("cointelegraph","https://cointelegraph.com/rss"),
    ("bbc-biz",      "https://feeds.bbci.co.uk/news/business/rss.xml"),
    ("marketwatch",  "https://www.marketwatch.com/rss/topstories"),
]

# Coin -> keyword map (case-insensitive topics we care about, for divergence-checking)
WATCH = {
    "BTC": ["bitcoin", "btc"],
    "ETH": ["ethereum", "eth", "ether "],
    "SOL": ["solana", "sol"],
    "HYPE": ["hyperliquid", "hype"],
    "macro": ["fed", "fomc", "rate", "inflation", "cpi", "recession", "etf", "tariff"],
    "risk-off": ["crash", "selloff", "liquidation", "collapse", "panic", "dump", "plunge"],
    "risk-on": ["rally", "surge", "all-time", "record", "breakout", "pump", "soar"],
}

DIR_POS = ["surge", "rally", "pump", "soar", "breakout", "record", "all-time", "gain",
           "bull", "buy", "accumulat", "inflow", "approve", "etf inflows", "rate cut"]
DIR_NEG = ["crash", "dump", "plunge", "selloff", "collapse", "panic", "liquidation",
           "slump", "bear", "sell", "outflow", "reject", "hike", "recession", "downgrade"]

UA = "Mozilla/5.0 (compatible; news-gate/1.0)"


def fetch_rss(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as e:
        return None


def tone(text):
    t = text.lower()
    pos = sum(1 for w in DIR_POS if w in t)
    neg = sum(1 for w in DIR_NEG if w in t)
    if pos > neg:
        return "POS"
    if neg > pos:
        return "NEG"
    return "NEU"


def main():
    out = []
    for source, url in FEEDS:
        xml = fetch_rss(url)
        if not xml:
            out.append({"source": source, "error": "fetch failed"})
            continue
        try:
            root = ET.fromstring(xml)
        except Exception as e:
            out.append({"source": source, "error": f"parse failed: {e}"})
            continue
        items = root.findall(".//item")[:15]
        for it in items:
            title = it.findtext("title") or ""
            if not title:
                continue
            t = title.lower()
            topics = [k for k, kws in WATCH.items() if any(kw in t for kw in kws)]
            if not topics:
                continue
            out.append({
                "source": source,
                "title": title.strip(),
                "topics": topics,
                "tone": tone(title),
                "ts": int(time.time() * 1000),
            })

    # Write durable JSONL log (append)
    with open("data/news_gate.jsonl", "a") as f:
        f.write(json.dumps({"ts": int(time.time() * 1000), "count": len(out)}) + "\n")

    # Print summary
    div = [x for x in out if x.get("tone") in ("POS", "NEG")]
    print(f"NEWS GATE · {len(out)} watch-relevant headlines · {len(div)} directional")
    for x in div[:12]:
        print(f"  [{x['source']:13}] {x['tone']:3} {', '.join(x['topics']):20} {x['title'][:90]}")
    if not div:
        print("  (no directional watch-headlines this pull)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
