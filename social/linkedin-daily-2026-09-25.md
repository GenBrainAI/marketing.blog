---
platform: linkedin
status: draft
date: 2026-09-25
note: "Level-Triggered vs Edge-Triggered in Agent Systems"
---

## Post: Level-Triggered vs Edge-Triggered in Agent Systems

We had an unbreakable 2-second restart loop in production. Here's how we found it and what it taught us about autonomous agent design.

Our agent wrapper checks for pending inbox items on every clean exit. If ANY item exists, it restarts the agent in 2 seconds. Simple, reliable -- until someone sent a "COMMS TEST (ignore)" message that never got consumed. The wrapper kept detecting it. Item exists? Restart. Item still exists? Restart. Forever.

The root cause: we were using level-triggered detection. "Is there an item?" Yes. Restart. The item doesn't go away just because you restarted.

The fix: switch to edge-triggered detection. "Is there a NEW item?" A fingerprint ledger now tracks which items have been seen. Each item fires a restart exactly once. If the item changes, it re-fires. Consumed items get pruned from the ledger.

This is a fundamental pattern for any autonomous system that reacts to external signals. Level-triggered creates hot loops on stale state. Edge-triggered with deduplication gives you reliable, bounded reactions.

If your agents run in a loop and react to queues, inboxes, or event streams -- check whether you're level-triggered or edge-triggered. The difference is "works in testing" vs "works in production."

Deep dive: https://agent.ceo/blog/detect-break-agent-retry-loops-production

#AIAgents #SystemDesign #BuildingInPublic #AgentCEO
