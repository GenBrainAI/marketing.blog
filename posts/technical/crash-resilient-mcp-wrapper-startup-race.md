---
title: "Tutorial: How to Build a Crash-Resilient MCP Server Wrapper for Production Agents"
slug: "crash-resilient-mcp-wrapper-startup-race"
date: 2026-10-08
category: technical
cluster: "tutorials"
tags: [mcp, crash-recovery, stdio, startup-race, wrapper, tutorial]
description: "A practical tutorial on building a shell wrapper around an MCP stdio server that handles crashes, startup races, and dual-scope configuration conflicts — so your agent's tools never silently disappear."
relatedPosts:
  - /blog/outer-loop-shell-script-keeps-agents-alive
  - /blog/prompt-watchdog-daemon-keeps-agents-working
  - /blog/detect-break-agent-retry-loops-production
  - /blog/image-pinning-latest-tag-customer-agent-drift
  - /blog/policy-gate-compulsive-agent-discipline
---

# How to Build a Crash-Resilient MCP Server Wrapper for Production Agents

Our CEO agent lost the ability to talk to every other agent in our cyborgenic organization. No error message. No crash log. The MCP tools -- `send_to_agent`, `get_agent_inbox`, `complete_task_unverified` -- just stopped working. Calls timed out or returned nothing. The agent kept running, kept trying to do work, but it was deaf and mute. A pod restart fixed it. Until it happened again.

The root cause was not one bug. It was three, stacked on top of each other, each one hiding the others.

This tutorial walks through the wrapper we built to fix all three. If you run MCP servers in production -- especially stdio-based servers for agent tooling -- you will hit these same failure modes.

## How MCP stdio Servers Die

Claude Code spawns MCP servers as stdio subprocesses. The server reads JSON-RPC from stdin, writes responses to stdout. Simple. But "simple" carries a lethal assumption: the subprocess lives as long as the session.

When the MCP server process dies, Claude Code does not restart it. The tools that server provided just vanish. No error surfaces in the agent's context window. Tool calls silently fail or hang. The agent has no mechanism to know its tools are gone, much less bring them back.

In our fleet, the `agent-hub` MCP server connects the agent to NATS (messaging), Neo4j (knowledge graph), and the Task Management System. When it dies, the agent cannot receive tasks, report progress, or communicate with other agents. It is still alive but operationally dead.

We needed a wrapper between Claude Code and the MCP server -- something that looks like one long-lived process to the client but can restart the actual server underneath.

## Bug 1: The Startup Race

On a pod restart or session restart, the MCP server process starts before Claude Code's MCP client sends its `initialize` JSON-RPC handshake. The server opens stdin, waiting for the handshake. But the client has not connected yet. The server reads EOF, interprets it as "no client," and exits cleanly with code 0.

Our first wrapper had a simple retry loop: retry on non-zero exit, stop on zero. A clean exit meant the server shut down gracefully. Done.

Except this clean exit happened in under a second. The server never served a single request. It started, read EOF, exited 0, and the wrapper said: "Clean shutdown, my work here is done." Tools gone forever.

### The Fix: Time-Based Exit Classification

The key insight: a clean exit means different things depending on when it happens.

```bash
MIN_SERVE_SECONDS=${MCP_MIN_SERVE_SECONDS:-10}
start_time=$(date +%s)

# ... start the server, wait for it to exit ...

end_time=$(date +%s)
runtime=$((end_time - start_time))

if [ "$exit_code" -eq 0 ]; then
    if [ "$runtime" -ge "$MIN_SERVE_SECONDS" ]; then
        # Ran for 10+ seconds, served real requests, exited cleanly
        echo "Genuine shutdown after ${runtime}s. Exiting."
        exit 0
    fi
    # Exited in under 10 seconds — never connected to a client
    echo "Fast clean exit (${runtime}s) — startup race. Retrying..."
fi
```

If the server ran for 10 or more seconds and then exited 0, it actually handled requests and chose to shut down. That is a genuine exit. If it exited 0 in under 10 seconds, it never spoke to a client. That is the startup race. Retry.

## Bug 2: Crashes Without Recovery

The startup race was the sneaky failure. Crashes were the loud one. The MCP server connects to NATS, Neo4j, and PostgreSQL. Any of those dependencies going briefly unavailable could crash the server. A `ConnectionResetError` when the client disconnects abruptly. An OOM kill from the kernel.

Different exit codes need different strategies:

| Exit Code | Runtime | Category | Action |
|-----------|---------|----------|--------|
| 0 | 10s or more | Genuine shutdown | Exit, no retry |
| 0 | Under 10s | Startup race | Retry, 1s fixed delay, up to 30 attempts |
| 137 | Any | OOM kill (SIGKILL) | Exit immediately, let K8s restart pod |
| 143/130 | Any | SIGTERM/SIGINT | Exit immediately, graceful shutdown |
| Any other non-zero | Any | Crash | Retry, exponential backoff, up to 20 attempts |

The two retry categories get **independent budgets**. A crash does not eat into the startup-race budget. A startup race does not eat into the crash budget. This matters because a server might race 5 times on startup (burning 5 fast-clean retries) and then crash twice during normal operation (burning 2 crash retries). You do not want the startup races to leave you with only 15 crash retries.

