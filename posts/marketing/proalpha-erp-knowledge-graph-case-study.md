---
title: "Case Study: How ProAlpha Turned 365 ERP Entities into Navigable AI Memory"
slug: "proalpha-erp-knowledge-graph-case-study"
date: 2026-06-04
category: technical
cluster: "case-studies"
tags: [case-study, erp, knowledge-graph, neo4j, design-partner, enterprise, proalpha, knowledge-base]
description: "ProAlpha deployed agent.ceo's knowledge graph on their ERP documentation — 365 entities, 2,820 graph nodes. AI agents now answer cross-module dependency questions that vector search alone cannot."
relatedPosts:
  - /blog/vector-search-organizational-knowledge
  - /blog/build-ai-agent-knowledge-base-wiki-mcp-tools
  - /blog/agent-native-knowledge-base-llm-wiki-domain-expert
  - /blog/credential-management-multi-cloud
  - /blog/building-custom-mcp-servers-cyborgenic
---

# Case Study: How ProAlpha Turned 365 ERP Entities into Navigable AI Memory

Enterprise ERP systems are among the most documentation-heavy, relationship-dense software environments in existence. A manufacturing ERP like ProAlpha has hundreds of interconnected modules where changes in one area cascade through others in non-obvious ways. Knowing *that* procurement feeds inventory is one thing. Knowing exactly *which* configuration fields in procurement affect *which* downstream processes in production planning — that's the knowledge that costs $200-400/hour in consultant time and takes weeks to assemble.

GenBrain AI is the company behind [agent.ceo](https://agent.ceo), and ProAlpha is our first design partner deploying the Agent-Native Knowledge Base on real enterprise ERP documentation.

## The problem: trapped expertise

ProAlpha's ERP documentation spans hundreds of modules with deep interdependencies. Before deploying agent.ceo, answering a cross-module dependency question — "If we change this procurement configuration, what downstream processes are affected?" — required either an experienced consultant who carried the relationships in their head, or hours of manual documentation tracing.

Three specific pain points drove the deployment:

1. **Consultant dependency.** Cross-module questions required expensive human experts ($200-400/hour) who understood the dependency chains. That expertise walks out the door at 5pm.
2. **RAG limitations.** AI assistants built on vector search could find *similar text*, but they could not follow *typed relationships* between entities. Asking "what depends on the procurement module" returned documents that mention procurement — not documents connected to procurement through actual dependency edges.
3. **Onboarding cost.** New team members took months to develop the working knowledge of how modules connect. That knowledge isn't in any single document — it's in the spaces *between* documents.

## What we deployed

ProAlpha's ERP documentation was ingested into agent.ceo's [Agent-Native Knowledge Base](/blog/agent-native-knowledge-base-llm-wiki-domain-expert) — a Neo4j knowledge graph with typed relationships, paired with vector search for semantic queries.

**By the numbers:**

| Metric | Value |
|--------|-------|
| ERP entities ingested | 365 |
| Graph nodes created | 2,820 |
| Relationship types | `DEPENDS_ON`, `CONFIGURED_BY`, `FEEDS_INTO`, `TRIGGERS` |
| Agent access | MCP tools with scoped OAuth tokens |
| Ingestion approach | Deterministic XML parsing (no LLM in the hot path) |

The architecture is straightforward: ERP documentation goes in, a traversable knowledge graph comes out. AI agents connect via [MCP tools](/blog/building-custom-mcp-servers-cyborgenic) — `kb_search`, `kb_read`, `kb_graph_neighbors`, `kb_graph_describe` — using scoped [platform API keys](/blog/platform-api-keys-ace-scoped-auth) with read-only access to the product documentation space.

## Where graph beats vector

The deployment surfaced a clear pattern across three query types:

**Simple factual queries** — "What is entity X?" — vector search and graph perform similarly. Both find the right document. No advantage either way.

**Dependency questions** — "What entities depend on module Y?" — graph traversal finds **3-5x more relevant context** than vector search. Vector search returns documents that *mention* the module. Graph traversal returns documents *connected to* the module through typed edges. The difference is between "this text is similar" and "this entity has a `DEPENDS_ON` relationship."

**Cross-module impact analysis** — "If we change configuration Z in procurement, what downstream processes are affected?" — **only graph traversal works.** Vector search cannot follow typed edges between entities. It finds documents about procurement. It does not find the chain from procurement → inventory → production planning → cost accounting that an actual dependency analysis requires.

This is the core insight: for enterprise systems with deep structural relationships, [vector search alone is necessary but not sufficient](/blog/vector-search-organizational-knowledge). The relationships *between* documents carry as much information as the documents themselves.

## What this means for due diligence

The immediate application is for VC/PE firms and consultancies doing technical due diligence on ERP-dependent businesses. Configuration audits, integration planning, and dependency mapping that previously took weeks of consultant time can now be run as agent-driven analyses against the knowledge graph.

An agent can traverse the graph, follow dependency chains, and produce an impact analysis in minutes — not because it's smarter than a human consultant, but because the knowledge graph makes the relationships explicit and traversable rather than implicit and scattered across hundreds of documents.

## What's next

ProAlpha is our first design partner, and the deployment validated three architectural decisions:

1. **Graph + vector, not graph or vector.** Both are needed. Vector handles the "find me something about X" queries. Graph handles the "show me everything connected to X" queries. The retrieval layer orchestrates both.
2. **Deterministic ingestion for structural data.** No LLM in the parsing pipeline for ERP XML — fast, cheap, and idempotent. `MERGE` on `(kind, external_id)` means re-running the ingester doesn't duplicate nodes.
3. **Scoped access is non-negotiable.** Enterprise data requires per-role access control from day one, not as a bolt-on. Support agents see product docs. Engineering agents see architecture docs. The OAuth scoping handles this without manual token management.

The pipeline is designed to scale: more document sources, more entity types, more relationship types. The graph gets more valuable with every entity added — each new node creates new traversal paths that surface connections no one explicitly documented.

---

**Want AI agents that understand your enterprise systems — not just the documents, but the dependencies between them?** [agent.ceo](https://agent.ceo) builds agent-native knowledge graphs that turn documentation into navigable, traversable organizational memory. Start with a design partner deployment.
