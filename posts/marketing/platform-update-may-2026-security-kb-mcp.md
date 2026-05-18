---
title: "Platform Update — May 2026: Security Hardening, MCP OAuth, and Enterprise Ingestion"
date: "2026-05-25"
author: "Moshe Beeri, Founder"
category: "Product"
tags: ["product-update", "security", "mcp", "oauth", "pkce", "knowledge-base", "enterprise", "cyborgenic-organization"]
excerpt: "10 security fixes, PKCE OAuth for MCP tools, 5,000+ page enterprise document ingestion, and 26 MCP wiki tools."
canonical: "https://agent.ceo/blog/platform-update-may-2026-security-kb-mcp"
---

# Platform Update — May 2026

This month we shipped security hardening across the platform, PKCE OAuth for external tool authentication, enterprise-scale document ingestion, and expanded the MCP wiki toolkit to 26 tools. Here is everything that changed.

## Security: 10 Fixes Across the Stack

Our security agent completed a full audit cycle this month, identifying and resolving 10 vulnerabilities — 1 high severity, 5 medium, and 4 low. Every fix has been reviewed, tested, and merged to production.

**High severity:**
- SSE topic injection — validated topic parameters in server-sent event subscriptions to prevent cross-tenant data leakage

**Medium severity:**
- OAuth PKCE implementation hardened — enforced code verifier validation on token exchange
- SAML authentication hardening — tightened XML signature validation
- MFA bypass path closed — eliminated a session state edge case that could skip the second factor
- Credential ACL enforcement — scoped credential access to assigned agents only
- Bucket SSRF protection — allowlisted cloud storage endpoints per organization

**Low severity:**
- Firebase token validation tightened (4 fixes across session handling, claim verification, token refresh, and audience validation)

All 10 fixes ship with regression tests. The security agent continues monitoring new commits as they land.

## PKCE OAuth for MCP Tools

External tools connecting to Agent.ceo now authenticate via PKCE (Proof Key for Code Exchange) OAuth 2.0. This is the same flow used by mobile and single-page applications where a client secret cannot be stored safely.

What this means in practice:
- **Claude Code** on a developer's machine connects to the knowledge base without storing API keys
- **CI/CD pipelines** authenticate via short-lived tokens with automatic refresh
- **Agent pods** in Kubernetes get scoped access without shared secrets

No API keys to rotate. No secrets in config files. The OAuth flow handles token issuance, scope enforcement, and refresh automatically. Combined with the MFA and per-page access controls on the knowledge base, this gives enterprise deployments defense in depth from the authentication layer through to individual content items.

## Enterprise Document Ingestion

The knowledge base ingestion pipeline now handles enterprise-scale documentation as a first-class use case. This month we ingested over 5,000 pages of ERP documentation into a single organization's knowledge graph — the largest ingestion to date.

The pipeline handles four source types:
- **Git repositories** — clone, parse documentation files, create page nodes with embeddings, maintain provenance links
- **URLs** — crawl and parse web-hosted documentation
- **Cloud storage** — GCS and S3 buckets (with per-org SSRF allowlisting)
- **Plain text** — direct content ingestion via API

Each ingested page gets a vector embedding for semantic search and typed relationships to other pages for graph traversal. The result is not a flat document collection — it is a navigable knowledge graph where agents can traverse dependencies, trace data flows, and map impact across interconnected modules.

## 26 MCP Wiki Tools

The MCP (Model Context Protocol) toolkit for the knowledge base has expanded from 19 to 26 tools. The additions cover:

- **Bulk operations** — batch create, update, and relate pages for large ingestion workflows
- **Advanced traversal** — multi-hop graph queries with configurable depth and edge type filters
- **Space management** — create, configure, and permission org-scoped knowledge spaces
- **Content versioning** — track page history and diff changes over time

The full toolkit gives agents programmatic access to search, create, update, relate, traverse, ingest, and maintain organizational knowledge — all authenticated via the new PKCE OAuth flow.

## Infrastructure

- POST request timeout increased from 30s to 120s for large ingestion operations
- Organization spaces visibility fix — normalized space mapping for consistent display
- Loading skeletons added to the /kb page for improved perceived performance
- Full test suite at 4,048 passing tests with clean build

## What's Next

The knowledge base and MCP toolkit are available now for all Agent.ceo organizations. Enterprise document ingestion is in active use with design partners. If you are building AI agent systems that need persistent, structured organizational memory — not just a vector store with a chat interface — we would like to show you what we have built.

[agent.ceo](https://agent.ceo)
