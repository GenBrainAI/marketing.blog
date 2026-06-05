1/ We hardened our customer org provisioning after the :latest tag nearly took down external agent fleets.

4 fixes. Here's what changed and why. 🧵

2/ Fix 1: SHA pinning replaces :latest

Every customer org now provisions with a pinned image digest — not a mutable tag.

Result: no more silent version drift. When we ship a fix, we know exactly which orgs have it and which need an update. Rollbacks are one SHA swap.

3/ Fix 2: Proper NATS credential generation

Customer agents connect to our NATS mesh for inter-agent messaging. Before: shared default creds provisioned once. Now: unique, scoped credentials generated per org at provisioning time.

Each org gets its own auth boundary.

4/ Fix 3: Observable degraded mode

Previously, if an agent's MCP server was unreachable, it failed silently. Users saw timeouts with no explanation.

Now agents report degraded state explicitly. Operators see the issue in dashboards before a single support ticket lands.

5/ Fix 4: A2A agent registry — full fleet

Our A2A agent card expanded from 3 to 6 agents. Every agent in the org is now discoverable via the Agent-to-Agent protocol.

External systems can query capabilities, health, and endpoints for the complete fleet.

6/ The root cause was a :latest tag that resolved once and never again — a well-known DevOps anti-pattern that hits differently in multi-tenant AI platforms.

Full post-mortem and implementation details:
https://agent.ceo/blog/hardened-customer-org-provisioning-platform-update
