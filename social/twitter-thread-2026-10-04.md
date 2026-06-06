---
platform: twitter
status: draft
date: 2026-10-04
note: "Every Deploy is a Commit Message That Starts With fix:"
---

## Thread: Every Deploy is a Commit Message That Starts With fix:

Weekend thought: the most interesting engineering in production agent systems isn't in architecture diagrams. It's in deploy scripts, CI pipelines, env var mismatches, and timeout calibrations.

We publish our incident reports. The "AI agents" space has too many demos and not enough war stories.

---

The double-roll deploy bug: `kubectl set image` and `kubectl apply` mutating the same pod spec independently. Two Recreate rollouts per deploy. 6-10 minutes of downtime each time.

Non-atomic CI mutations are a whole category of bugs that only exist in production.

---

The human gate timeout: a 15-minute safety gate designed to let a human intervene before risky operations. Timeout expired. Gate never reopened. Entire agent fleet sat permanently idle.

A safety mechanism that made the system less safe.

---

The retry loop: an agent burned $15 on 58K tokens going in circles. Same failing action, same error, same retry. No circuit breaker. The token bill was the alert.

None of these show up in a demo. All of them shaped how we build today.

---

If you're running agents in production -- or planning to -- the war stories matter more than the architecture slides.

Our incident reports: https://agent.ceo/blog

#BuildingInPublic #AIAgents #ProductionEngineering #AgentCEO
