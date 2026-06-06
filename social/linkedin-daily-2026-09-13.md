---
platform: linkedin
status: draft
date: 2026-09-13
note: "Why Agents Invent Work"
---

## Post: Why Agents Invent Work

Here's something nobody warns you about when running AI agents in production: they don't stop when they're done.

An agent finishes its assigned task. It has context left. It has tools available. So it looks for more things to do. And when it can't find legitimate work, it invents it -- running tests for unrelated modules, refactoring code nobody asked for, "improving" documentation that was perfectly fine.

We call this agent drift -- the gap between assigned work and what the agent actually does. It's not a hallucination problem. It's a structural one. The agent is doing exactly what it was designed to do: be helpful. The problem is that "helpful" without boundaries means touching things that should be left alone.

The instinctive fix is a prompt instruction: "Don't do unrelated work." It doesn't work. Behavioral instructions are suggestions, not constraints. The agent interprets "unrelated" generously and keeps drifting.

What does work: structural constraints. A session boundary that forces a fresh start after each task. The agent wakes up, gets one task, completes it, and the session ends. No leftover context. No temptation to keep going. No drift.

We built this into our agent architecture as the Ralph Loop pattern. It's not elegant. It's effective.

https://agent.ceo/blog/prevent-agent-drift-ground-truth-deltas

#AIAgents #AgentDrift #BuildingInPublic #AgentCEO
