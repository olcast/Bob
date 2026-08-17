#!/usr/bin/env python3
"""news_check.py — free, no-auth headline check for macro_preflight's Step 0
"disconfirming search" / catalyst-calendar requirement.

Why this exists: `web_search` is disabled in this environment (no provider
configured — Brave/Perplexity/Exa all need an API key nobody has set up yet).
This is the interim, zero-cost substitute: pull known finance-news RSS feeds
(Bloomberg Markets, FT) directly via HTTP, no auth, no key, and grep for
BTC/crypto/macro-relevant keywords + surface anything published in the last
N hours.

This is NOT a full disconfirming-search replacement — it only sees headlines
from these two sources' RSS output, not a full web index, and cannot search
for a SPECIFIC named event the way `web_search` could. It is a real partial
fix for "did anything just happen" (Step 0's actual concern) at zero cost,
until a real search provider is configured.

Usage:
    python3 news_check.py                       # default keyword set, last 24h
    python3 news_check.py --keywords BTC bitcoin fed fomc
    python3 news_check.py --hours 6
    python3 news_check.py --json

Read-only, no auth, no keys required. Sources are untrusted external content —
treat headlines as leads to verify, not as ground truth.
"""
import argparse
import datetime
import json
import re
import sys
import urllib.request
from email.utils import parsedate_to_datetime

FEEDS = [
    ("Bloomberg Markets", "https://www.bloomberg.com/feeds/markets/news.rss"),
    ("Financial Times",   "https://www.ft.com/rss/home"),
]

DEFAULT_KEYWORDS = [
    "bitcoin", "btc", "crypto", "hyperliquid", "ethereum", "fed", "fomc",
    "rate", "inflation", "cpi", "jackson hole", "powell", "warsh",
    "treasury", "yield", "dollar", "oil", "opec", "war", "geopolit",
    "sanction", "regulation", "sec ", "etf",
]

ITEM_RE = re.compile(r"<item>(.*?)</item>", re.DOTALL)
TITLE_RE = re.compile(r"<title>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</title>", re.DOTALL)
LINK_RE = re.compile(r"<link>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</link>", re.DOTALL)
DESC_RE = re.compile(r"<description>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</description>", re.DOTALL)
PUBDATE_RE = re.compile(r"<pubDate>\s*(.*?)\s*</pubDate>", re.DOTALL)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (openclaw hl-ops news_check)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="replace")


def parse_rss(xml):
    items = []
    for m in ITEM_RE.finditer(xml):
        block = m.group(1)
        title_m = TITLE_RE.search(block)
        link_m = LINK_RE.search(block)
        desc_m = DESC_RE.search(block)
        pub_m = PUBDATE_RE.search(block)
        if not title_m:
            continue
        pub = None
        if pub_m:
            try:
                pub = parsedate_to_datetime(pub_m.group(1))
            except Exception:
                pub = None
        items.append({
            "title": title_m.group(1).strip(),
            "link": link_m.group(1).strip() if link_m else "",
            "desc": (desc_m.group(1).strip() if desc_m else "")[:300],
            "pub": pub.isoformat() if pub else None,
        })
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keywords", nargs="*", default=None,
                     help="override the default keyword list")
    ap.add_argument("--hours", type=float, default=24.0,
                     help="only surface items published within this many hours (default 24)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    keywords = [k.lower() for k in (args.keywords or DEFAULT_KEYWORDS)]
    now = datetime.datetime.now(datetime.timezone.utc)
    cutoff = now - datetime.timedelta(hours=args.hours)

    all_items = []
    errors = []
    for name, url in FEEDS:
        try:
            xml = fetch(url)
            items = parse_rss(xml)
            for it in items:
                it["source"] = name
            all_items.extend(items)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{name}: {e}")

    hits = []
    for it in all_items:
        text = (it["title"] + " " + it["desc"]).lower()
        matched = [k for k in keywords if k in text]
        if not matched:
            continue
        pub_dt = None
        if it["pub"]:
            try:
                pub_dt = datetime.datetime.fromisoformat(it["pub"])
            except Exception:
                pub_dt = None
        in_window = (pub_dt is None) or (pub_dt >= cutoff)
        if in_window:
            hits.append({**it, "matched_keywords": matched})

    hits.sort(key=lambda h: h["pub"] or "", reverse=True)

    if args.json:
        print(json.dumps({
            "asOfUtc": now.isoformat(),
            "hoursWindow": args.hours,
            "keywords": keywords,
            "sourcesQueried": [n for n, _ in FEEDS],
            "sourceErrors": errors,
            "totalItemsSeen": len(all_items),
            "hits": hits,
        }, indent=2))
        return 0

    print(f"NEWS CHECK — as of {now.strftime('%Y-%m-%d %H:%M:%S')} UTC "
          f"(window: last {args.hours:.0f}h)")
    print(f"Sources: {', '.join(n for n, _ in FEEDS)} (free RSS, no auth — "
          f"headline-only, not a full search index)")
    if errors:
        print("SOURCE ERRORS:")
        for e in errors:
            print(f"  - {e}")
    print()
    if not hits:
        print(f"NO matches for {len(keywords)} tracked keywords across "
              f"{len(all_items)} items seen. Consistent with a quiet tape — "
              f"does NOT prove nothing happened (RSS-only, not a full search).")
    else:
        print(f"{len(hits)} matching headline(s):")
        for h in hits:
            pub = h["pub"][:16].replace("T", " ") if h["pub"] else "??"
            print(f"  [{pub} UTC] ({h['source']}) {h['title']}")
            print(f"      matched: {', '.join(h['matched_keywords'])}")
            if h["link"]:
                print(f"      {h['link']}")
    print()
    print("This is a PARTIAL substitute for a real search provider (web_search "
          "is disabled — no Brave/Perplexity/Exa key configured). Treat a clean "
          "run as 'nothing on Bloomberg/FT RSS', not as 'confirmed nothing "
          "happened anywhere'. Read-only, no auth.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
