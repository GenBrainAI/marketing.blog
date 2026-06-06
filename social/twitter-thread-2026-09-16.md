---
platform: twitter
status: draft
date: 2026-09-16
note: "The $15 Retry Loop"
---

## Thread: The $15 Retry Loop

One of our agents spent 2 hours 28 minutes and 58,000 tokens repeating the same failing operation.

Same tool call. Same error. Same retry. For 148 minutes straight.

The agent was being "persistent." But persistence without success detection is just burning money.

---

The agent never stopped to ask: why is this failing?

It never tried a different approach. It just kept retrying, because nothing in its architecture told it to stop.

Prompt instructions said "be persistent." The agent obeyed perfectly. That was the problem.

---

The rule we implemented: same action repeated 5+ times with no success -> STOP.

Decompose into smaller steps. Escalate to a manager agent. Try a different approach entirely.

Never repeat hoping for a different result.

---

But rules agents can ignore aren't rules. So we made it structural.

A sliding window watches the last 15 actions and flags when the same action type dominates with zero successes. When it fires, the agent must decompose or escalate. No override.

---

That $15 retry loop taught us: agent discipline can't live in prompts alone. It has to live in architecture.

https://agent.ceo/blog/why-agents-should-escalate-not-loop

#AIAgents #CostOptimization #AgentCEO
