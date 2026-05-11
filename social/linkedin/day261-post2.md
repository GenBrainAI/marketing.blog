---
platform: linkedin
day: 261
date: 2027-01-26
topic: "What happens when isolation fails — our blast radius analysis"
linkedPost: "isolation-blast-radius"
---

Good security architecture starts with one question: what happens when a layer fails?

We run three isolation layers for tenant separation: Kubernetes namespaces with RBAC, NetworkPolicies, and NATS account boundaries. Each one is designed to hold independently. But I still needed to know the blast radius if one breaks.

So we tested it. Deliberately.

Scenario 1: RBAC misconfiguration. We created a service account with overly broad permissions. Result: the account could list resources in other namespaces but could not access them because NetworkPolicies blocked all cross-namespace traffic. NATS account boundaries also held. Blast radius: metadata exposure only. No data access.

Scenario 2: NetworkPolicy gap. We temporarily removed deny-by-default egress. Result: pods could reach other namespaces at the network level but could not authenticate to other tenants' NATS accounts or Firestore collections. Blast radius: port scanning possible. No data access.

Scenario 3: NATS account leak. We configured a test account with incorrect subject imports. Result: the account could see messages from another tenant's subject space but could not act on them because the Kubernetes service account lacked permissions to the target tenant's resources. Blast radius: message visibility only. No operational impact.

In every scenario, the remaining two layers contained the failure. No single-layer breach resulted in cross-tenant data access or operational interference.

This is why we overengineered isolation. Not because we expect failures. Because when they happen, the blast radius must be zero.

Read more: [Isolation Blast Radius Analysis](https://agent.ceo/blog/isolation-blast-radius)

#CyborgenicOrganization #SecurityTesting #BlastRadius #DefenseInDepth #AgentCEO #BuildInPublic

— Moshe Beeri, Founder, GenBrain AI
