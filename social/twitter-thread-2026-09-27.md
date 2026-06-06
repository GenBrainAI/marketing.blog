---
platform: twitter
status: draft
date: 2026-09-27
note: "The Most Important Code in Our Agent System Is a Bash Script"
---

## Thread: The Most Important Code in Our Agent System Is a Bash Script

The most critical infrastructure in our AI agent fleet isn't Python. Isn't the model. Isn't MCP tools.

It's a ~1,200-line bash wrapper script. It keeps Claude Code running.

The AI does the thinking. The bash script keeps it alive.

---

When people ask about our agent fleet, they ask about the model, the prompts, the tool integrations. Nobody asks about the outer loop -- the thing that launches the agent, watches for crashes, handles OOM kills, recovers auth failures, and decides when to restart.

---

It manages the difference between "agent finished its work" and "agent died unexpectedly." Two situations that look similar from the outside but need completely different responses. One means sleep. The other means recover and relaunch.

---

When this script breaks, every agent in the fleet stops. Not degrades. Stops. We've had fleet-wide outages caused by subtle shell bugs -- nothing to do with AI, nothing to do with application logic. Pure wrapper failure.

Unglamorous. Essential.

---

We wrote about the first 60 seconds of an agent wakeup -- what the bash script actually does before the AI even starts thinking: https://agent.ceo/blog/anatomy-agent-wakeup-cycle-first-60-seconds

#AIAgents #Infrastructure #BuildingInPublic #AgentCEO
