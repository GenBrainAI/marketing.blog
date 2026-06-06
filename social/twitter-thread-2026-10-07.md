---
platform: twitter
status: draft
date: 2026-10-07
note: "Your MCP Server Exited Cleanly. That's the Problem."
---

## Thread: Your MCP Server Exited Cleanly. That's the Problem.

Exit code 0 means success. Except when your MCP stdio server starts up, reads EOF before the client connects, and shuts down. Clean exit. No error. Your agent wakes up with zero tools and no idea why.

A genuine shutdown after hours of serving looks identical to a startup race that lasted 200ms. Both return exit 0.

---

Our fix: measure uptime. We use a MIN_SERVE_SECONDS threshold of 10.

If the server ran for 10+ seconds and exited with code 0 -- real shutdown, don't retry.

If it exited in under 10 seconds with code 0 -- startup race. The server read EOF before the client sent `initialize`. Retry immediately.

---

We split retries into two independent budgets with separate counters:

Startup races (exit 0, <10s uptime): 30 retries, 1s delay. Fast and transient -- the client just needs another moment.

Crashes (non-zero exit -- 137 OOM/SIGKILL, 143 SIGTERM, 130 SIGINT): 20 retries, exponential backoff. Something is broken, hammering won't help.

---

Two counters, two strategies, one wrapper. The agent never notices the difference.

The dangerous part isn't the crash. It's the silent clean exit that eats your agent's tooling without a trace.

---

Full writeup on the outer-loop pattern: https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#MCP #AIAgents #ProductionEngineering #AgentCEO
