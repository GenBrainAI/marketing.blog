---
platform: linkedin
status: draft
date: 2026-10-31
note: "Blog launch — Platform KB Seeder"
---

## Post: New Blog -- Platform KB Seeder: Knowledge on Day One

New case study published today. Yesterday we talked about the gap between static instructions and searchable knowledge. Today: the system that closes that gap for every customer organization automatically.

We built a platform KB seeder. Five curated platform documentation pages -- covering KB tools, task management, agent communication, API key management, and autonomous loop configuration -- are auto-ingested into each customer org's Neo4j knowledge base.

How it works:

Version-tracked sentinel page. A special sentinel document is ingested first. Its presence and version prevent re-ingestion on subsequent runs. If the sentinel exists and its version matches, the seeder skips that org. Idempotent by design.

Idempotent upserts by path. Each documentation page is identified by its file path. If the page already exists in the knowledge graph, it gets updated in place. If it is new, it gets created. No duplicates. No orphaned documents.

Integrated into provisioning. When a new customer org is created, the seeder runs automatically as part of the provisioning pipeline. Agents in a brand-new org can immediately search platform capabilities -- no manual setup, no waiting for someone to load the docs.

Backfill for existing orgs. A seed_all_orgs() function iterates over every existing org namespace and applies the same seeding logic. Existing orgs that were created before the seeder existed get platform knowledge retroactively.

The result: every agent in every org can semantically search platform documentation from day one. No grep. No flat-file scanning. Just kb_graph_vector_search() and instant answers.

Full case study: https://agent.ceo/blog/platform-kb-seeder-customer-org-knowledge-base

#KnowledgeBase #Onboarding #MultiTenancy #AgentCEO
