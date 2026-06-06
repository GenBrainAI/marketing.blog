---
platform: twitter
status: draft
date: 2026-10-08
note: "Blog launch: How to Build a Crash-Resilient MCP Server Wrapper"
---

## Thread: How to Build a Crash-Resilient MCP Server Wrapper

New post: we published the full crash-resilient MCP wrapper implementation. A shell script that sits between Claude Code and the MCP server, retrying as needed. Claude Code sees one long-lived process. The wrapper handles everything underneath.

Why it matters: stdio MCP servers die silently. No error in the agent's context. Tools just vanish mid-session.

---

The wrapper classifies every exit into three categories:

1. Genuine shutdown: ran 10+ seconds (MIN_SERVE_SECONDS), exit 0. Real completion -- no retry.

2. Startup race: ran under 10 seconds, exit 0. Server read EOF before client sent `initialize`. Retry up to 30 times (MAX_FAST_CLEAN_RETRIES), 1s delay.

3. Crash: non-zero exit. 137 = OOM/SIGKILL, 143 = SIGTERM, 130 = SIGINT. Retry up to 20 times (MAX_RETRIES), exponential backoff.

---

Two independent retry counters. Startup races burn through fast retries without touching the crash budget. Crashes back off exponentially without resetting the startup counter.

The distinction matters: a startup race is transient. A crash means something is broken. Different problems, different retry strategies.

---

Bonus bug we cover in the post: the dual-scope config problem. MCP server registered at both user scope AND local scope. Claude Code sometimes picked the registration that didn't have crash recovery, bypassing the wrapper entirely. Fix: one authoritative scope per server.

---

Full tutorial with implementation: https://agent.ceo/blog/crash-resilient-mcp-wrapper-startup-race

#MCP #CrashRecovery #Tutorial #AgentCEO
