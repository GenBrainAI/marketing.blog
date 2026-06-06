---
title: "How We Made AI Agents That Won't Die Mid-Task"
slug: "autonomous-loop-stop-hook-gate-ai-agents"
date: 2026-08-11
category: technical
cluster: autonomous-operations
tags: [autonomous-loops, stop-hook, daemon, dry-run, production, agent-lifecycle]
description: "Deep dive into the stop-hook gate, prompt watchdog, and automata status reporter that keep AI agents alive and productive through their task queues."
relatedPosts:
  - /blog/how-to-build-self-pacing-autonomous-loops
  - /blog/debugging-ai-agent-relaunch-loop-production-incident
  - /blog/task-management-autonomous-ai
  - /blog/agent-lifecycle-management
  - /blog/24-7-operations-zero-overhead
---

# How We Made AI Agents That Won't Die Mid-Task

An AI agent halfway through a database migration decides its session is over. It exits. The migration is half-applied. The task sits in "in_progress" forever. Downstream agents wait for an artifact that will never arrive. The entire sprint stalls because one agent quit early.

This was our reality six months ago. Agents would drop out of their sessions at the worst possible moments -- mid-commit, mid-deploy, mid-verification. The root cause was simple: nothing in the session lifecycle knew or cared whether the agent had unfinished work. Session timeout hit, the process exited, and whatever was in flight just stopped.

We needed agents that refuse to die while they have pending tasks. Not immortal agents -- agents with a survival instinct tied to their work queue. Here is how we built it.

## The Problem: Uncoordinated Exit

Claude Code sessions have natural exit points. Context fills up, idle timeouts fire, the orchestrator decides to cycle the pod. Every one of these is a potential task-killer.

The damage compounds. A stuck task blocks its dependents. The CEO agent's sprint controller flags it as stalled. Someone has to manually investigate, restart, and often redo the work. In a system running six agents 24/7, one premature exit per day means six hours of wasted compute per week and a permanently unreliable task pipeline.

We needed a mechanism that was aware of the agent's task state at the moment of exit, and could intervene.

## The Architecture: A Three-Component Control Loop

The solution is three components that form a closed loop: one that pushes work in, one that prevents premature exit, and one that lets operators see what is happening.

### Component 1: The Stop-Hook Gate

`autonomous_stop.py` is a Claude Code stop hook. Every time a session attempts to exit, Claude Code calls registered stop hooks before actually terminating. Ours does one thing: checks whether the agent has unfinished tasks.

The core function, `_should_block_for_pending_work()`, scans the TMS task registry for any tasks assigned to this agent's `ROLE_ID` with an active status -- `in_progress`, `accepted`, or `assigned`. If it finds any, it returns `{"decision": "block"}` with exit code 2. The session stays alive.

But we do not block forever. A counter file at `/tmp/stop_block_count` tracks how many times the hook has blocked in the current session. After three blocks (`MAX_STOP_BLOCKS = 3`), the hook steps aside and allows exit. Why three? Because if an agent has been blocked three times and still has not completed its tasks, something is structurally wrong -- a bug, a dependency deadlock, an unreachable service. Holding the session open longer will not fix it. Better to let the session die, let the wrapper restart it with a clean slate, and let the agent pick up the task fresh.

This is a deliberate design choice: the gate is a nudge, not a prison. Three chances to finish your work. After that, the system assumes the problem is not "not enough time" but "something else is broken."

The hook also respects `AUTONOMOUS_LOOP_DRY_RUN` -- when set, it logs what it would do without actually blocking. Essential for testing in staging without accidentally trapping sessions.

### Component 2: The Prompt Watchdog

Preventing exit is only half the problem. An agent that stays alive but sits idle is just as wasteful. `prompt_watchdog.py` runs as a background daemon and handles the other half: making sure the agent actually works on its pending tasks.

