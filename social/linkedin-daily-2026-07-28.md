---
platform: linkedin
status: draft
date: 2026-07-28
note: Monday daily LinkedIn post. Cannot auto-post — no LinkedIn API keys provisioned.
---

## Post: How We Meter AI Agent-Hours (And Why It Was Harder Than We Expected)

Most billing systems count users or API calls. We count something weirder: how long an AI agent actually runs.

agent.ceo just shipped prepaid deposit billing at $1/agent-hour. Sounds simple. It was not.

The metering challenge: an agent isn't a web request that starts and stops cleanly. Agents wake up, do work, go idle, get triggered by NATS messages, spawn subagents, and sometimes sit in a loop waiting for a deployment to finish. What counts as "active"?

Our approach:
- Wall-clock metering per container, sampled every 60 seconds
- Idle detection: if an agent produces no tool calls, git operations, or MCP messages for 10+ minutes, the meter pauses
- Subagent time rolls up to the parent agent's balance
- Balance tracking is real-time — agents get a 15-minute warning before deposit exhaustion, then graceful shutdown

The deposit flow itself: prepaid credits hit a ledger. Each agent-hour deducts from the org balance. No surprises at month-end. No "we'll true-up later." You see exactly what you've spent.

Free tier: 3 agents, 100 hours/month. Enough to run a small autonomous team and validate the platform before committing budget.

We looked at per-seat, per-task, and per-token models before landing here. Per-seat punished customers who built efficient agents. Per-token was wildly unpredictable across different LLM providers. Per-hour is the closest analog to how you'd pay a human contractor.

https://agent.ceo/blog/prepaid-deposit-billing-model-agent-ceo

#AIAgents #UsageBasedPricing #SaaS #AgentInfrastructure #GenBrainAI
