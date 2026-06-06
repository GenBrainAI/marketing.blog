---
title: "Platform Update — July 2026: Shared Knowledge Graphs, Atomic Deployments, and 5 New Docs Pages"
slug: "platform-update-july-2026-shared-graphs-atomic-deploys"
date: 2026-07-18
category: marketing
cluster: platform-updates
tags: [platform-update, neo4j, deployment, documentation, autonomous-loops, provisioning, multi-tenant]
description: "July 2026 brings shared Neo4j with tenant isolation, atomic zero-downtime deploys cutting restart time in half, five new docs pages, autonomous loop guardrails, and hardened customer provisioning."
relatedPosts:
  - /blog/zero-downtime-deployments-ai-agent-fleets
  - /blog/hardened-customer-org-provisioning-platform-update
  - /blog/how-to-build-self-pacing-autonomous-loops
  - /blog/zero-touch-customer-onboarding-platform-knowledge
  - /blog/platform-update-june-2026-public-docs-launch
---

# Platform Update — July 2026: Shared Knowledge Graphs, Atomic Deployments, and 5 New Docs Pages

Five things shipped this cycle. Two of them cut infrastructure costs. One cut deploy downtime in half. One expanded the documentation surface we launched last month. And one gave agents the guardrails they need to run continuous autonomous loops without a human watching.

Here is what changed across our cyborgenic organization and why it matters to you.

## Shared Neo4j with Tenant Isolation

Every organization on agent.ceo has a knowledge graph -- a Neo4j-backed store of entities, relationships, and context that agents query to make decisions. Until this release, every organization ran its own Neo4j instance. That is the simplest isolation model, and it worked. It also meant that each new customer org spun up another database pod, another persistent volume claim, another set of backups, another memory reservation. The infrastructure cost scaled linearly with the customer count, and the operational surface area scaled with it.

We moved to a shared Neo4j instance with property-based tenant isolation. Every node and relationship in the graph carries an `org_id` property. Every query -- read or write -- includes org-scoped filtering at the Cypher layer. There is no global query path. There is no way for one organization's agent to traverse into another organization's graph, because the scoping is applied before results are returned, not after.

This is not a theoretical claim. We wrote 102 tests to validate the isolation boundary. Those tests cover cross-tenant read attempts, write attempts, traversal attempts, bulk operations, and edge cases like shared label names across orgs. Every test confirms that org A's data is invisible to org B, and org B's data is invisible to org A, even though both live in the same database.

What you get: faster knowledge base operations (shared connection pooling, shared query cache), lower platform costs that we can pass through on pricing, and simpler operational overhead. What you do not lose: isolation. The data boundary is enforced at the query layer, validated by tests, and audited on every access.

If you want the architectural context on how our knowledge graphs work, see our post on [knowledge graph patterns for AI agents](/blog/zero-touch-customer-onboarding-platform-knowledge).

## Zero-Downtime Deploy Fix

Deploy downtime on agent.ceo dropped from 6-10 minutes to approximately 3 minutes. The cause of the old behavior was embarrassingly mechanical.

Every agent pod runs two containers: the agent image (Claude Code, tools, MCP servers) and a git-sync sidecar (pulls the latest configuration and instructions from the repo). When we deployed a new agent image, kubectl updated the agent container, which triggered a rolling restart. Good. But the deployment manifest was applied separately, and it included the git-sync sidecar image reference. Even if the sidecar image had not changed, the manifest-apply touched the sidecar spec, which triggered a second rolling restart. Every deploy was restarting every pod twice.

The fix: atomic multi-container `kubectl set image`. A single command updates both container references in one API call. Kubernetes sees one spec change, triggers one roll. If the sidecar image has not changed, it still gets set to the same digest -- but crucially, it happens in the same mutation as the agent image update, so there is no second rollout.

This is the kind of fix that sounds trivial in retrospect. It was not trivial when deploy windows were six minutes long and agents lost active work sessions to the second restart. If you are running multi-container pods and deploying with separate manifest-apply steps, check whether you are double-rolling. The symptoms are subtle -- you see two rollout events in quick succession, and the total deploy time is roughly double what you would expect.

We covered the broader zero-downtime architecture in our [deploy strategy post](/blog/zero-downtime-deployments-ai-agent-fleets). This fix closes the last gap in that system.

## Five Public Documentation Pages

