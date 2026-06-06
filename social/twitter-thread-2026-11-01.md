---
platform: twitter
status: draft
date: 2026-11-01
note: "max_reconnect_attempts=-1 Doesn't Mean What You Think"
---

## Thread: max_reconnect_attempts=-1 Doesn't Mean What You Think

We set `max_reconnect_attempts=-1` in nats-py. Infinite reconnect. Bulletproof.

Our gateway went 503 for hours anyway.

Here's what happened:

---

Auth failures during reconnect are treated as fatal by nats-py.

The library doesn't retry. It closes the connection permanently. Your "infinite reconnect" becomes "zero reconnect" the moment the NATS server can't validate credentials -- even if it's a momentary auth-callout hiccup.

---

The fix: a watchdog goroutine that checks every 30 seconds whether the NATS client is permanently closed.

Not disconnected -- closed. Big difference.

Disconnected = still trying to reconnect.
Closed = given up entirely.

If closed, the watchdog creates a fresh connection from scratch.

---

The subtle part: nats-py's own reconnect logic is fine for network blips. The watchdog doesn't replace it. It handles the one case nats-py won't -- when the library itself decides to stop trying.

"Infinite retry" only works when the library agrees with your definition of "retryable."

---

Full deep dive on building self-healing NATS connections for agent infrastructure:

https://agent.ceo/blog/self-healing-connections-resilient-ai-agent-infrastructure

#NATS #Reconnection #Resilience #AgentCEO
