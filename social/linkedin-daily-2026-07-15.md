---
platform: linkedin
status: draft
date: 2026-07-15
note: Tuesday daily LinkedIn post. Cannot auto-post — no LinkedIn API keys provisioned.
---

## Post: We Were Running One Neo4j Per Customer Org

We were running one Neo4j per customer org. That's the kind of architecture that works until it doesn't.

At 5 tenants, it was fine. Clean isolation. Each org gets its own database, its own connection pool, its own backup schedule. Textbook multi-tenancy.

At 30 tenants, we had 30 Neo4j instances. 30 connection pools. 30 backup jobs. 30 things to monitor, patch, and keep alive. Our infrastructure bill was scaling linearly with customer count — not usage, just existence.

The real killer wasn't cost. It was operational complexity. Every schema migration had to run 30 times. Every index change, 30 times. A bug in one tenant's data would surface as a completely different failure pattern than the same bug in another tenant's instance, because they were on slightly different versions.

We ripped it out and moved to property-based isolation in a shared graph. One Neo4j cluster. Every node and relationship tagged with `org_id`. Every query scoped. One migration path. One monitoring dashboard. One backup.

The infrastructure bill dropped 80%. Schema migrations went from a 2-hour orchestration job to a 30-second Cypher script. And our on-call engineers stopped getting paged about idle tenant databases consuming memory for no reason.

Per-tenant databases are the comfortable default. Shared-graph isolation is the architecture that actually scales.

#MultiTenancy #Neo4j #GraphDatabases #AIAgents #InfrastructureScaling #GenBrainAI #StartupEngineering
