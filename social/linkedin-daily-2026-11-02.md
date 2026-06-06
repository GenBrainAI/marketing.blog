---
platform: linkedin
status: draft
date: 2026-11-02
note: "Your Callback Signatures Are Breaking Your Reconnect Loop"
---

## Post: Your Callback Signatures Are Breaking Your Reconnect Loop

A one-character bug took down our NATS reconnect loop. Not a typo in a config file. A missing `*_args` in a callback signature.

nats-py passes arguments to its callbacks -- `disconnected_cb`, `reconnected_cb`, `error_cb`. If your callback doesn't accept those arguments, Python raises a TypeError. That TypeError happens inside nats-py's reconnect loop. And it can abort the entire loop.

So your "reconnect handler" that logs a warning? It just killed your reconnection.

The fix is almost embarrassingly simple:

```python
async def _nats_disconnected(*_args):
    logger.warning("NATS disconnected")
```

That `*_args` accepts whatever nats-py throws at it -- one argument, three arguments, none. Your callback does its job, and the reconnect loop keeps running.

We found this because our gateway would sometimes reconnect perfectly and sometimes die permanently on the same failure mode. The difference was which callback nats-py invoked during that particular reconnect attempt.

If you're using nats-py in production, audit every callback signature right now. A TypeError in a reconnect handler is silent, fatal, and completely avoidable.

Full writeup: https://agent.ceo/blog/self-healing-connections-resilient-ai-agent-infrastructure

#NATS #Python #AsyncIO #AgentCEO
