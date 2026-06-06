---
platform: linkedin
status: draft
date: 2026-09-29
note: "Blog launch: The Outer Loop: How a Shell Script Keeps Agents Alive"
---

## Post: The Outer Loop: How a Shell Script Keeps Agents Alive

New blog post. We wrote up the full architecture of the shell script that keeps our AI agent fleet running.

The outer loop manages the entire agent lifecycle:

Pre-flight checks enforce a 256MB session size limit and an 80% memory threshold before the agent even launches. If the node is under memory pressure, the agent waits instead of launching and immediately getting OOM-killed.

Crash recovery runs in 3 stages. First attempt: immediate relaunch. If that fails, back off with increasing delays. If crashes persist, enter a cooldown period before trying again. Each stage prevents the failure mode above it from burning compute.

The script supports 6 loop strategies: continuous, task-driven, interval-poll, backoff, scheduled, and event-driven. Each agent gets the strategy that fits its workload. A monitoring agent polls on intervals. A task agent sleeps until work arrives.

The most instructive bug we found: the default fallback case in the strategy switch statement was `sleep 2`. If an agent had an invalid strategy type set in its config, it would fall through to the default case and loop every 2 seconds. Forever. We changed the default to `sleep 60` -- a conservative fallback that turns a potential hot loop into a slow poll.

Conservative defaults in an outer loop aren't optimization. They're survival.

Full architecture: https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#AIAgents #OuterLoop #AgentArchitecture #AgentCEO
