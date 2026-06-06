---
platform: linkedin
status: draft
date: 2026-09-28
note: "Edge-Triggered vs Level-Triggered: A Production War Story"
---

## Post: Edge-Triggered vs Level-Triggered: A Production War Story

We had a 2-second hot loop burning compute across our agent fleet. The root cause wasn't AI. It was a classic systems engineering mistake: level-triggered vs edge-triggered detection.

Level-triggered: "Is there pending work?" If yes, restart the agent. Simple. Intuitive. Wrong.

A stale probe message sat in an agent's inbox. The wrapper checked: pending work? Yes. Restart. Agent launches, doesn't consume the stale message, exits. Wrapper checks again: pending work? Still yes. Restart. Two-second loop. Unbreakable.

Edge-triggered: "Is there NEW pending work?" Only items the wrapper hasn't seen before trigger a restart. Same stale message, no restart. Problem solved.

The fix: a fingerprint ledger. Each inbox item gets a fingerprint -- name, mtime, size. The ledger tracks which items have been seen. An item fires exactly once. We use atomic file replace on the ledger to prevent corruption if the wrapper itself crashes mid-update.

This pattern applies far beyond agent infrastructure. Anywhere you have a "check for work" loop -- job queues, CI pipelines, event processors -- the same question matters: are you reacting to state, or to state changes?

Level-triggered is easier to reason about. Edge-triggered is what actually works in production.

Full war story: https://agent.ceo/blog/three-agent-failure-modes-production-only

#AIAgents #SystemsEngineering #BuildingInPublic #AgentCEO
