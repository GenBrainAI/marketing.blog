---
title: "Tutorial: How to Build a Stop-Hook Gate That Keeps Agents Working"
slug: "stop-hook-gate-keep-agents-working"
date: 2026-10-15
category: technical
cluster: tutorials
tags: [stop-hook, autonomous-loop, task-management, session-lifecycle, tutorial]
description: "A practical tutorial on building a stop hook that prevents AI agents from exiting their session when they still have assigned work — closing the gap between task completion and task pickup."
relatedPosts:
  - /blog/ralph-loop-one-task-per-session-anti-drift
  - /blog/prompt-watchdog-daemon-keeps-agents-working
  - /blog/outer-loop-shell-script-keeps-agents-alive
  - /blog/policy-gate-compulsive-agent-discipline
  - /blog/level-triggered-edge-triggered-agent-pending-work
---

# Tutorial: How to Build a Stop-Hook Gate That Keeps Agents Working

Your agent finishes a task. It calls `complete_task_unverified()`, writes a tidy progress note, and decides there is nothing left to do. The Claude Code session exits with code 0 — a clean, successful exit. The wrapper script sees the clean exit and parks the agent, waiting for an external wakeup signal.

Meanwhile, the TMS has two more tasks assigned to this agent. Status: "assigned." The prompt watchdog could inject them — but the session is already gone. There is nothing to inject into. The agent sits idle with work in its queue until something externally restarts it.

This is the gap: between "agent decides to exit" and "watchdog could inject work," there is a hook opportunity. A stop hook that checks for pending tasks and says "no, don't exit yet — you have work." We shipped this in commit `eb056af45`, and it closed the single biggest source of idle time in our fleet. This tutorial walks through the exact implementation.

## The Hook Interface

The stop-hook gate runs as a Stop hook in Claude Code. It fires when the agent tries to end its session — after the agent's last message, before the process terminates. The hook receives session context via stdin as JSON and must produce one of two outputs:

**Allow exit:**
```json
{"decision": "approve"}
```
Exit code 0. The session ends normally.

**Block exit:**
```json
{"decision": "block", "reason": "You have 2 tasks in status 'assigned'. Check your inbox."}
```
Exit code 2. The session stays alive. The agent receives the block reason and can continue working.

That is the entire interface. One JSON object in, one JSON object out, and an exit code that determines whether the session lives or dies.

## The Core Decision: `_should_block_for_pending_work()`

The gate logic lives in a single function that returns a tuple: `(should_block: bool, reason: str)`. It checks three conditions in order, and the order matters.

### Check 1: Dry-Run Mode

```python
if os.environ.get("AUTONOMOUS_LOOP_DRY_RUN", "").lower() in ("true", "1"):
    return (False, "dry-run mode — exit approved")
```

When you are testing the autonomous loop, you do not want the stop hook trapping your agent in a session you cannot control. The `AUTONOMOUS_LOOP_DRY_RUN` environment variable disables blocking entirely. Set it during development, unset it in production.

### Check 2: Block Count Limit

```python
MAX_STOP_BLOCKS = 3
STOP_BLOCK_COUNT_FILE = Path("/tmp/stop_block_count")

current_count = int(STOP_BLOCK_COUNT_FILE.read_text().strip()) if STOP_BLOCK_COUNT_FILE.exists() else 0
if current_count >= MAX_STOP_BLOCKS:
    return (False, f"block count {current_count} >= {MAX_STOP_BLOCKS} — allowing exit")
```

This is the deadlock breaker. If the agent has already been blocked three times this session and still wants to exit, something is wrong. The tasks might be blocked by an external dependency. The agent might not have the tools or permissions to make progress. Trapping it forever would be worse than letting it restart.

The counter lives in `/tmp/stop_block_count` — ephemeral storage that survives within a session but clears on pod restart. The wrapper script (`claude_wrapper.sh`) resets this counter to 0 at the start of each new session, so every session gets a fresh set of three chances.

### Check 3: Active TMS Tasks

```python
active_statuses = {"in_progress", "accepted", "assigned"}
pending = [t for t in task_registry if t["assignee"] == ROLE_ID and t["status"] in active_statuses]

if pending:
    # Increment block count
    new_count = current_count + 1
    STOP_BLOCK_COUNT_FILE.write_text(str(new_count))
    return (True, f"{len(pending)} task(s) still active: {', '.join(t['task_id'] for t in pending)}")

return (False, "no pending tasks — exit approved")
```

This is the real check. Scan the task registry for tasks where the assignee matches this agent's role ID and the status is one of `in_progress`, `accepted`, or `assigned`. If any exist, block the exit and increment the counter.

The agent receives the block reason — including which tasks are pending — and can act on it. The prompt watchdog detects the agent is idle and re-injects a "check your tasks" prompt. The agent picks up the next task, works on it, and the cycle continues.

## The Main Flow

Putting it together, the `main()` function reads stdin, makes the decision, and outputs the result:

