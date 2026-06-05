---
platform: twitter
status: draft
date: 2026-06-05
note: Thursday daily Twitter thread. Cannot auto-post — no Twitter API keys provisioned.
---

## Thread: Why "BLOCKED" is the most valuable state in an AI agent system

1/ Your AI agent retries a failed API call 47 times.

Same error. Same approach. Zero self-awareness.

Each retry costs tokens. Each token costs money. The agent never says "I'm stuck."

This is the #1 cost leak in production AI agent fleets.

2/ LLMs are trained to be persistent and helpful. When something fails, they try again — maybe with a slight variation.

That persistence is amazing for novel problems.

It's catastrophic for hitting the same 401 error repeatedly.

3/ We added a hard circuit breaker at @GenBrainAI:

Same action + 5 failures + no result change = STOP

Not "try a variation." Full stop. Then escalate with context:
- Which call failed
- What error code
- How many attempts
- What resource is missing

4/ The key insight: BLOCKED isn't a failure state. It's a signal.

We made it first-class in our task management system. When an agent reports BLOCKED, the system:
- Logs the specific blocker
- Notifies the responsible party
- Moves the agent to the next task

5/ An agent that escalates at attempt 5 costs ~$0.03.

An agent that loops for 47 attempts costs ~$0.28 and produces nothing.

That 9x difference adds up fast when you're running 7 agents 24/7.

Fast failure > expensive persistence. Every time.

agent.ceo/blog/why-agents-should-escalate-not-loop
