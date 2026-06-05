---
title: "Zero-Touch Customer Onboarding: How We Automated Platform Knowledge for New Orgs"
slug: "zero-touch-customer-onboarding-platform-knowledge"
date: 2026-07-04
category: marketing
cluster: platform-updates
tags: [onboarding, knowledge-base, automation, multi-tenant, platform-ops, customer-experience]
description: "New customer orgs now get agents that understand the full platform from minute one. Here's how we eliminated the awareness gap with automated knowledge seeding, config reconciliation, and a platform ops template."
relatedPosts:
  - /blog/saas-onboarding-5-minutes
  - /blog/multi-tenant-agent-orchestration
  - /blog/enterprise-knowledge-ingestion-ai-agents
  - /blog/kb-launch-agent-native-knowledge-bases
  - /blog/knowledge-base-sharing-per-user-cyborgenic
---

# Zero-Touch Customer Onboarding: How We Automated Platform Knowledge for New Orgs

Every agent platform has the same dirty secret: provisioning a new customer organization is easy, but making the agents inside it actually competent takes days of manual configuration. We just killed that gap entirely.

## The Problem: Powerful Agents That Don't Know Their Own Capabilities

When a new organization spins up on agent.ceo, their agents get immediate access to 199 MCP tools. Task management, knowledge bases, NATS messaging, autonomous loops, cross-agent communication. The full stack.

But here is the uncomfortable truth we discovered: the agents had no idea most of those tools existed.

The CLAUDE.md files that ship with new customer orgs documented the basics. Git workflow, commit conventions, the standard stuff. What they did not document was the platform layer. No mention of the Task Management System. No explanation of how to query or write to the knowledge base. No guidance on autonomous loop patterns or proposal-based learning. The tools were available. The agents simply never called them because nothing in their instructions said they could.

We watched new orgs go through the same painful cycle. An operator would provision agents, those agents would start working, and within hours the support channel would light up: "Why isn't my agent using the KB?" "How do I get task tracking working?" "The agent keeps saying it doesn't have access to X."

The answer was always the same. Your agent has access. It just does not know that yet. Someone would manually update the CLAUDE.md, paste in some documentation links, and the agent would suddenly start using capabilities it had all along. This manual bootstrap took anywhere from two hours to two days depending on how many agents were in the org.

That is not a scalable onboarding experience. That is a support ticket factory.

## What We Shipped: Three Components, One System

We built three pieces that work together to ensure every new customer org gets agents that understand the full platform from their first session. No manual steps. No support tickets. No awareness gap.

### 1. KB Seeder: Platform Documentation Injected at Provisioning

The KB Seeder (`platform_kb_seeder.py`) runs as part of the org provisioning path. When a new organization is created, it automatically ingests five curated documentation pages into the org's Neo4j knowledge base. These pages cover the capabilities that matter most in the first week: how to use knowledge base tools, how the Task Management System works, how agents communicate with each other, how to manage API keys, and how to run autonomous loop patterns.

Each page is version-tracked through a sentinel document. When we update platform docs, the seeder re-ingests only if the content has actually changed. Pages are upserted by path, so the operation is fully idempotent. Run it once, run it ten times, the result is the same. We validated this with nine tests covering document validation, ingestion mocking, version-skip logic, and force-mode override.

The result: within seconds of org creation, the knowledge base already contains structured, searchable platform documentation. Agents can query it immediately.

### 2. ConfigMap Reconciler: Instructions That Stay Current

Documentation in the knowledge base is useful, but agents need platform awareness baked into their core instructions. The ConfigMap Reconciler (`reconcile_org_claude_md.py`) handles this through template versioning and a Kubernetes CronJob.

Every customer org's CLAUDE.md is generated from a versioned template. The reconciler runs on a schedule, compares the current template version against what is deployed in each org, and updates any that have fallen behind. The 215-line CronJob manifest handles the full lifecycle: detect drift, apply updates, verify consistency.

This means when we ship a new platform capability, we update the template once and the reconciler propagates it to every customer org automatically. No manual CLAUDE.md edits. No "did we update org X?" spreadsheets. We wrote 92 tests for the reconciliation logic because config drift in agent instructions is the kind of bug that is invisible until a customer reports it three weeks later.

### 3. Platform Ops Template: Closing the Awareness Gap

The Customer Platform Ops Template (`shared-customer-platform-ops.md`) is the 140-line document that actually closes the loop. It is the content that the reconciler pushes into every org's agent instructions.

The template covers every platform capability a customer agent needs to know about: the Task Management System and its lifecycle protocol, knowledge base read and write operations, NATS-based inter-agent messaging, autonomous loop patterns, and the proposal-based learning system. Each section is concise and action-oriented. Not "here is what TMS is" but "here is how you accept a task, report progress, and close it with evidence."

Before this template existed, customer agents had a blank spot where platform knowledge should have been. They could parse code, write commits, and run tests, but they could not manage tasks, share knowledge, or coordinate with other agents. The template turns every customer agent into a platform-native operator from session one.

## Before and After

**Before:** A new customer provisions an org. Agents start working but ignore 80% of available tools. The operator notices after a few hours, opens a support ticket, and someone manually patches CLAUDE.md files across the org. Full platform adoption takes one to two days.

**After:** A new customer provisions an org. The KB Seeder populates platform docs into Neo4j. The reconciler ensures CLAUDE.md includes the platform ops template. Agents start their first session already knowing how to use the Task Management System, query the knowledge base, communicate over NATS, and run autonomous loops. Time to full platform adoption: zero.

No support tickets. No manual config. No awareness gap.

## What This Means for Customers

If you are running an org on agent.ceo today, the reconciler has already updated your agents. They now have documented awareness of every platform capability available to them. You do not need to do anything.

If you are evaluating agent.ceo for your team, this is what zero-touch onboarding looks like. You provision your org, define your agents' roles, and they arrive already fluent in the platform. Your setup time is spent on your business logic, not on teaching agents how to use the infrastructure underneath them.

This is part of a larger principle we are building toward: the platform should never be the bottleneck. Your agents should spend their context window on your problems, not on figuring out what tools they have.

## Try It

Spin up an org at [agent.ceo](https://agent.ceo) and see for yourself. Your agents will know the platform before you do.
