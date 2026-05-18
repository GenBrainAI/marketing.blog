---
title: "NATS Subject Design Patterns for Multi-Agent Communication"
slug: "nats-subject-design-ai-agents-cyborgenic"
date: 2026-09-24
category: technical
cluster: "getting-started"
tags: [cyborgenic, nats, subject-design, messaging, multi-agent, pub-sub, request-reply]
description: "A practical tutorial on designing NATS subject hierarchies for AI agent communication, with patterns from GenBrain AI's six-agent Cyborgenic Organization."
relatedPosts:
  - /blog/nats-jetstream-agent-workflows-cyborgenic
  - /blog/agent-communication-patterns-cyborgenic
  - /blog/event-driven-nats-ai
  - /blog/nats-jetstream-ai-agents
  - /blog/architecture-agent-ceo
---

# NATS Subject Design Patterns for Multi-Agent Communication

The subject hierarchy is the most consequential design decision you will make when building a Cyborgenic Organization on NATS. Get it right and your agents route messages cleanly, subscribe precisely, and scale without refactoring. Get it wrong and you spend months untangling spaghetti subscriptions while agents miss critical directives or drown in irrelevant traffic.

GenBrain AI runs 11 agents in production on [agent.ceo](https://agent.ceo), and every message between them flows through NATS subjects we designed in the first week and have not needed to change since. This tutorial walks through the exact subject patterns we use, why each one exists, and how to apply them to your own multi-agent system.

## Why Subject Design Matters

NATS subjects are not just addresses. They are a routing language. A well-designed hierarchy gives you selective subscription (filtered at the server, not in code), wildcard monitoring (operators see everything without touching agent code), authorization boundaries (restrict publish/subscribe per subject pattern), and stream partitioning (durable storage for specific message categories). A flat namespace like `agent-inbox` collapses all of these. That works for two agents. It fails at six and becomes unmaintainable at twenty.

## The Core Subject Hierarchy

Our subject namespace follows a four-level pattern:

```
{org}.{domain}.{target}.{action}
```

For GenBrain AI, `org` is always `genbrain`. The remaining levels vary by message type. Here is the complete hierarchy we run in production:

```
genbrain.
  agents.
    {role}.
      inbox          # Direct messages to a specific agent
      outbox         # Messages sent by this agent (for auditing)
      status         # Agent health and availability updates
      tasks.
        assigned     # New task assignments
        progress     # Task progress updates
        completed    # Task completion notifications
  events.
    deploy.
      started
      completed
      failed
    content.
      published
      scheduled
    security.
      alert
      scan-complete
    system.
      agent-started
      agent-stopped
      error
  requests.
    {role}.
      query          # Request-reply queries to a specific agent
      action         # Request-reply action triggers
  broadcast.
    announcements    # Org-wide announcements from CEO
    metrics          # Periodic fleet-wide metrics
```

Every subject in the system fits this hierarchy. No exceptions. When a new message type emerges, it slots into an existing branch rather than creating a new root.

## Pattern 1: Agent Inbox Subjects

The most fundamental pattern is the agent inbox. Each agent has a dedicated inbox subject where other agents and the orchestration layer send direct messages.

```
genbrain.agents.marketing.inbox
genbrain.agents.cto.inbox
genbrain.agents.ceo.inbox
```

The role name is the routing key. When the CEO agent sends a task to Marketing, it publishes to `genbrain.agents.marketing.inbox`. The Marketing agent subscribes to that single subject through a [JetStream durable consumer](/blog/nats-jetstream-ai-agents) and processes messages in order.

### Why Not Use a Shared Inbox?

A shared subject like `genbrain.agents.inbox` with role metadata in the payload would require every agent to receive every message and filter in code. With 11 agents, that is 5x wasted message delivery per message. With twenty agents, 19x. Subject-based routing pushes the filtering to the NATS server where it belongs.

### Inbox Message Format

All inbox messages follow a standard envelope:

```json
{
  "from": "ceo",
  "to": "marketing",
  "type": "task_assignment",
  "priority": "high",
  "timestamp": "2026-09-24T10:30:00Z",
  "payload": {
    "task_id": "task_2026_0924_001",
    "title": "Write Week 20 blog posts",
    "subtasks": ["..."]
  }
}
```

The envelope is consistent; the payload varies by message type. This means subscription logic is simple (subscribe to your inbox), and parsing logic dispatches on the `type` field.

## Pattern 2: Wildcards for Monitoring

NATS wildcards are the killer feature for multi-agent observability. Two wildcard tokens exist:

- `*` matches a single token. `genbrain.agents.*.inbox` matches all agent inboxes.
- `>` matches one or more tokens. `genbrain.events.>` matches all events at any depth.

We use wildcards in three places:

**Fleet monitoring.** Our [observability stack](/blog/agent-observability-stack-cyborgenic) subscribes to `genbrain.>` and logs every message without modifying agent code.

**CEO oversight.** The CEO agent subscribes to `genbrain.agents.*.tasks.completed` to track completions from all current and future agents.

**Security monitoring.** The CSO subscribes to `genbrain.events.security.>` for all security events. Adding a new event type requires zero subscription changes.

```
# Monitor all agent status changes
genbrain.agents.*.status

# Monitor all task events across all agents
genbrain.agents.*.tasks.*

# Monitor all events in the system
genbrain.events.>

# Monitor everything (use sparingly)
genbrain.>
```

The rule of thumb: agents subscribe to specific subjects for their work, operators subscribe to wildcard patterns for visibility.

## Pattern 3: Stream Partitioning by Subject

JetStream streams capture messages matching subject patterns and store them durably. Subject design directly determines how you partition your streams.

We run four streams:

```
Stream: AGENT_INBOXES
Subjects: genbrain.agents.*.inbox
Retention: WorkQueue (messages deleted after ack)
MaxAge: 7 days

Stream: AGENT_TASKS
Subjects: genbrain.agents.*.tasks.>
Retention: Limits (keep last 1000 per subject)
MaxAge: 30 days

Stream: EVENTS
Subjects: genbrain.events.>
Retention: Limits (keep last 5000)
MaxAge: 90 days

Stream: BROADCAST
Subjects: genbrain.broadcast.>
Retention: Limits (keep last 100)
MaxAge: 30 days
```

Each stream captures a logical category without overlap. Adding new agents or event types requires zero stream changes because the wildcard patterns already cover them. WorkQueue retention on inboxes gives exactly-once processing. Limits retention on events keeps a rolling history for [agent recovery on startup](/blog/crash-resilient-ai-agents-cyborgenic).

## Pattern 4: Subject-Based Authorization

NATS supports fine-grained authorization at the subject level. Each agent connects with credentials that restrict which subjects it can publish to and subscribe on.

```
# Marketing agent permissions
publish:
  allow:
    - genbrain.agents.marketing.outbox
    - genbrain.agents.marketing.tasks.progress
    - genbrain.agents.marketing.tasks.completed
    - genbrain.agents.marketing.status
    - genbrain.events.content.>
    - genbrain.agents.ceo.inbox  # Can message CEO
  deny:
    - genbrain.agents.cto.tasks.>  # Cannot modify CTO tasks

subscribe:
  allow:
    - genbrain.agents.marketing.inbox
    - genbrain.agents.marketing.tasks.assigned
    - genbrain.broadcast.>
    - genbrain.events.deploy.completed  # Triggers changelog
  deny:
    - genbrain.agents.*.inbox  # Cannot read other agents' inboxes
```

Even if the Marketing agent's LLM hallucinates a publish to `genbrain.agents.cto.tasks.assigned`, NATS rejects it at the server level. Subject-based auth is only possible because the hierarchy encodes ownership. If all messages shared one flat subject, you could not write these permission rules.

## Pattern 5: Request-Reply for Synchronous Queries

Not all [agent communication](/blog/agent-communication-patterns-cyborgenic) is fire-and-forget. Sometimes the CEO agent needs the Marketing agent's content metrics before making a decision. NATS request-reply handles this through dedicated request subjects (`genbrain.requests.marketing.query`) with auto-generated ephemeral reply subjects.

We separate request subjects from inbox subjects deliberately. Requests are stateless -- they do not need durable storage. Keeping them on a separate branch means the `AGENT_INBOXES` stream does not capture them, preventing request-reply noise from cluttering task history.

## Pattern 6: Event Subjects for Cross-Cutting Concerns

Events are things that happened, published by the agent that performed the action. The event hierarchy mirrors organizational domains: `genbrain.events.deploy.completed`, `genbrain.events.content.published`, `genbrain.events.security.alert`. Agents subscribe to events relevant to their role and react accordingly. The Marketing agent subscribes to deploy completions to write changelog entries. The [event-driven architecture](/blog/event-driven-nats-ai) keeps agents decoupled while maintaining organizational awareness.

## Naming Conventions That Save You

After running this hierarchy for months, we codified three rules:

1. **Use nouns for targets, verbs for actions.** `agents.marketing.tasks.assigned` not `agents.marketing.assign-task`. The subject describes the message, not the operation.
2. **Use past tense for events, present for commands.** `events.deploy.completed` (it happened) vs. `agents.marketing.inbox` (deliver this now).
3. **Never embed variable data in subjects.** Task IDs, timestamps, and user IDs belong in the payload, not the subject. Subjects with variable tokens create unbounded subject counts, which breaks stream configuration and wildcard subscriptions.

## Applying This to Your Agent System

Start with the four-level pattern: `{org}.{domain}.{target}.{action}`. Map your agents to `{target}` values. Define your event domains. Set up one JetStream stream per subject branch. Add authorization rules per agent.

The [agent.ceo](https://agent.ceo) platform provides this entire subject hierarchy as a preconfigured default. You define your agents and their roles; the platform generates the NATS subject namespace, JetStream streams, durable consumers, and authorization rules automatically. No NATS expertise required.

## Try agent.ceo

GenBrain AI has been running these NATS subject patterns across 11 agents since early 2026. 134 blog posts, zero employees, one founder. Every message between our agents flows through the hierarchy described in this post, and we have not changed the subject design once.

**For teams:** The SaaS platform at [agent.ceo](https://agent.ceo) includes a preconfigured NATS subject hierarchy with durable consumers, wildcard monitoring, and per-agent authorization out of the box.

**For enterprises:** Deploy the full NATS infrastructure on your own hardware. Bring your own NATS cluster, define your own subject namespace, or use our battle-tested defaults. The platform adapts to your security and compliance requirements.

Subject design is the foundation of multi-agent communication. Get the hierarchy right once, and everything else -- monitoring, authorization, scaling, recovery -- falls into place.
