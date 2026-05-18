---
title: "Agent Communication Patterns: Pub/Sub, Request-Reply, and Broadcast in a Cyborgenic Organization"
slug: "agent-communication-patterns-cyborgenic"
date: 2026-06-30
category: technical
cluster: "ai-agent-orchestration"
tags: [cyborgenic, nats, pub-sub, request-reply, broadcast, messaging, communication-patterns, multi-agent]
description: "How a Cyborgenic Organization uses NATS pub/sub, request-reply, broadcast, and point-to-point messaging patterns to coordinate six autonomous AI agents in production."
relatedPosts:
  - /blog/nats-jetstream-ai-agents
  - /blog/agent-to-agent-messaging
  - /blog/event-driven-nats-ai
  - /blog/multi-agent-architecture-patterns
  - /blog/architecture-agent-ceo
---

# Agent Communication Patterns: Pub/Sub, Request-Reply, and Broadcast in a Cyborgenic Organization

A Cyborgenic Organization runs on communication. Six AI agents -- CEO, CTO, Backend, Fullstack, CSO, and Marketing -- operate concurrently across different repositories, different runtimes, and different schedules. Without a deliberate communication architecture, these agents would duplicate work, miss critical events, and make decisions on stale information. The messaging layer is the nervous system that holds the entire Cyborgenic structure together.

GenBrain AI built its agent communication on NATS, a lightweight messaging system that supports multiple communication patterns out of the box. This post breaks down every pattern we use, when each one applies, and how the subject namespace conventions keep 11 agents coordinated without chaos.

## Why Communication Patterns Matter in Multi-Agent Systems

Most multi-agent frameworks treat communication as an afterthought: agents call each other through function signatures or share a global state object. That approach collapses under production conditions. Agents start and stop independently. Some run on cron schedules, others fire on events. A synchronous call chain means one slow agent blocks everyone downstream.

NATS solves this by decoupling producers from consumers at the transport level. The sender publishes a message to a subject. Whether zero, one, or fifty subscribers receive it depends entirely on the subscription topology. This decoupling lets a [Cyborgenic Organization](/blog/cyborgenic-organizations) scale agent count without rewriting communication logic.

## Pattern 1: Pub/Sub for Event Broadcasting

Pub/sub is the default pattern for events that multiple agents might care about but that require no response. The publisher fires a message onto a subject, and every active subscriber on that subject receives a copy.

### When We Use It

Deploy completions, security alerts, content published notifications, and infrastructure state changes all flow through pub/sub. The Backend agent pushes code, the CI pipeline succeeds, and a `genbrain.events.deploy.complete` message goes out. The CSO agent picks it up and triggers a post-merge security scan. The Marketing agent picks it up and drafts a changelog entry. The CTO picks it up and updates the sprint tracker.

```
Subject: genbrain.events.deploy.complete
Payload:
{
  "service": "api-gateway",
  "commit": "a3f7b21",
  "environment": "production",
  "timestamp": "2026-06-30T02:15:00Z",
  "triggered_by": "backend"
}
```

No agent needs to know which other agents are listening. The Backend agent publishes and moves on. This is the key advantage: adding a seventh agent that cares about deploys requires zero changes to the Backend agent's code.

### Subject Convention

All broadcast events follow the pattern `genbrain.events.<domain>.<action>`. This lets agents subscribe broadly (`genbrain.events.>` for everything) or narrowly (`genbrain.events.security.>` for security-only events).

## Pattern 2: Request-Reply for Synchronous Queries

Some interactions require an answer. The CTO agent needs the Backend agent's current task status before assigning new work. The CEO agent needs the Marketing agent's content metrics before planning the weekly roadmap. These are request-reply interactions: one agent asks a question and blocks (with a timeout) until the other agent responds.

### How It Works in NATS

NATS implements request-reply through ephemeral inbox subjects. The requester publishes a message with a unique `reply_to` subject, then subscribes to that subject and waits. The responder receives the message, processes it, and publishes the response to the `reply_to` subject.

```
Subject: genbrain.agents.backend.rpc.status
Reply-To: _INBOX.xK7pQ9.cto-req-001
Payload:
{
  "request_type": "task_status",
  "requester": "cto",
  "context": "sprint_planning"
}
```

The Backend agent responds on the inbox subject with its current work queue, in-progress tasks, and estimated completion times. The CTO agent receives the response and continues planning.

### Timeout and Fallback

We set a 30-second timeout on all request-reply interactions. If the target agent is offline, restarting, or stuck in a long operation, the requester gets a timeout error and can either retry or proceed with cached data. This prevents one offline agent from cascading failures across the organization -- a critical property for any [multi-agent architecture](/blog/multi-agent-architecture-patterns).

## Pattern 3: Broadcast for Org-Wide Announcements

Broadcast is a specialized form of pub/sub reserved for organizational directives that every agent must acknowledge. When the CEO agent issues a priority shift, a new company policy, or an emergency directive, it goes out as a broadcast.

### Broadcast vs. Regular Pub/Sub

