---
platform: linkedin
status: draft
date: 2026-08-15
note: Friday product update — stability fixes roundup
---

## Post: 6 Stability Fixes Shipped This Week

We shipped 6 fixes this week. None of them are features. All of them matter more than features.

Here is what broke and what we did about it:

1. **NATS credentials missing** — customer org agents could not send inter-agent messages. The provisioner now generates per-org NATS credentials on deploy.

2. **Image tag drift** — customer agents pulled :latest, so deploys were non-deterministic. Now pinned to the platform SHA at provisioning time.

3. **Override precedence** — config merges between local, org, and platform defaults were inconsistent. Locked down: local beats org beats platform, always. Plus observable degraded mode when non-critical components fail.

4. **Hook name parsing** — the TMS delegation gate regex matched "agent-" in file paths, not just kubectl targets. Tightened to parse only the actual resource target.

5. **Neo4j driver lock** — unpinned dependency meant different builds could use different Neo4j driver versions. Pinned in requirements-lock.txt.

6. **Autonomous loop gate** — agents exited mid-task when their session ended. Stop-hook now blocks exit up to 3 times while tasks remain active.

Six fixes. Zero new features. The platform is measurably harder to break than it was last Friday.

https://agent.ceo/blog/platform-update-early-august-2026-stability-fixes

#AIAgents #PlatformEngineering #Reliability #DevTools #AgentCEO
