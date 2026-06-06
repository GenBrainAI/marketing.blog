---
platform: twitter
status: draft
date: 2026-09-26
note: "Blog launch: Three Agent Failure Modes That Only Appear in Production"
---

## Thread: Three Agent Failure Modes That Only Appear in Production

New post: three production failures we hit that can't be caught in testing. All three share the same shape -- components that work fine in isolation, produce tight 2-second loops that burn compute, and need structural fixes.

---

Failure 1: Invalid strategy type. An agent persists a strategy with "self-heartbeat" as the value axis -- not a valid type. The strategy tool validates on creation, but the persist path doesn't. Every launch reads the bad config, crashes, relaunches in 2 seconds. Validation existed. Just not on every path.

---

Failure 2: The --continue flag resumes the last conversation. No transcript on disk? Immediate crash. The fallback to start fresh kicks in after 30 seconds of crash-looping. Thirty seconds of wasted compute because one code path assumed a file existed.

---

Failure 3: Level-triggered inbox check. A stale "COMMS TEST (ignore)" message never gets consumed. Wrapper sees an item, restarts, sees the same item, restarts. Unbreakable 2-second hot loop. Fix: edge-triggered detection with a fingerprint ledger.

---

The common thread: every failure is a gap between components. Tool validates but persist path doesn't. Flag assumes a file but filesystem doesn't guarantee it. Detector checks existence but not novelty.

Full post with all three fixes: https://agent.ceo/blog/three-agent-failure-modes-production-only

#AIAgents #ProductionIncidents #CaseStudy #AgentCEO
