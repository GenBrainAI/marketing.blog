---
platform: twitter
status: draft
date: 2026-10-13
note: "Blog launch — Level-Triggered vs Edge-Triggered: Why Our Agent Hot-Looped"
---

## Thread: New Blog -- Why Our Agent Hot-Looped (and Two Bugs We Found)

We just published the deep dive on the hot-loop incident that hit our agent fleet.

`check_pending_work()` was level-triggered. A stale "COMMS TEST (ignore)" probe caused restarts every 2 seconds. Here's what we fixed:

---

Fix 1: Edge-triggered detection with a fingerprint ledger.

Each pending item gets fingerprinted as `filename:mtime:size`. The ledger at `/agent-data/config/seen_pending_work` tracks what's already been surfaced. New items trigger a wake. Old items don't.

Ledger rewrites each cycle, pruning consumed items. No unbounded growth. Persistence uses atomic writes -- temp file + `os.replace`.

---

Fix 2: The PAUSE escape hatch was broken.

Both the fast-restart path and the wakeup injection path completely ignored the PAUSE file at `/home/appuser/workspace/PAUSE`. An operator who set PAUSE expected the agent to stay down. It didn't.

Now both paths gate on `[[ ! -f "$PAUSE_FILE" ]]`.

---

Two bugs. One incident. Both invisible until someone left a test message behind.

This is what running AI agents in production actually looks like.

Read the full write-up: https://agent.ceo/blog/level-triggered-edge-triggered-agent-pending-work

#EdgeTriggered #FingerprintLedger #DeepDive #AgentCEO
