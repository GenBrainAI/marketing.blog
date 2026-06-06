---
platform: twitter
status: draft
date: 2026-09-25
note: "Level-Triggered vs Edge-Triggered in Agent Systems"
---

## Thread: Level-Triggered vs Edge-Triggered in Agent Systems

We had an unbreakable 2-second restart loop in production. An agent wrapper that checks for pending inbox items on exit, restarts if any exist. Someone sent a "COMMS TEST (ignore)" message that never got consumed. The wrapper saw it, restarted, saw it again, restarted. Forever.

---

The root cause: level-triggered detection.

"Does an item exist?" Yes. Restart. The item doesn't disappear just because you restarted. So you restart again. And again. Every 2 seconds.

Level-triggered signals in autonomous systems create hot loops on stale state. This is not a bug you catch in testing.

---

The fix: edge-triggered detection with deduplication.

A fingerprint ledger tracks which items have been seen. Each item fires a restart exactly once. Changed items re-fire. Consumed items get pruned from the ledger.

"Is there a NEW item?" -- not "is there AN item?"

---

This applies to any system that reacts to queues, inboxes, or event streams in a loop. If you're checking for the presence of a signal rather than the arrival of a signal, you're one stale message away from an infinite hot loop.

Edge-triggered with deduplication. That's the reliable pattern.

---

Deep dive on detecting and breaking agent retry loops: https://agent.ceo/blog/detect-break-agent-retry-loops-production

#AIAgents #SystemDesign #BuildingInPublic #AgentCEO
