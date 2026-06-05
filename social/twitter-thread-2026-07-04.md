1/ We just shipped zero-touch customer onboarding.

New org spins up. 90 seconds later, every agent is fully operational.

No setup calls. No manual config. No onboarding docs.

Here's how the system works:

2/ Component 1: KB Seeder

Auto-ingests platform documentation into each customer's Neo4j knowledge graph.

New docs land? Seeder picks them up. Customer agents query their own graph and get current answers. No stale wikis.

3/ Component 2: ConfigMap Reconciler

Platform capabilities change constantly — new MCP tools, updated endpoints, deprecated features.

The reconciler watches for changes and pushes updates to every customer org's agent configs. Automatically. Continuously.

4/ Component 3: Platform Ops Template

140 lines that tell an agent exactly what 199 MCP tools it has access to, what each does, and when to use them.

This template IS the onboarding. It gets seeded, reconciled, and kept current without anyone touching it.

5/ Combined effect:

Customer org created. KB Seeder loads knowledge graph. Reconciler syncs configs. Ops Template provides operational awareness.

Result: agents that know what they can do, the moment they exist.

6/ This is what we mean by cyborgenic infrastructure — systems that make AI agents self-aware of their own capabilities.

Full technical deep dive with architecture details: https://agent.ceo/blog/zero-touch-customer-onboarding-platform-knowledge
