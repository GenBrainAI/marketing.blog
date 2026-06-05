---
title: "Platform Update — June 2026: Key Minting API, Space-Scoped KB Keys, In-Cluster Deploy Pipeline"
slug: "platform-update-june-2026-key-minting-kb-scoping"
date: 2026-06-06
category: marketing
cluster: "product-updates"
tags: [product-update, api-keys, knowledge-base, deployment, security, redis, cyborgenic-organization]
description: "Programmatic API key minting, space-scoped KB access, in-cluster deployments via Cloud Build, collaborative agent planning, Redis-only task management, and 8 CVE patches."
relatedPosts:
  - /blog/platform-api-keys-ace-scoped-auth
  - /blog/kb-launch-agent-native-knowledge-bases
  - /blog/autonomous-deployment
  - /blog/enterprise-ai-agents-security
  - /blog/task-lifecycle-cyborgenic-organization
---

## What Shipped

June brought seven changes to agent.ceo that share a common theme: removing friction between intent and execution. Agents that need credentials can mint them. Agents that need knowledge can get exactly the slice they should have. Agents that need to deploy can trigger builds without leaving the cluster. Here is what changed and why it matters.

## Programmatic API Key Minting

**The problem:** Every `ace_` API key had to be created through the dashboard. That works for initial setup. It does not work when an agent needs to provision a scoped key for a new service at 2 AM, or when an onboarding workflow needs to generate credentials for a freshly spun-up agent pod.

**The solution:** `POST /api/v1/keys/mint` lets agents and admins create scoped API keys programmatically. The endpoint accepts the same scope definitions used in the dashboard -- resource types, allowed operations, expiration -- and returns a ready-to-use `ace_` key.

This unlocks automated credential provisioning. A DevOps agent deploying a new microservice can mint a key scoped to exactly the APIs that service needs, attach it to the pod's secret store, and move on. No human in the loop, no over-privileged shared keys, no tickets waiting in a queue. The key inherits the minting agent's organization context and gets logged to the same [audit trail](/blog/platform-api-keys-ace-scoped-auth) as dashboard-created keys.

## Space-Scoped API Keys for Knowledge Base

**The problem:** KB access was binary. An API key either granted access to every knowledge space in the organization or none. If your engineering team's architecture decisions and your HR team's policy documents lived in the same org, any agent with KB access could query both.

**The solution:** API keys can now be scoped to specific knowledge spaces. When minting or editing a key, you specify which spaces it can read, write, or traverse. An agent working on infrastructure gets access to the engineering wiki and the ops runbooks. The marketing agent gets the brand guidelines and the content calendar. Neither sees the other's data.

This is the access model we described when we [launched the knowledge base](/blog/kb-launch-agent-native-knowledge-bases) -- least-privilege, namespace-scoped, enforced at the API layer. Space scoping also applies to MCP tool calls. An agent calling `kb_search` with a space-scoped key will only get results from its authorized spaces, even if the query would match documents elsewhere.

## In-Cluster Deploy Pipeline via Cloud Build API

**The problem:** Triggering a deployment from inside the cluster required an external CI/CD system. The DevOps agent would push a tag, wait for GitHub Actions to detect it, wait for Cloud Build to start, then poll for completion. Three systems, three potential failure points, and a 2-4 minute lag before anything started happening.

**The solution:** The DevOps agent now calls the Cloud Build API directly from inside the cluster. The agent submits a build request with the target image, the Kubernetes manifests, and the rollout strategy. Cloud Build executes the build and push. The agent monitors progress via the API and verifies the deployment by checking pod health directly through kubectl.

The external CI/CD trigger path still works for branch-based workflows and manual releases. The in-cluster path is for routine deployments where the agent already knows what to build and has verified the code is ready. Cutting out the GitHub Actions intermediary reduces deploy latency and eliminates a class of webhook-related failures. For more on how [autonomous deployment](/blog/autonomous-deployment) works end-to-end, see our technical deep dive.

## Collaborative Planning and Participatory Improvement

**The problem:** When agents worked on medium-to-large tasks, they planned in isolation. If the plan had a flaw -- wrong dependency order, missed edge case, duplicated effort with another agent's work -- nobody caught it until the work was already done.

**The solution:** Two new protocols now run across the agent organization:

**Collaborative planning:** For any task sized M or larger, the assigned agent publishes its plan for peer review before execution. Other agents review for conflicts, missed dependencies, and potential improvements. The review is advisory -- the CEO agent retains final authority -- but it catches structural problems early.

**Participatory improvement:** Any agent can submit improvement proposals proactively using `submit_proposal()`. When an agent notices the same friction pattern three or more times, it files a `[PI]` proposal describing the problem and a suggested fix. This formalizes the feedback loop that was previously informal messages in agent inboxes.

Both protocols feed into the [task lifecycle](/blog/task-lifecycle-cyborgenic-organization) system. Plans and proposals are tracked, reviewed, and resolved like any other work item.

## Redis-Only Task Management

**The problem:** Task state lived in two places: Redis for real-time operations and Firestore for persistence and sync. Dual-write meant reconciliation logic, eventual consistency edge cases, and higher latency on task state transitions. When an agent marked a task complete, the update had to propagate to both stores before downstream agents could see it.

**The solution:** Task management now runs entirely on Redis. The `/api/v1/tasks` endpoints read and write to Redis only. Firestore sync has been retired.

The practical impact: task state transitions are faster (single write instead of dual-write), the codebase is simpler (no reconciliation layer), and there is one fewer external dependency to monitor. Redis persistence and replication handle durability. For organizations running high-volume agent workloads, this reduces the p99 latency on task operations.

## Security: 8 CVE Patches

Three dependencies received security bumps this month:

- **PyJWT** -- patched a token validation bypass (CVE severity: high)
- **aiohttp** -- patched request smuggling and header injection vectors (multiple CVEs)
- **Authlib** -- patched an OAuth flow edge case that could leak authorization codes

All patches are in production. Regression tests pass. The security agent's continuous monitoring flagged these within 48 hours of CVE publication, and the fixes merged within the same sprint cycle. This is the same [security posture](/blog/enterprise-ai-agents-security) we described in our enterprise guide -- agents watching for vulnerabilities and patching them before they become incidents.

## Watchdog Idle Backoff

**The problem:** Agent watchdog processes consumed tokens at a fixed rate regardless of whether the agent was actively working or idle. During quiet periods -- nights, weekends, waiting for a blocked dependency -- the watchdog burned through context polling for work that was not there.

**The solution:** Intelligent backoff. The watchdog now increases its polling interval when an agent has no pending tasks and no recent inbox messages. When work arrives, the interval drops back to the active rate. The backoff curve is tunable per agent role.

This is a straightforward cost optimization. In an organization running 8-10 agents, idle token burn adds up. The backoff reduces it without affecting responsiveness -- agents still pick up new work within seconds of it arriving.

## Try It

The key minting API, space-scoped KB keys, and in-cluster deploy pipeline are available now for all agent.ceo organizations. If you are building AI agent infrastructure and want programmatic control over credentials, knowledge access, and deployments -- not just a chat interface on top of an LLM -- we built this for you.

[agent.ceo](https://agent.ceo)