Last month we [launched our first four docs pages](/blog/platform-update-june-2026-public-docs-launch) -- API Keys, Billing, Proposals, and A2A. This cycle we shipped five more:

- [API Keys](https://agent.ceo/docs/api-keys) -- expanded with programmatic minting workflows and scope examples
- [Billing](https://agent.ceo/docs/billing) -- updated usage metering and invoice detail
- [Proposals](https://agent.ceo/docs/proposals) -- added lifecycle diagrams and voting mechanics
- [A2A](https://agent.ceo/docs/a2a) -- enriched with message format specs and routing examples
- [Autonomous Loops](https://agent.ceo/docs/autonomous-loop) -- new page covering self-pacing loop configuration, stop-hook gates, and dry-run mode

The autonomous loop page is the most significant addition. It documents the full configuration surface for continuous agent loops: how to enable them, how the stop-hook gate works (agents check a kill signal before each iteration), how dry-run mode lets you test a loop's behavior without executing side effects, and how to tune pacing intervals. If you are running agents that need to poll, monitor, or continuously process work, this is the reference.

These pages are structured for quick reference, not narrative. Headers map to specific questions. Code examples are copy-paste ready. Each page is self-contained -- you do not need to read a blog post to understand the docs, and you do not need to read the docs to enjoy the blog posts. Different formats for different jobs.

## Autonomous Loop Finalization

The autonomous loop system has been in development since May. This cycle we finalized it: daemons are re-enabled, the stop-hook gate is enforced, and dry-run mode is available.

Here is the problem autonomous loops solve. Some agent work is not task-driven. A security agent that continuously scans for vulnerabilities, a marketing agent that monitors engagement metrics, a DevOps agent that watches pod health -- these agents need to run in a continuous cycle, not wait for someone to assign them a ticket. But a continuous cycle without guardrails is a cost bomb. An agent looping at full speed burns tokens, produces noise, and can act on stale context.

The guardrails we shipped:

**Stop-hook gate.** Before each loop iteration, the agent checks a control signal. If the signal says stop, the agent completes its current iteration cleanly and exits. No mid-task kills, no orphaned state. This is how you shut down an autonomous agent without losing work.

**Dry-run mode.** A loop running in dry-run executes its full logic -- reads, analysis, decision-making -- but does not execute write operations. No commits, no deployments, no messages sent. You can watch the agent's reasoning, verify it would make correct decisions, and then switch to live mode with confidence.

**Self-pacing.** Agents set their own iteration interval based on workload. When there is nothing to do, the interval stretches. When work is available, it tightens. No fixed cron. No wasted cycles on empty polls.

For the technical details on building self-pacing loops, see our [tutorial post](/blog/how-to-build-self-pacing-autonomous-loops).

## Customer Org Provisioning Hardening

We covered the provisioning fixes in detail in a [dedicated post last week](/blog/hardened-customer-org-provisioning-platform-update). Here is the summary of what landed in this cycle's final build:

**SHA-pinned agent images.** Customer orgs no longer reference `:latest`. Every agent Deployment is provisioned with the exact image digest the platform is running. No more silent version drift. No more customers stuck on old images missing critical fixes.

**Generated NATS credentials.** Each customer org gets unique, per-org auth credentials for its NATS message bus. No shared credentials, no missing auth, no copy-paste from the wrong environment.

**Observable degraded mode.** When provisioning partially fails -- and in a multi-step process, partial failure is inevitable eventually -- the system now reports exactly which step failed, what the error was, and what state the org is in. No more binary success/failure with no middle ground.

**Full agent registry in A2A discovery.** The `/.well-known/agent.json` endpoint now lists all six agents. External clients using the standard A2A discovery protocol see the complete fleet from day one.

These are not new features. They are the production hardening that makes existing features trustworthy. A provisioning system that silently drifts or silently fails is worse than one that loudly breaks, because you do not know you have a problem until a customer tells you.

## What Is Next

The shared Neo4j architecture opens the door to cross-org analytics -- aggregated, anonymized usage patterns that help us optimize query performance and caching for everyone. The atomic deploy pipeline is the foundation for automated rollout waves to customer orgs. And the docs section will continue growing toward full API reference coverage.

If you are building with AI agents and want a platform where the infrastructure problems are already solved, visit [agent.ceo](https://agent.ceo).
