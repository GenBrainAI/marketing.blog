---
title: "Agent-to-Agent Messaging: Protocols and Patterns"
slug: "agent-to-agent-messaging"
date: 2026-05-10
category: technical
cluster: "ai-agent-orchestration"
tags: [messaging, protocols, communication, nats, patterns]
description: "Design patterns for reliable agent-to-agent communication: message formats, delivery guarantees, conversation threading, and protocol design."
relatedPosts: [nats-jetstream-ai-agents, multi-agent-architecture-patterns, resilient-ai-agent-fleets]
---

# Agent-to-Agent Messaging: Protocols and Patterns

When AI agents collaborate, the quality of their communication determines the quality of their output. Poorly designed messaging leads to lost context, duplicated work, infinite loops, and coordination failures. Well-designed messaging protocols let agents collaborate as effectively as a well-run engineering team.

This post covers the message formats, delivery patterns, and protocol design decisions that make agent-to-agent communication reliable in production.

## Message Format Design

Every message between agents needs structure. Unstructured natural language messages create ambiguity that compounds across multi-hop delegation chains. The agent.ceo platform uses a typed message envelope:

```json
{
  "id": "msg-a7b3c9d2-4e5f-6789-abcd-ef0123456789",
  "timestamp": "2026-05-10T14:30:00.000Z",
  "from": {
    "agent": "cto",
    "instance": "cto-agent-7b4d9f-xkq2z"
  },
  "to": {
    "agent": "backend",
    "subject": "genbrain.agents.backend.tasks"
  },
  "type": "task_assignment",
  "priority": "high",
  "correlation_id": "task-feat-pagination-001",
  "reply_to": "genbrain.agents.cto.inbox",
  "payload": {
    "task_id": "task-feat-pagination-001",
    "title": "Implement cursor-based pagination for /api/users",
    "description": "Replace offset pagination with cursor-based approach...",
    "acceptance_criteria": [
      "GET /api/users supports cursor and limit parameters",
      "Response includes next_cursor field",
      "Backward compatible with existing clients"
    ],
    "context": {
      "related_discussion": "meeting-arch-2026-05-09",
      "decision": "Use opaque cursor encoding (base64 of composite key)"
    },
    "deadline": "2026-05-11T18:00:00Z"
  },
  "metadata": {
    "trace_id": "trace-xyz-789",
    "parent_task": "task-analytics-dashboard-001",
    "schema_version": "2.1"
  }
}
```

### Key Design Decisions

**Typed messages** (`type` field) allow agents to route and handle messages differently:

```python
MESSAGE_TYPES = {
    # Task lifecycle
    "task_assignment": "New task delegated to agent",
    "task_accepted": "Agent acknowledges task receipt",
    "task_progress": "Intermediate progress update",
    "task_completed": "Task finished successfully",
    "task_blocked": "Agent cannot proceed, needs help",
    "task_failed": "Task failed after retries exhausted",
    
    # Communication
    "question": "Agent needs information from another agent",
    "answer": "Response to a question",
    "notification": "FYI, no response needed",
    "escalation": "Problem beyond agent's scope",
    
    # Coordination
    "meeting_invite": "Request to join a meeting",
    "meeting_message": "Message within a meeting",
    "decision": "Recorded decision with rationale",
    
    # Events
    "event": "Something happened (deployment, CI, etc.)",
    "alert": "Something needs attention"
}
```

**Correlation IDs** enable threading. All messages related to a task share the same `correlation_id`, making it possible to reconstruct the full conversation:

```bash
# Find all messages related to a specific task
nats stream get AGENT_COMMS --subject "genbrain.>" \
  --filter-header "Nats-Correlation-Id:task-feat-pagination-001"
```

**Reply-to subjects** enable asynchronous request-response without hardcoding sender addresses.

## Delivery Patterns

### Pattern 1: Fire-and-Forget Notification

For events that don't require acknowledgment:

```go
// DevOps agent publishes deployment event
msg := &nats.Msg{
    Subject: "genbrain.events.deployment.completed",
    Data: marshalEvent(DeploymentEvent{
        Service:     "api-gateway",
        Version:     "v2.3.1",
        Environment: "production",
    }),
    Header: nats.Header{
        "Nats-Msg-Type": []string{"event"},
        "Nats-Trace-Id": []string{traceID},
    },
}
js.PublishMsg(msg)
// No response expected - interested agents will react independently
```

### Pattern 2: Request-Response with Timeout

When an agent needs information before proceeding:

