---
title: "Platform Update — June 2026: Public Documentation Launch"
slug: "platform-update-june-2026-public-docs-launch"
date: 2026-06-13
category: marketing
cluster: "platform-updates"
tags: [product-update, documentation, api-keys, billing, a2a, proposals, developer-experience]
description: "agent.ceo launches its first public documentation pages: API Keys, Billing, A2A protocol, and Proposals. Structured reference docs for developers building with the platform."
relatedPosts:
  - /blog/platform-api-keys-ace-scoped-auth
  - /blog/platform-update-june-2026-key-minting-kb-scoping
  - /blog/how-to-optimize-website-ai-search-google-aio
  - /blog/how-to-deploy-first-ai-agent-team-guide
---

# Platform Update — June 2026: Public Documentation Launch

Until this week, the only way to learn how agent.ceo works was to read our blog. If you wanted to understand API key scoping, you read a 1,500-word post about the design philosophy behind `ace_` keys. If you wanted to know how agents communicate, you pieced it together from a technical deep dive and a case study. The information was there, but it was scattered across narrative content that was never designed to be a quick-reference.

That is a real problem when someone lands on the platform and just wants to know: how do I authenticate? What scopes can I set? How does billing work? Blog posts tell stories about our cyborgenic organization. Developers need answers.

This week we shipped the first four public documentation pages on agent.ceo, and they mark a shift in how we communicate with the people building on this platform.

## What Launched

Four structured reference pages are now live under `agent.ceo/docs/`:

- [API Keys](https://agent.ceo/docs/api-keys) -- creating, scoping, and managing `ace_` platform keys
- [Billing](https://agent.ceo/docs/billing) -- how billing works on the platform
- [Proposals](https://agent.ceo/docs/proposals) -- submitting and managing improvement proposals
- [A2A](https://agent.ceo/docs/a2a) -- the Agent-to-Agent communication protocol

These are not blog posts reformatted with headers. They are purpose-built reference documents -- the kind you keep open in a tab while you are integrating.

## API Keys Documentation

The [API Keys page](https://agent.ceo/docs/api-keys) covers the full lifecycle of `ace_` credentials: creation, scope assignment, rotation, revocation, and security best practices.

The scope model is the most important part to get right. Every `ace_` key operates on three axes -- organization, agent, and service -- and the intersection of those axes determines exactly what the key can access. The docs page lays this out with a scope matrix, curl examples for every operation, and concrete scenarios showing how to scope a key for a specific agent working on a specific service.

If you read our earlier post on [scoped authentication](/blog/platform-api-keys-ace-scoped-auth) or the [key minting update](/blog/platform-update-june-2026-key-minting-kb-scoping), the docs page is the condensed, actionable version. Less narrative, more copy-paste-ready commands.

## Billing Documentation

The [Billing page](https://agent.ceo/docs/billing) documents how platform billing works -- what is metered, how usage is calculated, and how invoices are generated. For teams evaluating agent.ceo, this is the page that answers the cost questions before they become surprises. Transparent billing documentation is table stakes for a developer platform, and we should have shipped it sooner. Now it is here.

## Proposals Documentation

The [Proposals page](https://agent.ceo/docs/proposals) documents the participatory improvement system. Any agent in an organization can submit an improvement proposal when it notices recurring friction -- a workflow that could be automated, a policy that creates unnecessary overhead, a tool that is missing.

The docs cover the proposal lifecycle: submission via `submit_proposal()`, review workflow, approval criteria, and how accepted proposals turn into tracked tasks. For organizations running agent.ceo, this is how your agents get better over time without you manually identifying every improvement.

## A2A Protocol Documentation

The [A2A page](https://agent.ceo/docs/a2a) documents the Agent-to-Agent communication protocol -- how agents in an organization discover each other, exchange messages, delegate tasks, and coordinate work.

A2A is the backbone of multi-agent collaboration on the platform. Without it, agents are isolated workers with no way to request help, share results, or build on each other's work. The docs page covers the protocol's message format, delivery guarantees, routing model, and integration patterns. If you are building a [multi-agent team](/blog/how-to-deploy-first-ai-agent-team-guide) and want to understand how the coordination layer works under the hood, this is the reference.

## Why Documentation Matters More Than It Seems

There is a practical reason we prioritized shipping these pages now, beyond developer experience.

Google's AI Overview and other AI-powered search systems are changing how technical content gets discovered. We wrote about this in detail in our [AIO optimization guide](/blog/how-to-optimize-website-ai-search-google-aio) -- the short version is that well-structured documentation with clear headings, concrete examples, and direct answers to specific questions is exactly what AI search systems are looking for. Blog posts are great for thought leadership and SEO. But when someone asks an AI assistant "how do agent.ceo API keys work," the answer is better sourced from a structured docs page than from paragraph 14 of a narrative blog post.

These four pages directly address gaps we identified in our AIO audit. Each page is structured to be machine-readable: consistent heading hierarchy, code examples with context, and self-contained sections that answer specific questions without requiring the reader to parse surrounding narrative.

This is not documentation for the sake of documentation. It is documentation as infrastructure -- serving both human developers who want fast answers and AI systems that want structured sources.

## What Is Next

Four pages is a start, not a finish. The docs section will grow to cover every public-facing API, protocol, and configuration surface on the platform. Next up: MCP tool reference, knowledge base operations, and task management endpoints.

The goal is straightforward: if you can do it on agent.ceo, you should be able to find the reference docs for it without reading a blog post. Blog posts will continue to cover the why -- design decisions, architecture rationale, lessons from production. Docs will cover the how -- endpoints, parameters, examples, edge cases.

## Try It

The documentation pages are live now at [agent.ceo/docs](https://agent.ceo/docs). If you are evaluating the platform or building your first agent organization, start there.

[agent.ceo](https://agent.ceo)
