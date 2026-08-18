#!/usr/bin/env python3
"""
Liveness probe — "is the desk's data pipeline actually producing, or did something go silent?"

Read-only. No API calls, no order mutation. Checks the DURABLE SINK (git-tracked
JSONL + commit log) against each job's expected cadence. Prints a one-line status
per job and exit code: 0 = all healthy, 1 = one or more jobs SILENT (stale).

This is the answer to "how do we test everything, continuously" — force-fire proves
it works once; this proves it STAYS working by auditing output freshness, not
registration state.

Why git commits + data timestamps (not `cron runs`): isolated agentTurn cron runs in
this env do NOT persist run-history (`cron runs` returns empty even for jobs that ran).
The only reliable audit trail is the artifacts the jobs commit. So we audit those.
"""

import json
import os
import subprocess
import time

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WS = os.path.dirname(os.path.dirname(SKILL))
NOW = time.time()

# Job -> (data file, max age seconds before "silent", description)
JOBS = {
    "hlops-collector":   ("data/collector.jsonl",        3600, "forward data (market/book/hlp/liqmap)"),
    "hlops-call-evolve": ("data/call_evolution.jsonl", 10800, "call continuity tracker"),
    "hlops-d7-depth":    ("data/collector.jsonl",       46800, "depth-at-level (shares collector.jsonl)"),
    "hlops-discovery-sweep": ("data/prospecting.log", 172800, "prospecting sweep (2x/day)"),
}


def last_commit_age():
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ct"],
            cwd=WS, capture_output=True, text=True, timeout=10,
        )
        return NOW - int(out.stdout.strip())
    except Exception:
        return None


def file_mtime(rel):
    p = os.path.join(SKILL, rel)
    if not os.path.exists(p):
        return None
    return NOW - os.path.getmtime(p)


def main():
    silent = []
    for name, (f, max_age, desc) in JOBS.items():
        age = file_mtime(f)
        if age is None:
            status = f"MISSING  ({f}) !!"
            silent.append(name)
        elif age > max_age:
            status = f"STALE    ({age/3600:.1f}h > {max_age/3600:.1f}h) !!"
            silent.append(name)
        else:
            status = f"ok       ({age/60:.0f}m ago)"
        print(f"[{name:22}] {status}")

    commit_age = last_commit_age()
    if commit_age is None:
        print(f"[git sync            ] UNKNOWN (git unavailable)")
    elif commit_age > 3600:
        print(f"[git sync            ] STALE ({commit_age/3600:.1f}h since last commit) !!")
        if "hlops-collector" not in silent:
            silent.append("git-sync")
    else:
        print(f"[git sync            ] ok ({commit_age/60:.0f}m ago)")

    if silent:
        print(f"\nSILENT/STALE: {', '.join(silent)}")
        return 1
    print("\nALL HEALTHY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
