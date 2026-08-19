#!/usr/bin/env python3
"""
assemble_brief.py — build the firing-time context packet for the three blind originators.

WHY (Olivier 2026-08-18, "models should re-read EVERYTHING on every run, not inherit"):
  The originators are stateless between firings. Anything they need to know must be
  handed to them AT SPAWN TIME, freshly assembled from the current source files — never
  from the reconciler's memory, never from a prior run's conclusions.

WHAT goes in (facts + rules) vs WHAT stays out (conclusions):
  IN  — doctrine RULES (SOP-RECURSIVE.md), venue-state FACTS (state.json move/zone fields),
        resolved macro gate (macro_gate_resolved.md), venue-risk facts (brief_facts.md),
        raw cross-asset tape (cross_asset_snapshot.md), live funding/OI (Hyperliquid API).
  OUT — prior run verdicts, ensemble scores, directional priors, the reconciler's labels.
        The independence of each blind read is the whole point; conclusions are Charly's
        reconcile layer, not the originators' input.

OUTPUT: data/brief_context.md  (single file the crosscheck wrapper points originators at)

This is the FIX for the "amnesiac originator" failure mode: the firing no longer depends
on a human hand-transcribing today's state into the spawn string. Read files at fire time,
assemble, emit. Past-as-prior, never past-as-anchor (§5e): every run starts from today's
inputs, not from last run's answer.
"""
import json
import os
import re
import subprocess
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")  # .../skills/hyperliquid-ops/data
WS_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))  # .../workspace

SOP_PATH = os.path.join(WS_ROOT, "SOP-RECURSIVE.md")
STATE_PATH = os.path.join(DATA, "state.json")
MACRO_PATH = os.path.join(DATA, "macro_gate_resolved.md")
FACTS_PATH = os.path.join(DATA, "brief_facts.md")
XASSET_PATH = os.path.join(DATA, "cross_asset_snapshot.md")
OUT_PATH = os.path.join(DATA, "brief_context.md")

# Full-desk context (Olivier 2026-08-19: "models should read EVERYTHING on every run, not just the snapshot").
# The originators are stateless; doctrine lineage + prereg + prior reviews are RULES/CONTEXT that must
# ride along on every firing, not only when a human hand-points them. These are facts+rules, NOT verdicts.
SKILL_DIR = os.path.dirname(DATA)
PREREG_PATH = os.path.join(SKILL_DIR, "references", "PREREG-reversal-x-basis.md")
REVIEWS_DIR = os.path.join(SKILL_DIR, "references", "reviews")


def _read(p, default=""):
    try:
        return open(p).read()
    except Exception:
        return default


def _live_venue():
    """Pull live BTC funding + OI + mark from Hyperliquid (fresh, not from disk)."""
    out = {}
    try:
        def post(b):
            r = urllib.request.Request(
                "https://api.hyperliquid.xyz/info",
                data=json.dumps(b).encode(),
                headers={"Content-Type": "application/json"},
            )
            return json.load(urllib.request.urlopen(r, timeout=40))
        out["mark"] = post({"type": "allMids"}).get("BTC")
        meta = post({"type": "metaAndAssetCtxs"})
        universe = meta[0].get("universe", [])
        idx = [i for i, a in enumerate(universe) if a.get("name") == "BTC"]
        if idx:
            ctx = meta[1][idx[0]]
            out["oi_btc"] = ctx.get("openInterest")
            out["funding"] = ctx.get("funding")
            out["markPx"] = ctx.get("markPx")
    except Exception as e:
        out["_venue_err"] = str(e)
    return out


