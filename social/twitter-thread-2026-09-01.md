---
platform: twitter
status: draft
date: 2026-09-01
note: "Monday technical — hook system categories thread"
---

## Thread: The Hook System That Makes Agent Rules Unbreakable

We run AI agents in production with Claude Code. They follow rules — not because we asked nicely, but because Python hooks enforce every rule at runtime.

Here is how the hook system works, one category at a time:

---

Session start hooks: ground-truth delta. When an agent wakes up, a hook diffs the codebase against the agent's last known state. It surfaces what changed while the agent was offline.

Result: no agent re-does work another agent already shipped.

---

Policy gate: pre_tool_use.py. Every tool call passes through a policy gate before execution. The gate returns allow, deny, or ask.

"Never push to main" is not a line in a doc. It is a gate that intercepts the git push and returns deny. The push never executes.

---

Observation hooks: JSONL audit trail. Every tool call is logged — tool name, arguments, timestamp, agent ID. When an agent misbehaves, you replay the exact sequence of actions. No guessing.

---

Human interaction tracking. When a user chats with an agent, hooks detect the interaction and the autonomous loop stands down. The agent knows it is in a conversation, not running a background task.

---

Cybernetic learning: anti-pattern to gate to block. When we find a recurring failure mode, we compile it into an anti-pattern index. The policy gate checks every tool call against the index.

Document the failure once. Prevent it forever.

Full deep-dive: agent.ceo/blog/hook-system-enforce-agent-discipline-runtime

#AIAgents #AgentArchitecture #BuildingInPublic #AgentCEO
