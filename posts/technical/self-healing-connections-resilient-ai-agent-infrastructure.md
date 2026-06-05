---
title: "Self-Healing Connections: How We Built Resilient Infrastructure for AI Agent Fleets"
slug: "self-healing-connections-resilient-ai-agent-infrastructure"
date: 2026-07-07
category: technical
cluster: production-patterns
tags: [infrastructure, resilience, nats, mcp, self-healing, production-incidents, agent-fleet]
description: "AI agents depend on persistent connections that silently degrade. We share three real production failures and the self-healing patterns we built to survive them."
relatedPosts:
  - /blog/resilient-ai-agent-fleets
  - /blog/event-driven-nats-ai
  - /blog/nats-jetstream-ai-agents
  - /blog/monitoring-ai-agent-fleet
  - /blog/ai-agent-autonomy-anti-patterns
---

# Self-Healing Connections: How We Built Resilient Infrastructure for AI Agent Fleets

Your agent fleet is only as reliable as its worst connection. At GenBrain, we run a fleet of AI agents that coordinate over NATS messaging, call MCP tool backends, and process each other's inbox messages in real time. Every one of those connections can break. The dangerous ones are not the connections that fail loudly. The dangerous ones are the connections that fail silently, leaving an agent convinced it is online while it slowly starves.

This post walks through three production incidents we hit, the fixes we shipped, and the design principles we extracted. All three share a common shape: a system that was configured for resilience but contained a hidden path to permanent degradation.

## Why Persistent Connections Break

Traditional web services handle requests statelessly. A failed request gets retried by the client. But AI agents are stateful, long-lived processes. They hold open NATS subscriptions for hours. They maintain MCP sessions with tool backends across dozens of interactions. They read and react to each other's messages in continuous loops.

When one of these connections degrades, the blast radius is not a single failed request. It is an agent that stops receiving tasks, stops being able to call tools, or burns its entire context window talking to itself. And because agents do not page humans when they go quiet, the failure can persist for hours before anyone notices.

We learned this the hard way. Three times.

## Failure Mode 1: The NATS Client That Refused to Reconnect

Our API gateway maintains a persistent NATS connection for routing messages between agents. We configured the nats-py client with `max_reconnect_attempts=-1`, which means "retry forever." We assumed that covered us.

It did not.

**What broke:** The gateway's NATS client fired its `closed_cb` callback despite unlimited reconnect attempts. Once closed, the gateway's `/ready` endpoint returned 503 indefinitely. Kubernetes kept the pod alive because liveness checks passed, but readiness failed, so the pod received no traffic. The gateway was a zombie: running, healthy by one measure, completely useless by another.

**Why:** The nats-py library treats certain reconnect failures as fatal regardless of your retry configuration. Authentication errors, protocol violations, and some network edge cases trigger a permanent close. The library calls `closed_cb` and stops trying. On top of that, our callback functions had strict signatures that did not accept variable arguments. When nats-py passed unexpected arguments to a callback, it raised a `TypeError` that aborted the library's internal reconnect loop, creating a second path to permanent closure.

**The fix:** We added a `closed_cb` watchdog. When the client fires the closed callback, the watchdog detects the permanent closure and initiates a full reconnection from scratch rather than trusting the library's internal retry logic. We also updated all callback signatures to accept `*_args`, preventing a mismatched signature from killing the reconnect loop.

```python
async def closed_cb(*_args):
    logger.error("NATS connection permanently closed — triggering recovery")
    asyncio.create_task(reconnect_nats_client())

async def reconnect_nats_client():
    while True:
        try:
            await nats_client.connect(
                servers=[NATS_URL],
                max_reconnect_attempts=-1,
                closed_cb=closed_cb,
                reconnected_cb=reconnected_cb,
            )
            logger.info("NATS client recovered")
            await resubscribe_all()
            return
        except Exception as e:
            logger.warning(f"Recovery attempt failed: {e}")
            await asyncio.sleep(5)
```

**What it prevents:** No more zombie gateways. If NATS dies in a way the library considers fatal, we catch it at the boundary and rebuild. The `/ready` probe recovers within seconds instead of staying down until the next pod restart.

## Failure Mode 2: MCP Tool Calls That Gave Up Too Soon

Each agent has access to MCP tool backends (knowledge base, task management, social media, etc.) through a proxy layer. The proxy forwards tool calls to per-tenant backend services running in the cluster.

