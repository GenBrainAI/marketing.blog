---
platform: twitter
status: draft
date: 2026-09-29
note: "Blog launch: The Outer Loop: How a Shell Script Keeps Agents Alive"
---

## Thread: The Outer Loop: How a Shell Script Keeps Agents Alive

New post: the full architecture of the shell script that keeps our AI agent fleet alive.

Pre-flight checks, crash recovery, 6 loop strategies, and edge-triggered work detection. Here's the breakdown.

---

Pre-flight: before the agent launches, the wrapper enforces a 256MB session size limit and an 80% memory threshold. If the node is under memory pressure, the agent waits. Better to delay than to launch and immediately get OOM-killed.

---

Crash recovery runs in 3 stages. Immediate relaunch first. If that fails, increasing backoff delays. If crashes persist, cooldown period. Each stage prevents the failure mode above it from burning compute.

6 loop strategies: continuous, task-driven, interval-poll, backoff, scheduled, event-driven. Each agent gets the strategy that fits its workload.

---

The best bug we found: the default fallback in the strategy switch was `sleep 2`. Invalid strategy type in config? Fall through to default. Loop every 2 seconds. Forever.

Fix: changed default to `sleep 60`. Conservative defaults in an outer loop aren't optimization -- they're survival.

---

Full architecture post: https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#AIAgents #OuterLoop #AgentArchitecture #AgentCEO
