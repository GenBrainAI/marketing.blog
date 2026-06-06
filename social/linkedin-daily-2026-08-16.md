---
platform: linkedin
status: draft
date: 2026-08-16
note: Saturday engagement — MCP debugging story
---

## Post: The Most Expensive Character in Our Codebase

Every MCP connection in our platform started timing out. Every agent, every customer org, simultaneously. "MCP server agent-hub connection timed out after 20000ms."

The MCP servers were running. Network was clean. Resources normal. But the connections timed out anyway.

We spent hours checking the obvious. Then we read the wrapper script character by character.

The root cause was one ampersand. The shell script that launched the MCP server ran the process in the background with a trailing &. The shell returned immediately, the stdio pipe lost its owner, and the MCP client read EOF on the first byte.

The intermittent behavior made it worse. Sometimes the backgrounded process attached to the inherited pipe fast enough. Sometimes it did not. Timing-dependent. Race condition. Invisible in unit tests.

The fix: replace `python -m mcp_servers.agent_hub_mcp &` with `exec python -m mcp_servers.agent_hub_mcp`. One keyword, one deleted character. Platform-wide recovery.

The rule for stdio-based MCP servers: the process that speaks JSON-RPC must own stdin and stdout directly. Never background it.

https://agent.ceo/blog/debugging-mcp-timeout-stdio-wrapper-production

#MCP #Debugging #AIInfrastructure #AgentCEO #BuildInPublic
