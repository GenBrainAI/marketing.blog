---
platform: twitter
status: draft
date: 2026-07-22
note: Tuesday daily Twitter post. Cannot auto-post — no Twitter API keys provisioned.
---

## Thread: Multi-Tenant Isolation in a Shared Knowledge Graph

1/ 102 tests validate that Tenant A's data is invisible to Tenant B.

Even when both tenants have a node called "auth."

Here's how we built multi-tenant isolation in Neo4j for AI agents:

2/ The problem: Neo4j has no native tenant partitions. Every node lives in the same graph.

If your Cypher query doesn't filter by org_id, you just leaked data. And "just filter by org_id" falls apart when you have 47 queries and one joins through a shared label.

3/ Our approach: property-based isolation at the query layer.

Every node carries org_id. Every query is wrapped in a tenant-scoped function that injects the filter BEFORE execution. Not as middleware that "should" catch it. The system enforces it — we don't trust query authors to remember.

4/ What the 102 tests cover:
- Direct reads across tenant boundaries (blocked)
- Relationship traversals crossing tenants (blocked)
- Shared label names leaking via pattern matching (isolated)
- Write ops creating cross-tenant edges (rejected)
- Admin queries crossing boundaries (permitted + audited)

5/ "Just add org_id to your queries" is a policy. Wrapping every query in a tenant-scoped function that enforces it structurally is an architecture.

Policies get forgotten. Architecture doesn't.

Full breakdown: https://agent.ceo/blog/multi-tenant-neo4j-knowledge-graph-ai-agents
