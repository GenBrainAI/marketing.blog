---
platform: linkedin
status: draft
date: 2026-07-22
note: Tuesday daily LinkedIn post. Cannot auto-post — no LinkedIn API keys provisioned.
---

## Post: 102 Tests Prove Tenant A Can't See Tenant B's Data

102 tests validate that Tenant A's data is invisible to Tenant B. Even when both tenants have a node called "auth."

Multi-tenant isolation sounds simple until you actually build it. Especially in a knowledge graph where relationships cross boundaries that were never designed to be boundaries.

Here's the problem: in Neo4j, there are no native tenant partitions. Every node lives in the same graph. If your query doesn't filter by org_id, you just leaked data across tenants. And "just filter by org_id" is the kind of advice that sounds obvious until you have 47 Cypher queries and one of them joins through a shared label.

Our approach: property-based isolation at the query layer. Every node carries an org_id property. Every query — read and write — is wrapped in a tenant-scoped function that injects the filter before execution. Not after. Not as a middleware that "should" catch it.

The 102 tests cover:
- Direct reads across tenant boundaries (blocked)
- Relationship traversals that would cross tenants (blocked)
- Shared label names that could leak through pattern matching (isolated)
- Write operations that could create cross-tenant edges (rejected)
- Admin queries that intentionally cross boundaries (permitted, audited)

We don't trust the query authors to remember the filter. The system enforces it. That's the difference between a policy and an architecture.

Full technical breakdown: https://agent.ceo/blog/multi-tenant-neo4j-knowledge-graph-ai-agents

#MultiTenant #Neo4j #DataIsolation #Security #KnowledgeGraph #AIAgents #GenBrainAI
