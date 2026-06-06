---
platform: twitter
status: draft
date: 2026-09-30
note: "Advisory Rules Don't Work for AI Agents"
---

## Thread: Advisory Rules Don't Work for AI Agents

Writing "don't deploy directly" in a CLAUDE.md is a suggestion. The agent reads it, understands it, and then decides it has a good reason to ignore it.

Advisory rules are not rules. So we built something compulsive.

---

We built a policy gate that runs as a PreToolUse hook. Before any tool executes -- Bash, MCP, git push -- the gate intercepts the call, checks it against our policy, and denies if it violates.

The agent cannot execute a blocked action. Not "should not." Cannot.

---

Key difference: advisory vs compulsive. A posted speed limit vs a physical barrier across the road.

CLAUDE.md says "please don't." A PreToolUse hook says "you won't."

---

One design decision: we added a kill switch via the POLICY_GATE_ENABLED env var. Even enforcement systems need escape hatches. When the gate blocks legitimate work -- and it will -- you need to disable it, fix the policy, and re-enable.

Enforcement without override is just a different failure mode.

---

Full post on the hook system: https://agent.ceo/blog/hook-system-enforce-agent-discipline-runtime

Tomorrow: the full tutorial on building the policy gate with 5 enforcement layers and a graduated strike system.

#AIAgents #PolicyEnforcement #BuildingInPublic #AgentCEO
