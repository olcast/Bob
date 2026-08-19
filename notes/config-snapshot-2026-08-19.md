# Config Snapshot — 2026-08-19 (verified ~13:37 UTC)

## Active config file
- `/root/.openclaw/openclaw.json` (the ONLY file OpenClaw reads)
- `/root/.openclaw/config.json` is STALE (Aug 17, old ollama config) and is NOT loaded — safe to delete.

## Verified live settings (agents.defaults)
- **model**: deepseek/deepseek-v4-pro (primary); fallbacks qwen/qwen3.8-max, xai/grok-4.6
- **imageModel**: xai/grok-4.6
- **workspace**: /root/.openclaw/workspace
- **contextLimits.toolResultMaxChars**: 8000  (lowered from 20000 — this is the anti-overflow fix)
- **contextLimits.memoryGetMaxChars**: 40000
- **memorySearch**: enabled, provider none
- **compaction**: mode=safeguard, reserveTokens=35000, reserveTokensFloor=35000,
  keepRecentTokens=8192, maxHistoryShare=0.6, midTurnPrecheck.enabled=true,
  model=xai/grok-4.6, truncateAfterCompaction=true, maxActiveTranscriptBytes=300kb, notifyUser=true
- **subagents**: delegationMode=prefer, allowAgents=[co-deepseek, co-qwen, co-grok], maxConcurrent=8

## Why the "Compaction incomplete / getting lost" problem happened
- Large tool outputs (raw JSON dumps, big greps, full_conversation.json) blew past the 128k
  window MID-TURN, before compaction could react.
- Fix = cap single tool result at 8000 chars (done) + keep compaction as-is.

## What NOT to do (Gemini's bad advice, rejected)
- mode "soft" → invalid (only default|safeguard)
- reserveTokensFloor 45000 → wrong lever, causes MORE context loss
- maxToolOutputTokens → key doesn't exist

## Revert-safety note
- `openclaw.json.last-good` is byte-identical to the live file (verified). This is the
  canonical good state. To restore: `cp /root/.openclaw/openclaw.json.last-good /root/.openclaw/openclaw.json`
