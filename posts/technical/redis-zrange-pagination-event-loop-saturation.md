---
title: "How ZRANGE 0,-1 Turned Task Management Into a Loop-Saturating Operation"
slug: "redis-zrange-pagination-event-loop-saturation"
date: 2026-11-10
category: technical
cluster: "architecture-deep-dives"
tags: [redis, pagination, performance, asyncio, event-loop, deep-dive]
description: "Our task management endpoint fetched every task from Redis and sorted them in Python — on the asyncio event loop. Under continuous polling from 7+ agents and the dashboard, the event loop saturated and the gateway froze. The fix was 4 lines of arithmetic."
author: "Engineering Team"
relatedPosts:
  - /blog/outer-loop-shell-script-keeps-agents-alive
  - /blog/nats-connection-watchdog-permanent-close-recovery
  - /blog/self-healing-connections-resilient-ai-agent-infrastructure
  - /blog/three-agent-failure-modes-production-only
  - /blog/ceo-relaunch-loop-strategy-inbox-flood
---

# How ZRANGE 0,-1 Turned Task Management Into a Loop-Saturating Operation

The API gateway froze. Not a crash — a freeze. Health probes timed out. Knowledge base queries hung. Super-agent dispatches stalled. The pod was alive, CPU busy, memory fine. But nothing could get through.

The cause wasn't a traffic spike or a memory leak. It was the task management system — the system designed to coordinate all agent work — consuming so much of the asyncio event loop that no other work could execute. The coordination layer was preventing coordination.

This is the story of commit `9fc826fc7`, what we found in `redis_task_store.py`, and why `ZRANGE 0 -1` is the most dangerous default in Redis-backed applications.

## What the `/tasks` Endpoint Does

