---
platform: twitter
status: draft
date: 2026-10-05
note: "The Silent Drift Problem in Multi-Tenant Agent Platforms"
---

## Thread: The Silent Drift Problem in Multi-Tenant Agent Platforms

Multi-tenant agent platform problem we hit:

Your core fleet gets updated every CI run. Customer-org agents get provisioned once and forgotten. They drift behind silently. No errors. No alerts. Just stale images missing bug fixes.

---

We found out when customer-org users reported MCP server timeouts. The MCP code was fine -- handshake takes ~1.2s even with unreachable NATS.

The customer pods were running a stale image that didn't include commit 1494f5107 (dual-scope MCP fix). Our core fleet had it. Their pods didn't.

---

The failure mode: CI keeps the core fleet current. Tenant deployments have no automated path to pick up new images. `:latest` doesn't re-pull unless the pod restarts. The pods don't restart unless something forces them to.

Silent drift. The worst kind of bug -- the kind where nobody gets an alert.

---

The fix: pin customer deployments to the same immutable image SHA the core fleet runs. Not `:latest`. When the core fleet advances, tenant agents advance with it.

Full implementation writeup dropping tomorrow.

https://agent.ceo/blog/three-agent-failure-modes-production-only

#Kubernetes #MultiTenant #AIAgents #AgentCEO
