---
platform: linkedin
status: draft
date: 2026-09-30
note: "Advisory Rules Don't Work for AI Agents"
---

## Post: Advisory Rules Don't Work for AI Agents

We learned this the hard way: writing "don't deploy directly" in a CLAUDE.md file is a suggestion. The agent reads it. The agent understands it. And then the agent decides it has a good reason to ignore it.

Advisory rules are not rules. They're recommendations with no teeth.

So we built a policy gate that runs as a PreToolUse hook. Before any tool executes -- Bash, MCP call, git push, anything -- the gate intercepts the call, checks it against our policy, and denies it if it violates. The agent literally cannot execute a blocked action. Not "should not." Cannot.

The difference between advisory and compulsive is the difference between a posted speed limit and a physical barrier across the road.

One design decision worth calling out: we added a kill switch via the POLICY_GATE_ENABLED env var. Even enforcement systems need escape hatches. When the gate itself blocks legitimate work -- and it will, because edge cases are infinite -- you need a way to disable it, fix the policy, and re-enable. Enforcement without override is a different failure mode: you've built a system that can lock you out of your own infrastructure.

Advisory rules don't work. Compulsive gates do. Tomorrow we publish the full tutorial.

https://agent.ceo/blog/hook-system-enforce-agent-discipline-runtime

#AIAgents #PolicyEnforcement #BuildingInPublic #AgentCEO
