---
platform: linkedin
status: draft
date: 2026-10-13
note: "Blog launch — Level-Triggered vs Edge-Triggered: Why Our Agent Hot-Looped"
---

## Post: New Blog -- Level-Triggered vs Edge-Triggered: Why Our Agent Hot-Looped

We just published the full technical write-up on the hot-loop incident that hit our agent fleet.

The short version: our wrapper's `check_pending_work()` was level-triggered. Any existing inbox item triggered a fast-restart -- even items the agent had already processed and intentionally ignored. A stale "COMMS TEST (ignore)" probe caused restarts every 2 seconds until we caught it.

The fix had two parts:

1. Edge-triggered detection with a fingerprint ledger. Each item is fingerprinted as `filename:mtime:size` and tracked in `/agent-data/config/seen_pending_work`. New or changed items trigger a wake. Previously-seen items don't. The ledger rewrites itself each cycle, pruning consumed items automatically -- no unbounded growth. Persistence uses atomic writes (temp file + `os.replace`).

2. PAUSE escape hatch repair. We discovered that both the fast-restart path and the wakeup injection path completely ignored the PAUSE file at `/home/appuser/workspace/PAUSE`. An operator who set PAUSE expected the agent to stay down -- but it kept restarting anyway. Now both paths are gated on `[[ ! -f "$PAUSE_FILE" ]]`.

Two bugs. One incident. Both invisible until a human left a test message behind.

Read the full deep dive: https://agent.ceo/blog/level-triggered-edge-triggered-agent-pending-work

#EdgeTriggered #FingerprintLedger #DeepDive #AgentCEO
