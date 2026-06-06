---
platform: linkedin
status: draft
date: 2026-10-08
note: "Blog launch: How to Build a Crash-Resilient MCP Server Wrapper"
---

## Post: How to Build a Crash-Resilient MCP Server Wrapper

New blog post. We published the full implementation of our crash-resilient MCP server wrapper -- the shell script that sits between Claude Code and the actual MCP server, keeping tools alive across every failure mode.

The core problem: MCP stdio servers die silently. When they crash, there is no error injected into the agent's context. The agent just loses its tools mid-session. No notification, no fallback. It keeps running, but every tool call fails.

Our wrapper intercepts all three exit categories:

1. Genuine shutdown -- the server ran for 10+ seconds (MIN_SERVE_SECONDS), exited with code 0. That's a real completion. No retry.

2. Startup race -- the server ran for under 10 seconds, exited with code 0. This happens when the server starts, reads EOF on stdin before the client sends `initialize`, and shuts down thinking there's nothing to do. We retry up to 30 times (MAX_FAST_CLEAN_RETRIES) with a 1-second delay.

3. Crash -- non-zero exit code. Exit 137 means OOM or SIGKILL, 143 means SIGTERM, 130 means SIGINT. We retry up to 20 times (MAX_RETRIES) with exponential backoff.

We also cover a subtle config bug: MCP servers registered at both user scope and local (project) scope. Claude Code sometimes picked the registration without crash recovery, bypassing the wrapper entirely. The fix was ensuring a single authoritative scope per server.

Claude Code sees one long-lived process. The wrapper handles everything underneath.

Full tutorial: https://agent.ceo/blog/crash-resilient-mcp-wrapper-startup-race

#MCP #CrashRecovery #Tutorial #AgentCEO
