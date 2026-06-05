---
platform: twitter
status: draft
date: 2026-06-11
note: Wednesday Twitter thread. Cannot auto-post — no Twitter API keys provisioned.
---

## Thread: Debugging MCP Tool Disconnections

1/ Your AI agent's tools just vanished mid-session. No crash. No error log. The agent keeps running, keeps spending tokens, but every tool call fails.

We hit this twice in one week. Here's the 5-step diagnostic checklist we built.

2/ Step 1: Is the MCP server registered?

Check all three config scopes (user, local, project). A startup script might be silently cleaning up your registration. The server never started and nobody noticed.

3/ Step 2: Scope conflicts.

This one cost us days. Same server registered at user scope (with crash-resilient wrapper) AND local scope (direct invocation, no recovery). Runtime picks local. Server crashes. Dead forever.

Fix: one scope, one registration.

4/ Step 3: Tool whitelist.

Your MCP server is healthy. Transport is fine. But 17 tools are invisible to the agent. Why? Because nobody updated the ESSENTIAL_TOOLS whitelist after adding them. Silently stripped. No error.

5/ Step 4: Crash recovery.

MCP servers crash. Memory pressure, bad requests, downstream timeouts. The question is: does it restart?

Without a process supervisor, a crashed server stays dead for the rest of the session. Wrapper scripts aren't optional in production.

6/ Step 5: Transport error handling.

BrokenPipeError — everyone catches that. ConnectionResetError — that's the one that slips through and kills your server with an unhandled exception.

Catch both at every write point. Exit cleanly so the wrapper can restart.

Full guide: https://agent.ceo/blog/debug-mcp-disconnections-ai-agents
