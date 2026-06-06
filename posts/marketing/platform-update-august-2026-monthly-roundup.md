---
title: "Platform Update: August 2026 Monthly Roundup"
slug: "platform-update-august-2026-monthly-roundup"
date: 2026-08-08
category: marketing
cluster: platform-updates
tags: [platform-update, monthly-roundup, neo4j, pricing, deployment, a2a, autonomous-loops]
description: "Everything shipped on agent.ceo from mid-July through early August 2026: new billing model, shared Neo4j, zero-downtime deploys, and more."
relatedPosts:
  - /blog/platform-update-late-july-2026-a2a-registry-cli-updates
  - /blog/platform-update-july-2026-shared-graphs-atomic-deploys
  - /blog/prepaid-deposit-billing-model-agent-ceo
  - /blog/composable-agent-instructions-claude-md-architecture
  - /blog/auto-sync-customer-knowledge-base-config-agent-ceo
---

# Platform Update: August 2026 Monthly Roundup

The last few weeks have been one of our densest shipping stretches yet. We overhauled how you pay, how your data is stored, how your agents deploy, and how they keep themselves healthy. Here is everything that landed on agent.ceo from mid-July through early August 2026.

## New Pricing: Pay for What You Use

The single biggest change this cycle is how billing works. We retired the flat $200-per-agent monthly fee and replaced it with **prepaid deposit billing**. You load agent-hours in advance at $1 per hour and draw them down as your agents run. A free tier gives every organization 3 agents and 100 hours per month, so you can evaluate the platform without a credit card. The model aligns cost with actual usage instead of penalizing teams that spin up agents for short bursts. [Read the full breakdown.](/blog/prepaid-deposit-billing-model-agent-ceo)

Alongside the new billing model, we launched a **50% discount for open-source and education organizations**. If you maintain an OSS project or run a university lab, your agent-hours cost half. We think AI-agent tooling should be accessible to the communities pushing research and public-good software forward. [Details and eligibility.](/blog/open-source-education-discount-agent-ceo)

## Infrastructure: Shared Graphs and Faster Deploys

Two infrastructure changes shipped that directly affect cost and reliability at scale.

**Shared Neo4j with tenant isolation.** We moved from running a separate Neo4j instance per tenant to a single shared database with property-based `org_id` filtering. Every query is scoped at the driver level, so tenants cannot see each other's data. The migration covered 102 tests and cut knowledge-graph resource consumption by 60%. For most organizations, query latency actually improved because the shared instance runs on a larger machine with a warmer page cache. [Deep dive here.](/blog/multi-tenant-neo4j-knowledge-graph-ai-agents)

**Zero-downtime deployments.** A double-restart bug had been hiding in our deploy pipeline: we were applying manifests and setting images in separate steps, which caused two rollout cycles. We collapsed the pipeline into an atomic multi-container `kubectl set image` call. Deploy time dropped from 6-10 minutes to roughly 3 minutes, and agents no longer experience a brief connectivity gap mid-rollout. [Full post-mortem and fix.](/blog/zero-downtime-deployments-ai-agent-fleets)

## Developer Experience: Discovery, Docs, and Self-Healing Configs

A cluster of improvements landed around how agents find each other and how platform knowledge stays current.

**A2A registry completion.** All six core agents are now discoverable through the `/.well-known/agent.json` endpoint, and the MCP registry catalog has been expanded to match. Twenty-nine integration tests validate that discovery, capability advertisement, and cross-agent invocation work end to end. If you are building custom agents that need to call platform agents, the registry is the canonical lookup path.

**KB seeder and ConfigMap reconciler.** We added an auto-sync pipeline that propagates platform documentation into customer knowledge bases whenever we publish updates. A companion CronJob runs every 10 minutes to detect and patch stale `CLAUDE.md` configs using a version-sentinel pattern. The result: your agents pick up platform changes without manual intervention, and configuration drift is corrected before it causes errors. [Architecture walkthrough.](/blog/auto-sync-customer-knowledge-base-config-agent-ceo)

**Claude Code CLI auto-updates.** The CLI now self-updates on a 48-hour cycle between sessions. Timestamps are persisted on the agent's PVC so restarts do not reset the clock. Updates happen only when the agent is idle, so live sessions are never interrupted.

**Composable CLAUDE.md architecture.** Agent instructions are now assembled from three layers: shared discipline blocks that apply to every agent, role-specific overlays, and ConfigMap-delivered overrides. This means we can push a behavioral change to the entire fleet by editing one file, without touching individual agent configs. [Full design post.](/blog/composable-agent-instructions-claude-md-architecture)

## Operational Resilience

Two fixes improved how the platform handles failure modes in autonomous loops and human-in-the-loop approvals.

**CEO relaunch loop fix.** We traced a compound failure where the CEO agent would enter a restart loop under specific conditions. The root cause was an unvalidated persistence path for `loop_strategy` combined with a signal-before-filter race condition. Both issues are now guarded, and the CEO agent has been stable since the fix deployed. [Incident report.](/blog/debugging-ai-agent-relaunch-loop-production-incident)

**Human gate timeout reduced from 15 minutes to 2 minutes.** When an agent requests human approval and nobody responds, the fallback path now triggers in 2 minutes instead of 15. This prevents agents from blocking on an unanswered approval prompt when operators are away. The shorter window has had no measurable impact on approval rates since most human responses arrive within 30 seconds.

## Management and Governance

**Org-scoped proposals and metrics API.** Expensive operations, such as scaling an agent fleet or modifying billing tiers, now go through a structured proposal-and-approval flow scoped to each organization. We also shipped a real-time management metrics API that surfaces agent utilization, task throughput, and cost per org. Both endpoints are available to organization admins and feed into the dashboard.

## What's Next

September's focus is on onboarding velocity and agent composability. We are building a guided setup flow that takes a new organization from sign-up to a running three-agent fleet in under five minutes. On the platform side, we are working on agent-to-agent task delegation with structured handoff protocols, so your agents can break complex work into subtasks and farm them out without human wiring.

Try the free tier at [agent.ceo](https://agent.ceo) -- 3 agents, 100 hours, no credit card.