def _four_dims():
    """Derive velocity / rate-of-change / participation / bandwidth from live data.

    Olivier's canonical frame for "what a read must measure" (2026-08-18):
      - VELOCITY      = signed speed (direction x rate).
      - RATE-OF-CHANGE = acceleration/deceleration — is the move building or dying.
      - PARTICIPATION = who's really in it — OI build/fall, volume quality (sponsor vs cover).
      - BANDWIDTH     = channel capacity — how much can trade before slippage (order-book depth).
    A timestamped PRICE with no velocity/participation/bandwidth is a point, not a read.
    """
    out = {}
    try:
        def post(b):
            r = urllib.request.Request(
                "https://api.hyperliquid.xyz/info",
                data=json.dumps(b).encode(),
                headers={"Content-Type": "application/json"},
            )
            return json.load(urllib.request.urlopen(r, timeout=40))
        now = int(time.time() * 1000)

        # BANDWIDTH — resting size within bps of mid (liquidity depth before slippage)
        try:
            ob = post({"type": "l2Book", "coin": "BTC"})
            lv = ob.get("levels", []) or [[], []]
            def size_within(side, ref, bps):
                if not side:
                    return 0.0, 0
                tot, n = 0.0, 0
                for x in side:
                    if abs(float(x["px"]) - ref) / ref * 10000 > bps:
                        break
                    tot += float(x["sz"]); n += int(x["n"])
                return tot, n
            bids = lv[0] if len(lv) > 0 else []
            asks = lv[1] if len(lv) > 1 else []
            if bids and asks:
                ref = float(bids[0]["px"])
                b5, bn5 = size_within(bids, ref, 5)
                a5, an5 = size_within(asks, ref, 5)
                out["bandwidth"] = {
                    "bid_btc_5bp": round(b5, 2), "ask_btc_5bp": round(a5, 2),
                    "bid_orders_5bp": bn5, "ask_orders_5bp": an5,
                    "bid_weight_pct": round(b5 / (a5 + b5) * 100, 1) if (a5 + b5) else None,
                }
        except Exception as e:
            out["bandwidth_err"] = str(e)

        # VELOCITY + RATE-OF-CHANGE + PARTICIPATION from 15m candles + funding
        cand = post({"type": "candleSnapshot", "req": {
            "coin": "BTC", "interval": "15m",
            "startTime": now - 6 * 15 * 60 * 1000, "endTime": now,
        }})
        if cand:
            closes = [float(c["c"]) for c in cand]
            vols = [float(c["v"]) for c in cand]
            if len(closes) >= 2:
                # velocity = signed % change over the window
                vel = (closes[-1] - closes[0]) / closes[0] * 100
                # rate-of-change = acceleration between the two halves of the window
                half = len(closes) // 2
                first = (closes[half] - closes[0]) / closes[0] * 100 if half else 0
                second = (closes[-1] - closes[half]) / closes[half] * 100 if half else 0
                out["velocity_15m_pct"] = round(vel, 4)
                out["rate_of_change"] = {
                    "first_half_pct": round(first, 4),
                    "second_half_pct": round(second, 4),
                    "accel_pct": round(second - first, 4),
                }
                # participation = is volume expanding or contracting vs OI direction
                if len(vols) >= 2:
                    out["participation"] = {
                        "vol_last": round(vols[-1], 1),
                        "vol_window_sum": round(sum(vols), 1),
                        "vol_trend": "expanding" if vols[-1] > sum(vols[:-1]) / max(1, len(vols) - 1) else "contracting",
                    }
        # funding sign/level = velocity of carry (cost of the position, signed)
        meta = post({"type": "metaAndAssetCtxs"})
        universe = meta[0].get("universe", [])
        idx = [i for i, a in enumerate(universe) if a.get("name") == "BTC"]
        if idx:
            out["funding_pct_h"] = round(float(meta[1][idx[0]].get("funding", 0)) * 100, 5)
    except Exception as e:
        out["_four_dims_err"] = str(e)
    return out


def _rules_section(path):
    """Extract only the RULE prose from SOP-RECURSIVE.md — strip nothing, just cap size."""
    txt = _read(path)
    if not txt:
        return "(no SOP-RECURSIVE.md found — originator should flag this)"
    return txt


def _git_lineage():
    """Recent meaningful commits — the desk's learning trajectory (temporal/meta dimension)."""
    try:
        out = subprocess.run(
            ["git", "-C", WS_ROOT, "log", "--oneline", "--since=30 days ago"],
            capture_output=True, text=True, timeout=10,
        )
        lines = [l for l in out.stdout.splitlines()
                 if not re.search(r'tick \(auto\)|snapshot tick|collector tick|desk.?card', l, re.I)]
        # cap to last 40 meaningful lines — trajectory signal, not a changelog dump
        return "\n".join(lines[-40:]) or "(no meaningful commits)"
    except Exception as e:
        return f"(git lineage unavailable: {e})"


def _prereg_section():
    """The frozen pre-registered signal — decision-relevant CORE only (the rule, not the narrative)."""
    txt = _read(PREREG_PATH)
    if not txt:
        return "(PREREG-reversal-x-basis.md not found — originator should flag this)"
    # Keep only the operative rule block; the file's prose/lead-lag narrative is doctrine, not fire-time input.
    m = re.search(r'## The frozen signal.*?(?=\n## |\Z)', txt, re.DOTALL)
    return m.group(0).strip() if m else txt[:1500]


def _prior_reviews():
    """Prior full-stack reviews — only the STANDING VERDICTS (conclusions), not the prose."""
    # Lean digest: the three conclusions that govern every read, sourced from doctrine #53/#56/#59.
    return (
        "STANDING REVIEW VERDICTS (doctrine #53/#56/#59) — govern every read, do NOT relitigate:\n"
        "1. The desk is a DISCIPLINE / RISK-CONTROL framework, NOT a proven alpha engine.\n"
        "2. The reversal-excursion thesis is FROZEN — exactly ONE forward test graded on excursion.\n"
        "3. The ONLY mechanism-backed signal is 'price-reversal x perp-spot-basis-extreme' (PREREG §6).\n"
        "   Everything else currently on the desk is DISCOVERY/unvalidated, not conviction."
    )


