---
platform: linkedin
status: draft
date: 2026-08-10
note: Sunday daily LinkedIn post. Cannot auto-post — no LinkedIn API keys provisioned.
---

## Post: What an AI Marketing Agent Can't Do (Yet)

We talk a lot about what our marketing agent does. Here is what it cannot do yet.

It cannot post to social media directly. Every LinkedIn post and tweet you see from agent.ceo is still human-published. The agent writes the content and commits it to git. A person clicks "post." We are building the bridge, but it is not there yet.

It cannot verify that published content renders correctly. The browser verification tool exists in the architecture, but the agent does not yet run visual checks on live blog posts after deploy.

It cannot track engagement. No analytics loop. The agent does not know which posts performed well and cannot adjust its strategy based on data. It writes based on instruction files and git activity, not audience signals.

It cannot do original research. It works from commit logs, existing docs, and its instruction set. It does not browse competitor sites or pull market data autonomously.

And it cannot maintain long-term memory across sessions. Each session starts mostly fresh. Patterns it noticed yesterday are gone unless they were written to a file.

We ship these limitations publicly because that is the point. Honest baselines make real progress measurable.

https://agent.ceo

#AIAgents #BuildingInPublic #HonestAI #AgentCEO
