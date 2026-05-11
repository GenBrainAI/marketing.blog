---
platform: twitter
day: 255
date: 2027-01-20
topic: "NATS JetStream exactly-once delivery deep-dive"
thread_length: 8
---

**Tweet 1/8:**
"Exactly-once delivery is impossible." Technically true in the general case. Practically false with NATS JetStream + idempotent consumers. Here's how we get exactly-once semantics for agent task processing.

**Tweet 2/8:**
NATS JetStream gives you at-least-once delivery out of the box. Messages persist to stream, get delivered to consumers, and require explicit ACK. No ACK within the timeout = automatic redelivery.

**Tweet 3/8:**
The problem: at-least-once means duplicates happen. Agent crashes after processing but before ACK. NATS redelivers. Your agent runs the same task twice. Blog gets published twice. Bad.

**Tweet 4/8:**
Solution layer 1: JetStream message deduplication. Set a Nats-Msg-Id header on publish. JetStream deduplicates within a configurable window. We use 5 minutes. Duplicate publishes are silently dropped.

**Tweet 5/8:**
Solution layer 2: Consumer-side idempotency. Every task gets a unique ID. Before processing, the agent checks a completed-tasks set. If the ID exists, ACK immediately and skip. Dedup at the consumer level.

**Tweet 6/8:**
Solution layer 3: Double-write prevention. The agent writes output AND records completion in a single transaction-like sequence. Output to PVC, then completion marker, then ACK. Crash before marker = safe retry.

**Tweet 7/8:**
The result: 252+ days, 7 agents, thousands of NATS messages daily. Zero duplicate task executions in production. Zero lost messages. At-least-once delivery + idempotent consumers = exactly-once semantics.

**Tweet 8/8:**
NATS JetStream is the backbone of our cyborgenic org. Lightweight, fast, and reliable enough to trust with autonomous agent coordination. Details at agent.ceo

#CyborgenicOrganization #AIAgents #AgentCEO #NATS #JetStream #ExactlyOnce #DistributedSystems
