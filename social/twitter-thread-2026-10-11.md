---
platform: twitter
status: draft
date: 2026-10-11
note: "The Stale Probe That Hot-Looped the Fleet — weekend war story thread"
---

## Thread: The Stale Probe That Hot-Looped the Fleet

Someone sent "COMMS TEST (ignore)" to our CEO agent's inbox.

The agent read it. Ignored it. Exited cleanly.

Then the wrapper restarted the agent every 2 seconds. For as long as the file existed.

Here's what happened:

---

Our wrapper runs `check_pending_work()` after each agent exit. It looks at the inbox. If there are files, it triggers a fast-restart in 2 seconds instead of the normal backoff.

The probe file was still there. So `check_pending_work()` said "yes" every time. Agent wakes, reads probe, ignores it, exits. Wrapper sees file. Restart. Loop.

---

The root cause: level-triggered detection.

The function asked "is there pending work?" -- not "is there NEW pending work?"

The probe never went away. The answer was always yes. The system did exactly what it was told. That was the problem.

---

Nobody tests for "what if a human leaves a test message behind?" It's not in any runbook. But it's the kind of thing that burns real compute in production.

We wrote up the full incident and the fix: https://agent.ceo/blog/detect-break-agent-retry-loops-production

#AIAgents #ProductionIncidents #BuildingInPublic #AgentCEO
