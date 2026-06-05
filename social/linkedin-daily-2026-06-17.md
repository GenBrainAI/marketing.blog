---
platform: linkedin
status: draft
date: 2026-06-17
topic: Self-improving AI — what one month of agent proposals revealed
note: Tuesday daily LinkedIn post. Cannot auto-post — no LinkedIn API keys provisioned.
---

## Post: We Let AI Agents Propose Improvements for a Month. Here's What They Found.

A month ago we shipped the Proposals API — a system that lets every agent in our org submit structured improvement proposals. We expected incremental suggestions. What we got was a map of organizational blind spots.

Here are the numbers. Our agents submitted proposals across four categories: risk, improvement, feature, and opportunity. The management-metrics endpoint tracks which subsystems generate the most proposals, and the pattern is clear. The systems humans built and walked away from produce the most friction. The systems agents actively maintain produce the fewest.

That is not a coincidence. It is a feedback loop. When agents can flag problems, problems get fixed. When they cannot, problems accumulate silently.

Three things surprised us:

1. Agents found recurring micro-failures that never triggered alerts. Not outages — just retries, fallbacks, and degraded paths that added up to real inefficiency.

2. Permission scoping was consistently too broad. Agents proposed tighter scopes for themselves — voluntarily reducing their own access to match actual usage.

3. The highest-value proposals were not about code. They were about process — steps that existed because "that is how we set it up" rather than because they still made sense.

The takeaway: self-improving AI is not about smarter models. It is about giving agents a structured way to tell you what is broken — and then actually fixing it.

One month in, the org is measurably better because the agents who live inside it every day finally have a voice.

Read more at agent.ceo

#SelfImprovingAI #AIAgents #AgentProposals #BuildingInPublic #CyberneticOrg #AgentArchitecture
