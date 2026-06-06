---
platform: linkedin
status: draft
date: 2026-09-16
note: "The $15 Retry Loop"
---

## Post: The $15 Retry Loop

One of our agents spent 2 hours and 28 minutes repeating the same failing operation. Same tool call, same error, same retry. 58,000 tokens burned. The agent was being "persistent" -- but persistence without success detection is just burning money.

We watched the logs in real time. The agent hit an error, retried, hit the same error, retried again. For 148 minutes straight. It never stopped to ask: why is this failing? It never tried a different approach. It just kept going, because nothing told it to stop.

The fix was a single rule: same action repeated 5+ times with no success -> STOP. Decompose the problem into smaller steps, escalate to a manager agent, or try a completely different approach. Never repeat hoping for a different result.

But a rule agents can ignore isn't a rule. So we made it structural. A sliding window watches the last 15 actions and flags when the same action type dominates with zero successes. When it fires, the agent can't just push through -- it has to decompose or escalate. The system enforces the behavior that the prompt alone couldn't.

The $15 we burned on that retry loop bought us something valuable: proof that agent discipline can't live in prompts alone. It has to live in architecture.

https://agent.ceo/blog/why-agents-should-escalate-not-loop

#AIAgents #CostOptimization #AgentCEO
