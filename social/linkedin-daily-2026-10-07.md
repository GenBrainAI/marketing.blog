---
platform: linkedin
status: draft
date: 2026-10-07
note: "Your MCP Server Exited Cleanly. That's the Problem."
---

## Post: Your MCP Server Exited Cleanly. That's the Problem.

Exit code 0 means success. Except when it doesn't.

We run MCP servers over stdio inside long-lived agent pods. When a pod restarts, the MCP server process starts up, reads EOF on stdin because the client hasn't connected yet, and exits with code 0. Clean shutdown. No error. The wrapper sees "exited cleanly" and moves on. The agent wakes up with zero tools available and no indication why.

The real problem: a genuine shutdown after hours of serving looks identical to a startup race that lasted 200 milliseconds. Both return exit code 0. Both produce no error output.

Our fix: measure how long the server actually ran. We track a MIN_SERVE_SECONDS threshold of 10 seconds. If the process served for 10+ seconds and exited with code 0, that's a real shutdown -- don't retry. If it exited in under 10 seconds with code 0, that's a startup race where the server read EOF before the client sent `initialize` -- retry immediately.

We split retries into two independent budgets:

- Startup races (exit 0, under 10s uptime): 30 retries, 1-second delay between each. These are fast and transient -- the client just needs another moment to connect.
- Crashes (non-zero exit, not a signal): 20 retries with exponential backoff. Something is genuinely broken and hammering it won't help. OOM kills (137) and shutdown signals (143/130) exit immediately -- no retry, let Kubernetes handle it.

Two counters, two strategies, one wrapper. The agent never notices.

Full writeup on the outer-loop pattern: https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#MCP #AIAgents #ProductionEngineering #AgentCEO