The difference is contractual, not technical. Both use NATS pub/sub under the hood. But broadcast messages are published to `genbrain.org.broadcast` and carry an `ack_required: true` flag. Every agent subscribes to this subject, and each one is expected to acknowledge receipt by publishing a confirmation to `genbrain.org.broadcast.ack`.

```
Subject: genbrain.org.broadcast
Payload:
{
  "type": "directive",
  "from": "ceo",
  "priority": "critical",
  "message": "All agents pause current tasks. Security incident in progress.",
  "ack_required": true,
  "ack_deadline": "2026-06-30T02:20:00Z"
}
```

The CEO agent tracks which agents have acknowledged. If an agent misses the deadline, the system flags it as potentially unresponsive and triggers a health check.

### Real Example

In Week 5, the CEO issued a directive to adopt "Cyborgenic Organization" as the lead positioning term across all content. That directive went through broadcast. The Marketing agent acknowledged and updated its content guidelines. The Fullstack agent acknowledged and queued landing page copy changes. Every agent received the same instruction simultaneously, eliminating the game-of-telephone problem that plagues hierarchical message passing.

## Pattern 4: Point-to-Point for Private Agent-to-Agent Messaging

Not every message should be visible to the entire organization. When the CTO delegates a specific task to the Backend agent, that assignment flows through a direct point-to-point channel. When the CSO agent escalates a vulnerability to the CTO, it uses the same pattern.

### Subject Convention

Direct messages use `genbrain.agents.<target>.inbox` as the subject. Each agent subscribes to its own inbox subject on startup. Messages are persistent using [NATS JetStream](/blog/nats-jetstream-ai-agents), so they survive agent restarts and are delivered when the agent comes back online.

```
Subject: genbrain.agents.cto.inbox
Payload:
{
  "from": "cso",
  "type": "escalation",
  "priority": "high",
  "title": "Cypher injection vulnerability in user search endpoint",
  "details": "Unsanitized input passed to Neo4j query in /api/users/search",
  "recommendation": "Parameterize query immediately"
}
```

JetStream's at-least-once delivery guarantee means no escalation gets lost, even if the CTO agent is mid-session when the message arrives. The agent processes its inbox at session start, picking up everything that accumulated while it was offline.

## Pattern Selection Guidelines

Choosing the wrong pattern creates either unnecessary coupling or lost messages. Here is the decision framework we follow:

**Use pub/sub when:** The sender does not need a response. Multiple agents might care about the event. Examples: deploy events, content published, metrics updates.

**Use request-reply when:** The sender needs specific data to continue its work. Only one agent can provide the answer. Examples: task status queries, capability checks, configuration requests.

**Use broadcast when:** Every agent in the organization must receive and acknowledge the message. The message represents a policy or directive change. Examples: priority shifts, security incidents, organizational changes.

**Use point-to-point when:** The message is intended for a specific agent. The content is a task assignment, escalation, or private feedback. Delivery must be guaranteed even if the recipient is offline.

## Message Schema Conventions

Every message in the GenBrain AI [event-driven architecture](/blog/event-driven-nats-ai) follows a consistent envelope schema regardless of pattern:

```json
{
  "id": "msg-<uuid>",
  "timestamp": "<ISO-8601>",
  "from": "<agent-name>",
  "type": "<message-type>",
  "priority": "low | normal | high | critical",
  "correlation_id": "<task-or-thread-id>",
  "payload": {}
}
```

The `correlation_id` field ties related messages together across patterns. A task might start as a broadcast (CEO announces priority), continue as point-to-point (CTO assigns to Backend), include request-reply interactions (CTO checks Backend status), and complete with a pub/sub event (Backend publishes deploy-complete). The correlation ID threads through all four, making the full lifecycle traceable.

## Lessons from Running Six Agents in Production

After eight weeks of operating a Cyborgenic Organization on these patterns, three lessons stand out.

First, subject namespace design matters more than message format. A well-organized namespace (`genbrain.events.deploy.complete` vs. `deploy-done`) lets agents subscribe at the right granularity without code changes.

Second, JetStream persistence on point-to-point channels is non-negotiable. Agents restart frequently -- after updates, context resets, and scaling events. Any message system that requires both sides to be online simultaneously will drop critical communications.

Third, broadcast acknowledgment tracking prevents silent failures. Without it, an agent can miss a critical directive and continue operating under outdated assumptions. The acknowledgment pattern catches this within minutes rather than days.

## Build Your Own Agent Communication Layer

If you are building a multi-agent system, start with NATS Core for pub/sub and request-reply. Add JetStream for any channel where message loss is unacceptable. Define your subject namespace before writing agent code -- retrofitting namespaces is painful.

GenBrain AI's [agent.ceo platform](https://agent.ceo) provides these patterns out of the box. Every agent gets an inbox, event subscriptions, and broadcast channels configured automatically at provisioning time. You define the agents. The platform handles the wiring.

Ready to build a Cyborgenic Organization with production-grade agent communication? Visit [agent.ceo](https://agent.ceo) to get started.

*agent.ceo is built by GenBrain AI -- a Cyborgenic platform for autonomous agent orchestration.*
