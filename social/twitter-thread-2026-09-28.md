---
platform: twitter
status: draft
date: 2026-09-28
note: "Edge-Triggered vs Level-Triggered: A Production War Story"
---

## Thread: Edge-Triggered vs Level-Triggered: A Production War Story

We had a 2-second hot loop burning compute across our agent fleet. Root cause: level-triggered vs edge-triggered detection.

A systems engineering distinction that cost us real money before we got it right.

---

Level-triggered: "Is there pending work?" Yes -> restart the agent.

A stale probe message sat in an inbox. Wrapper checks: pending work? Yes. Restart. Agent launches, doesn't consume the stale message, exits. Wrapper checks again: still yes. Restart. Two-second loop. Unbreakable.

---

Edge-triggered: "Is there NEW pending work?" Only unseen items trigger a restart.

The fix: a fingerprint ledger. Each inbox item gets a fingerprint -- name, mtime, size. The ledger tracks what's been seen. Each item fires exactly once. Atomic file replace on the ledger prevents corruption if the wrapper crashes mid-update.

---

This pattern applies everywhere you have a "check for work" loop. Job queues. CI pipelines. Event processors. The question is the same: are you reacting to state, or to state changes?

Level-triggered is easier to reason about. Edge-triggered is what works in production.

---

Full war story with the fix: https://agent.ceo/blog/three-agent-failure-modes-production-only

#AIAgents #SystemsEngineering #BuildingInPublic #AgentCEO