```bash
MAX_RETRIES=${MCP_MAX_RETRIES:-20}
MAX_FAST_CLEAN_RETRIES=${MCP_MAX_FAST_CLEAN_RETRIES:-30}

retry_count=0
fast_clean_count=0

while true; do
    start_time=$(date +%s)
    python -m mcp_servers.agent_hub_mcp &
    child_pid=$!
    echo "$child_pid" > /tmp/agent-hub-mcp.pid
    wait $child_pid
    exit_code=$?
    child_pid=""
    runtime=$(( $(date +%s) - start_time ))

    # Signal-based exits: forward and stop
    if [ "$exit_code" -eq 137 ] || [ "$exit_code" -eq 143 ] || \
       [ "$exit_code" -eq 130 ]; then
        exit "$exit_code"
    fi

    # Clean exit classification
    if [ "$exit_code" -eq 0 ]; then
        if [ "$runtime" -ge "$MIN_SERVE_SECONDS" ]; then
            exit 0  # Genuine shutdown
        fi
        fast_clean_count=$((fast_clean_count + 1))
        if [ "$fast_clean_count" -ge "$MAX_FAST_CLEAN_RETRIES" ]; then
            echo "Startup race retry budget exhausted ($fast_clean_count)"
            exit 1
        fi
        sleep 1
        continue
    fi

    # Crash: exponential backoff
    retry_count=$((retry_count + 1))
    if [ "$retry_count" -ge "$MAX_RETRIES" ]; then
        echo "Crash retry budget exhausted ($retry_count)"
        exit 1
    fi
    backoff=$(( 2 ** retry_count ))
    [ "$backoff" -gt 60 ] && backoff=60
    sleep "$backoff"
done
```

The exponential backoff for crashes starts at 2 seconds, doubles each time (4s, 8s, 16s...), and caps at 60 seconds. This prevents hammering a database that is temporarily down while still recovering quickly from transient errors.

## Bug 3: The Dual-Scope Configuration Conflict

This one was invisible for weeks. The MCP server was registered in two places:

1. **User scope** -- via `claude mcp add -s user` in the wrapper script
2. **Local scope** -- via `.claude.json` written by a Python configuration script

Claude Code would sometimes pick the local-scope registration, which invoked `python -m mcp_servers.agent_hub_mcp` directly -- bypassing the wrapper entirely. No retry logic. No crash recovery. If that direct invocation died, the tools were gone.

The fix was two-fold. In the configuration script: when the crash-resilient wrapper exists and is executable, register the wrapper as the MCP command instead of the direct Python invocation. In the entrypoint: remove conflicting user-scope registrations and clean up stale entries from prior versions.

One MCP registration. One code path. The wrapper is always in the middle.

## Process Management Details

The wrapper needs clean process management to avoid stale PIDs and orphaned children:

```bash
child_pid=""

cleanup() {
    if [ -n "$child_pid" ]; then
        kill -TERM "$child_pid" 2>/dev/null
        wait "$child_pid" 2>/dev/null
    fi
    rm -f /tmp/agent-hub-mcp.pid
}

trap cleanup SIGTERM SIGINT EXIT
```

SIGTERM and SIGINT are trapped and forwarded to the child process for graceful shutdown. The PID file is cleared on exit to prevent a future wrapper instance from trying to kill a PID that now belongs to an unrelated process. All output is logged to `/tmp/agent-hub-mcp.log` with UTC timestamps for debugging.

## The Architecture

The final architecture looks like this:

```
Claude Code session
  └── spawns MCP server via stdio
      └── start_agent_hub_mcp.sh (wrapper)
          └── python -m mcp_servers.agent_hub_mcp (actual server)
              └── Connected to NATS, Neo4j, TMS
```

Claude Code sees one long-lived stdio process. It never knows the actual server restarted. The wrapper absorbs all the failure modes -- startup races, crashes, transient dependency outages -- and presents a stable interface to the client.

## Making It Configurable

Every threshold is an environment variable with a sane default:

| Variable | Default | Purpose |
|----------|---------|---------|
| `MCP_MAX_RETRIES` | 20 | Crash retry budget |
| `MCP_MAX_FAST_CLEAN_RETRIES` | 30 | Startup race retry budget |
| `MCP_MIN_SERVE_SECONDS` | 10 | Threshold for "genuine" clean exit |

In Kubernetes, set these in your pod spec. Agents with flaky dependencies might need higher crash budgets. Agents on fast hardware might lower the minimum serve threshold. The defaults work for our fleet of 7 agents running 24/7.

## Lessons

Three things we learned building this:

**Exit code 0 is not always success.** It can mean "I started and immediately had nothing to do because nobody was there yet." Time-based classification solved this.

**One server, one registration.** Dual-scope MCP configs create a silent race condition where sometimes your wrapper runs and sometimes it does not. Audit your `.claude.json` and user-scope registrations. There should be exactly one path to your server.

**Separate retry budgets for separate failure modes.** Startup races and crashes have different causes, different frequencies, and different recovery strategies. Mixing them into one counter means a flurry of startup races can leave you with no budget for a later crash.

Our CEO agent has not lost its MCP tools since deploying this wrapper. The startup race, which happened on roughly 40% of pod restarts, is now invisible -- the wrapper retries in under a second, and the agent never notices. Crashes recover automatically with exponential backoff. The dual-scope bug is structurally impossible because the wrapper is the only registered entry point.

If you are running MCP servers in production, you need something like this. The protocol does not handle reconnection for you. Your wrapper is your reliability layer.

---

We build [agent.ceo](https://agent.ceo) -- a platform where AI agents run an entire organization. These failure modes are real, discovered in production, and fixed with the patterns described here. If you are building with MCP servers and want to see how a full agent fleet handles reliability, check out [agent.ceo](https://agent.ceo).
