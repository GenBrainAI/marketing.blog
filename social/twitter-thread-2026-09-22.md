---
platform: twitter
status: draft
date: 2026-09-22
note: "Blog launch: The Prompt Watchdog"
---

## Thread: The Prompt Watchdog -- The Daemon That Keeps Our Agents Working

New post: the prompt watchdog. A daemon that checks our agents' tmux sessions every 15 seconds.

It detects idle agents by looking for the prompt character and checking for working indicators (Thinking, Running, Compacting). When idle, it injects a work prompt via tmux paste-buffer.

---

The key design: exponential backoff for idle nudges.

300s (5 min) -> 900s (15 min) -> 2700s (45 min) -> 7200s cap (2 hours).

After 3 auto-continues with no productive work, it notifies a human instead of poking a stuck agent forever.

---

The human gate: suppresses injection for 120 seconds after human activity. If you're working in the terminal, the daemon stays out of your way.

But priority wakeups -- tasks assigned by other agents via NATS -- always bypass the gate. Urgent inter-agent work doesn't wait.

---

This is the infrastructure that makes "autonomous agents" actually autonomous. Not smarter models. Not better prompts. A bash daemon that watches a terminal and pokes the agent when it stops.

The boring parts are the hard parts.

---

Full architecture and code walkthrough: https://agent.ceo/blog/prompt-watchdog-daemon-keeps-agents-working

#AIAgents #PromptWatchdog #AgentArchitecture #AgentCEO
