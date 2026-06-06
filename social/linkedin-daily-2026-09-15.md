---
platform: linkedin
status: draft
date: 2026-09-15
note: "Blog launch: The Ralph Loop — One Task Per Session"
---

## Post: The Ralph Loop -- One Task Per Session

New blog post: the Ralph Loop, our structural anti-drift pattern for AI agents.

The problem it solves: agents that finish their assigned work, then keep going -- refactoring code nobody asked for, running tests on unrelated modules, "improving" things that were fine. Prompt instructions don't prevent this. Structure does.

The Ralph Loop uses three files:

- current-task.json -- what to work on right now
- backlog.json -- what's next, sorted by priority
- A FRESH_START signal that forces a completely new session after each task

The agent wakes up, gets exactly one task injected into its context, works on it, marks it done, and the session wrapper starts a completely fresh session for the next task. No context bleeding between tasks. No invented work.

Three sources feed tasks into the loop: NATS inbox messages from other agents, directive files from the operator, and the shared task registry (TMS). The backlog stays prioritized. The agent never has to decide what to do next -- the structure decides for it.

It's a simple pattern. That's the point. The fewer decisions the agent makes about what to work on, the more reliably it works on the right thing.

Full technical writeup: https://agent.ceo/blog/ralph-loop-one-task-per-session-anti-drift

#AIAgents #RalphLoop #AgentArchitecture #AgentCEO
