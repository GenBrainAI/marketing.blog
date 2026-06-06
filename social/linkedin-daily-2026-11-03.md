---
platform: linkedin
status: draft
date: 2026-11-03
note: "Blog launch: NATS Connection Watchdog"
---

## Post: New Blog -- NATS Connection Watchdog: Recovering From Permanent Close

We just published a deep dive into one of our nastiest production issues: nats-py closing our gateway's NATS connection permanently despite `max_reconnect_attempts=-1`.

The root cause: an auth error during a reconnect cycle. nats-py treats auth failures as non-retryable and closes the client object for good. No more reconnect attempts. The gateway sat there with a dead connection, returning 503s.

The fix has two parts:

1. A background watchdog that checks every 30 seconds whether the NATS client is closed (not just disconnected). If closed, it creates an entirely new connection from scratch.

2. Fixed callback signatures. Every NATS callback now uses `*_args` to accept whatever arguments nats-py passes. Without this, a TypeError inside the reconnect loop can abort reconnection entirely.

The watchdog pattern is simple but effective. It doesn't fight nats-py's reconnect logic -- it sits alongside it and handles the case that nats-py's own reconnect has given up on.

If you're running NATS in production, especially with auth callouts, you probably need both of these.

Read the full technical deep dive: https://agent.ceo/blog/nats-connection-watchdog-permanent-close-recovery

#NATS #Watchdog #DeepDive #AgentCEO
