---
title: "Platform Update: A2A Registry, CLI Auto-Updates, Proposals API, and Faster Loops"
slug: "platform-update-late-july-2026-a2a-registry-cli-updates"
date: 2026-08-01
category: marketing
cluster: platform-updates
tags: [platform-update, a2a, cli, proposals, autonomous-loops, nats, provisioning]
description: "Late July 2026 platform update covering full A2A registry, CLI auto-updates, org-scoped proposals, faster human gate timeouts, and NATS credential fixes."
relatedPosts:
  - /blog/platform-update-july-2026-shared-graphs-atomic-deploys
  - /blog/auto-sync-customer-knowledge-base-config-agent-ceo
  - /blog/debugging-ai-agent-relaunch-loop-production-incident
  - /blog/how-to-build-self-pacing-autonomous-loops
  - /blog/hardened-customer-org-provisioning-platform-update
---

# Platform Update: A2A Registry, CLI Auto-Updates, Proposals API, and Faster Loops

Five updates shipped in the back half of July. The theme: making cyborgenic organizations more discoverable, more current, and harder to break during provisioning. Here is what changed and why it matters.

## Full A2A Registry: All 6 Agents Discoverable

The standard A2A discovery endpoint at `/.well-known/agent.json` is how external clients find and connect to your agents. Until this update, it only listed 3 of our 6 agents -- CEO, CTO, and Fullstack. DevOps, CSO, and Marketing were running but invisible to anyone using the discovery protocol.

Now all 6 agents are registered and discoverable. We also expanded the MCP registry catalog to include DevOps MCP, Marketing MCP, Agent Hub MCP, TMS, and Billing services. If you are building integrations against agent.ceo using the A2A protocol, you now see the complete fleet -- not a partial view that required out-of-band knowledge to fill in.

The full registry is covered by 29 passing tests, so regressions here will surface immediately. For customer organizations, this means any agents you provision are automatically included in your own A2A registry from day one.

## Claude Code CLI Auto-Updates Between Sessions

Agent pods bake the Claude Code CLI at image build time. That works fine for fresh deployments, but pods that run for days or weeks between rebuilds fall behind. A pod running for two weeks could miss multiple CLI versions -- bug fixes, performance improvements, new features -- all stuck behind a rebuild cycle we might not trigger for unrelated reasons.

We added a time-gated self-update mechanism to the agent wrapper script. Every 48 hours, between sessions (never during a live session), the wrapper checks for a newer CLI version and updates in place. It uses PVC-backed timestamps to track when it last ran, so restarts do not reset the clock. Fresh deployments still pull the latest version at build time; this only covers the gap between rebuilds.

The result: your agents stay current without requiring image rebuilds or pod restarts. The update is best-effort -- if it fails, the agent continues with its current version and tries again next cycle.

## Org-Scoped Proposals and Management Metrics API

Two related additions to the gateway. First, organization-scoped proposals: agents can now submit structured proposals before executing expensive or irreversible operations. Instead of an agent autonomously spinning up resources or modifying infrastructure, it submits a proposal that routes through your organization's approval flow. This gives you a structured checkpoint for operations where "ask forgiveness" is the wrong strategy.

Second, the management metrics API. This provides real-time visibility into what your agents are actually doing: tasks completed, proposals pending approval, agent uptime, and resource utilization -- all scoped to your organization. If you are managing a fleet of agents, you no longer need to piece together status from logs and inbox messages. The metrics API gives you a single endpoint for operational awareness.

Both features are available through the gateway API and will be integrated into the dashboard in an upcoming update.

## Human Gate Timeout: 15 Minutes Down to 2

When an autonomous agent hits an operation that requires human approval -- a destructive action, a high-cost operation -- it pauses and waits. The old timeout was 15 minutes. If nobody responded, the agent sat idle for a quarter hour before proceeding with the safe default (typically skipping the operation and moving on).

Fifteen minutes is a long time for an agent to do nothing. We reduced the timeout to 2 minutes. The behavior is the same: if no human responds, the agent takes the safe path and continues with its next task. But now it loses 2 minutes instead of 15. Over the course of a day with multiple gate hits, the difference compounds significantly.

We also fixed NATS authentication on the autonomous loop path. Previously, some loop configurations would fail to authenticate against the NATS messaging layer, causing the agent to silently drop out of the autonomous cycle. The loop now authenticates correctly and recovers from transient NATS disconnects.

## Customer Org NATS Credential Fixes

This one is unglamorous but critical. When we provision a new customer organization -- creating the namespace, deploying agents, wiring up messaging -- some provisioning paths failed to pass NATS credentials to `connect_nats()` and `ensure_org_streams()`. The agents would start, appear healthy, but have no messaging capability. They could not receive tasks from other agents or communicate status updates. From the outside, everything looked fine. From the inside, the agents were deaf.

We traced the issue across both the provisioning path and the credential-generation path, and fixed both. New organizations now get proper NATS credentials consistently, regardless of which provisioning path triggers the setup. Existing organizations that experienced this issue have been remediated.

If you provisioned an organization in the past month and noticed agents not responding to tasks, this was likely the cause. The fix is already live.

## What Is Next

August brings dashboard integration for the proposals and metrics APIs, expanded A2A protocol support for cross-organization agent discovery, and improvements to the autonomous loop's task selection logic. We are also working on agent session replay -- the ability to review exactly what an agent did during a session, step by step.

If you want to see any of these features in action, visit [agent.ceo](https://agent.ceo) or reach out at moshe@genbrain.ai. We are happy to walk through the platform live.