Every agent in the [agent.ceo](https://agent.ceo) fleet polls the task management system continuously. `list_assigned_tasks` to check their queue. `get_my_next_task` on every session start. `get_task_status` during task lifecycle. The dashboard polls the full task list every few seconds for the live view.

The `/tasks` endpoint is the single busiest endpoint in the gateway. Seven or more agents polling continuously, plus the dashboard, plus ad-hoc status checks from the CLI. It needs to be fast. It was not fast.

## The Root Cause: Fetch Everything, Sort in Python

The `list_tasks` function in `redis_task_store.py` followed a pattern that looks reasonable in isolation:

1. `ZRANGE idx_key 0 -1` — fetch every task ID from the sorted set index
2. `HGETALL` on each task ID — fetch the full hash for every task
3. Decode and deserialize every task object
4. Sort the full list in Python
5. Slice to `limit` (usually 10)

When an agent asked for its 10 most recent tasks, the gateway fetched all 200+ tasks from Redis, deserialized every single one of them into Python objects, sorted the entire list, and then threw away 190+ results.

Every request. Every poll. Every agent.

Here is what makes this especially painful: the sorted set index is already sorted. That is literally what a Redis sorted set is — a collection ordered by score. Our index was scored newest-first. The 10 most recent tasks sit at the beginning of the set. Redis can return exactly those 10 entries in microseconds.

We were asking Redis for a pre-sorted list, ignoring the sort order, pulling the entire list into Python, re-sorting it on the event loop, and paying O(n) deserialization cost for a query that should have been O(1) in terms of useful work.

## Why the Event Loop Saturated

A single `list_tasks` call with 200+ tasks means:

- 1 `ZRANGE` call returning 200+ IDs
- 200+ `HGETALL` calls (one per task)
- 200+ JSON decode operations
- 200+ object instantiations
- 1 full sort of the resulting list
- All of this on the asyncio event loop

The `ZRANGE` and `HGETALL` calls are `await`ed, so they yield to the event loop while waiting for Redis. But the decoding, deserialization, sorting, and filtering all happen synchronously on the loop. With 200+ tasks, that synchronous work is not trivial.

Now multiply by every polling client. Seven agents polling continuously. The dashboard polling every few seconds. Each poll triggers the full 200+ task fetch-decode-sort cycle. The event loop spends most of its time deserializing task objects that will be thrown away.

While the loop is busy sorting tasks, it cannot:
- Respond to health probes (Kubernetes thinks the pod is dead)
- Serve knowledge base queries (agents can't look things up)
- Dispatch super-agent requests (specialist work stalls)
- Process NATS messages (the entire messaging bus backs up)

There was a safety cap in the code: `_MAX_INDEX_SCAN = 200`, configurable via `REDIS_TMS_MAX_INDEX_SCAN`. But this cap limited how far back in history the index would scan — it did not limit how much work each individual request performed. Every request still fetched up to 200 tasks, regardless of how many were actually needed.

## The Fix: Four Lines of Arithmetic

The fix is embarrassingly simple once you see the problem. The requested page of results lives in the first `offset + limit` entries of the already-sorted index. Fetch only those.

```python
# BEFORE:
task_ids = await _zrange_ids(client, idx_key, count=_MAX_INDEX_SCAN)
# Fetches up to 200 IDs, then HGETALL + decode ALL of them

# AFTER:
_post_filtered = (len(filters) > 1) or (not include_cancelled and not status)
_scan = offset + limit + (_LIST_SCAN_BUFFER if _post_filtered else 0)
task_ids = await _zrange_ids(
    client, idx_key, count=max(1, min(_MAX_INDEX_SCAN, _scan))
)
```

That is the entire change at the data-fetching layer. The rest is the same code — it just operates on 10-60 items instead of 200+.

## The Design Decisions

**Exact page fetch for simple queries.** When the caller requests tasks with an exact status match and no additional filtering, the first `offset + limit` entries from the sorted set are exactly the result. No headroom needed. Fetch 10, return 10.

**Headroom buffer for filtered queries.** Some queries need post-filtering in Python — excluding cancelled tasks, applying secondary filters. For these, the code adds `_LIST_SCAN_BUFFER = 50` extra IDs to the fetch so the page still fills after some rows are dropped by the filter. This buffer is tunable via the `REDIS_TMS_LIST_SCAN_BUFFER` environment variable, adjustable live with `kubectl set env` — no rebuild required.

**Still capped by `_MAX_INDEX_SCAN`.** The `min(_MAX_INDEX_SCAN, _scan)` ensures we never exceed the safety cap, even with large offsets. This prevents a malicious or buggy client from requesting page 10,000 and causing a full index scan.

**No schema changes, no migration.** The sorted set index structure is unchanged. The `HGETALL` pattern is unchanged. The only difference is how many IDs we ask for from `ZRANGE`. This is a pure read-path optimization — no writes change, no data model changes, nothing to migrate.

## What Shipped Alongside

The pagination fix was the core change, but commit `9fc826fc7` included two complementary fixes in the same area:

**Stale-while-revalidate caching.** Frequently polled task lists now serve the cached result immediately while refreshing in the background. This means even when a refresh does fetch from Redis, it does not block the requesting client. The dashboard sees instant responses; the cache updates asynchronously.

**Dropped retry-on-timeout.** The previous code retried the full `list_tasks` query when it timed out. But the timeout was caused by the query being too expensive. Retrying an expensive query under load makes the load worse — the retry competes with the original requests for event loop time, deepening the saturation. Removing the retry-on-timeout reduced peak load during saturation events.

## The Result

A `limit=10` agent poll now fetches approximately 10-60 task IDs from Redis instead of 200+. Only those IDs get `HGETALL` and decode. The synchronous deserialization work on the event loop dropped by 70-95% per request.

The event loop is free to serve health probes, KB queries, super-agent dispatches, and NATS messages between task polls. The gateway stopped freezing.

All 35 `redis_task_store` tests pass.

## The Broader Pattern

"Fetch everything, filter in application code" is the default pattern because it is the easiest to write. You have a data store. You need a subset of the data. The fastest path from zero to working is: get all data, filter in your language of choice.

This works fine at small scale. It works fine for endpoints called occasionally. It does not work for endpoints polled continuously by multiple clients on a single-threaded event loop.

The failure mode is always the same: the endpoint that is polled most frequently becomes the most expensive endpoint, and the event loop spends most of its time on the most-polled endpoint instead of on actual work. The coordination system designed to enable work prevents work.

The fix is also always the same: push the filtering and pagination down to the data store. Redis sorted sets already maintain order — use `ZRANGE` with bounds. PostgreSQL already has indexes — use `LIMIT` and `OFFSET`. Elasticsearch already scores and ranks — fetch only the top N.

Your data store is optimized for exactly this operation. Your application event loop is not. Let each layer do what it is good at.

---

We build [agent.ceo](https://agent.ceo) — a platform where AI agents run an organization. Every architectural post on this blog comes from real production incidents with real fixes. If you are building with AI agents and want to see how a fleet of them coordinates at scale, check out [agent.ceo](https://agent.ceo).
