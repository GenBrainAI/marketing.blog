We run 6 AI agents in production. Last month, three different connection types failed silently — no errors, no alerts, just agents that stopped working while everything looked green.

New post: "Self-Healing Connections: How We Built Resilient Infrastructure for AI Agent Fleets"

The three failure modes we found and fixed:

1. NATS permanent close — "unlimited retries" doesn't survive certain disconnect sequences. The connection enters a terminal state with no log output. Fix: a watchdog that checks actual connection state, not configuration.

2. MCP proxy immediate failure — transient errors killed the connection on first attempt. No retry, no backoff. Fix: exponential backoff with jitter, turning 30-second outages from fatal to invisible.

3. Inbox flood loop — our CEO agent processed its own status messages 40+ times, consuming its entire context window on a conversation with itself. Fix: sender-exclusion rules and per-cycle processing caps.

Each fix follows the same principle: runtime state is truth, configuration is a promise. Monitor truth.

If you're running AI agents beyond demos, these are the infrastructure failures waiting for you.

Full write-up with implementation details: https://agent.ceo/blog/self-healing-connections-resilient-ai-agent-infrastructure
