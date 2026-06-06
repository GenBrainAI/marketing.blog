---
platform: linkedin
status: draft
date: 2026-10-20
note: "Blog launch — One Neo4j, Many Tenants"
---

## Post: New Blog -- One Neo4j, Many Tenants

New post today. We designed our knowledge graph for database-per-tenant isolation. Each customer org would get its own Neo4j instance -- separate StatefulSets, separate credentials, clean boundaries.

Then reality showed up. Neo4j Community Edition doesn't support multiple databases. We had one shared instance. Our customer org agents were configured to connect to per-org Neo4j instances that simply didn't exist.

So we accepted reality and redesigned. One shared Neo4j instance with property-based tenant isolation. Every node and relationship gets an `org_id` property. Every Cypher query includes `WHERE n.org_id = $org_id`. No exceptions.

The result: one StatefulSet instead of N. One credential secret mirrored to each org namespace. One backup process. One monitoring dashboard. The operational simplicity is significant -- we're not managing a fleet of databases, we're managing one.

The isolation guarantee comes from discipline at the query layer. If every MATCH statement filters by org_id, tenant data cannot cross boundaries. It's deterministic, auditable, and far simpler to operate than running separate database instances for each organization.

Sometimes the architecture you designed isn't the architecture you need. Accepting constraints instead of fighting them led to a simpler, more maintainable system.

Read the full post: https://agent.ceo/blog/shared-neo4j-property-tenant-isolation-knowledge-graph

#Neo4j #MultiTenancy #KnowledgeGraph #AgentCEO
