---
platform: twitter
status: draft
date: 2026-11-03
note: "Blog launch: NATS Connection Watchdog"
---

## Thread: NATS Connection Watchdog -- Recovering From Permanent Close

New blog: how we built a watchdog for the one thing nats-py's reconnect logic won't handle -- a permanently closed client.

---

The problem: `max_reconnect_attempts=-1` should mean infinite retry. But auth failures during reconnect are fatal. nats-py closes the client permanently. No more retries.

Our gateway sat with a dead NATS connection for hours. 503s everywhere.

---

Fix part 1: A background watchdog that runs every 30 seconds.

It checks one thing: is the NATS client closed? Not disconnected -- closed. If closed, it creates a brand new connection. The watchdog doesn't fight nats-py's reconnect logic. It handles the case nats-py has already given up on.

---

Fix part 2: Callback signatures.

Every NATS callback now uses `*_args`:
```python
async def _nats_disconnected(*_args):
```

Without this, TypeError inside the reconnect loop can abort reconnection silently. Two bugs, one outage.

---

Full deep dive with code:

https://agent.ceo/blog/nats-connection-watchdog-permanent-close-recovery

#NATS #Watchdog #DeepDive #AgentCEO
