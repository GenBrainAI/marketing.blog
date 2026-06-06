---
platform: twitter
status: draft
date: 2026-10-15
note: "Blog launch — How to Build a Stop-Hook Gate That Keeps Agents Working"
---

## Thread: New Blog -- Build a Stop-Hook Gate That Keeps Agents Working

New tutorial: how to build the stop-hook gate that prevents our AI agents from quitting with unfinished work.

The hook fires on session exit, checks the TMS for `assigned`, `accepted`, or `in_progress` tasks. If any exist: `{"decision": "block"}`, exit code 2. Agent stays alive.

---

The block count mechanism prevents deadlock.

A counter at `/tmp/stop_block_count` increments on each block. At 3, the hook steps aside and lets the session end. Counter resets at session start.

Why 3? If the agent can't progress after 3 blocks, it's stuck on something external. Fresh context on restart beats an infinite trap.

---

This is part of a full autonomous loop:

Session start injects task -> agent works -> stop hook blocks premature exit -> watchdog re-injects -> agent continues -> hook approves exit when queue is clear -> wrapper restarts fresh.

Each piece is small. Together they keep agents productive 24/7.

---

The post includes dry-run mode via `AUTONOMOUS_LOOP_DRY_RUN` env var. Test the gate without actually trapping your agent.

Full tutorial with code: https://agent.ceo/blog/stop-hook-gate-keep-agents-working

#StopHook #AutonomousLoop #Tutorial #AgentCEO
