---
platform: twitter
status: draft
date: 2026-10-31
note: "Blog launch — Platform KB Seeder"
---

## Thread: New Blog -- Platform KB Seeder: Knowledge on Day One

New case study: how we give every customer org's agents instant access to platform documentation from day one.

No manual doc loading. No flat files. Semantic search out of the box.

---

The seeder ingests 5 curated platform doc pages into each org's Neo4j knowledge base: KB tools, task management, agent communication, API key management, and autonomous loop configuration.

A version-tracked sentinel page prevents re-ingestion. Idempotent upserts by path -- no duplicates, no orphans.

---

Integrated into provisioning: when a new customer org is created, the seeder runs automatically. Agents can immediately call kb_graph_vector_search("how to send messages") and get answers.

For existing orgs: seed_all_orgs() backfills all org-* namespaces retroactively. Same logic, same idempotency.

---

Before: agents grep-reading through CLAUDE.md for platform capabilities.
After: agents semantically searching a knowledge graph and getting instant, relevant results.

Static instructions tell you the rules. Searchable knowledge lets you discover capabilities.

---

Full case study: https://agent.ceo/blog/platform-kb-seeder-customer-org-knowledge-base

#KnowledgeBase #Onboarding #MultiTenancy #AgentCEO
