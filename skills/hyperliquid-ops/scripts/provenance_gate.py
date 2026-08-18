#!/usr/bin/env python3
"""PROVENANCE GATE — the incentive design's front line (OLIVIER, 2026-08-18).

Stops the R7 failure class (empirical base rates quoted without n/source/event) BEFORE a
call goes live, instead of catching it after the fact. Reads STRUCTURED fields, not regex.

A call that claims a base rate must carry a `provenance` object mapping each claim to
{rate, n, source} — otherwise it is FLAGGED. A call may also carry a `probabilities` object
whose values must sum to ~1.0 with a named residual.

Non-fatal: the flag travels with the call into grading (see falsifiability_score.py).

Usage:
  provenance_gate.py <call.json>            # file
  cat call.json | provenance_gate.py -      # stdin
Exit 0 = pass, 1 = flagged (informational — call still records)."""
import json, sys

# Statistic names that MUST be backed by {rate,n,source} if quoted anywhere.
backed = []

def gate(call):
    findings = []
    prov = call.get("provenance", {})
    # 1. Every entry in `provenance` must have {rate,n,source}; a demoted/retired one
    #    must carry status != "active" and must NOT be used as conviction.
    for key, val in prov.items():
        if not isinstance(val, dict):
            findings.append(f"provenance[{key}] is not an object — needs {{rate,n,source}}.")
            continue
        if val.get("status") in ("DEMOTED", "retired", "disowned"):
            # demoted figure present is fine ONLY if explicitly marked non-use. Accept a
            # boolean `use:false` OR a string that STARTS with 'none'. Reject only a real use.
            use = val.get("use")
            used = False
            if use is False or use is None:
                used = False
            elif isinstance(use, str):
                used = not use.strip().lower().startswith("none")
            else:
                used = True
            if used:
                findings.append(f"demoted figure '{key}' is being USED — doctrine #53 violation.")
            continue
        need = {"rate", "n", "source"}
        missing = [k for k in need if k not in val or val[k] in (None, "")]
        if missing:
            findings.append(f"provenance[{key}] missing {missing} — empirical claim without n/source (R7).")

    # 2. Probabilities, if present as a structured object, must sum to ~1.0 with a residual named.
    probs = call.get("probabilities")
    if isinstance(probs, dict) and probs:
        tot = sum(float(v) for v in probs.values() if isinstance(v, (int, float)))
        if abs(tot - 1.0) > 0.02:
            findings.append(f"probabilities sum to {tot:.2f}, not 1.0 (derived-prob rule).")
        residual_named = any("resid" in k.lower() or "chop" in k.lower() for k in probs)
        if not residual_named:
            findings.append("probabilities has no named residual/chop state (C4 class: 45+30+15=90%).")
    elif isinstance(probs, dict) and not probs:
        pass  # empty is fine — no claims
    else:
        p_up = call.get("p_up")
        if isinstance(p_up, (int, float)) and not prov:
            findings.append("p_up present but no provenance object backs any base rate (R7).")

    # 3. Known-misattribution hard-block: if a call QUOTES 66% as leg-2 or 85% as reclaim
    #    WITHOUT a provenance correction, block. (Rebuilt calls annotate these under `provenance`.)
    thesis = (call.get("thesis", "") + " " + call.get("note", "")).lower()
    # 3b. Hard-blocks only fire if the claim is NOT already corrected in `provenance`.
    leg2_fixed = isinstance(prov.get("leg2_reverse", {}), dict) and abs(float(prov["leg2_reverse"].get("rate", 0)) - 0.55) < 0.01
    sweep_fixed = isinstance(prov.get("sweep_reclaim_85", {}), dict) and prov["sweep_reclaim_85"].get("status") in ("DEMOTED", "retired", "disowned")
    if "leg-2" in thesis and "66%" in thesis and not leg2_fixed:
        findings.append("KNOWN MISATTRIBUTION: leg-2 quoted at 66%; desk measures 55% (n=191, repro #48). doctrine R7.")
    if "85%" in thesis and ("reclaim" in thesis or "sweep" in thesis) and not sweep_fixed:
        findings.append("KNOWN DISOWNED: '~85% reclaim' was demoted (doctrine #53); do not use as conviction.")

    return (len(findings) == 0, findings)

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "-"
    raw = (sys.stdin.read() if src == "-" else open(src).read()).strip()
    try:
        call = json.loads(raw)
    except Exception as e:
        print(f"gate: could not parse JSON ({e})"); sys.exit(2)
    ok, findings = gate(call)
    if ok:
        print("PROVENANCE GATE: PASS"); sys.exit(0)
    print(f"PROVENANCE GATE: FLAGGED ({len(findings)} finding(s))")
    for f in findings:
        print(f"  - {f}")
    sys.exit(1)

if __name__ == "__main__":
    main()
