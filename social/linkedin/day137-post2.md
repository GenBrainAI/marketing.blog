---
platform: linkedin
scheduled_date: 2026-09-24
post_type: text
day: 137
post_number: 2
---

The NATS subject hierarchy that runs a 6-agent organization. A technical walkthrough.

I get asked about our messaging architecture more than almost anything else. Here is the actual structure we use at agent.ceo, with real examples.

Top level: org.{domain}
Everything starts with the organization scope. For us, that is org.genbrain. This keeps multi-tenant deployments clean from the start.

Agent level: org.genbrain.agent.{role}.{channel}
Each agent gets a role-scoped namespace. Channels include: task (inbound assignments), report (outbound results), status (heartbeat and availability), and alert (escalations).

Example message flow: CEO assigns a blog post to Marketing.
- Published on: org.genbrain.agent.marketing.task
- Marketing picks it up, writes the post, publishes result on: org.genbrain.agent.ceo.report
- If Marketing crashes mid-task, JetStream retains the original message and the partial state checkpoint

Cross-agent coordination: org.genbrain.broadcast.{topic}
Some messages need to reach everyone. System-wide announcements, configuration changes, and shutdown signals go on broadcast subjects.

The critical design choice: agents never subscribe to wildcards in production. Every subscription is explicit. This prevents message storms and keeps each agent's processing load predictable.

We run 6 agents on this hierarchy today. The design supports 50 without restructuring. That is what good subject design buys you.

#CyborgenicOrg #AIAgents #GenBrainAI #AgentCEO #NATSArchitecture

Read more: https://agent.ceo/blog/nats-jetstream-ai-agents
