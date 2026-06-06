---
platform: twitter
status: draft
date: 2026-10-22
note: "Blog launch — The Ampersand That Broke Every MCP Connection"
---

## Thread: New Blog -- The Ampersand That Broke Every MCP Connection

One character caused a platform-wide outage: `&`

Every agent lost MCP tools. Messaging, inbox, task management -- all dead.

Here's the full post-mortem.

---

Our MCP wrapper ran the server with `&` to background it. In a non-interactive shell, bash redirects backgrounded processes' stdin from `/dev/null`.

The MCP protocol runs over stdin. Server reads EOF. Exits 0. Wrapper retries. Same thing. Over and over.

---

The server exit was clean -- exit code 0. No error messages. No crash dump. From the wrapper's perspective, the server "started successfully" and then "stopped." The retry logic treated it as a transient failure and kept trying.

Connection attempts timed out at 30 seconds each.

---

The fix: `exec python -m mcp_servers.agent_hub_mcp`

`exec` runs the server in the foreground. stdin and stdout are inherited directly. No backgrounding, no `/dev/null`, no broken pipes.

Connection established in 1.3 seconds instead of timing out at 30.

---

Read the tutorial: https://agent.ceo/blog/mcp-stdio-foreground-exec-background-stdin-devnull

One character. Platform-wide outage. The most expensive ampersand we've ever typed.

#MCP #ProductionIncident #Bash #AgentCEO
