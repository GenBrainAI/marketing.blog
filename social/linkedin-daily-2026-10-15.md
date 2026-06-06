---
platform: linkedin
status: draft
date: 2026-10-15
note: "Blog launch — How to Build a Stop-Hook Gate That Keeps Agents Working"
---

## Post: New Blog -- How to Build a Stop-Hook Gate That Keeps Agents Working

We just published the full tutorial on building the stop-hook gate that keeps our AI agents from quitting early.

The core mechanic: when an agent session tries to exit, a hook fires and checks the TMS for active tasks -- anything in `assigned`, `accepted`, or `in_progress` status. If tasks exist, the hook returns `{"decision": "block", "reason": "..."}` with exit code 2. The agent stays alive. The prompt watchdog re-injects the next task. Work continues.

The block count mechanism prevents deadlock. A counter at `/tmp/stop_block_count` increments each time the hook blocks an exit. At 3, the hook stops blocking and lets the session end. The counter resets at session start. This handles the case where an agent genuinely can't progress -- a missing secret, a crashed dependency, a task that needs human input. Three attempts is enough signal.

This is one piece of a larger autonomous loop:

1. Session start injects the next task from TMS
2. Agent works on the task
3. Stop hook prevents premature exit (up to 3 times)
4. Watchdog re-injects work after each block
5. Agent continues through its queue
6. Eventually the hook approves exit (no tasks or 3 blocks hit)
7. Wrapper restarts with fresh context

The post includes a dry-run mode via the `AUTONOMOUS_LOOP_DRY_RUN` env var so you can test without trapping your agent.

Read the full tutorial: https://agent.ceo/blog/stop-hook-gate-keep-agents-working

#StopHook #AutonomousLoop #Tutorial #AgentCEO
