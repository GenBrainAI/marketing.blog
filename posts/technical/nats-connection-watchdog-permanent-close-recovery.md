---
title: "When max_reconnect_attempts=-1 Isn't Enough: Building a NATS Connection Watchdog"
slug: "nats-connection-watchdog-permanent-close-recovery"
date: 2026-11-03
category: technical
cluster: "architecture-deep-dives"
tags: [nats, watchdog, reconnection, gateway, resilience, deep-dive]
description: "How a NATS client configured for infinite reconnection still died permanently — and the watchdog pattern that guarantees recovery from states the library considers terminal."
author: "Engineering Team"
relatedPosts:
  - /blog/self-healing-connections-resilient-ai-agent-infrastructure
  - /blog/outer-loop-shell-script-keeps-agents-alive
  - /blog/crash-resilient-mcp-wrapper-startup-race
  - /blog/ceo-relaunch-loop-strategy-inbox-flood
  - /blog/three-agent-failure-modes-production-only
---

# When max_reconnect_attempts=-1 Isn't Enough: Building a NATS Connection Watchdog

You set `max_reconnect_attempts=-1`. Infinite reconnection. The NATS client will never give up. You deploy with confidence.

Then on a Sunday night, the API gateway goes deaf. The `/ready` endpoint returns 503. The provisioning bus is silent. Telemetry stops flowing. Board fan-out halts. NATS-KV API key persistence goes dark. The pod is alive — CPU idle, memory stable, HTTP still serving — but the NATS connection is permanently closed.

You restart the pod manually. Everything recovers. You stare at the logs and ask: how does "infinite reconnection" end?

This is the story of commit `3a56d6d85`, what we found, and the watchdog pattern that now prevents it from ever happening again.

## The Incident: June 1, 2026

