---
platform: twitter
status: draft
date: 2026-07-15
note: Tuesday daily Twitter post. Cannot auto-post — no Twitter API keys provisioned.
---

## Thread: Per-Tenant Databases Don't Scale for AI Agents

1/ We were running one Neo4j per customer org.

At 5 tenants: clean, simple, textbook multi-tenancy.

At 30 tenants: 30 instances, 30 connection pools, 30 backup jobs. Infrastructure bill scaling with customer count, not usage.

2/ The cost wasn't even the worst part.

Every schema migration ran 30 times. Every index change, 30 times. Bugs surfaced differently across tenants because instances drifted to slightly different versions.

Our on-call engineers were getting paged about idle databases burning memory.

3/ So we ripped it out. Moved to property-based isolation in a shared Neo4j cluster.

One database. Every node tagged with `org_id`. Every query scoped to the tenant. One migration path. One backup. One dashboard.

4/ Results:
- Infra bill down 80%
- Schema migrations: 2-hour orchestration job → 30-second Cypher script
- Zero idle-database alerts
- Faster onboarding (new tenant = new org_id, not new database)

5/ Per-tenant databases are the comfortable default. Shared-graph isolation is the architecture that actually scales.

If you're building a multi-tenant AI platform, think hard before giving every customer their own database.
