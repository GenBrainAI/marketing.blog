---
platform: linkedin
status: draft
date: 2026-11-09
note: "Push Pagination to Your Data Store"
---

## Post: Push Pagination to Your Data Store

Yesterday I posted about our ZRANGE 0,-1 problem -- fetching the entire task index on every poll. Here's the fix.

Instead of fetching all IDs and filtering in Python, we now fetch only offset+limit IDs directly from Redis. A limit=10 request fetches ~10 IDs from the sorted set. Not 200+.

For queries that need post-filtering (exclude cancelled tasks, filter by assignee), we add a small headroom buffer. Fetch 30-60 IDs instead of 10, apply the filter, return the first 10 that match. If the buffer runs dry, fetch another batch. Still vastly fewer than "all of them."

The result: a limit=10 poll now fetches 10-60 IDs instead of 200+. Each request completes in microseconds instead of milliseconds. The event loop is free again for KB queries, health probes, and super-agent work.

The lesson is simple but easy to forget: "fetch everything, filter in app code" is the default because it's the easiest thing to write. It works fine at low scale. It doesn't survive continuous polling from multiple consumers.

Push filtering to the layer that already has the data indexed. Push pagination to the layer that already has the data sorted. Your application code should handle business logic, not re-implementing what your data store already does natively.

https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#Redis #Pagination #Performance #AgentCEO
