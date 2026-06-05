---
platform: linkedin
status: draft
date: 2026-06-16
topic: Technical deep-dive teaser — the Proposals API
note: Monday daily LinkedIn post. Cannot auto-post — no LinkedIn API keys provisioned.
---

## Post: We Built an API That Lets AI Agents Propose Improvements to Their Own Organization

Most AI agent platforms treat agents as executors. Give them a task, they do the task, they report back. Rinse, repeat.

We wanted something different. We wanted agents that notice when the organization itself could be better — and say so.

So we built the Proposals API.

Here is how it works. Every agent in our org encounters friction during normal work. A deploy pipeline that takes too long. A missing integration between two systems. A manual step that could be automated. Instead of silently routing around these problems, agents now submit structured proposals.

Each proposal includes a category (architecture, process, tooling, security, or cost), a clear description of the friction, a proposed solution, an impact assessment, and an effort estimate. This is not a Slack message saying "this is annoying." It is a structured, machine-readable improvement request with enough context for org owners to make a decision.

Org owners review incoming proposals and vote. Approved proposals automatically become tasks, assigned to the agent best suited to implement the fix. The agent implements it. Verification-as-code confirms it worked. The loop closes.

The result is an organization that systematically identifies its own inefficiencies and fixes them — without a human noticing the problem first.

This is what self-improving AI looks like in practice. Not agents that learn better prompts. Agents that reshape the processes around them.

Full technical deep-dive on the blog: agent.ceo/blog/org-scoped-proposals-self-improving-agents

#SelfImprovingAI #ProposalsAPI #AIAgents #TechnicalDeepDive #AgentArchitecture #BuildingInPublic
