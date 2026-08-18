#!/usr/bin/env python3
"""GAME-THEORY RED-TEAM PACKET — builds the structured brief fed to an adversarial red-team model
(a DIFFERENT model family than the producer/challenger — e.g. Grok `grok-4.20-beta-latest-reasoning`
or DeepSeek `deepseek-v4-pro` as the odd family out) to argue the incentive-structure case AGAINST
a live desk call. This is deliberately NOT another "give me your own p_up" vote — doctrine #8
(v3.2) explicitly rejected multi-agent debate as default because correlated forecasts on the same
question just produce consensus theater. This packet asks a different question entirely:

  "Given this call and this positioning data, who is positioned on the other side, what forces
   them out (or doesn't), what's the pain trade, and what is the single best reason the market
   WANTS to prove this call wrong?"

That is genuinely distinct information — a stress-test of the call's assumed mechanism, not a
second forecast. Feed the packet's JSON to the red-team model verbatim; do not add narrative or
pre-interpretation (same fact-firewall discipline as R5's blind-audit packets, applied here in the
opposite direction — this one is deliberately NOT blind, because game-theory reasoning needs the
thesis to argue against it).

Usage:
  python3 redteam_packet.py call.json --coin BTC
  (call.json is the same SCORE-shaped record used elsewhere: ts,h,up,dn,p_up,p_base,by, optionally
   a free-text "thesis" field with the mechanism/invalidation)

Read-only: shells out to oi_flow.py --json and pulls the latest liqmap tick from collector.jsonl if
present. No /exchange calls, no keys.
"""
import json, sys, argparse, subprocess, os

HERE = os.path.dirname(os.path.abspath(__file__))

def load(path):
    return json.loads(open(path).read())

def latest_liqmap(coin):
    """Pull the most recent liqmap tick for `coin` from data/collector.jsonl, if any."""
    path = os.path.join(HERE, "..", "data", "collector.jsonl")
    if not os.path.exists(path):
        return None
    best = None
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("kind") == "liqmap" and row.get("coin") == coin:
                best = row  # keep last match (file is append-only, chronological)
    return best

def run_oi_flow(coin):
    try:
        out = subprocess.run(
            ["python3", os.path.join(HERE, "oi_flow.py"), "--coins", coin, "--json"],
            capture_output=True, text=True, timeout=30,
        )
        if out.returncode != 0:
            return {"error": out.stderr.strip()[:500]}
        data = json.loads(out.stdout)
        rows = data.get("rows", [])
        return rows[0] if rows else {"error": "no row returned"}
    except Exception as e:
        return {"error": str(e)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("call_json")
    ap.add_argument("--coin", default="BTC")
    args = ap.parse_args()

    call = load(args.call_json)
    positioning = run_oi_flow(args.coin)
    liqmap = latest_liqmap(args.coin)

    packet = {
        "coin": args.coin,
        "the_call": {
            "up_target": call.get("up"),
            "down_target": call.get("dn"),
            "p_up": call.get("p_up"),
            "horizon_hours": call.get("h"),
            "thesis": call.get("thesis"),  # may be absent; free-text mechanism if provided
            "by": call.get("by"),
        },
        "positioning": positioning,
        "liquidation_fuel": liqmap,
        "questions_for_the_redteam": [
            "Who is positioned on the OTHER side of this call right now, and what evidence (funding, OI, "
            "liq-map fuel skew) supports that?",
            "What forces the other side to capitulate, hold, or actually be validated? Name the mechanism "
            "(funding bleed, liquidation cascade, thin-book squeeze, or: nothing forces them and the call is wrong).",
            "State the PAIN TRADE explicitly: which direction hurts the most currently-positioned money, and is "
            "that the direction this call is arguing for or against?",
            "Give the single best reason the market's incentive structure wants to PROVE THIS CALL WRONG — "
            "not a generic bear/bull case, the specific mechanism that would make the crowded side right.",
            "Is there a forced flow (liquidation cluster, funding cost, thin weekend book) that dominates "
            "opinion here regardless of what either side 'believes'?",
        ],
        "instructions": (
            "Answer the five questions directly and concisely. Do not restate the call's own reasoning back "
            "as agreement — your job is adversarial: find the strongest case that breaks it, using the "
            "positioning data given, not vibes. If the data genuinely gives no edge to the other side, say so "
            "plainly — 'no counter-positioning found' is a valid, useful answer, not a failure."
        ),
    }
    print(json.dumps(packet, indent=2, default=str))

if __name__ == "__main__":
    main()
