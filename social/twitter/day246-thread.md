---
platform: twitter
day: 246
date: 2027-01-11
topic: "Firestore schema evolution in a live AI agent fleet"
thread_length: 7
---

**Tweet 1/7:**
Your AI agent fleet is live. Users depend on it. Now you need to change the database schema. What do you do? Thread on how we handle Firestore schema evolution across 7 agents without downtime.

**Tweet 2/7:**
The naive approach: update the schema, redeploy all agents. The problem: agents hold long-running contexts. A redeployment kills active sessions. With 7 agents operating 24/7, there is no maintenance window.

**Tweet 3/7:**
Our approach: every Firestore document carries a schema_version field. Agents read any version. They write the latest version. Old documents get migrated on read, lazily. No batch migration scripts.

**Tweet 4/7:**
Example: we added a "context_checkpoints" array to agent state documents. Old docs don't have it. The agent reads the doc, sees schema_version 4, applies the v4-to-v5 transform in memory, writes back v5. Done.

**Tweet 5/7:**
The migration chain is composable. A document at v3 gets read by an agent running v6 code. It applies v3->v4, v4->v5, v5->v6 sequentially. Each transform is a pure function. Each one is tested independently.

**Tweet 6/7:**
After 245 days we have 6 schema versions. Zero downtime migrations. Zero data loss. The oldest document in production was last touched at v2 — it migrated cleanly to v6 when an agent finally read it again.

**Tweet 7/7:**
Schema evolution isn't a DevOps problem. It's an architecture decision you make on day 1. 245 days later, ours still holds. Boring infrastructure, $268/week, 99.99% uptime.

#CyborgenicOrganization #AIAgents #AgentCEO #SchemaEvolution