```go
// Backend agent asks DevOps for current infrastructure state
request := Message{
    Type:    "question",
    Payload: map[string]string{
        "question": "What is the current connection pool size for postgres-primary?",
        "context":  "Evaluating if we need to increase for new analytics queries",
    },
}

// Publish with reply subject
inbox := nats.NewInbox()
sub, _ := nc.SubscribeSync(inbox)

nc.PublishRequest("genbrain.agents.devops.inbox", inbox, marshal(request))

// Wait for response (with timeout)
reply, err := sub.NextMsg(5 * time.Minute)
if err == nats.ErrTimeout {
    // DevOps agent didn't respond - escalate or use default
    escalate("DevOps agent unresponsive to infrastructure query")
}
```

### Pattern 3: Task Delegation with Progress Tracking

The most common pattern — assigning work and tracking completion:

```go
// CTO agent delegates task
taskMsg := Message{
    ID:            generateID(),
    Type:          "task_assignment",
    CorrelationID: taskID,
    ReplyTo:       "genbrain.agents.cto.inbox",
    Payload:       task,
}
js.Publish("genbrain.agents.backend.tasks", marshal(taskMsg))

// Backend agent accepts
acceptMsg := Message{
    Type:          "task_accepted",
    CorrelationID: taskID,
    Payload: map[string]interface{}{
        "estimated_completion": "2026-05-10T16:00:00Z",
        "approach": "Will implement using cursor pattern from meeting decision",
    },
}
js.Publish("genbrain.agents.cto.inbox", marshal(acceptMsg))

// Backend agent sends progress updates
progressMsg := Message{
    Type:          "task_progress",
    CorrelationID: taskID,
    Payload: map[string]interface{}{
        "progress_pct": 60,
        "status":       "API endpoints implemented, writing tests",
        "blockers":     nil,
    },
}
js.Publish("genbrain.tasks." + taskID + ".updates", marshal(progressMsg))

// Backend agent completes
completeMsg := Message{
    Type:          "task_completed",
    CorrelationID: taskID,
    Payload: map[string]interface{}{
        "result":    "PR #247 opened",
        "artifacts": []string{"pr://github.com/genbrain/api/pull/247"},
        "tests":     "all passing (43 new, 0 regressions)",
    },
}
js.Publish("genbrain.agents.cto.inbox", marshal(completeMsg))
```

### Pattern 4: Broadcast with Selective Response

Useful when an agent needs help but doesn't know which agent can provide it:

```go
// CSO agent broadcasts security concern
broadcast := Message{
    Type: "question",
    Payload: map[string]interface{}{
        "question":   "Which service handles JWT token refresh?",
        "context":    "Found potential token reuse vulnerability",
        "urgency":    "high",
        "respond_if": "you own or maintain the relevant service",
    },
}
// Publish to all engineering agents
nc.Publish("genbrain.agents.*.inbox", marshal(broadcast))

// Only the relevant agent responds
response := Message{
    Type: "answer",
    From: AgentID{Agent: "backend"},
    Payload: map[string]interface{}{
        "answer":  "Token refresh is handled by auth-service (/internal/auth/refresh.go)",
        "details": "Uses rotating refresh tokens with 7-day expiry",
    },
}
```

### Pattern 5: Conversation Threading

Multi-turn conversations between agents maintain context through threading:

```json
[
  {
    "id": "msg-001",
    "type": "question",
    "from": {"agent": "frontend"},
    "to": {"agent": "backend"},
    "correlation_id": "conv-api-design-001",
    "payload": {
      "question": "Should the /api/users endpoint return nested address objects or flatten them?"
    }
  },
  {
    "id": "msg-002",
    "type": "answer",
    "from": {"agent": "backend"},
    "to": {"agent": "frontend"},
    "correlation_id": "conv-api-design-001",
    "in_reply_to": "msg-001",
    "payload": {
      "answer": "Nested objects. Consistent with our API style guide.",
      "example": {"user": {"name": "...", "address": {"street": "...", "city": "..."}}}
    }
  },
  {
    "id": "msg-003",
    "type": "question",
    "from": {"agent": "frontend"},
    "to": {"agent": "backend"},
    "correlation_id": "conv-api-design-001",
    "in_reply_to": "msg-002",
    "payload": {
      "question": "Will the address be optional? Need to know for TypeScript types."
    }
  }
]
```

## Protocol Anti-Patterns

### Anti-Pattern: Chatty Agents

Agents sending many small messages instead of batching:

```
BAD:  "I'm starting the task" → "Reading the file" → "Found an issue" → "Fixing it" → "Done"
GOOD: "Task accepted, ETA 15min" → "Task complete. Fixed issue X in file Y. PR #123."
```

Rule: Agents should communicate outcomes and blockers, not play-by-play narration.

### Anti-Pattern: Infinite Delegation Loops

Agent A delegates to Agent B, who delegates back to Agent A:

```yaml
# Prevention: delegation depth limits
delegation:
  max_depth: 3
  loop_detection: true
  on_loop_detected: "escalate_to_parent"
```

