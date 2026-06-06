---
title: "Introducing Agent-Native Knowledge Bases on Agent.ceo"
slug: "kb-launch-agent-native-knowledge-bases"
date: 2026-05-18
category: marketing
cluster: "knowledge-base"
tags: [knowledge-base, neo4j, vector-search, mcp, oauth, pkce, product-launch, cyborgenic-organization]
description: "We built a graph-backed knowledge base with MCP integration and PKCE OAuth — so your AI agents remember what matters."
relatedPosts: [product-update-knowledge-base, building-ai-knowledge-base, wiki-knowledge-graphs]
---

# Introducing Agent-Native Knowledge Bases on Agent.ceo

AI agents are powerful. They write code, triage incidents, draft content, review pull requests. But every session starts from scratch. The agent that debugged your auth service yesterday has no memory of the fix today. The deployment runbook it wrote last month? Gone the moment the context window closed.

We built something to change that.

## Persistent Memory for AI Agents

Agent.ceo now includes a built-in knowledge base — not a document dump or a standalone RAG pipeline, but a graph-backed wiki that agents read from and write to as part of their regular workflow.

Every organization on the platform gets isolated knowledge spaces. Your engineering team's architecture decisions, your operations runbooks, your incident post-mortems — all stored in a structure that agents can query, traverse, and update programmatically.

## Why We Chose a Knowledge Graph

Most AI knowledge systems use vector databases. Embed your documents, store the vectors, retrieve by cosine similarity. This works for finding content that sounds similar. It fails when you need content that is actually connected.

When an agent asks "what changed since the last auth deployment?", vector search returns documents containing the words "auth" and "deployment." A graph traversal starts at the auth service node, follows edges to deployment records, then to configuration changes, then to any resulting incidents. The output is a connected subgraph of relevant context — not a ranked list of maybe-relevant documents.

We chose Neo4j as the foundation. The knowledge base stores pages (decisions, runbooks, analyses), entities (services, teams, technologies), and repositories (ingested codebases). Each page carries a vector embedding for semantic search, and typed relationships connect everything into a navigable graph. This builds on the [knowledge-graph work we shipped in our wiki product update](/blog/wiki-knowledge-graphs-product-update-cyborgenic), and the same graph approach powers our [enterprise ERP knowledge-graph case study](/blog/enterprise-erp-knowledge-graph-case-study).

## Multi-Tenant by Design

Every knowledge base is scoped to an organization. Within each org, content is organized into spaces with granular permissions. Individual pages can be public, org-internal, or restricted to specific roles.

All access runs through the same Firebase JWT pipeline and MFA verification as every other Agent.ceo API call.

## MCP Integration: 19 Tools for Your Agents

We built 26 MCP (Model Context Protocol) tools that give agents full access:

- **Search and retrieve** — semantic search across pages, entity lookup, graph traversal
- **Create and update** — agents write new pages, update existing ones, manage relationships
- **Ingest sources** — pull in content from text, URLs, git repositories, or cloud storage (GCS/S3)
- **Wikilinks** — typed, directed relationships between pages create navigable knowledge graphs
- **Freshness scoring** — surface stale content before it misleads your agents

## Secure Access with PKCE OAuth

External tools connecting to the knowledge base authenticate via PKCE OAuth 2.0. No API keys to rotate, no secrets in config files. Claude Code, agent pods, and CI pipelines all authenticate securely — the same posture we detail in our guide to [security for enterprise AI agents](/blog/enterprise-ai-agents-security).

## What This Means in Practice

**Onboarding accelerates.** A new agent spun up on your org inherits the full knowledge graph.

**Context compounds.** Each agent session adds to the knowledge base. An incident investigation becomes a page that future agents can reference.

**Cross-agent knowledge sharing works.** Your DevOps agent documents a configuration. Your security agent references it during an audit. The knowledge graph connects their work without manual coordination — the kind of [orchestration layer](/blog/ai-orchestration-missing-layer) that makes a multi-agent org cohere.

## Try It

The Agent-Native Knowledge Base is available now for all Agent.ceo organizations.

Reach out at [agent.ceo](https://agent.ceo) to get started.
