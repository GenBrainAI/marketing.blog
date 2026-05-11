---
platform: linkedin
day: 255
date: 2027-01-20
topic: "NATS JetStream patterns we use in production"
linkedPost: "nats-patterns-production"
---

Some specific NATS JetStream patterns we run in production across our 7-agent fleet. Sharing because I have not seen many teams document this for AI agent architectures.

Pattern 1: Task stream with consumer groups. Each agent type has a durable consumer on the task stream. CTO agent consumes code review tasks. DevOps agent consumes deployment tasks. Support agent consumes customer queries. JetStream handles routing and load balancing natively.

Pattern 2: Heartbeat streams with TTL. Every agent publishes a heartbeat every 30 seconds. Messages expire after 90 seconds. If DevOps agent checks the heartbeat stream and finds no recent message from CTO agent, it triggers an alert. Simple, stateless health monitoring.

Pattern 3: Replay on restart. When an agent recovers from a spot instance preemption, it requests replay of unacknowledged messages from its consumer. JetStream delivers them in order. The agent processes them sequentially, then switches to real-time consumption. No special recovery logic needed.

Pattern 4: Cross-agent pub/sub for events. Non-critical events (blog published, deployment completed, security scan passed) go to a pub/sub subject. Any agent can subscribe. No guaranteed delivery needed. Just best-effort notification.

The key design choice: separate durable task delivery from ephemeral event notification. Not every message needs exactly-once. Knowing which ones do is the actual engineering work.

Read more: [NATS Patterns in Production](https://agent.ceo/blog/nats-patterns-production)

#CyborgenicOrganization #NATS #JetStream #DistributedSystems #AIAgents #AgentCEO #SystemDesign

— Moshe Beeri, Founder, GenBrain AI
