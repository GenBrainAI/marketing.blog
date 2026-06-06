---
title: "Tutorial: Why stdio Servers Must Run in the Foreground — The Ampersand That Broke Every MCP Connection"
slug: "mcp-stdio-foreground-exec-background-stdin-devnull"
date: 2026-10-22
category: technical
cluster: "tutorials"
tags: [mcp, stdio, bash, exec, foreground, tutorial, production-incident]
description: "A practical tutorial on why backgrounding stdio-based servers with & kills the protocol channel in non-interactive shells — and how exec gives you a correct, minimal wrapper for MCP, LSP, and any JSON-RPC-over-stdio server."
relatedPosts:
  - /blog/crash-resilient-mcp-wrapper-startup-race
  - /blog/outer-loop-shell-script-keeps-agents-alive
  - /blog/crash-loop-fresh-pvc-has-resumable-session
  - /blog/detect-break-agent-retry-loops-production
  - /blog/three-agent-failure-modes-production-only
---

# Why stdio Servers Must Run in the Foreground: The Ampersand That Broke Every MCP Connection

Every agent in our fleet went deaf and mute at the same time. GenBrain core agents, customer org agents -- all of them. The error was identical across the board:

```
MCP server agent-hub connection timed out after 20000ms
```

No agent could send messages. No agent could read its inbox. No agent could update tasks. Platform-wide outage of every MCP tool.

The root cause was one character in a shell script: `&`.

This tutorial explains exactly why that character is fatal for stdio-based servers, what bash does differently in interactive vs. non-interactive shells, and how to build a correct minimal wrapper for any MCP, LSP, or JSON-RPC-over-stdio server.

## How MCP stdio Works

MCP (Model Context Protocol) servers communicate over stdio. The client -- Claude Code in our case -- spawns the server as a subprocess. stdin carries JSON-RPC requests to the server, stdout carries responses back, stderr is for diagnostics.

Claude Code pipes JSON-RPC into the wrapper's stdin and reads responses from stdout. The wrapper relays these to the actual MCP server process.

This works when the server process inherits the wrapper's file descriptors. It breaks catastrophically when it does not.

## What `&` Does in a Non-Interactive Shell

Here is the line that caused the outage:

```bash
python -m mcp_servers.agent_hub_mcp &
```

That trailing `&` backgrounds the process. In an interactive shell -- your terminal -- a backgrounded process inherits the terminal's stdin. But Claude Code does not spawn MCP servers in an interactive shell. It spawns them as subprocesses in a **non-interactive shell**. Here is the critical difference:

**In a non-interactive shell, bash redirects a backgrounded process's stdin from `/dev/null`.**

This is not a bug. It is specified POSIX behavior. A non-interactive shell has no terminal to share, so backgrounded processes get `/dev/null` as their stdin. The process can read from it, but it gets EOF immediately because `/dev/null` is empty.

So what happened to our MCP server:

1. Claude Code spawns the wrapper, piping JSON-RPC to its stdin
2. The wrapper runs `python -m mcp_servers.agent_hub_mcp &`
3. Bash redirects the Python process's stdin from `/dev/null`
4. Python reads stdin, gets EOF instantly
5. The MCP server exits cleanly -- exit code 0
6. Claude Code's `initialize` handshake never reaches the server
7. Connection times out after 20 seconds

The JSON-RPC messages were going into the wrapper's stdin. But the Python process was reading from `/dev/null`. The protocol channel was dead before the first message.

## The Retry Loop That Made It Worse

Our wrapper was not naive. It had crash-resilient retry logic -- 118 lines of it. Built to handle the [startup race problem](/blog/crash-resilient-mcp-wrapper-startup-race) where the MCP server starts before the client connects.

The wrapper detected the fast clean exit (exit code 0 in under a second) and correctly classified it as suspicious. So it retried. But every respawn also ran `python -m mcp_servers.agent_hub_mcp &` -- backgrounded. Every new process got `/dev/null` as stdin. Every one read EOF and exited cleanly.

The wrapper was causing the exact problem it was designed to solve. The retry infrastructure that existed to fight a startup race was fighting a self-inflicted stdin race, and it could never win because the `&` guaranteed every attempt would fail identically.

After exhausting its retry budget, the wrapper gave up. Tools gone. Agent deaf.

## What Made This a Regression

The `&` was not new. The wrapper script had always backgrounded the server. But it was not always the only way to start the MCP server.

Before commit `1494f5107`, some code paths bypassed the wrapper entirely and called `python -m mcp_servers.agent_hub_mcp` directly -- in the foreground. Those paths worked because the Python process inherited stdin from Claude Code without any backgrounding.

When the wrapper became the exclusive launch path for both scopes, the `&` went from "sometimes bypassed" to "always hit." That is when every agent in the fleet lost MCP.

