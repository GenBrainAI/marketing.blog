---
platform: twitter
status: draft
date: 2026-11-08
note: "Your Task Endpoint Fetches Every Task on Every Poll"
---

## Thread: Your Task Endpoint Fetches Every Task on Every Poll

Our task endpoint did ZRANGE 0,-1 on every request. That fetches the ENTIRE sorted set from Redis. Then HGETALL on every ID. Decode in Python. Sort. Slice to limit=10. Return.

200+ tasks decoded to return 10. On every poll. From 7 agents + dashboard.

---

Redis serves a bounded ZRANGE in microseconds. The sorted set was already sorted. We were paying zero cost at the data layer and enormous cost asking for everything, deserializing everything, re-sorting it in Python, and throwing away 95%.

---

The async event loop had no time left. KB queries timed out. Health probes failed. Super-agent work stalled.

The task management system became the bottleneck that prevented all task management. Peak irony.

---

Sometimes the bottleneck isn't your database. It's the question you're asking it.

The data store already had the answer. We just kept asking for everything instead.

https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#Redis #Performance #AsyncIO #AgentCEO
