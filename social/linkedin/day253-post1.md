---
platform: linkedin
day: 253
date: 2027-01-18
topic: "GKE spot instances — running agents on preemptible infrastructure"
linkedPost: "gke-spot-instances-agents"
---

Most people hear "preemptible infrastructure" and think "unreliable." We hear it and think "cheap."

Our 7-agent fleet runs on GKE spot instances. Google can reclaim any node at any time with 30 seconds of notice. For a traditional application, that is a nightmare. For a Cyborgenic Organization designed around restarts, it is a feature.

Here is why it works. Every agent in our fleet already handles restarts gracefully. Context checkpointing to Firestore means state survives termination. NATS JetStream ensures no messages are lost during transitions. The agent comes back, rehydrates its context, and picks up where it left off. Average recovery time: 27 seconds.

Spot instances are not a hack we bolted on. They are a natural fit for an architecture that treats failure as normal. We built restart budgets, living migrations, and context recovery long before we moved to spot. The infrastructure cost savings were a consequence of good architecture, not the goal.

When your system already handles 9 restarts per week without breaking a sweat, the question stops being "can we run on preemptible nodes?" It becomes "why would we pay 3x more for guaranteed ones?"

253 days in. Still running on borrowed compute. Still shipping.

Read more: [GKE Spot Instances for Agent Fleets](https://agent.ceo/blog/gke-spot-instances-agents)

#CyborgenicOrganization #GKE #SpotInstances #CloudCost #AIAgents #AgentCEO #BuildInPublic

— Moshe Beeri, Founder, GenBrain AI
