1/ We shipped a critical MCP fix three weeks ago.

Our customers never got it.

Their AI agents kept failing with the exact bug we'd already patched. Here's how that happened. 🧵

2/ We run a multi-tenant AI agent platform. Each customer org gets its own fleet of agents, provisioned from our platform images.

Customers started reporting MCP timeouts — tools disconnecting mid-session. We checked our code. The fix was already shipped.

3/ The root cause? We tagged platform images with :latest.

In a single-tenant deploy, :latest works fine — you roll pods, they pull the new image.

In multi-tenant? The tag resolves ONCE at first pull. Customer orgs never re-pulled. They were stuck on month-old code.

4/ This is an invisible failure mode:
- Your CI is green
- Your staging works perfectly
- Your fix is deployed... to YOUR cluster
- But customer orgs are frozen in time, running the old broken version

No alert fires. No metric moves. Customers just suffer.

5/ The :latest anti-pattern is well-documented in single-cluster DevOps. But in multi-tenant AI platforms — where each customer runs independent agent fleets — it's a completely different beast.

The image tag becomes a silent version lock.

6/ Tomorrow we're publishing the full post-mortem: how we hardened provisioning with SHA pinning, proper NATS credential generation, observable degraded mode, and full A2A agent discovery.

Read the precursor on debugging MCP disconnections now:
https://agent.ceo/blog/debug-mcp-disconnections-ai-agents
