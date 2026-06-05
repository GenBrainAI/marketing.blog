---
platform: linkedin
status: draft
date: 2026-06-19
topic: Building in Public — production incidents and AI agent SRE
note: Thursday daily LinkedIn post. Cannot auto-post — no LinkedIn API keys provisioned.
---

## Post: Our AI Agents Were Silently Dropping Messages. Here's What We Built to Stop It.

Last week, one of our agents stopped responding to tasks. No errors. No crashes. Just... silence.

The root cause: its NATS connection had died without triggering any disconnect event. Messages were being published to a subscription that no longer existed. From the outside, the agent looked healthy. From the inside, it was deaf.

This is the kind of bug that only shows up in production. In development, connections stay up. In a real cluster running 24/7, network blips happen. TLS handshakes expire. Load balancers rotate. And your agent just stops hearing.

**Our fix: a NATS watchdog.**

A lightweight background process that monitors every agent's message bus connection. If no heartbeat arrives within a configurable window, the watchdog forces a reconnect. If the reconnect fails, it escalates to the management layer and logs the incident. The agent never has to know — it just starts receiving messages again.

This is not novel engineering. It is the same pattern every SRE team uses for database connections, health checks, and service meshes. The insight is that AI agents need the exact same operational discipline.

We run AI agents in real production roles — not demos, not prototypes. That means we deal with the same infrastructure failures any production service faces. Dead connections. Silent data loss. Cascading timeouts.

If you are building AI agents for production, treat them like production services. Monitor them. Watchdog them. Build the recovery path before you need it.

More about how we operate a fleet of AI agents: agent.ceo

#AIAgents #SRE #BuildingInPublic #ProductionAI #NATS #Observability #DevOps
