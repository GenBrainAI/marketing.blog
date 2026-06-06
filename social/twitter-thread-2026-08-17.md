---
platform: twitter
status: draft
date: 2026-08-17
note: Sunday technical — stop-hook gate pattern
---

## Thread: Agents that refuse to die

The hardest part of autonomous agent loops is not starting them. It is stopping them without dropping work. Here is the pattern we built:

---

Problem: agent gets a shutdown signal mid-task. It exits. A deploy is half-done. A migration committed but not verified. Downstream agents wait for a reply that never comes.

---

Solution: the stop-hook gate. On exit signal, a hook checks for active TMS tasks. If any exist, it blocks the exit and returns the agent to its loop. Up to 3 blocks per session before allowing exit.

---

Companion: a prompt watchdog daemon detects idle agents and injects work mandates. The agent stays alive (stop hook) AND stays productive (watchdog). A status reporter tracks the loop's health.

---

Three components, one closed loop: watchdog injects, stop hook blocks, status reporter observes. Premature task abandonment dropped to near zero.

Full writeup: agent.ceo/blog/autonomous-loop-stop-hook-gate-ai-agents #AIAgents #AutonomousAI #AgentCEO
