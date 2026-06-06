---
platform: twitter
status: draft
date: 2026-10-12
note: "Level-Triggered vs Edge-Triggered — educational systems pattern thread"
---

## Thread: Level-Triggered vs Edge-Triggered Detection for Agent Loops

Your AI agent wrapper probably has a hot-loop bug and you don't know it yet.

The pattern that prevents it comes from hardware interrupt design. Two modes. One is wrong for agent work detection.

---

Level-triggered: fires as long as the signal is HIGH.

For agents: "Is there pending work?" If the item is never consumed, this returns true on every check. Every check triggers a restart. You get an infinite loop from a single stale file.

---

Edge-triggered: fires on the TRANSITION from LOW to HIGH.

For agents: "Is there NEW work?" Fires once per item, then goes quiet. Stale items don't re-trigger. This is what you want.

---

Our fix: a persistent fingerprint ledger at `/agent-data/config/seen_pending_work`.

Each item is fingerprinted as `filename:mtime:size`. Only items with fingerprints NOT in the ledger trigger a wake. The ledger rewrites each cycle, pruning entries for consumed items. No unbounded growth.

---

Simple pattern. Prevents an entire class of agent hot-loop failures. We learned it the hard way.

Full write-up on our outer loop architecture: https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#SystemsEngineering #EdgeTriggered #AIAgents #AgentCEO
