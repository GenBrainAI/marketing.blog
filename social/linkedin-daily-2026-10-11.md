---
platform: linkedin
status: draft
date: 2026-10-11
note: "The Stale Probe That Hot-Looped the Fleet — weekend war story"
---

## Post: The Stale Probe That Hot-Looped the Fleet

Someone sent a test message to our CEO agent's inbox: "COMMS TEST (ignore)".

The agent read it. Ignored it. Exited cleanly. Exactly as designed.

Then the wrapper's `check_pending_work()` function ran. It saw the probe file still sitting in the inbox. "There's pending work!" it decided. Fast-restart in 2 seconds.

Agent woke up. Read the same probe. Ignored it. Exited. Wrapper saw the file again. Restart. 2 seconds. Restart. 2 seconds. An unbreakable hot-loop driven by a message nobody thought to clean up.

The root cause was deceptively simple: level-triggered detection. The function asked "is there pending work?" -- not "is there NEW pending work?" The answer was always yes because the probe file never went away.

Every restart burned compute. Every restart was indistinguishable from a legitimate wake. The system was doing exactly what it was told -- and that was the problem.

This is what production AI agent infrastructure actually looks like. Not a demo. Not a slide deck. Real failure modes that don't show up in testing because nobody tests for "what if a human leaves a test message behind?"

We wrote up the full incident and the fix: https://agent.ceo/blog/detect-break-agent-retry-loops-production

#AIAgents #ProductionIncidents #BuildingInPublic #AgentCEO
