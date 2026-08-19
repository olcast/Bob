#!/usr/bin/env python3
"""
refresh_desk_card.py — regenerate data/current_call.md from live venue + current_call.json,
then (optionally) send/pin the updated card to Telegram.

This is the single authoritative "last call always in view" renderer.
FACTS from live API + current_call.json; conclusions = the registered call lines only.
"""
import json, sys, time, urllib.request

BASE = "/root/.openclaw/workspace/skills/hyperliquid-ops"
CC = f"{BASE}/data/current_call.json"
OUT = f"{BASE}/data/current_call.md"

def post(b):
    r = urllib.request.Request(
        "https://api.hyperliquid.xyz/info",
        data=json.dumps(b).encode(),
        headers={"Content-Type": "application/json"},
    )
    return json.load(urllib.request.urlopen(r, timeout=40))

def main():
    # live venue
    mark = float(post({"type": "allMids"}).get("BTC"))
    meta = post({"type": "metaAndAssetCtxs"})
    i = [k for k, a in enumerate(meta[0]["universe"]) if a.get("name") == "BTC"][0]
    c = meta[1][i]
    oi = float(c.get("openInterest"))
    fund = float(c.get("funding"))

    # registered call facts (source of truth)
    cc = json.load(open(CC))
    ts = time.strftime("%H:%M UTC", time.gmtime())
    sign = "+" if fund >= 0 else "-"

    direction = cc.get("direction", "SHORT")
    note = cc.get("thesis_note", "65,018 squeeze: OI fell + funding = exhaustion, not sponsorship")

    # re-short line (move2) from current_call.json
    reshort_trigger = cc.get("reshort_trigger", "15m close < 64,550")
    # Schema drift guard: reshort_trigger may be a dict {level, note} (current_call.json)
    if isinstance(reshort_trigger, dict):
        lvl = reshort_trigger.get("level")
        lvl_s = f"{lvl:,}" if isinstance(lvl, (int, float)) else str(lvl)
        note_s = reshort_trigger.get("note", "")
        reshort_trigger = f"15m close < {lvl_s} ({note_s})" if note_s else f"15m close < {lvl_s}"
    reshort_entry = cc.get("reshort_entry", 64550)
    reshort_target = cc.get("reshort_path", "63,650 → 62,500 → 61,600")
    reshort_death = cc.get("reshort_death", "15m close > 65,020")

    move3 = cc.get("move3_break", "15m < 62,500 pool break → 61,800 / 61,400")
    longtrap = cc.get("longtrap", "15m reclaim 63,938")
    terminus = cc.get("terminus", "61,600 (max pain)")

    txt = (
        f"━━━ DESK CALL — {ts} ━━━\n"
        f"DIRECTION: {direction}\n"
        f"({note})\n\n"
        f"▶ RE-SHORT (primary)\n"
        f"   {reshort_trigger} = SHORT\n"
        f"   {reshort_entry} → {reshort_target}\n"
        f"   DEATH: {reshort_death}\n\n"
        f"▶ MOVE-3 (deep, dormant)\n"
        f"   {move3}\n\n"
        f"▶ LONG-the-trap (contingent)\n"
        f"   {longtrap}\n\n"
        f"⇒ TERMINUS: {terminus}\n\n"
        f"───────────────\n"
        f"mark {mark:.0f} | OI {oi:.0f} | funding {sign}{abs(fund)*100:.4f}%/h\n"
        f"{ts}\n"
        f"━━━━━━━━━━━━━━━━"
    )

    with open(OUT, "w") as f:
        f.write(txt)

    # --send flag: emit to stdout so a wrapper can message() it
    if "--send" in sys.argv:
        print(txt)

    print(f"[refresh_desk_card] wrote {OUT} ({len(txt)} bytes) @ {ts}")

if __name__ == "__main__":
    main()
