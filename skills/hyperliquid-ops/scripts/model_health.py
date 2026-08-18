#!/usr/bin/env python3
"""
model_health.py — "always keep comms": is every model in the firing chain actually still
answering, right now? Whole-chain liveness, not just the primary.

Pings each provider with a 1-token call and reports ALIVE / DEAD with a reason.
Read-only, no key printing, reads credentials from openclaw.json (never hardcoded).

Why: DeepSeek credit runs out overnight; Qwen / Grok can hit their own limits too.
The fallback chain (DeepSeek -> Qwen -> Grok) only saves us if each hop ANSWERS when
called. This prober is the pre-firing gate: the crosscheck wrapper checks it and only
spawns originators that are ALIVE, so overnight degradation is CLEAN (2-model ensemble)
instead of a hard crash at 04:00.

Exit codes: 0 = all alive, 1 = some dead (print the dead list). JSON to stdout for the
wrapper to consume.

Usage:  python3 model_health.py          # human summary
        python3 model_health.py --json    # machine-readable {"alive":[..],"dead":[..]}
"""

import json
import os
import sys
import time
import urllib.request

CONFIG = "/root/.openclaw/openclaw.json"

# provider -> (display name, baseUrl, apiKey path in config)
PROVIDERS = [
    ("deepseek", "DeepSeek", "https://api.deepseek.com", ["models", "providers", "deepseek"]),
    ("qwen",     "Qwen",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
                 ["models", "providers", "qwen"]),
    ("grok",     "Grok",    "https://api.x.ai/v1", ["models", "providers", "xai"]),
]


def _cfg():
    return json.load(open(CONFIG))


def _models_for(cfg, path):
    try:
        node = cfg
        for k in path:
            node = node[k]
        return node
    except Exception:
        return {}


def _ping(base, key, model):
    """1-token completion. Returns (ok, detail)."""
    body = {
        "model": model,
        "messages": [{"role": "user", "content": "ok"}],
        "max_tokens": 1,
    }
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    try:
        r = urllib.request.urlopen(req, timeout=25)
        d = json.load(r)
        return True, "ok"
    except urllib.error.HTTPError as e:
        try:
            msg = json.load(e).get("error", {}).get("message", "") or e.reason
        except Exception:
            msg = e.reason
        code = e.code
        # classify the common fatal cases
        low = (msg or "").lower()
        if code == 429 or "rate limit" in low:
            return False, f"RATE-LIMITED ({code})"
        if "insufficient" in low or "balance" in low or "quota" in low or "billing" in low:
            return False, f"CREDIT/QUOTA ({code})"
        if "invalid" in low and ("key" in low or "api" in low):
            return False, f"INVALID KEY ({code})"
        return False, f"HTTP {code}: {msg[:80]}"
    except urllib.error.URLError as e:
        return False, f"NETWORK: {e.reason}"
    except Exception as e:
        return False, f"ERR: {e}"


def probe():
    cfg = _cfg()
    alive, dead = [], []
    # xAI key lives on disk (.xai_api_key), NOT in openclaw.json (held in sqlite xai:manual profile)
    xai_key_file = "/root/.openclaw/workspace/.xai_api_key"
    for key_name, disp, base, path in PROVIDERS:
        prov = _models_for(cfg, path)
        api_key = prov.get("apiKey")
        if not api_key and key_name == "grok" and os.path.exists(xai_key_file):
            api_key = open(xai_key_file).read().strip() or None
        if not api_key:
            dead.append({"name": disp, "reason": "NO KEY IN CONFIG"})
            continue
        # pick a flagship model id: provider's first registered model, or a hardcoded known id
        models = prov.get("models", [])
        model_id = models[0]["id"] if models and isinstance(models[0], dict) else None
        if not model_id:
            model_id = {
                "deepseek": "deepseek-v4-pro",
                "qwen": "qwen3.8-max",
                "grok": "grok-4.6",
            }.get(key_name)
        ok, detail = _ping(base, api_key, model_id)
        if ok:
            alive.append({"name": disp, "model": model_id})
        else:
            dead.append({"name": disp, "model": model_id, "reason": detail})
    return alive, dead


def main():
    alive, dead = probe()
    if "--json" in sys.argv or "--json" in os.environ.get("MH_JSON", ""):
        print(json.dumps({"alive": alive, "dead": dead, "ts": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())}))
    else:
        for a in alive:
            print(f"[{a['name']:8}] ALIVE  ({a['model']})")
        for d in dead:
            print(f"[{d['name']:8}] DEAD   ({d.get('model','?')}) — {d['reason']}")
        if dead:
            print(f"\nDEAD: {', '.join(d['name'] for d in dead)}")
    return 1 if dead else 0


if __name__ == "__main__":
    raise SystemExit(main())
