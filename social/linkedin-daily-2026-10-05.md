---
platform: linkedin
status: draft
date: 2026-10-05
note: "The Silent Drift Problem in Multi-Tenant Agent Platforms"
---

## Post: The Silent Drift Problem in Multi-Tenant Agent Platforms

When you run a multi-tenant AI agent platform, your core fleet gets updated on every CI run. Customer-org agents get provisioned once and forgotten. They drift behind silently -- no errors, no alerts, just gradually falling behind on bug fixes and stability improvements.

Until a customer hits a bug you fixed three releases ago.

We discovered this when customer-org users reported MCP server timeouts. The MCP code was fine -- the handshake takes ~1.2s even with an unreachable NATS bus. The customer pods were just running a stale image pinned to `:latest` that didn't include commit 1494f5107 (the dual-scope MCP fix). Our core fleet had the fix. Their pods didn't.

The failure mode is specific to multi-tenant platforms: your CI keeps the core fleet current, but tenant deployments have no automated path to pick up new images. `:latest` doesn't re-pull unless the pod restarts. The pods don't restart unless something forces them to.

The fix: pin customer deployments to the same immutable image SHA the core fleet runs, not `:latest`. When the core fleet advances, tenant agents advance with it. No more silent drift.

Full writeup coming tomorrow with the implementation details.

Read more: https://agent.ceo/blog/three-agent-failure-modes-production-only

#Kubernetes #MultiTenant #AIAgents #AgentCEO
