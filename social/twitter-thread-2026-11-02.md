---
platform: twitter
status: draft
date: 2026-11-02
note: "Your Callback Signatures Are Breaking Your Reconnect Loop"
---

## Thread: Your Callback Signatures Are Breaking Your Reconnect Loop

A missing `*_args` in a Python function signature killed our NATS reconnect loop.

Not a config error. Not a network issue. A TypeError.

---

nats-py passes arguments to its callbacks: `disconnected_cb`, `reconnected_cb`, `error_cb`.

If your callback doesn't accept those arguments, Python raises TypeError. That TypeError happens inside nats-py's reconnect loop. It can abort the entire reconnection.

Your reconnect handler just killed your reconnection.

---

The fix:

```python
async def _nats_disconnected(*_args):
    logger.warning("NATS disconnected")
```

That `*_args` accepts whatever nats-py passes -- one arg, three args, none. Your callback runs, the reconnect loop continues.

---

We found this because our gateway would sometimes reconnect perfectly and sometimes die on the same failure. The difference was which callback nats-py called during that specific reconnect attempt.

If you use nats-py in production, audit every callback signature now.

---

Full writeup on NATS reconnect edge cases:

https://agent.ceo/blog/self-healing-connections-resilient-ai-agent-infrastructure

#NATS #Python #AsyncIO #AgentCEO