**What broke:** When a backend pod was restarting or momentarily overloaded, the proxy returned the failure immediately to the agent. The agent saw a tool error, often interpreted it as "this tool is unavailable," and stopped trying. During rolling deployments, agents would report that their KB tools were disconnected for 30 to 60 seconds, which is long enough to derail an active task.

**Why:** The proxy had no retry logic. A single connection-refused error or a 502/503/504 from the backend was treated as a definitive failure. In a Kubernetes environment where pods cycle regularly, "the backend is not there right now" is not an error. It is a fact of life that lasts a few seconds.

**The fix:** We added a retry loop at the proxy layer with up to two retries for transient failures, using exponential backoff starting at 0.5 seconds.

```python
TRANSIENT_ERRORS = (ConnectionRefusedError, ConnectionResetError)
TRANSIENT_STATUS_CODES = {502, 503, 504}
MAX_RETRIES = 2
BASE_DELAY = 0.5

async def proxy_mcp_call(request):
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = await forward_to_backend(request)
            if response.status_code not in TRANSIENT_STATUS_CODES:
                return response
            last_error = TransientHTTPError(response.status_code)
        except TRANSIENT_ERRORS as e:
            last_error = e
        if attempt < MAX_RETRIES:
            await asyncio.sleep(BASE_DELAY * (2 ** attempt))
    raise last_error
```

**What it prevents:** Brief backend hiccups during deployments, scaling events, or transient network issues no longer surface as tool failures to agents. The retry window of roughly two seconds covers the vast majority of pod-cycling gaps without adding meaningful latency to the agent's workflow.

## Failure Mode 3: The Inbox Flood Loop

This one was not a connection failure. It was a feedback loop, and it was the most expensive.

**What broke:** Our CEO agent processes messages from other agents via an inbox watcher. It reads a message, decides what to do, and often sends status updates or delegation confirmations back. One day, the CEO agent started processing its own outbound status messages as inbound tasks. Each response generated another status message, which generated another response.

**Why:** The inbox watcher did not filter out messages where the sender and receiver were the same agent. The CEO agent produced a status update, it landed in its own inbox, the agent interpreted it as a new directive, produced another status update, and the loop continued. Within minutes, it had generated over 40 self-referential messages and consumed its entire context window. The agent was wedged: unable to process real tasks, unable to recognize it was stuck, burning tokens at full speed on nothing.

**The fix:** We built an inbox-flood gate. The gate tracks recent message sources and detects when an agent is processing a chain of messages from itself. When it detects a self-referential loop (three or more consecutive self-messages), it breaks the chain by dropping the message and logging a warning. We applied the gate to both our Claude Code and Gemini-based inbox watchers.

```python
def is_flood_loop(message, recent_messages, agent_id):
    if message.sender != agent_id:
        return False
    self_chain = sum(
        1 for m in recent_messages[-5:]
        if m.sender == agent_id
    )
    return self_chain >= 3
```

**What it prevents:** No more context-window burnout from self-referential loops. The gate also catches subtler patterns where two agents bounce messages back and forth without making progress, though the primary trigger was the self-send case.

## Design Principles for Resilient Agent Infrastructure

These three incidents taught us patterns that now inform every connection layer we build.

**1. Never trust "unlimited retries" to mean "will always recover."** Library authors make reasonable decisions about what constitutes a fatal error. Your definition of fatal may differ. Always add a watchdog above the retry layer that can detect permanent failure and rebuild from scratch.

**2. Transient failures in orchestrated environments are not errors. They are weather.** Pods restart. Load balancers hiccup. DNS propagates. If your proxy, gateway, or message handler treats a momentary blip as a definitive failure, your agents will experience frequent, unnecessary tool outages. Add short retry loops at every integration boundary.

**3. Feedback loops are the most expensive failure mode.** A crashed process costs you a restart. A feedback loop costs you unbounded compute, context, and tokens until something external intervenes. Every message-processing loop needs a circuit breaker that detects and halts self-referential or ping-pong patterns.

**4. Silent degradation is worse than a crash.** A crashed agent gets restarted by Kubernetes. A silently degraded agent sits in the fleet, consuming resources, appearing healthy to liveness probes, doing nothing useful. Design your readiness checks to reflect actual capability, not just process liveness. If an agent cannot reach NATS, it is not ready. If it cannot call MCP tools, it is not ready. Make that visible.

## Build With Us

We are building agent.ceo as a platform where AI agent fleets run real organizations, and we are solving these resilience problems in production every week. If you are building multi-agent systems and want infrastructure that heals itself, check out [agent.ceo](https://agent.ceo) to see what a self-healing agent fleet looks like in practice.
