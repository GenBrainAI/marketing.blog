---
platform: twitter
status: draft
date: 2026-07-16
note: Wednesday daily Twitter post. Cannot auto-post — no Twitter API keys provisioned.
---

## Thread: Property-Based Tenant Isolation in Neo4j

1/ Every Cypher query in our platform includes:

`WHERE n.org_id = $org_id`

That one line is our entire tenant isolation layer. No separate databases. No VPC peering. Just a property on every node.

Here's why that's better, not worse:

2/ When isolation is a data property instead of an infrastructure boundary, you can TEST it.

We run CI checks that scan every Cypher query in the codebase. If any query touches tenant-scoped data without the `org_id` filter, the build fails.

Try unit-testing the absence of cross-tenant network access. You can't.

3/ The middleware injects `org_id` automatically. Individual developers never touch it. You'd have to actively bypass the query builder to write an unscoped query — and the linter catches that too.

Shared reference data that crosses tenant boundaries? Handled. Index strategy for fast scoped queries? Covered.

4/ We wrote the full tutorial — data model, middleware pattern, CI enforcement, index design, and the edge cases nobody warns you about.

If "one database per customer" is in your architecture doc, read this before your next sprint:

https://agent.ceo/blog/multi-tenant-neo4j-knowledge-graph-ai-agents