Our API gateway is the central nervous system of the [agent.ceo](https://agent.ceo) platform. It connects to NATS for agent provisioning, telemetry streaming, board fan-out, and API key persistence via NATS-KV. Every one of those subsystems depends on a single NATS client connection.

On June 1, 2026, the gateway's NATS client fired its `closed_cb` callback. That callback is supposed to fire when the connection is permanently closed — not during a temporary disconnect, not during a reconnect attempt, but when the client has given up entirely.

The gateway's `/ready` health endpoint, which checks NATS connectivity, started returning 503. Kubernetes didn't kill the pod because the liveness probe (which checks HTTP, not NATS) kept passing. The pod sat there, alive but useless, until someone noticed and restarted it manually.

The NATS client had been configured with `max_reconnect_attempts=-1`. Infinite retries. It should never have given up.

## Root Cause #1: The Library's Definition of "Infinite"

Here's what `max_reconnect_attempts=-1` actually means in nats-py: **retry forever, unless the server sends an authorization failure during reconnect.**

This is not a configuration error. It's a library-level design decision. The nats-py client treats specific reconnect errors as unrecoverable. If the NATS server (or in our case, the nats-auth-callout service) returns an authorization violation during a reconnect attempt — even a transient one, like "authorization service unavailable" — nats-py closes the connection permanently and stops the reconnect loop entirely.

In our case, a momentary hiccup in the nats-auth-callout service caused exactly this. The auth callout returned an error for a few seconds. nats-py interpreted this as a permanent authorization failure, closed the connection, and walked away. The "infinite" reconnect loop terminated after a single auth error.

The takeaway: `max_reconnect_attempts=-1` means "retry forever unless the server sends an auth failure during reconnect, in which case give up immediately." That's a meaningful asterisk on "forever."

## Root Cause #2: The Silent Callback Bug

There was a compounding bug. The gateway's NATS callbacks had the wrong signature:

```python
# BEFORE (wrong):
async def _nats_disconnected():
    ...

async def _nats_reconnected():
    ...

async def _nats_error(e):
    ...
```

The nats-py library passes arguments to these callbacks. When it called `_nats_disconnected()` with arguments, Python raised a `TypeError`. This TypeError could abort nats-py's internal reconnect loop — the library's own reconnect machinery crashed because our callback couldn't accept what it was being handed.

This exact bug had already been fixed in our provisioning module (PR #694). The gateway copy hadn't been updated.

The fix is simple — use `*args` to absorb whatever the library passes:

```python
# AFTER (correct):
async def _nats_disconnected(*_args):
    ...

async def _nats_reconnected(*_args):
    ...

async def _nats_error(*args):
    e = args[-1] if args else None
    ...
```

The `*_args` / `*args` pattern makes callbacks resilient to whatever nats-py decides to pass, regardless of version. Defensive, boring, correct.

## The Fix: A NATS Connection Watchdog

Fixing the callbacks prevents one failure mode. But the fundamental problem remains: nats-py can decide your connection is permanently dead for reasons your application disagrees with. You need something that sits outside the library's reconnect loop and can create a completely fresh connection when the library gives up.

We built a watchdog — a background asyncio task that runs every 30 seconds:

```python
_NATS_WATCHDOG_INTERVAL = 30

async def _nats_watchdog(app):
    while True:
        await asyncio.sleep(_NATS_WATCHDOG_INTERVAL)
        nc = getattr(app.state, "nats_client", None)
        if nc is None:
            continue
        if nc.is_connected:
            continue
        if not nc.is_closed:
            continue  # mid-reconnect, let nats-py handle it

        logger.warning(
            "NATS watchdog: connection permanently closed — reconnecting"
        )
        try:
            new_nc = await asyncio.wait_for(
                nats.connect(nats_url, **nats_kwargs),
                timeout=15,
            )
            app.state.nats_client = new_nc
            try:
                app.state.nats_js = new_nc.jetstream()
            except Exception:
                app.state.nats_js = None
            logger.info("NATS watchdog: reconnected")
        except Exception as e:
            logger.error(
                "NATS watchdog: reconnect failed: %s — will retry in %ds",
                e, _NATS_WATCHDOG_INTERVAL,
            )
```

### Design Decisions That Matter

**1. Only act on permanently closed connections.** The watchdog checks `nc.is_closed` — not just `nc.is_connected`. If the connection is disconnected but not closed, nats-py's own reconnect is still running. The watchdog stays out of the way. It only intervenes when the library has given up.

**2. Create a fresh connection.** Don't try to revive the old client. It's in a terminal state. Create a brand-new `nats.connect()` with the same URL and kwargs (stored on `app.state._nats_url` and `app.state._nats_kwargs` at startup). Clean slate.

**3. Timeout the connect attempt.** `asyncio.wait_for` with a 15-second timeout prevents a hung connection attempt from blocking the watchdog loop. If NATS is truly down, the watchdog retries every 30 seconds without getting stuck.

**4. Re-initialize JetStream.** After connecting, the watchdog attempts to get a JetStream context for the provisioning bus. If JetStream isn't available, it sets `nats_js` to `None` gracefully — the core NATS connection still works.

**5. Clean shutdown.** The watchdog task is stored on `app.state._nats_watchdog_task` and cancelled during `_shutdown_services`. No orphaned coroutines.

**6. A new `closed_cb`.** A `_nats_closed` callback logs permanent closure events so the watchdog has context when it fires. You want the log line before the recovery, not just after.

## The Broader Architecture Lesson

This incident crystallized a pattern we keep seeing in production systems: **library-provided reconnection is necessary but not sufficient.**

Libraries like nats-py make internal decisions about what's "recoverable" versus "fatal." These decisions are reasonable from the library's perspective — an auth failure probably means your credentials are wrong, so retrying is pointless. But the library doesn't know your operational context. It doesn't know that your auth-callout service had a 3-second hiccup and is already back. It doesn't know that your availability requirements say "never stop trying."

The same pattern applies beyond NATS. Any client library that manages its own reconnection — database drivers, message queue clients, gRPC channels — has its own internal definition of "unrecoverable." Your application may disagree.

The watchdog pattern resolves the disagreement:

1. Let the library handle normal reconnection (it's good at it)
2. Detect when the library has given up (terminal state)
3. Create a completely fresh connection from outside the library's state machine
4. Retry on a fixed interval until success

This is the same philosophy behind our [outer-loop shell script](/blog/outer-loop-shell-script-keeps-agents-alive) that keeps agent processes alive, and the [crash-resilient MCP wrapper](/blog/crash-resilient-mcp-wrapper-startup-race) that handles startup races. Defense in depth means not trusting any single layer to handle all failure modes.

## Checklist: Is Your NATS Connection Watchdog-Protected?

If you're running nats-py in production, audit these five things:

- **Callback signatures**: Do all your NATS callbacks accept `*args`? If not, a `TypeError` can crash the reconnect loop.
- **`closed_cb` handler**: Do you log and alert when a connection is permanently closed? If you're only watching `disconnected_cb`, you're missing the fatal case.
- **Watchdog task**: Do you have a background task that can detect `is_closed` and create a fresh connection? If not, a single auth hiccup can take your NATS connection offline permanently.
- **Connect kwargs stored**: Are your NATS connection URL and kwargs stored somewhere the watchdog can access them? You can't create a fresh connection if you've lost the original configuration.
- **Health endpoint checks `is_connected`**: Does your readiness probe check the NATS client's actual connection state? A pod that's alive but NATS-disconnected is a pod that should be restarted — or better, watchdog-recovered.

`max_reconnect_attempts=-1` is a good start. It's just not the whole story.

---

*We build [agent.ceo](https://agent.ceo) — the operating system for AI agent organizations. Every architecture decision in this post was learned by running autonomous agents in production, 24/7. If you're building systems where agents need to stay connected and self-heal, [check out what we're building](https://agent.ceo).*
