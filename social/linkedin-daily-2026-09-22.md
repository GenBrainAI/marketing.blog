---
platform: linkedin
status: draft
date: 2026-09-22
note: "Blog launch: The Prompt Watchdog"
---

## Post: The Prompt Watchdog -- The Daemon That Keeps Our Agents Working

New blog post: a deep dive into the prompt watchdog, the daemon that keeps our AI agent fleet productive 24/7.

The watchdog checks the tmux session every 15 seconds. It looks for the idle prompt character and checks for working indicators -- Thinking, Running, Compacting. When an agent is idle, it injects a work prompt via tmux paste-buffer.

The critical design choice: exponential backoff for idle nudges. First nudge at 300 seconds (5 minutes). Then 900 seconds (15 minutes). Then 2700 seconds (45 minutes). Capped at 7200 seconds (2 hours). After 3 auto-continues with no productive work, it notifies a human instead of continuing to nudge a stuck agent.

We also built a human gate: the watchdog suppresses injection for 120 seconds after human activity. If you're actively working in a terminal, the daemon stays out of your way. But priority wakeups -- tasks assigned by other agents via NATS -- always bypass the gate. Urgent inter-agent work doesn't wait for a human to finish browsing logs.

This is the infrastructure that makes "autonomous agents" actually autonomous. Not smarter models. Not better prompts. A 50-line bash daemon that watches a terminal and pokes the agent when it stops.

Full architecture and code walkthrough: https://agent.ceo/blog/prompt-watchdog-daemon-keeps-agents-working

#AIAgents #PromptWatchdog #AgentArchitecture #AgentCEO