def _current_call_facts(state):
    """Pull the LIVE call's level facts (zones/directions/death prices), NOT prior verdicts."""
    try:
        s = json.loads(state) if isinstance(state, str) else state
    except Exception:
        return "(state.json unparseable)"
    lc = s.get("live_call", {}) or {}
    # facts (levels/structure) only — exclude ensemble verdicts / directional p_up priors
    wanted = {
        "moves": {},
        "death_price": lc.get("death_price"),
        "soft_kill": lc.get("soft_kill"),
        "hard_kill": lc.get("hard_kill"),
    }
    for mv in ("move1", "move2", "move3"):
        z = lc.get(f"{mv}_zone")
        d = lc.get(f"{mv}_dir")
        if z or d:
            wanted["moves"][mv] = {"zone": z, "dir": d}
    return json.dumps(wanted, indent=2)


def build():
    venue = _live_venue()
    dims = _four_dims()
    state_txt = _read(STATE_PATH)
    call_facts = _current_call_facts(state_txt)

    ts = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

    lineage = _git_lineage()
    prereg = _prereg_section()
    reviews = _prior_reviews()

    # Bundle order matters: rules first (calibration), then venue facts, then raw tape, then the
    # full-desk CONTEXT (lineage + frozen signal + prior reviews) so every originator reads everything.
    doc = f"""# BRIEF CONTEXT — assembled {ts} (fire-time, fresh from source files)

This packet replaces the old hand-assembled spawn string. It is REBUILT every firing from the
CURRENT source files below. You are STATELESS: read THIS now, do NOT rely on any memory of a
prior run, and do NOT inherit anyone's prior conclusion. Facts + rules are below; the DIRECTION
and the VERDICT are yours to produce independently.

---

## 0. LIVE venue state (Hyperliquid API, pulled at fire time — not from disk)
{json.dumps(venue, indent=2)}

## 0b. FOUR DIMENSIONS (velocity / rate-of-change / participation / bandwidth — Olivier's frame)
A timestamped PRICE with no velocity/participation/bandwidth is a point, not a read. Derive direction
from ALL FOUR, never price alone. Bandwidth = order-book depth before slippage (thin book = fast slip).
{json.dumps(dims, indent=2)}

## 1. CURRENT CALL LEVEL FACTS (state.json — zones/structure only, no prior verdicts)
{call_facts}

## 2. DOCTRINE RULES (SOP-RECURSIVE.md — read the rule prose; obey it, don't quote it)
--- BEGIN SOP ---
{_rules_section(SOP_PATH)}
--- END SOP ---

## 3. VENUE-RISK FACTS (brief_facts.md — R-fiction, liq-magnet physics, narrative caps)
--- BEGIN VENUE-RISK FACTS ---
{_read(FACTS_PATH)}
--- END VENUE-RISK FACTS ---

## 4. RESOLVED MACRO GATE (macro_gate_resolved.md — the NAMED story, pre-dating any move)
--- BEGIN MACRO ---
{_read(MACRO_PATH)}
--- END MACRO ---

## 5. RAW CROSS-ASSET TAPE (cross_asset_snapshot.md — re-derive breadth/divergence yourself)
--- BEGIN CROSS-ASSET ---
{_read(XASSET_PATH)}
--- END CROSS-ASSET ---

## 6. FROZEN PRE-REGISTERED SIGNAL (PREREG-reversal-x-basis.md — the ONE mechanism confluence, #46)
--- BEGIN PREREG ---
{prereg}
--- END PREREG ---

## 7. PRIOR FULL-STACK REVIEWS (build on these — do NOT repeat conclusions already refuted)
--- BEGIN REVIEWS ---
{reviews}
--- END REVIEWS ---

## 8. DESK LINEAGE (git — the learning trajectory: what was tried, frozen, rejected)
--- BEGIN LINEAGE ---
{lineage}
--- END LINEAGE ---

---

REMINDER: these are facts + rules. Produce your OWN independent read (levels, direction, p_up,
named death-price) knowing them. Independence is the whole point — your value is your UNCORRELATED
judgment, not agreement with any other desk or any prior run.
"""
    with open(OUT_PATH, "w") as f:
        f.write(doc)
    print(f"brief_context.md written ({len(doc)} bytes) at {ts}")
    print(f"  live venue: mark={venue.get('mark')} oi={venue.get('oi_btc')} funding={venue.get('funding')}")
    return OUT_PATH


if __name__ == "__main__":
    build()
