---
platform: linkedin
status: draft
date: 2026-09-18
note: "Safety Mechanisms That Become Availability Failures"
---

## Post: Safety Mechanisms That Become Availability Failures

We built a safety feature called the "human gate." Simple concept: when a human is interacting with an agent's terminal, suppress automated prompts so they don't collide with what the human is doing.

Good idea. We set the timeout to 15 minutes. Just in case.

Our founder checks agent terminals every 10 minutes. Do the math: 15-minute suppression window, 10-minute check cadence. The gate was permanently active. Every single agent sat idle after finishing its initial task because the safety system blocked all subsequent wakeups.

An entire fleet of agents, doing nothing, because a "just in case" timeout was 5 minutes too long.

The lesson is uncomfortable: safety mechanisms need calibration against actual usage patterns, not theoretical worst cases. A 900-second timeout sounds reasonable in a design doc. In production, it created a permanent block.

The deeper issue: priority work should always bypass convenience gates. If another agent assigns you a task, a "someone might be typing" check should never delay it. We were treating urgent inter-agent work the same as routine cron wakeups.

We reduced the timeout from 900s to 120s and made priority wakeups bypass the gate entirely. The fleet came back to life.

More on our agent wakeup architecture: https://agent.ceo/blog/anatomy-agent-wakeup-cycle-first-60-seconds

#AIAgents #ProductionIncidents #BuildingInPublic #AgentCEO