```python
def main():
    input_data = json.loads(sys.stdin.read())

    # Check for pending work
    should_block, block_reason = _should_block_for_pending_work()

    if should_block:
        print(f"[stop] BLOCKING exit — {block_reason}", file=sys.stderr)
        log_stop_event(input_data, "block", block_reason)
        print(json.dumps({"decision": "block", "reason": block_reason}))
        sys.stdout.flush()
        sys.exit(2)

    # No pending work — approve exit
    log_stop_event(input_data, "approve", "instant-approve")
    print(json.dumps({"decision": "approve"}))
    sys.stdout.flush()
```

Stderr gets the human-readable log line. Stdout gets the machine-readable JSON. The exit code tells Claude Code what to do. Clean separation.

## The Block Sequence in Practice

Here is what a typical session looks like with the stop-hook gate active:

1. **Session starts.** The wrapper resets `/tmp/stop_block_count` to 0. The session start hook injects the current task.
2. **Agent works.** Completes the task, calls `complete_task_unverified()`.
3. **Agent tries to exit.** Stop hook fires. Checks TMS — two more tasks assigned. Block count is 0, under the limit. Returns `{"decision": "block", "reason": "2 task(s) still active"}`. Exit code 2. Session stays alive.
4. **Watchdog injects.** The prompt watchdog detects the agent is between tasks and sends "check your tasks." The agent calls `get_agent_inbox()`, picks up the next task.
5. **Agent works again.** Completes the second task.
6. **Agent tries to exit again.** Stop hook fires. One more task. Block count is 1. Blocked again.
7. **Cycle repeats.** Agent picks up the third task, completes it.
8. **Agent tries to exit.** Stop hook fires. No pending tasks. Returns `{"decision": "approve"}`. Session exits cleanly.

And the escape hatch path:

1. **Agent is blocked** but cannot make progress — maybe the task depends on a service that is down.
2. **Block count increments:** 1, 2, 3.
3. **Fourth exit attempt:** block count (3) equals `MAX_STOP_BLOCKS` (3). Exit approved.
4. **Wrapper restarts** the agent with fresh context. The TMS tasks are still there, but now the agent gets a clean context window and a fresh perspective. Often, the dependency has resolved by the time the new session starts.

## Why MAX_STOP_BLOCKS = 3

Three is the sweet spot between too permissive and too persistent. One block would barely matter — the agent exits after a single retry. Five or more and you risk the agent burning tokens on tasks it genuinely cannot complete, spinning through the same "I cannot reach the database" → "check your tasks" → "I still cannot reach the database" loop.

Three blocks means the agent gets three chances to pick up remaining work. If it cannot make progress after three attempts, the task is likely blocked by something outside its control. Letting the session exit and restart with fresh context is better than trapping the agent in a loop where every iteration costs money and produces nothing.

## The Larger Autonomous Loop

The stop-hook gate does not work alone. It is one component of a loop that keeps agents productive across session boundaries:

1. **Session start hook** injects the current task via the [Ralph Loop](/blog/ralph-loop-one-task-per-session-anti-drift) plus any standing mandates.
2. **Agent works** on the injected task.
3. **Stop hook** checks for pending work when the agent tries to exit — the gate you just built.
4. **[Prompt watchdog](/blog/prompt-watchdog-daemon-keeps-agents-working)** re-injects work prompts when the agent is idle but the session is still alive.
5. **[Outer loop wrapper](/blog/outer-loop-shell-script-keeps-agents-alive)** handles restart after an approved exit — fresh context, fresh block counter, next task from the queue.

The supporting infrastructure from the same commit (`eb056af45`) includes:

- **`agent_wakeup.py`** — post-compaction wakeup that re-injects the work prompt after context compression
- **`scheduled_loops.sh`** — periodic work cycles that run on a timer
- **`automata_status.py`** — a status reporter that checks daemon health, loop config, pending tasks, and recent activity for diagnostics

Together, these components close every gap where an agent could go idle with work available. The stop hook closes the most critical one: the gap between "agent decides to stop" and "system can inject more work."

## Wiring the Hook

To register the stop hook with Claude Code, add it to your settings:

```json
{
  "hooks": {
    "Stop": [
      {
        "type": "command",
        "command": "python3 /path/to/stop_hook.py"
      }
    ]
  }
}
```

And in your wrapper script, reset the block counter at session start:

```bash
echo "0" > /tmp/stop_block_count
```

That is it. One Python script, one counter file, one hook registration. Twenty tests cover the blocking gate, dry-run mode, mandates, and status output — write yours to match.

## The Result

Before the stop-hook gate, our agents averaged 1.2 tasks per session. They would complete their assigned work, exit, and wait for an external restart. With the gate, agents average 2.8 tasks per session. The idle gap between "task done" and "next task started" dropped from minutes (waiting for wrapper restart, session boot, context injection) to seconds (watchdog re-injection into the same live session).

The block count mechanism means we never trap an agent. The dry-run mode means we can test the loop safely. The counter reset means every session starts fresh. And the whole thing is fifty lines of Python.

---

We build this infrastructure at [agent.ceo](https://agent.ceo) — the platform for running autonomous AI agent organizations. The stop-hook gate, the prompt watchdog, the Ralph Loop, the outer wrapper — they are all part of a system designed to keep agents productive without human babysitting. If you are building autonomous agents that need to stay alive and working, check out what we are shipping.
