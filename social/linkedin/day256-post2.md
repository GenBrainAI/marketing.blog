---
platform: linkedin
day: 256
date: 2027-01-21
topic: "The message delivery guarantees autonomous agents actually need"
linkedPost: "agent-delivery-guarantees"
---

Not every message between agents needs the same delivery guarantee. Getting this wrong means you either over-engineer everything or under-protect critical paths. We learned to separate three tiers.

Tier 1 — Exactly-once, durable. Customer escalations. Deployment approvals. Security alerts. These are messages where a miss means real damage. NATS JetStream with consumer acks and deduplication. No exceptions.

Tier 2 — At-least-once, idempotent. Task assignments. Code review requests. Blog publishing triggers. Duplicates are annoying but not dangerous, because we design handlers to be idempotent. Processing the same task twice produces the same result without side effects.

Tier 3 — Best-effort, ephemeral. Status updates. Heartbeats. Metric reports. If one gets lost, the next one arrives in 30 seconds anyway. Plain NATS pub/sub, no persistence, minimal overhead.

The mistake I see teams make: treating all agent communication as Tier 1. That creates unnecessary infrastructure load and adds latency to everything. Or worse, treating everything as Tier 3 and wondering why tasks disappear.

Our current split across the 7-agent fleet: roughly 15% of messages are Tier 1, 35% are Tier 2, and 50% are Tier 3. The critical path is narrow, but it is absolutely protected.

Reliability is not about making everything bulletproof. It is about knowing what cannot fail and engineering accordingly.

Read more: [Agent Delivery Guarantees](https://agent.ceo/blog/agent-delivery-guarantees)

#CyborgenicOrganization #SystemDesign #Reliability #AIAgents #AgentCEO #DistributedSystems #Engineering

— Moshe Beeri, Founder, GenBrain AI
