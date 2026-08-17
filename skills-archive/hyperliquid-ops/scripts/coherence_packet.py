#!/usr/bin/env python3
"""LEDGER-COHERENCE PACKET — builds the brief fed to a long-context model (Gemini 3 Pro, 1M-token
window) to check a new call against the FULL doctrine + ledger history, not just the last read.
Nobody currently re-reads the entire ledger (#000-#084 + all doctrine deltas + lessons.json) before
grading or logging a new call — this closes that gap. It is a coherence/memory check, not another
forecast: "does this call contradict something the desk already learned and wrote down?"

Usage:
  python3 coherence_packet.py call.json

Concatenates (read-only, no mutation):
  - references/ledger-live/LEDGER.md (the git-tracked live ledger, #085+)
  - references/ledger-live/*.md / *.txt (raw #000-#084 paste + annotated mirror)
  - SKILL.md's doctrine sections (this file IS the doctrine — v2.3 through latest delta)
  - data/lessons.json (candidate + promoted lessons)
  - data/doctrine.json (machine-readable doctrine state, if present)

Feed the packet's JSON to the coherence-checker model verbatim. It is expected to be large (ledger
history can run to hundreds of KB) — that is the point of choosing a 1M-context model for this job,
not a smaller one.
"""
import json, sys, argparse, os, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")

def load_json(path):
    try:
        return json.loads(open(path).read())
    except Exception as e:
        return {"error": f"could not load {path}: {e}"}

def read_text(path, max_chars=400_000):
    try:
        with open(path, errors="replace") as f:
            data = f.read()
        if len(data) > max_chars:
            data = data[:max_chars] + f"\n\n...[TRUNCATED at {max_chars} chars]..."
        return data
    except Exception as e:
        return f"[could not read {path}: {e}]"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("call_json")
    args = ap.parse_args()

    call = load_json(args.call_json)

    ledger_dir = os.path.join(ROOT, "references", "ledger-live")
    ledger_files = {}
    if os.path.isdir(ledger_dir):
        for f in sorted(glob.glob(os.path.join(ledger_dir, "*"))):
            if os.path.isfile(f):
                ledger_files[os.path.basename(f)] = read_text(f)

    skill_md = read_text(os.path.join(ROOT, "SKILL.md"), max_chars=250_000)
    lessons = load_json(os.path.join(ROOT, "data", "lessons.json"))
    doctrine_json_path = os.path.join(ROOT, "data", "doctrine.json")
    doctrine_state = load_json(doctrine_json_path) if os.path.exists(doctrine_json_path) else None

    packet = {
        "the_new_call": call,
        "full_doctrine_skill_md": skill_md,
        "ledger_files": ledger_files,
        "lessons_json": lessons,
        "doctrine_json_state": doctrine_state,
        "instructions": (
            "You have the desk's ENTIRE doctrine (SKILL.md) and ledger history (ledger_files) in context. "
            "Check the_new_call against all of it and answer concisely:\n"
            "1. Does this call CONTRADICT any binding doctrine rule (numbered rules in SKILL.md, e.g. the "
            "protective-flip ban #22, the death-price guard #25b, the two-scenarios-max rule #2)? Quote the "
            "specific rule number if so.\n"
            "2. Does this call repeat a PATTERN that was already tested and REJECTED/killed in the ledger "
            "(e.g. pain-radii clustering #24, DSR gate #8, persona-framed auditing #8)? Name the ledger entry "
            "or doctrine delta if so.\n"
            "3. Does this call ignore a LESSON already logged in lessons.json that applies here?\n"
            "4. Is this call consistent with the desk's own prior reads on this same coin/level within the "
            "last few ledger entries (continuity per doctrine's continuity rule), or does it silently "
            "contradict a very recent read without acknowledging the change?\n"
            "5. If everything checks out clean, say so plainly — 'no contradiction found' is the expected "
            "and correct answer most of the time, not a failure to find something.\n"
            "This is a coherence/memory check, not a forecast — do not offer your own p_up or price targets."
        ),
    }
    print(json.dumps(packet, default=str))

if __name__ == "__main__":
    main()
