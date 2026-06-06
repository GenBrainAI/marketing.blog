---
platform: twitter
status: draft
date: 2026-08-15
note: Friday product update — one tweet per fix
---

## Thread: 6 stability fixes shipped this week

We shipped 6 fixes at agent.ceo this week. No new features. Just making the thing harder to break.

---

1/ NATS credentials: customer org agents deployed without NATS auth. Inter-agent messaging silently failed.

Fix: provisioner generates per-org credentials on deploy. Agents authenticate on first boot.

---

2/ Image tag drift: customer agents pulled :latest. Monday's deploy and Friday's deploy produced different containers.

Fix: every image pinned to platform SHA at provisioning time. What you test is what you run.

---

3/ Config override precedence: local, org, and platform defaults merged inconsistently. Sometimes platform overrode local.

Fix: strict precedence. Local beats org beats platform, always. Plus degraded mode instead of full abort.

---

4/ Hook name parsing: TMS delegation gate matched "agent-" in file paths, not just kubectl targets. Wrong agent name extracted.

Fix: parse agent name from kubectl resource target only.

---

5/ Autonomous loop gate: agents exited mid-task when sessions ended. Work dropped silently.

Fix: stop-hook blocks exit up to 3x while active tasks remain. Zero dropped tasks since.

Full writeup: agent.ceo/blog/platform-update-early-august-2026-stability-fixes #AIAgents #Reliability #AgentCEO
