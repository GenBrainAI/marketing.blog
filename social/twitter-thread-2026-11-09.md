---
platform: twitter
status: draft
date: 2026-11-09
note: "Push Pagination to Your Data Store"
---

## Thread: Push Pagination to Your Data Store

The fix for our ZRANGE 0,-1 problem: fetch only offset+limit IDs from Redis instead of the entire index.

limit=10 now fetches ~10 IDs. Not 200+.

---

For post-filtered queries (exclude cancelled, filter by assignee), we add a headroom buffer. Fetch 30-60 IDs, apply the filter, return the first 10 that match. If the buffer runs dry, fetch another batch.

Still vastly fewer than "all of them."

---

Result: each poll completes in microseconds instead of milliseconds. The event loop is free again for KB queries, health probes, super-agent work.

Seven agents + dashboard polling continuously. The difference between 10 IDs and 200+ IDs per request compounds fast.

---

"Fetch everything, filter in app code" is the default because it's easiest to write. It works at low scale. It doesn't survive continuous polling.

Push pagination to the layer that already has the data sorted. That's what it's for.

https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#Redis #Pagination #Performance #AgentCEO
