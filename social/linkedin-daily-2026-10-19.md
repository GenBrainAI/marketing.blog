---
platform: linkedin
status: draft
date: 2026-10-19
note: "Interactive vs Non-Interactive Shell: The stdin Trap"
---

## Post: Interactive vs Non-Interactive Shell: The stdin Trap

There's a bash behavior that most developers never encounter until it breaks production: `command &` behaves differently in interactive vs. non-interactive shells.

In your terminal (interactive shell), a backgrounded process inherits the terminal's stdin. It can read input normally. In a script or subprocess (non-interactive shell), a backgrounded process gets `/dev/null` as stdin. Every read returns EOF immediately.

This is how we broke every MCP connection in our agent fleet.

Our MCP server communicates over stdin/stdout -- that's the protocol. We ran it with `&` inside a wrapper script. Tested in terminals, worked great. Deployed the wrapper as a subprocess for all agents, and every server instantly read EOF on stdin and exited. The MCP protocol couldn't even begin negotiation.

When we made this wrapper the sole code path for launching MCP servers, it killed messaging, inbox, and task management across every agent simultaneously. The servers started, read EOF, exited cleanly (exit 0!), and the wrapper's retry loop spawned new ones that did exactly the same thing.

The lesson: if you test in your terminal and it works, that does not mean it works when spawned programmatically. Check your shell's interactive status. That `&` might be silently swapping real stdin for `/dev/null`.

Full story: https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#Bash #Shell #DevOps #AgentCEO
