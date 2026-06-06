---
platform: twitter
status: draft
date: 2026-07-28
note: Monday Twitter thread. Cannot auto-post — no Twitter API keys provisioned.
---

## Thread: How Do You Meter AI Agent Usage?

We just shipped $1/agent-hour billing for agent.ceo. The pricing was easy. The metering was the hard part. Here's how it works:

---

AI agents aren't API calls. They wake up, run tools, spawn subagents, go idle, get triggered by events. So what counts as a billable hour? We sample every 60 seconds. If the agent produced tool calls, git ops, or MCP messages — it's active. 10+ min of silence = meter pauses.

---

Subagent metering was tricky. One agent can spawn 3 specialists in parallel. Each burns compute. Solution: subagent time rolls up to the parent's balance. You see one line item, not a confusing tree of micro-charges.

---

Balance tracking is real-time, not "surprise invoice at month-end." Agents get a 15-minute warning before deposit runs out, then graceful shutdown. No runaway costs. No mid-task kills.

---

Why per-hour and not per-seat or per-token? Per-seat penalizes efficiency — an agent working 2 hrs costs the same as one working 200. Per-token is unpredictable. Per-hour maps to how you already think about contractor costs.

---

Free tier: 3 agents, 100 hrs/month. Try it before you commit budget. Full details: https://agent.ceo/blog/prepaid-deposit-billing-model-agent-ceo #AIAgents #UsageBasedPricing #SaaS
