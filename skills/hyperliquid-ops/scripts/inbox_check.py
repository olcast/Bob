#!/usr/bin/env python3
"""inbox_check.py — READ-ONLY Gmail inbox scan for catalyst/news alerts.

Scope, deliberately narrow:
  - Opens INBOX in IMAP *read-only* mode (readonly=True — the imaplib flag that
    stops the server from clearing the \\Seen flag on fetch, i.e. this cannot
    even mark mail as read, let alone send/delete/modify anything).
  - Only SEARCHes/FETCHes headers + snippet text. Never sends. Never deletes.
    Never moves/labels. Never touches any other mailbox/label than INBOX.
  - Filtered to a specific sender allowlist (Bloomberg/FT/catalyst-alert
    senders) by default — NOT a full inbox dump. Override with --senders if
    Olivier wants a wider net for a specific check.

Credentials: read from skills-archive/hyperliquid-ops/.secrets/gmail.env
  (chmod 600, git-ignored, never printed by this script).

Usage:
    python3 inbox_check.py                        # default allowlist, last 24h
    python3 inbox_check.py --hours 6
    python3 inbox_check.py --senders bloomberg.com ft.com
    python3 inbox_check.py --json
"""
import argparse
import datetime
import email
import email.utils
import imaplib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CREDS_PATH = os.path.join(HERE, "..", ".secrets", "gmail.env")

DEFAULT_SENDER_ALLOWLIST = [
    "bloomberg.com",
    "ft.com",
    "alerts@",       # generic catalyst-alert prefix used by many finance senders
    "news@",
]


def load_creds(path):
    if not os.path.exists(path):
        print(f"CREDENTIALS NOT FOUND at {path} — nothing to do.", file=sys.stderr)
        sys.exit(2)
    creds = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or "=" not in line:
                continue
            k, v = line.split("=", 1)
            creds[k] = v
    return creds


def decode_header_val(raw):
    if not raw:
        return ""
    parts = email.header.decode_header(raw)
    out = []
    for text, enc in parts:
        if isinstance(text, bytes):
            out.append(text.decode(enc or "utf-8", errors="replace"))
        else:
            out.append(text)
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=24.0,
                     help="only surface mail received within this many hours (default 24)")
    ap.add_argument("--senders", nargs="*", default=None,
                     help="override the default sender allowlist (substring match on From:)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    allowlist = [s.lower() for s in (args.senders or DEFAULT_SENDER_ALLOWLIST)]
    creds = load_creds(CREDS_PATH)
    addr = creds.get("GMAIL_ADDRESS")
    pw = creds.get("GMAIL_APP_PASSWORD", "").replace(" ", "")
    if not addr or not pw:
        print("Missing GMAIL_ADDRESS or GMAIL_APP_PASSWORD in creds file.", file=sys.stderr)
        sys.exit(2)

    now = datetime.datetime.now(datetime.timezone.utc)
    since = (now - datetime.timedelta(hours=args.hours)).strftime("%d-%b-%Y")

    try:
        m = imaplib.IMAP4_SSL("imap.gmail.com")
        m.login(addr, pw)
        m.select("INBOX", readonly=True)   # <-- hard read-only, cannot mutate anything
    except Exception as e:  # noqa: BLE001
        print(f"IMAP CONNECT/LOGIN FAILED: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        status, data = m.search(None, f'(SINCE "{since}")')
        if status != "OK":
            print(f"IMAP SEARCH FAILED: {status}", file=sys.stderr)
            sys.exit(2)
        ids = data[0].split()

        hits = []
        for msg_id in ids:
            status, msg_data = m.fetch(msg_id, "(BODY.PEEK[HEADER])")  # PEEK = no \Seen mutation
            if status != "OK":
                continue
            raw_headers = msg_data[0][1]
            msg = email.message_from_bytes(raw_headers)
            from_ = decode_header_val(msg.get("From", ""))
            subj = decode_header_val(msg.get("Subject", ""))
            date_raw = msg.get("Date", "")
            try:
                date_dt = email.utils.parsedate_to_datetime(date_raw)
                if date_dt.tzinfo is None:
                    date_dt = date_dt.replace(tzinfo=datetime.timezone.utc)
            except Exception:
                date_dt = None

            from_lower = from_.lower()
            if not any(s in from_lower for s in allowlist):
                continue
            if date_dt and date_dt < (now - datetime.timedelta(hours=args.hours)):
                continue

            hits.append({
                "from": from_,
                "subject": subj,
                "date": date_dt.isoformat() if date_dt else date_raw,
            })
    finally:
        try:
            m.close()
        except Exception:
            pass
        m.logout()

    hits.sort(key=lambda h: h["date"], reverse=True)

    if args.json:
        print(json.dumps({
            "asOfUtc": now.isoformat(),
            "hoursWindow": args.hours,
            "senderAllowlist": allowlist,
            "totalInboxMessagesScanned": len(ids),
            "hits": hits,
        }, indent=2))
        return

    print(f"INBOX CHECK — as of {now.strftime('%Y-%m-%d %H:%M:%S')} UTC "
          f"(window: last {args.hours:.0f}h, read-only, INBOX only)")
    print(f"Sender allowlist: {', '.join(allowlist)}")
    print(f"Scanned {len(ids)} inbox message(s) since {since}.")
    print()
    if not hits:
        print("No matches from the allowlisted senders in this window.")
    else:
        print(f"{len(hits)} matching message(s):")
        for h in hits:
            d = h["date"][:16].replace("T", " ") if h["date"] else "??"
            print(f"  [{d} UTC] {h['from']}")
            print(f"      {h['subject']}")
    print()
    print("Read-only (IMAP readonly=True + BODY.PEEK — cannot mark-read, send, "
          "delete, or modify). Headers/subject only, no body content fetched.")


if __name__ == "__main__":
    main()
