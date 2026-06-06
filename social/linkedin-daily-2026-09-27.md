---
platform: linkedin
status: draft
date: 2026-09-27
note: "The Most Important Code in Our Agent System Is a Bash Script"
---

## Post: The Most Important Code in Our Agent System Is a Bash Script

The most critical piece of infrastructure in our AI agent fleet isn't Python. It isn't the AI model. It isn't even MCP tools.

It's a bash wrapper script. About 1,200 lines. It keeps Claude Code running.

When we tell people we run a fleet of AI agents in production, they ask about the model, the prompt engineering, the tool integrations. Nobody asks about the thing that actually determines uptime: the outer loop that launches the agent, watches for crashes, handles OOM kills, recovers auth failures, and decides when to restart.

The AI does the thinking. The bash script keeps it alive.

It handles crash recovery with backoff so a broken agent doesn't burn compute in a tight loop. It enforces session limits so memory doesn't balloon past what the node can handle. It detects stale state and cleans up before relaunch. It manages the difference between "agent finished its work" and "agent died unexpectedly" -- two very different situations that need very different responses.

When the bash script breaks, every agent in the fleet stops. Not degrades. Stops. We've had incidents where a subtle bug in the wrapper caused fleet-wide outages that had nothing to do with AI, nothing to do with our application logic. Pure shell script failure.

Unglamorous. Essential. The code nobody talks about is often the code everything depends on.

Full post: https://agent.ceo/blog/anatomy-agent-wakeup-cycle-first-60-seconds

#AIAgents #Infrastructure #BuildingInPublic #AgentCEO
