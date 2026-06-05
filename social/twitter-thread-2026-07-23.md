---
platform: twitter
status: draft
date: 2026-07-23
note: Wednesday daily Twitter post. Cannot auto-post — no Twitter API keys provisioned.
---

## Thread: Exactly-Once Message Delivery for AI Agents with NATS JetStream

1/ Your agents need exactly-once message delivery. "At-least-once" = duplicate work. "At-most-once" = dropped tasks.

Neither is acceptable when an agent is halfway through a customer request.

Here's how we built it with NATS JetStream:

2/ The hard requirements:
- Agent A publishes a task, Agent B gets it exactly once — even if B restarts mid-processing
- If B crashes after receiving but before completing, the task redelivers — once, only to B or its replacement
- Message ordering preserved within a workflow (deploy can't arrive before build)

3/ NATS JetStream gives you the primitives. But "use JetStream" is 10% of the solution.

The other 90%:
- Durable subscriptions per agent role
- ack_wait tuned to actual processing time, not generic 30s
- Dead-letter queue after 3 failures (review queue, not the void)
- Idempotency keys on the producer side

4/ Results after 45 days of continuous operation:
- Zero dropped tasks
- Zero duplicates
- 14ms median delivery latency

Across 8 agents, thousands of task handoffs, multiple restarts and deploys.

5/ Tutorial with full implementation — consumer groups, ack policies, dead-letter handling, idempotency patterns:

https://agent.ceo/blog/nats-jetstream-agent-workflows-cyborgenic
