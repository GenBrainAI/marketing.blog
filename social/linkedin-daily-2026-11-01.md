---
platform: linkedin
status: draft
date: 2026-11-01
note: "max_reconnect_attempts=-1 Doesn't Mean What You Think"
---

## Post: max_reconnect_attempts=-1 Doesn't Mean What You Think

We set `max_reconnect_attempts=-1` in nats-py and assumed our NATS connections would reconnect forever. They didn't.

Here's what the docs don't emphasize: auth failures during reconnect are treated as fatal. The library closes the connection permanently and stops retrying. No more reconnect attempts. No error callback. Just silence.

Our API gateway went 503 for hours because of a momentary auth-callout hiccup during a reconnect cycle. The NATS server briefly couldn't validate credentials, nats-py treated it as a permanent auth rejection, and the client shut itself down. Infinite reconnect became zero reconnect.

The fix: a background watchdog that checks every 30 seconds whether the NATS client object is permanently closed. Not disconnected -- closed. If it detects a closed client, it creates a fresh connection from scratch.

The difference matters. A disconnected client is still trying to reconnect. A closed client has given up. Your monitoring might not distinguish between the two, but your uptime definitely will.

"Infinite retry" only works when the library agrees with your definition of "retryable."

Read the full deep dive: https://agent.ceo/blog/self-healing-connections-resilient-ai-agent-infrastructure

#NATS #Reconnection #Resilience #AgentCEO
