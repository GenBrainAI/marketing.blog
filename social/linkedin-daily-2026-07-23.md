---
platform: linkedin
status: draft
date: 2026-07-23
note: Wednesday daily LinkedIn post. Cannot auto-post — no LinkedIn API keys provisioned.
---

## Post: Your Agents Need Exactly-Once Delivery. Here's How We Built It.

Your agents need exactly-once message delivery. Here's how we built it with NATS JetStream.

When you have 8 AI agents passing tasks to each other, "at-least-once" delivery means duplicate work. "At-most-once" means dropped tasks. Neither is acceptable when an agent is halfway through a customer request.

The requirements were specific:

- Agent A publishes a task. Agent B must receive it exactly once, even if B restarts mid-processing.
- If B crashes after receiving but before completing, the task must be redelivered — but only once, and only to B (or its replacement).
- Message ordering must be preserved within a workflow. A deploy task can't arrive before the build task it depends on.

NATS JetStream gives us the primitives: persistent streams, consumer groups with ack policies, and replay on restart. But "use JetStream" is about 10% of the solution. The other 90% is:

- Designing consumer groups so each agent role has its own durable subscription
- Setting ack_wait to match actual agent processing time (not a generic 30-second default)
- Building dead-letter handling for tasks that fail 3 times — they go to a review queue, not into the void
- Idempotency keys on the producer side so network retries don't create duplicate messages

The result: zero dropped tasks across 45 days of continuous operation. Zero duplicates. 14ms median delivery latency.

Tutorial with full implementation details: https://agent.ceo/blog/nats-jetstream-agent-workflows-cyborgenic

#NATS #JetStream #MessageQueue #DistributedSystems #AIAgents #GenBrainAI #BuildingInPublic
