---
platform: twitter
status: draft
date: 2026-10-20
note: "Blog launch — One Neo4j, Many Tenants"
---

## Thread: New Blog -- One Neo4j, Many Tenants

New post: we designed for database-per-tenant. Reality gave us one shared Neo4j Community instance.

Here's how we made multi-tenancy work without multi-database support.

---

The original plan: each customer org gets its own Neo4j instance. Clean isolation. Separate StatefulSets. Separate credentials.

The reality: Neo4j Community Edition doesn't support multiple databases. We had one instance. Customer org agents were pointed at per-org instances that didn't exist.

---

The fix: accept reality. Share the instance. Enforce isolation at the query layer.

Every node and relationship gets an `org_id` property. Every Cypher query includes `WHERE n.org_id = $org_id`. No exceptions. No shortcuts. Property-based tenant isolation.

---

What we got: one StatefulSet instead of N. One credential secret mirrored to each org namespace. One backup target. One monitoring dashboard.

What we gave up: nothing that matters. Query-layer isolation is deterministic. If every MATCH filters by org_id, data can't leak across tenants.

---

Read the full breakdown: https://agent.ceo/blog/shared-neo4j-property-tenant-isolation-knowledge-graph

#Neo4j #MultiTenancy #KnowledgeGraph #AgentCEO
