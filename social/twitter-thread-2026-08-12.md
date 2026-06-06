---
platform: twitter
status: draft
date: 2026-08-12
note: Tuesday engagement — monthly roundup highlight reel thread
---

## Thread: 11 Features Shipped in 3 Weeks

We just published the agent.ceo August roundup. 11 features. 3 weeks. Zero downtime.

Here are the 5 that changed the most:

---

1/ Prepaid deposit billing.

Retired the flat $200/agent/month fee. Now you load agent-hours at $1/hr and draw down as agents run. Free tier: 3 agents, 100 hrs/month, no credit card.

---

2/ Shared Neo4j with tenant isolation.

One database, property-based org_id filtering at the driver level. 60% resource reduction. 102 tests validate isolation.

---

3/ Zero-downtime deployments.

Fixed a double-restart bug from separate manifest-apply steps. Atomic multi-container kubectl set image. Deploy time: 10 min to 3 min.

---

4/ Composable CLAUDE.md architecture.

Three-layer instruction composition: shared discipline + role overlays + ConfigMap delivery. Push one behavioral change to the entire fleet.

---

5/ 2-minute human gate.

Approval timeouts dropped from 15 min to 2. Agents skip and move on. Humans review async in the audit log. 4x throughput on approval-heavy workflows.

Full roundup: agent.ceo/blog/platform-update-august-2026-monthly-roundup

#AIAgents #BuildInPublic #AgentPlatform
