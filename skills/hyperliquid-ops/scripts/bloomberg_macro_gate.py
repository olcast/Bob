#!/usr/bin/env python3
"""
BLOOMBERG MACRO GATE — read ALL Bloomberg newsletter emails from Gmail (IMAP),
for the macro gate, at pre-EU / pre-US / US-close windows.

DISCIPLINE (Olivier's standing rule, encoded here):
  * These emails are BACKWARD-LOOKING. Grain of salt. They describe what already
    happened — they are CONTEXT/GATE, NEVER a forecast or a trade signal.
  * The desk's macro gate requires every price/level hypothesis be matched to a
    NAMED STORY that PRE-DATES the move. This script supplies those named stories.
  * John Authers is ALWAYS pinned first — his column is a required macro read.
  * Read-only IMAP. Never send, never modify, never delete.

Usage:  python3 bloomberg_macro_gate.py [--hours N] [--since <HH:MM UTC>]
  --hours N      pull emails from last N hours (default 6)
  --watch WINDOW one of: pre_eu|pre_us|us_close  (labels the log line)

Output: durable JSONL at data/bloomberg_gate.jsonl + stdout summary.
"""

import argparse
import imaplib
import email
import json
import os
import re
import time
from email.header import decode_header
from email.utils import parsedate_to_datetime

USER = "ol.castagne@gmail.com"
# Password file lives at the WORKSPACE ROOT (gitignored, chmod 600), not the skill dir.
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WS_ROOT = os.path.dirname(os.path.dirname(SKILL_DIR))
PW_FILE = os.environ.get("GMAIL_APP_PASSWORD_FILE", os.path.join(WS_ROOT, ".gmail_app_password"))
PASS = None
try:
    PASS = open(PW_FILE).read().strip().replace(" ", "")
except Exception:
    PASS = None

# Sender priorities: Authers always first; Bloomberg/Markets second; rest by recency.
PRIORITY = ["John Authers", "Bloomberg", "Bloomberg Markets", "Bloomberg Morning", "Bloomberg UK"]

# Macro-relevant keyword families for a coarse relevance tag (NOT a signal).
MACRO_KEYS = {
    "rates/bonds": ["yield", "bond", "treasury", "fed", "fomc", "rate", "borrowing", "10-year", "30-year"],
    "fx": ["dollar", "eur", "yen", "sterling", "fx", "currency", "yuan", "pound"],
    "commodities": ["oil", "crude", "gold", "copper", "brent", "opec", "natgas", "commodity"],
    "equities": ["stocks", "equity", "s&p", "nasdaq", "futures", "earnings", "rally", "selloff"],
    "policy/risk": ["central bank", "ecb", "boj", "boe", "inflation", "cpi", "recession", "tariff", "election", "war", "geopolitical", "china"],
}


def dec(s):
    if not s:
        return ""
    out = []
    for p, enc in decode_header(s):
        out.append(p.decode(enc or "utf-8", "replace") if isinstance(p, bytes) else p)
    return "".join(out)


def sender_rank(fr):
    for i, p in enumerate(PRIORITY):
        if p.lower() in fr.lower():
            return i
    return 99


def relevance(topics, body):
    hits = []
    b = body.lower()
    for fam, kws in MACRO_KEYS.items():
        if any(k in b or k in topics for k in kws):
            hits.append(fam)
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=int, default=6)
    ap.add_argument("--watch", default="macro", help="pre_eu|pre_us|us_close|macro")
    a = ap.parse_args()

    if not PASS:
        print("ERROR: no .gmail_app_password file found.")
        return 1

    M = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    M.login(USER, PASS)
    M.select("INBOX")

    since = time.strftime("%d-%b-%Y", time.gmtime(time.time() - a.hours * 3600))
    typ, data = M.search(None, "FROM", '"news.bloomberg.com"', "SINCE", since)
    ids = data[0].split() if data and data[0] else []

    cutoff = time.time() - a.hours * 3600
    items = []
    for i in ids:
        typ, d = M.fetch(i, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
        if not d or d[0] is None:
            continue
        msg = email.message_from_bytes(d[0][1])
        fr = dec(msg.get("From", ""))
        subj = dec(msg.get("Subject", "")).strip().replace("\r", " ").replace("\n", " ")
        date_s = msg.get("Date", "")
        try:
            dt = parsedate_to_datetime(date_s)
            ts = dt.timestamp()
        except Exception:
            ts = 0
        if ts >= cutoff:
            items.append((ts, sender_rank(fr), fr, subj))
    M.logout()

    items.sort(key=lambda x: (x[1], -x[0]))  # priority, then newest first

    out = []
    for ts, rank, fr, subj in items:
        rel = relevance(subj, subj)
        out.append({
            "ts": int(ts * 1000),
            "sender": fr,
            "subject": subj,
            "macro_topics": rel,
        })

    # durable log
    logdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(logdir, exist_ok=True)
    with open(os.path.join(logdir, "bloomberg_gate.jsonl"), "a") as f:
        f.write(json.dumps({"run_ts": int(time.time() * 1000), "watch": a.watch, "count": len(out)}) + "\n")

    print(f"BLOOMBERG MACRO GATE [{a.watch}] · {len(out)} newsletters last {a.hours}h (backward-looking — grain of salt)")
    for x in out[:20]:
        authers = "★" if "authers" in x["sender"].lower() else " "
        topics = ",".join(x["macro_topics"]) or "—"
        print(f"  {authers}[{topics:18}] {x['subject'][:80]}")

    if not out:
        print("  (no Bloomberg emails in window)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
