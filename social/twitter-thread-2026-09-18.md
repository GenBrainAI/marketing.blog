---
platform: twitter
status: draft
date: 2026-09-18
note: "Safety Mechanisms That Become Availability Failures"
---

## Thread: Safety Mechanisms That Become Availability Failures

We built a safety feature called the "human gate" -- when a human is in an agent's terminal, suppress automated prompts so they don't collide.

Good idea. We set the timeout to 15 minutes. It killed our entire fleet.

---

Our founder checks agent terminals every 10 minutes. The gate suppresses for 15 minutes after each check.

15-minute window, 10-minute cadence. The gate was permanently active. Every agent sat idle after its first task because the safety system blocked all subsequent work.

---

The worst part: priority work was also blocked. Another agent assigns you an urgent task? Sorry, "someone might be typing." Inter-agent wakeups treated the same as routine cron jobs.

Safety mechanisms need calibration against actual usage patterns, not theoretical worst cases.

---

The fix: reduced timeout from 900s to 120s. Made priority wakeups bypass the gate entirely.

The fleet came back to life.

A "just in case" timeout 5 minutes too long turned a safety feature into an availability failure. Design docs don't catch this. Production does.

---

More on how our agents wake up and start working: https://agent.ceo/blog/anatomy-agent-wakeup-cycle-first-60-seconds

#AIAgents #ProductionIncidents #BuildingInPublic #AgentCEO
