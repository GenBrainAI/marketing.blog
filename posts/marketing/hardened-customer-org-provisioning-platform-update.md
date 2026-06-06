---
title: "Platform Update: How We Hardened Customer Org Provisioning"
slug: "hardened-customer-org-provisioning-platform-update"
date: 2026-07-11
category: marketing
cluster: platform-updates
tags: [platform-update, customer-orgs, provisioning, nats, devops, multi-tenant, reliability]
description: "We shipped four production fixes to harden customer organization provisioning — pinning agent images to platform SHAs, generating proper NATS auth, adding observable degraded mode, and completing the A2A agent registry."
relatedPosts:
  - /blog/zero-touch-customer-onboarding-platform-knowledge
  - /blog/self-healing-connections-resilient-ai-agent-infrastructure
  - /blog/debug-mcp-disconnections-ai-agents
  - /blog/deploying-ai-agents-kubernetes
  - /blog/multi-tenant-agent-orchestration
---

# Platform Update: How We Hardened Customer Org Provisioning

Your agents were running an old version of the platform and nobody told you.

That is the one-sentence summary of the most consequential bug we fixed this cycle. A customer org reported intermittent MCP timeouts — tool calls hanging, agents losing connectivity mid-task. We dug in expecting a networking issue. What we found was worse: their agents were running a stale container image from weeks prior, missing critical stability fixes we had already shipped. The image tag said `latest`. The image was not latest. And our provisioning system had no mechanism to detect or correct the drift.

This post covers the four production fixes we shipped to harden customer org provisioning for every cyborgenic organization on the platform. If you run any multi-tenant platform — or even if you just deploy containers — the `:latest` tag lesson alone is worth your time.

## What Customers Experienced

The symptoms looked unrelated at first glance:

- **MCP tool timeouts**: Agents in a customer org would intermittently fail to reach MCP servers, producing timeout errors on tool calls that worked fine on our internal org.
- **Silent auth failures on NATS**: Customer org message buses would occasionally reject connections, but the agents would retry and sometimes succeed, making the problem appear transient.
- **Missing agents in discovery**: External clients hitting the A2A protocol endpoint at `/.well-known/agent.json` could only find three of our six agents. Half the fleet was invisible.

None of these screamed "provisioning bug." They looked like runtime issues — networking, load, maybe a flaky upstream. But when we correlated the timeline, a pattern emerged: these symptoms only appeared in customer orgs provisioned after a certain date, and they persisted even after we deployed fixes to the platform image.

That last detail was the key. We had shipped the fix. Customer orgs never received it.

## Root Cause 1: The `:latest` Tag Lie

Here is the DevOps anti-pattern that cost us a week of debugging: when we provisioned a new customer org, the agent Deployment manifests referenced `agent:latest`. On day one, that resolved to the current platform image. On day thirty, it still said `latest` — but the underlying SHA had not changed. Kubernetes does not re-pull `:latest` on a running Deployment unless you force a rollout. The tag is a pointer, not a promise.

The consequence was silent version drift. Our internal org ran the newest image because we actively deploy to it. Customer orgs ran whatever image happened to be current when they were first provisioned. When we shipped the dual-scope MCP fix — the one that resolved tool-call timeouts by properly handling both org-scoped and global MCP server registrations — our internal agents got it immediately. Customer agents did not. They were stuck on the old image, still hitting the bug we had already fixed.

This was the root cause of the MCP timeout reports. Not a networking issue. Not a load issue. A deployment hygiene issue with real customer impact.

## Root Cause 2: NATS Auth Was Either Missing or Wrong

Customer org NATS deployments had a credentials problem that manifested two ways. Some orgs were provisioned with no auth credentials at all — the NATS server accepted unauthenticated connections, which is a security gap. Others had credentials copied from the API gateway's environment variables, which meant customer org agents were trying to authenticate against a NATS server using credentials from a completely different NATS cluster. This worked exactly as poorly as you would expect.

## Root Cause 3: Partial Failures Were Invisible

Org provisioning is a multi-step process: create namespace, deploy NATS, generate secrets, spin up agents, register in the gateway. When step three failed but step four succeeded, we had an org with running agents that could not authenticate to their message bus. The provisioner reported success because it did not aggregate partial failures. There was no degraded mode — only "worked" or "crashed entirely."

## Root Cause 4: Incomplete Agent Registry

The A2A agent card at `/.well-known/agent.json` is how external systems discover which agents are available. We had hard-coded the initial agent list to three: CEO, CTO, and Fullstack. DevOps, CSO, and Marketing existed and were running, but they were invisible to any client using the standard discovery protocol. This was not a provisioning bug per se, but it compounded the trust problem — if a customer could not even see the full fleet, how could they trust the platform was fully operational?

## What We Fixed

**Fix 1: Generate real NATS credentials per org.** The `deploy_org_nats()` function now generates unique auth credentials for each customer org and writes them into a proper authorization block in `nats.conf`. A new helper, `_ensure_org_nats_credentials()`, creates or reuses a `nats-credentials` secret with a generated password. We also fixed a key reference bug in `agent_factory.py` — the secret key was `pass` when it should have been `password`. Small typo, real breakage.

**Fix 2: Pin agent images to the platform SHA.** This is the big one. Customer org agent Deployments are now provisioned with the specific image SHA that the platform is currently running — not `:latest`, not `:stable`, but the exact digest. When we ship a new platform image, we know which SHA every org is running, and we can roll them forward deliberately. No more silent drift. No more customers stuck on old images missing critical fixes.

**Fix 3: Observable degraded mode.** The provisioner now tracks each step independently and reports partial failures with specific detail — which step failed, what the error was, what state the org is in. Override precedence is consistent: org-level config beats defaults, explicit values beat inferred ones. If provisioning partially fails, you see exactly what worked and what did not, instead of a binary success/failure with no middle ground.

**Fix 4: Full agent registry.** DevOps, CSO, and Marketing are now included in `GATEWAY_INITIAL_AGENTS`. The A2A agent card lists all six agents. The MCP registry catalog is also complete. External clients using standard discovery see the full fleet from day one.

## Why This Matters

These fixes are not glamorous. There is no new feature here, no new capability to demo. What there is: a provisioning system that produces correct, authenticated, version-pinned, fully-discoverable customer orgs every time — and tells you clearly when something goes wrong instead of pretending everything is fine.

The `:latest` tag fix alone resolved an entire class of customer-reported issues. The MCP timeout reports from the re4ai org? Gone. Their agents are now running the same tested image as our internal fleet, with the dual-scope MCP fix included. We did not fix a new bug — we fixed the delivery mechanism that prevented an old fix from reaching them.

If you are building a multi-tenant platform, audit your image tags today. `:latest` in a Deployment manifest is a ticking clock. It works on day one and lies to you on day thirty. Pin to SHAs. Roll forward deliberately. Make drift observable.

## What is Next

We are extending the image-pinning system with automated rollout waves — when we ship a new platform image, customer orgs will receive it in staged rollouts with health checks between waves. We are also building provisioning dry-run mode so we can validate an org's full resource set before creating anything.

If you want to run your own AI agent organization on infrastructure that handles these problems for you, visit [agent.ceo](https://agent.ceo) and see what a hardened multi-tenant agent platform looks like in production.
