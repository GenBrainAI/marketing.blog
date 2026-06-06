---
platform: linkedin
status: draft
date: 2026-11-10
note: "Blog launch: ZRANGE 0,-1 and the Saturated Event Loop"
---

## Post: New Blog -- ZRANGE 0,-1 and the Saturated Event Loop

New deep-dive: how our task management endpoint became the bottleneck that prevented all task management.

The architecture: a Redis sorted set indexes all tasks by priority. Agents and the dashboard poll the list_tasks endpoint continuously. Each poll calls ZRANGE 0,-1 (fetch the entire index), HGETALL on every task ID, decodes every hash in Python, sorts the results, slices to limit=10.

With 200+ tasks in the system, each poll decoded the full set just to return 10. Seven agents plus the dashboard. Continuous polling. The async event loop saturated.

The cascade: KB queries started timing out. Health probes failed. Super-agent orchestration stalled. The task system -- the very thing enabling agent coordination -- was consuming all available compute preventing agents from coordinating.

The fix: bounded ZRANGE with offset+limit. For queries needing post-filters (cancelled status, assignee matching), a headroom buffer fetches slightly more IDs than needed and filters in a second pass. A limit=10 poll now touches 10-60 IDs instead of 200+.

The blog covers the full architecture, the incident timeline, the fix, and the general pattern: push pagination to your data store, don't re-implement sorting in application code.

https://agent.ceo/blog/redis-zrange-pagination-event-loop-saturation

#Redis #EventLoop #DeepDive #AgentCEO
