---
platform: linkedin
status: draft
date: 2026-11-08
note: "Your Task Endpoint Fetches Every Task on Every Poll"
---

## Post: Your Task Endpoint Fetches Every Task on Every Poll

We had a task management endpoint that worked perfectly in testing. Then we deployed it with 7 agents and a dashboard polling continuously.

The endpoint called ZRANGE 0,-1 on our Redis sorted set -- fetching the entire task index on every request. Then it ran HGETALL on every single task ID. Then it decoded all of them in Python. Then it sorted them. Then it sliced to limit=10 and returned the result.

200+ tasks decoded, sorted, and discarded to return 10. On every poll. From every agent. From every dashboard tab.

Redis can serve a bounded ZRANGE in microseconds. The sorted set was already sorted -- that's what sorted sets do. The cost wasn't Redis. The cost was us asking for everything, deserializing everything, re-sorting everything, and throwing away 95% of it.

The async event loop had no time left for anything else. KB queries timed out. Health probes failed. Super-agent work stalled. The task management system became the bottleneck that prevented all task management.

The irony: we built a task system so our agents could coordinate. The task system's own polling saturated the event loop so thoroughly that agents couldn't coordinate.

Sometimes the bottleneck isn't your database. It's the question you're asking it.

https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#Redis #Performance #AsyncIO #AgentCEO
