---
title: "Design Partner Program: Early Access to Agent-Native Knowledge Bases"
slug: "design-partner-program-knowledge-base"
date: 2026-05-18
category: marketing
cluster: "knowledge-base"
tags: [design-partner, knowledge-base, early-access, enterprise, neo4j, mcp]
description: "We are looking for 10 engineering teams running AI agents who need persistent, structured memory. Priority access, direct founder line."
relatedPosts: [kb-launch-agent-native-knowledge-bases, graph-traversal-vs-vector-search-ai-agents]
---

# Design Partner Program: Early Access to Agent-Native Knowledge Bases

We are looking for 10 design partners to shape the next generation of AI agent memory — the same persistent memory that powers our own cyborgenic organization.

## The Problem

AI agents forget everything between sessions. Your agent debugged a production incident yesterday and has no memory of it today. The architecture decisions documented last month vanish when the context window closes.

Vector search helps — but only for questions where "similar-sounding documents" equals "relevant context." Enterprise knowledge has structure: modules depend on modules, configurations cascade across systems, workflows connect across departments. Cosine similarity does not capture these relationships.

## What We Built

The Agent-Native Knowledge Base on agent.ceo combines a Neo4j knowledge graph with HNSW vector search. Agents read from it, write to it, and traverse organizational knowledge programmatically. (For the full launch details, see [Introducing Agent-Native Knowledge Bases](/blog/kb-launch-agent-native-knowledge-bases); for why we pair graph and vector, see [Graph Traversal vs Vector Search](/blog/graph-traversal-vs-vector-search-ai-agents).)

- **Graph + Vector**: Neo4j for typed relationships between entities. HNSW vector index for semantic search. Agents use both — vector search finds the starting point, graph traversal finds the context.
- **26 MCP Tools**: Full programmatic access — search, create, update, traverse, ingest. Agents interact with the knowledge base as a first-class tool, not a separate system.
- **PKCE OAuth 2.0**: Secure authentication for external tools. Claude Code, CI pipelines, and agent pods authenticate without API keys or shared secrets.
- **Multi-Tenant Isolation**: Per-organization knowledge spaces with granular permissions. Per-page access control. No cross-org data leakage.

We recently ingested 5,000+ pages of enterprise ERP documentation into a single knowledge graph. Agents answer cross-module dependency questions that no search engine can — the full write-up is in our [enterprise ERP knowledge-graph case study](/blog/enterprise-erp-knowledge-graph-case-study).

## What Design Partners Get

**Priority access** to the knowledge base platform, including features still in development.

**Direct founder access.** Weekly calls, shared Slack channel, same-day response on issues. You are not talking to support — you are talking to the person who built it.

**Roadmap influence.** Your use cases shape what we build next. Design partner feedback has already driven three major features: wikilink traversal, freshness scoring, and bulk ingestion from cloud storage.

**Dedicated onboarding.** We help you ingest your documentation, configure agent access, and validate the knowledge graph structure. Not a self-serve tutorial — hands-on engineering support.

## Who We Are Looking For

Engineering teams that meet at least two of these criteria:

- **Running AI agents in production** (or actively building toward production deployment)
- **5,000+ pages of internal documentation** (Confluence, SharePoint, custom wikis, or exported docs)
- **Multi-agent or multi-team AI usage** where shared memory across agents or sessions is a bottleneck
- **Enterprise software domain** with complex interdependencies between systems, modules, or configurations

Verticals where we see the strongest fit: enterprise software vendors, system integrators, large SaaS platforms, and regulated industries where audit trails matter.

## What We Ask

- A 15-minute intro call (live demo, no slides)
- Honest feedback on what works and what does not
- Permission to reference your use case anonymously in our documentation (no company names without explicit agreement)

## Get Started

Email moshe@genbrain.ai with a one-paragraph description of your documentation challenge. We will respond within 24 hours with a demo link.

[agent.ceo](https://agent.ceo)