## The Fix: `exec` and Nothing Else

The entire 118-line crash-resilient wrapper was replaced with 34 lines. The critical change:

```bash
exec python -m mcp_servers.agent_hub_mcp 2>> "$LOG_FILE"
```

`exec` replaces the current shell process with the Python process. No new subprocess. No backgrounding. The Python process becomes the wrapper process and inherits its file descriptors directly:

- **stdin**: Claude Code's JSON-RPC pipe -- the MCP protocol channel
- **stdout**: Claude Code's response pipe
- **stderr**: redirected to the log file for diagnostics

No `&`. No retry loop. No PID tracking. No signal forwarding. `exec` means the Python process IS the process, so `SIGTERM` reaches it directly. The shell is gone.

## Verification

We tested all three configurations:

| Method | Result |
|--------|--------|
| `python -m mcp_servers.agent_hub_mcp` (foreground, no wrapper) | Initialize handshake answered in 3.4s |
| Wrapper with `&` (backgrounded) | Timeout at 30s+ |
| Wrapper with `exec` (foreground replacement) | Initialize handshake answered in 1.3s |

The `exec` version is actually faster than the bare Python call because there is no intermediate shell process between Claude Code and the MCP server.

## Why the Retry Loop Was Unnecessary

Removing the crash-recovery wrapper sounds reckless until you count the existing recovery layers:

1. **In-process restart**: `agent_hub_mcp.py` has its own internal loop. When `mcp.run()` exits, it re-runs on the same stdio file descriptors. No new process, no new stdin pipe.
2. **Client-side reconnection**: Claude Code detects MCP server disconnects and respawns the command automatically.

Two layers of crash recovery already existed. The wrapper's retry loop was a third layer that added no resilience and introduced the bug that broke everything.

## Five Rules for stdio Server Wrappers

If you build wrappers for any stdio-based IPC protocol -- MCP, LSP, JSON-RPC, or custom -- these rules will save you from this class of bug:

### 1. Never background stdio servers

```bash
# WRONG: stdin becomes /dev/null in non-interactive shells
python -m my_server &

# RIGHT: run in the foreground or use exec
exec python -m my_server
```

`command &` in a non-interactive shell means `/dev/null` stdin. Your protocol channel is dead before the first message arrives.

### 2. Use `exec` when the wrapper's only job is to launch

If your wrapper sets environment variables, changes directory, configures logging, and then runs the server -- `exec` is the correct final step. It replaces the shell with the server process. The server inherits all file descriptors. No relay process needed.

```bash
#!/bin/bash
cd /app
export CONFIG_PATH=/etc/myserver/config.yaml
LOG_FILE="/var/log/myserver.log"
exec python -m my_mcp_server 2>> "$LOG_FILE"
```

### 3. stderr is separate from the protocol channel

You can safely redirect stderr to a log file without interfering with the stdin/stdout protocol. This is how you get diagnostics from a stdio server:

```bash
exec python -m my_server 2>> /tmp/my_server.log
```

stdin and stdout carry JSON-RPC. stderr carries your log lines. They do not interfere.

### 4. Question retry infrastructure around stdio

If your server has in-process reconnection AND the client respawns on disconnect, an outer retry loop adds failure surface without adding resilience. Each layer that restarts the process is a layer that can break the stdin pipe.

Before adding a retry wrapper, list the existing recovery mechanisms. If two already exist, your wrapper's job is launch, not recovery.

### 5. Test with the actual spawning mechanism

This rule would have caught our bug before production. Running `python -m server &` in your terminal works perfectly -- the backgrounded process inherits the terminal's stdin. The bug only manifests in non-interactive shells, which is exactly how Claude Code, VS Code, and other editors spawn stdio servers.

Test your wrapper the way it will actually be spawned:

```bash
# Simulates how Claude Code spawns MCP servers (non-interactive)
echo '{"jsonrpc":"2.0","method":"initialize","id":1}' | bash wrapper.sh
```

If you get a response, the stdio pipe is intact. If you get silence or a timeout, your wrapper is breaking the pipe.

## The Broader Lesson

We had 118 lines of carefully engineered crash recovery. Dual retry budgets. Time-based exit classification. PID tracking. Signal forwarding. All of it built to solve real problems we had actually hit in production.

All of it unnecessary once we removed the one character causing the problems. The crash-recovery infrastructure was fighting the consequences of `&` while `&` kept producing new crashes to recover from.

Sometimes the right fix is not a better retry loop. It is removing the thing that makes retries necessary.

---

*At [GenBrain AI](https://agent.ceo), we run a fleet of AI agents as a real organization -- all coordinating over MCP. Every bug like this becomes a lesson we publish. If you are building multi-agent systems or MCP infrastructure, check out [agent.ceo](https://agent.ceo).*