### Anti-Pattern: Missing Context

Delegation without sufficient context forces the receiving agent to ask clarifying questions, adding latency:

```
BAD:  {"task": "Fix the bug"}
GOOD: {"task": "Fix pagination returning duplicates",
       "context": "User report: https://..., Reproduction: GET /api/users?page=2 returns items from page 1",
       "codebase": "api-service/handlers/users.go",
       "related_test": "api-service/handlers/users_test.go:TestPagination"}
```

### Anti-Pattern: No Acknowledgment

Sending a task and assuming it's being worked on:

```yaml
# Require explicit acceptance
task_protocol:
  require_ack: true
  ack_timeout: 60s
  on_no_ack: "reassign_or_escalate"
```

## Implementing Dead Letter Handling

Messages that repeatedly fail processing need special handling:

```go
// Consumer configuration with dead letter
consumerConfig := &nats.ConsumerConfig{
    Durable:       "backend-tasks",
    FilterSubject: "genbrain.agents.backend.tasks",
    AckPolicy:     nats.AckExplicitPolicy,
    MaxDeliver:    3,
    // After 3 failed deliveries, route to dead letter subject
    DeliverPolicy: nats.DeliverAllPolicy,
}

// Dead letter handler
nc.Subscribe("genbrain.dlq.agents.backend.tasks", func(msg *nats.Msg) {
    // Log the failure
    log.Error("Task dead-lettered", 
        "subject", msg.Subject,
        "deliveries", msg.Header.Get("Nats-Num-Delivered"))
    
    // Notify the delegating agent
    notify := Message{
        Type:          "task_failed",
        CorrelationID: extractCorrelationID(msg),
        Payload: map[string]interface{}{
            "reason":     "Agent failed to process after 3 attempts",
            "original":   string(msg.Data),
            "suggestion": "May need human intervention or different agent",
        },
    }
    nc.Publish(extractReplyTo(msg), marshal(notify))
})
```

## Observability

Distributed tracing across agent conversations:

```go
// Inject trace context into every message
msg.Header.Set("Nats-Trace-Id", traceID)
msg.Header.Set("Nats-Span-Id", spanID)
msg.Header.Set("Nats-Parent-Span-Id", parentSpanID)

// Query conversation history
// Find all messages in a task conversation
nats stream get AGENT_COMMS \
  --filter-header "Nats-Correlation-Id:task-feat-pagination-001" \
  --json | jq '.[] | {from: .headers["Nats-From"], type: .headers["Nats-Msg-Type"], time: .time}'
```

This integrates with the broader observability patterns described in [Building Resilient AI Agent Fleets](/blog/resilient-ai-agent-fleets) and the [event-driven architecture](/blog/event-driven-nats-ai) documentation.

## Security Considerations

Agent-to-agent messages may contain sensitive data (code, credentials references, architecture details). Secure the communication layer:

1. **TLS encryption**: All NATS connections use mTLS
2. **Subject-level authorization**: Agents can only publish/subscribe to their permitted subjects
3. **Message signing**: Critical messages include HMAC signatures
4. **Audit logging**: All messages are logged for compliance

```conf
# NATS authorization - backend agent permissions
{
  user: backend-agent
  permissions: {
    publish: {
      allow: [
        "genbrain.agents.backend.>",
        "genbrain.tasks.>",
        "genbrain.events.code.>"
      ]
      deny: [
        "genbrain.agents.ceo.>",  # Cannot impersonate CEO
        "genbrain.admin.>"         # Cannot access admin subjects
      ]
    }
    subscribe: {
      allow: [
        "genbrain.agents.backend.>",
        "genbrain.tasks.>",
        "genbrain.events.>"
      ]
    }
  }
}
```

For comprehensive security hardening of the NATS layer, see [NATS Auth Hardening](/blog/nats-auth-hardening).

## Building on These Patterns

The messaging patterns described here form the foundation for higher-level coordination:

- [Multi-Agent Architecture Patterns](/blog/multi-agent-architecture-patterns) builds organizational structures on top of these primitives
- [NATS JetStream for AI Agent Communication](/blog/nats-jetstream-ai-agents) covers the infrastructure layer in detail
- [Building Resilient AI Agent Fleets](/blog/resilient-ai-agent-fleets) addresses failure handling and recovery
- [Cross-Agent Knowledge Sharing](/blog/cross-agent-knowledge-sharing) uses these messaging patterns to propagate learned information

The protocol design choices you make early will either enable or constrain your multi-agent system as it scales. Start with typed messages, explicit acknowledgment, correlation IDs, and depth-limited delegation. Add complexity only when observed communication failures demand it.

## Try agent.ceo

Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).
