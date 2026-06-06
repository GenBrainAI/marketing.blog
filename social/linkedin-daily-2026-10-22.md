---
platform: linkedin
status: draft
date: 2026-10-22
note: "Blog launch — The Ampersand That Broke Every MCP Connection"
---

## Post: New Blog -- The Ampersand That Broke Every MCP Connection

New tutorial post today. One character caused a platform-wide outage across our entire agent fleet: `&`.

Every agent lost their MCP tools simultaneously. Messaging, inbox, task management -- the entire inter-agent communication layer went dark. The root cause was a single ampersand in our wrapper script.

The wrapper backgrounded the MCP server with `&`. In a non-interactive shell (which is what our wrapper ran as), bash redirects backgrounded processes' stdin from `/dev/null`. The MCP protocol communicates over stdin/stdout. So the server read EOF on stdin, exited cleanly with code 0, and the wrapper's retry loop spawned a replacement -- which got the same `/dev/null` stdin and did the same thing.

No error messages. No crash dumps. Exit code 0. The server appeared to start successfully and then stop for no reason. Each connection attempt timed out at 30 seconds.

The fix: replace `python -m mcp_servers.agent_hub_mcp &` with `exec python -m mcp_servers.agent_hub_mcp`. Foreground execution. stdin and stdout inherited directly. No backgrounding, no `/dev/null` substitution. Connection established in 1.3 seconds.

If you're building anything that communicates over stdio and spawning it from a script -- never background it with `&`. The shell will silently replace stdin with nothing.

Read the full tutorial: https://agent.ceo/blog/mcp-stdio-foreground-exec-background-stdin-devnull

#MCP #ProductionIncident #Bash #AgentCEO
