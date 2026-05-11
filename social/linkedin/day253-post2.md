---
platform: linkedin
day: 253
date: 2027-01-18
topic: "The architecture that makes spot instances possible"
linkedPost: "spot-instance-architecture"
---

A thread on the architecture behind running AI agents on GKE spot instances.

The key insight: preemptible infrastructure only works if your system was designed for interruption from the start.

Our stack:
- GKE autopilot with spot node pools
- Firestore for persistent state and context checkpoints
- NATS JetStream for durable message queues
- Claude agents with stateless restart capability

When Google reclaims a spot node, here is what happens:

1. The agent receives a SIGTERM signal
2. It flushes current context to Firestore (takes ~2 seconds)
3. The pod terminates
4. GKE scheduler places a new pod on an available spot node
5. The agent boots, pulls its last checkpoint from Firestore
6. NATS JetStream replays any unacknowledged messages
7. The agent resumes work

Total downtime per preemption event: 20-35 seconds. We see roughly 2-3 preemptions per week across the fleet. That is maybe 90 seconds of total downtime weekly.

Compare that to the cost savings: spot instances run at 60-91% discount versus on-demand pricing. For a fleet of 7 agents running 24/7, that adds up fast.

The lesson is not "use spot instances." The lesson is "build for failure first, and cheap infrastructure becomes available to you automatically."

Read more: [Spot Instance Architecture](https://agent.ceo/blog/spot-instance-architecture)

#CyborgenicOrganization #CloudArchitecture #GKE #Kubernetes #AIAgents #AgentCEO #InfrastructureCost

— Moshe Beeri, Founder, GenBrain AI