The watchdog monitors the agent's session for idle periods. When it detects the agent is between tasks or has gone quiet, it injects a standing mandate message. For the CEO agent, this is `/ceo-operating-loop` -- a full operating cycle. For other agents, it is a targeted "check your inbox" prompt with the agent's role-specific mandate appended.

The injection is the critical piece. Without it, an agent whose session was just saved by the stop hook might simply do nothing. The watchdog closes that gap. Session stays alive (stop hook), agent gets nudged to work (watchdog), tasks get completed.

Like the stop hook, the watchdog supports dry-run mode. In production, you want injection. In staging, you want logs showing what would have been injected, without actually disrupting test sessions.

### Component 3: The Automata Status Reporter

`automata_status.py` is the observability layer -- 204 lines that answer the question "is the autonomous loop actually working right now?"

It reports on five dimensions:

**Daemon health.** Checks `/proc` for running instances of `prompt_watchdog`, `agent_wakeup`, and `scheduled_loops`. If any daemon is dead, you know immediately.

**Loop configuration.** Current mode, strategy type, whether injection is disabled. Tells you what the loop should be doing.

**Pending tasks.** Lists active TMS tasks for this agent, so you can see exactly what work is keeping the session alive.

**Stop-block count.** How many of the three blocks have been used this session. If you see 2/3, the agent is running out of runway.

**Recent logs.** Tails the last entries from watchdog, wakeup, and scheduled loop logs. When something goes wrong, the diagnosis starts here.

The reporter supports both human-readable output and `--json` for programmatic consumption. Our monitoring stack polls the JSON endpoint; operators use the human-readable version when debugging.

It also detects two special states: the presence of a `PAUSE` file (manual operator override to halt the loop) and the dry-run flag. Both are situations where the loop is intentionally not running, and the reporter distinguishes them from actual failures.

## The Session Lifecycle

The components do not exist in isolation. The session wrapper, `claude_wrapper.sh`, orchestrates the lifecycle:

1. **Session start:** Wrapper resets `/tmp/stop_block_count` to 0. Fresh session, fresh block budget.
2. **During session:** Watchdog injects work. Agent processes tasks. Stop hook guards exit.
3. **Session exit:** If tasks remain and blocks are under 3, hook blocks exit. Agent continues. If blocks hit 3, hook allows exit.
4. **Post-exit:** Wrapper restarts the session. Counter resets. Agent picks up where it left off.

Two other components support this cycle. `agent_wakeup.py` handles post-compaction recovery -- when the context window compresses, the agent needs a kick to resume work rather than sleeping. `scheduled_loops.sh` was previously guarded by an `exit 0` at the top of the script, effectively disabling periodic work. Removing that guard was a one-line fix with outsized impact.

## Testing the Untestable

Autonomous loops are notoriously hard to test. The behavior you care about -- "agent does not die when it should not" -- involves process lifecycle, file I/O, and timing. We wrote 20 tests covering:

- The blocking gate with 0, 1, 2, and 3 prior blocks
- Dry-run mode (no blocking, only logging)
- Task scanning across multiple registry files
- Status reporter output in both formats
- Watchdog mandate injection for different agent roles
- Counter reset on session start
- Edge cases: empty task registries, corrupted counter files, missing role IDs

The tests use filesystem mocking and process simulation. No actual Claude Code sessions needed. The test suite runs in under two seconds and catches regressions before they reach production.

## Results

Since deploying the autonomous loop finalization, premature task abandonment has dropped to near zero. Agents complete their assigned work before cycling. The sprint controller no longer flags phantom "stuck" tasks that were actually just abandoned by a dead session.

The design principle is worth stating explicitly: the three components form a closed control loop. The watchdog **injects** work. The stop hook **blocks** premature exit. The status reporter **observes** the loop's health. The wrapper **resets** state between sessions. No single component solves the problem. Together, they make agents that finish what they start.

---

We are building an organization where AI agents run autonomously, manage their own task queues, and never silently drop work. Visit [agent.ceo](https://agent.ceo) to see the system in action.
