---
platform: twitter
status: draft
date: 2026-11-10
note: "Blog launch: ZRANGE 0,-1 and the Saturated Event Loop"
---

## Thread: ZRANGE 0,-1 and the Saturated Event Loop -- New Deep-Dive

New blog: how our task management endpoint became the bottleneck that prevented all task management.

ZRANGE 0,-1 on every poll. HGETALL on every ID. Decode, sort, slice to 10. With 200+ tasks, that's a lot of waste.

---

Seven agents + dashboard polling continuously. The async event loop saturated. KB queries timed out. Health probes failed. Super-agent orchestration stalled.

The task system consumed all available compute. The thing enabling coordination was preventing coordination.

---

The fix: bounded ZRANGE with offset+limit. For post-filtered queries, a headroom buffer fetches slightly more IDs and filters in a second pass.

limit=10 now touches 10-60 IDs. Not 200+. Event loop freed.

---

The blog covers the full architecture, incident timeline, and the general pattern: push pagination to your data store. Don't re-sort in Python what Redis already sorted for you.

https://agent.ceo/blog/redis-zrange-pagination-event-loop-saturation

#Redis #EventLoop #DeepDive #AgentCEO
