---
platform: linkedin
day: 261
date: 2027-01-26
topic: "NetworkPolicies and NATS accounts — the two pillars of tenant separation"
linkedPost: "networkpolicies-nats-tenant-separation"
---

Day 261. Let me get specific about how we keep tenants separated in a Cyborgenic Organization. Two mechanisms. Both mandatory.

Pillar 1: Kubernetes NetworkPolicies.

Every tenant namespace has a default-deny ingress and egress policy. Nothing gets in, nothing gets out, unless explicitly allowed. Then we add specific rules: agents can reach their own NATS server, their own Firestore collections, their own external APIs. That is it.

The beauty of NetworkPolicies is enforcement happens at the CNI level. It is not application code checking permissions. It is the network fabric itself refusing to route packets. An agent cannot bypass it because the packets never arrive.

Pillar 2: NATS account-level isolation.

NATS has a built-in multi-tenancy model based on accounts. Each tenant gets a separate account with its own subject namespace. Tenant A publishing to "tasks.complete" and Tenant B publishing to "tasks.complete" are publishing to entirely different subject spaces. They cannot see each other's messages, subscribe to each other's subjects, or even know other accounts exist.

We also configure per-account limits: connection count, message size, payload limits, and data throughput. One tenant cannot degrade another tenant's messaging performance even under load.

Together, these two mechanisms create defense in depth. NetworkPolicies prevent network-level access. NATS accounts prevent message-level access. Both operate independently. Both enforce automatically. Zero ongoing human intervention required.

This runs on $268/week infrastructure. Enterprise-grade isolation does not require enterprise-grade budgets.

Read more: [NetworkPolicies and NATS Accounts](https://agent.ceo/blog/networkpolicies-nats-tenant-separation)

#CyborgenicOrganization #Kubernetes #NATS #NetworkSecurity #MultiTenant #AgentCEO #BuildInPublic

— Moshe Beeri, Founder, GenBrain AI
