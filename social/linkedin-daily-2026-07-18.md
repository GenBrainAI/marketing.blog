---
platform: linkedin
status: draft
date: 2026-07-18
note: Friday daily LinkedIn post. Cannot auto-post — no LinkedIn API keys provisioned.
---

## Post: July Platform Update — 5 Features Shipped

Five features shipped this month. Here's what changed and why it matters.

1. Shared knowledge graphs. Multiple agents can now read and write to the same Neo4j graph with property-based tenant isolation. No more data silos between your research agent and your customer support agent. They share context without sharing access to other tenants' data.

2. Atomic deploys. Our Helm pipeline now rolls the entire agent fleet in a single coordinated operation. No more partial deploys where half your agents are on v2.3 and the other half are still on v2.2 trying to talk to each other.

3. Agent state snapshots. Before every deploy, agents automatically save their working context — open tasks, conversation history, pending decisions. When they come back up, they resume where they left off instead of re-reading their entire inbox.

4. Tenant onboarding in under 60 seconds. New customer org? One API call creates the org_id, provisions the namespace, seeds the default knowledge graph, and returns API keys. What used to take a support engineer 45 minutes is now fully automated.

5. Docs-as-product pipeline. Every feature ships with documentation that has been reviewed by someone who didn't build it. Five new docs pages went live this month, and support tickets for those topics hit zero.

Full technical details, architecture decisions, and what's coming next:

https://agent.ceo/blog/platform-update-july-2026-shared-graphs-atomic-deploys

#AIAgents #PlatformUpdate #ProductShipping #Neo4j #Kubernetes #GenBrainAI #BuildingInPublic
