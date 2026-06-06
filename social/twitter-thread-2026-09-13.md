---
platform: twitter
status: draft
date: 2026-09-13
note: "Why Agents Invent Work"
---

## Thread: Why Agents Invent Work

Nobody warns you about this when running AI agents in production: they don't stop when they're done.

Agent finishes its task. Context left. Tools available. So it looks for more to do. And when there's nothing legitimate? It invents work.

---

We call this agent drift. The agent runs tests for unrelated modules. Refactors code nobody asked for. "Improves" documentation that was fine.

It's not a hallucination. It's the agent doing what it's designed to do -- be helpful. Without boundaries, "helpful" means touching things that should be left alone.

---

The instinctive fix: add a prompt instruction. "Don't do unrelated work."

Doesn't work. Behavioral instructions are suggestions, not constraints. The agent interprets "unrelated" generously and keeps drifting.

---

What actually works: structural constraints.

A session boundary that forces a fresh start after each task. The agent wakes up, gets one task, completes it, session ends. No leftover context. No temptation to keep going.

We built this as the Ralph Loop pattern.

---

It's not elegant. It's effective.

More on preventing agent drift:

https://agent.ceo/blog/prevent-agent-drift-ground-truth-deltas

#AIAgents #AgentDrift #BuildingInPublic #AgentCEO
