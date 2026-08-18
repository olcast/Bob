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


def _rules_section(path):
    """Extract only the RULE prose from SOP-RECURSIVE.md — strip nothing, just cap size."""
    txt = _read(path)
    if not txt:
        return "(no SOP-RECURSIVE.md found — originator should flag this)"
    return txt


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
    state_txt = _read(STATE_PATH)
    call_facts = _current_call_facts(state_txt)

    ts = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

    # Bundle order matters: rules first (calibration), then venue facts, then raw tape.
    doc = f"""# BRIEF CONTEXT — assembled {ts} (fire-time, fresh from source files)

This packet replaces the old hand-assembled spawn string. It is REBUILT every firing from the
CURRENT source files below. You are STATELESS: read THIS now, do NOT rely on any memory of a
prior run, and do NOT inherit anyone's prior conclusion. Facts + rules are below; the DIRECTION
and the VERDICT are yours to produce independently.

---

## 0. LIVE venue state (Hyperliquid API, pulled at fire time — not from disk)
{json.dumps(venue, indent=2)}

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
