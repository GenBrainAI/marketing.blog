1/ We found 3 silent failure modes running AI agents in production.

No errors. No alerts. Just agents that quietly stopped working.

New blog: "Self-Healing Connections" — here are the failures and the design principles behind each fix:

2/ Failure 1: NATS permanent close

max_reconnect_attempts=-1 (unlimited). Server goes down, comes back. Client stays dead.

Why: "unlimited retries" only covers the reconnection window. Once the client hits CLOSED state, it's permanent. No retries. No logs.

Fix: watchdog checks real connection state every 30s. Dead? Rebuild from scratch.

3/ Failure 2: MCP transient errors

MCP proxy gets a timeout or 503. Immediately closes the connection. No retry.

A 30-second blip in an upstream service kills an agent's tool access for the rest of its session.

Fix: exponential backoff with jitter. Retries: 1s, 2s, 4s, 8s, 16s. Transient errors become invisible. Permanent failures still surface fast.

4/ Failure 3: Inbox flood loop

Agent sends status update. Update routes to own inbox. Agent processes it. Generates new status. Processes that. 40 cycles later: full context window, zero useful work.

Fix: flood gate — skip self-sent messages, cap per-cycle processing, track origin chains.

5/ The design principle behind all three fixes:

Configuration tells you what SHOULD happen. Runtime state tells you what IS happening. If you only check config, you only catch config errors.

Every connection needs a watchdog. Every retry needs backoff. Every message loop needs a circuit breaker.

6/ Full write-up with code patterns and implementation details:

https://agent.ceo/blog/self-healing-connections-resilient-ai-agent-infrastructure

This is how we keep 6 AI agents running 24/7 at GenBrain AI. Follow the build at https://agent.ceo
