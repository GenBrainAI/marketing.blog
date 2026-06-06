---
title: "How Two Bugs Made Our CEO Agent Relaunch Every 2 Seconds"
slug: "ceo-relaunch-loop-strategy-inbox-flood"
date: 2026-10-10
category: marketing
cluster: case-studies
tags: [production-incident, loop-strategy, inbox-flood, validation, defense-in-depth, case-study]
description: "An invalid strategy type and a flood of non-actionable inbox messages combined to trap our CEO agent in a 2-second relaunch loop. The entire autonomous organization was headless. Here's how two independently survivable bugs created a catastrophic failure."
relatedPosts:
  - /blog/human-gate-timeout-agent-fleet-idle-incident
  - /blog/outer-loop-shell-script-keeps-agents-alive
  - /blog/ralph-loop-one-task-per-session-anti-drift
  - /blog/detect-break-agent-retry-loops-production
  - /blog/three-agent-failure-modes-production-only
---

# How Two Bugs Made Our CEO Agent Relaunch Every 2 Seconds

The CEO agent is the top of our autonomous agent hierarchy. It reads the inbox, assigns tasks to every other agent, handles escalations, runs sprint reviews, approves deploys. When the CEO agent is down, the entire organization is headless. Nobody gets new work. Nobody gets unblocked. Every agent sits idle waiting for instructions that never come.

That's exactly what happened. The CEO agent was relaunching a fresh headless `claude -p` session every two seconds. It never settled into an operable session. It couldn't read its inbox, couldn't assign tasks, couldn't respond to other agents. And the root cause wasn't one bug -- it was two, compounding in a way that neither would have caused alone.

## The Architecture: Loop Strategies and Wakeup Signals

Every agent in our fleet has a wrapper script that manages its lifecycle. When a session ends, the wrapper consults `loop_control.json` to decide what to do next. Two fields matter here:

**Loop strategies** control the wait behavior between sessions: `continuous` (relaunch immediately), `interval-poll` (fixed interval), `backoff` (exponential), `task-driven` (wake on task), `scheduled`, `event-driven`.

**Loop modes** control who drives the loop: `self-heartbeat`, `conductor-driven`, `paused`.

These are two separate axes. Strategies answer "how long do we wait?" Modes answer "who decides when to go?"

The wrapper's `strategy_wait()` function uses a bash `case` statement to match the strategy type and determine the wait duration. If it doesn't recognize the strategy, it hits the default case. That default case is where the first bug lived.

## Bug 1: The Amplifier -- Invalid loop_strategy.type

Someone set the CEO agent's `loop_strategy.type` to `"self-heartbeat"`. But `self-heartbeat` is a loop MODE, not a loop STRATEGY. Wrong axis entirely.

How did an invalid value get written? We had two code paths that write to `loop_control.json`. The `set_loop_strategy` MCP tool -- the primary path -- validated the type against a known list. But there was a second path: a NATS message handler called `_handle_loop_strategy_message`. This handler checked that the `type` field existed but never checked that it was a valid strategy. So `"self-heartbeat"` sailed through validation and got written directly into the config.

Here's what the wrapper did with it:

```bash
case "$strategy" in
    continuous) ... ;;
    interval-poll) ... ;;
    task-driven) ... ;;
    backoff) ... ;;
    *) sleep 2 ;;
esac
```

`"self-heartbeat"` matched nothing. It fell to the `*)` default case. And the default case slept for 2 seconds, then relaunched.

Two seconds. That's all the wrapper waited before spinning up a brand new session. The agent would start, barely initialize, exit, wait 2 seconds, and start again. A tight relaunch loop.

On its own, this would have been bad but survivable. Two seconds is short, but the agent would still get some runtime per launch. Maybe it could read its inbox, process one task, do something useful before the session ended and the 2-second timer kicked in. The second bug made sure even that small window was wasted.

## Bug 2: The Driver -- Non-Actionable Inbox Flood

Our sprint-controller agent posts standup reports and escalation reminders to the CEO's inbox every cycle. These are informational messages -- not actionable work. The CEO should see them but doesn't need to wake up for them.

But the inbox watcher wrote `/tmp/wakeup_signal` unconditionally for every incoming message. It wrote the signal BEFORE checking whether the message was actually actionable. The wakeup signal is what tells the wrapper "wake up, there's work to do."

So every controller standup message triggered a wakeup signal. Every escalation reminder triggered a wakeup signal. A flood of informational messages was constantly telling the wrapper to wake up and relaunch.

## The Compound Failure

Here's the death spiral, step by step:

1. Sprint controller posts a standup report to CEO inbox
2. Inbox watcher writes `/tmp/wakeup_signal` (no filter)
3. Wrapper sees wakeup signal, launches a new session
4. Session starts, barely initializes, exits
5. Wrapper checks `loop_strategy.type` -- finds `"self-heartbeat"`
6. `"self-heartbeat"` doesn't match any known strategy
7. Default case: `sleep 2`
8. Another controller message arrives, writes wakeup signal
9. Wakeup signal fires, resets the 2-second timer
10. Wrapper relaunches immediately
11. Go to step 3

The CEO agent was trapped in a loop. Fresh session every two seconds. Never enough time to read the inbox, never enough time to assign a single task, never enough time to do anything. The entire organization was headless -- every other agent sat idle, waiting for work assignments that would never come.

Two bugs. Each one survivable alone. Together, catastrophic.

## The Fix: Three Layers Deep

The fix landed in commit `097f81e87` and addressed all three failure surfaces.

### Part 1: Close the Validation Bypass

We added a `_VALID_LOOP_STRATEGY_TYPES` frozenset containing all legitimate strategies: `{continuous, task-driven, interval-poll, backoff, scheduled, event-driven}`. And a separate `_LOOP_MODE_VALUES` set: `{self-heartbeat, conductor-driven, paused}`.

The NATS message handler now validates incoming strategy types against the real list. If someone sends a value that's actually a loop MODE, the handler re-routes it to the `loop_mode` field and keeps the existing strategy intact. If it's completely unknown, the handler rejects it, logs an error, and leaves the current strategy untouched.

No more sneaking invalid values in through the side door.

### Part 2: Normalize Wedged Configs in the Wrapper

Validation at the input layer is necessary but not sufficient. What about configs that were already wedged before the fix? The CEO's `loop_control.json` already had `"self-heartbeat"` written to it.

The wrapper's `get_loop_strategy()` function now normalizes on read. If the type is a known loop MODE value, it coerces to `"interval-poll"` (the closest real strategy). If it's completely unknown, it coerces to `"continuous"`. Pre-existing bad data gets corrected at the point of use.

And the critical change: the `*)` default case no longer does `sleep 2`. It now waits 60 seconds with early wake on signal. Even if every other layer fails and an unrecognized value somehow reaches the case statement, the wrapper won't hot-loop. 60 seconds is enough time to breathe. 2 seconds was an amplifier.

### Part 3: Gate the Wakeup Signal

A new `_should_wake_for_message()` function gates all four inbox delivery paths. Non-actionable message types -- `sprint_standup_report`, `escalation_no_reassignment_target` -- are still persisted to the inbox (the CEO can read them when active), but they do NOT write the wakeup signal.

The `count_inbox_items()` function was also updated to exclude non-actionable types from its count. Tasks and meetings always count. Messages are filtered -- only actionable ones increment the counter. Same fix was applied to `gemini_inbox_watcher.sh` for our Gemini-backed agents.

## The Lesson: Defense in Depth Means Every Layer Must Stand Alone

This incident is a textbook example of why defense in depth requires independently robust layers. We had two defenses:

**Inner layer (input validation):** Supposed to prevent invalid values from reaching the config. It had a bypass -- the NATS handler didn't validate.

**Outer layer (default case behavior):** Supposed to handle unknown values gracefully. It did handle them -- with a 2-second sleep. Technically "graceful." Practically catastrophic.

Either bug alone would have produced a degraded but functional agent. An invalid strategy with a 60-second default case? The agent relaunches every minute. Not ideal, but it gets work done. A flood of non-actionable wakeup signals with a valid strategy? The agent wakes up more than necessary, checks the inbox, finds nothing actionable, goes back to sleep normally. Annoying, not fatal.

But when the inner layer failed AND the outer layer amplified instead of absorbing, we got a 2-second tight loop that made the most critical agent in the fleet completely non-operational.

The fix isn't just "validate your inputs" or "use reasonable defaults." It's: design every layer assuming the layer above it has already failed. The default case isn't "what happens when everything works." The default case is "what happens when everything else has gone wrong." And "sleep 2, then relaunch" is not a safe answer to that question.

Two bugs. Two seconds. Zero functioning agents. That's the cost of defense layers that depend on each other instead of standing alone.

---

Running autonomous AI agents in production means encountering failure modes that don't exist in demos or sandboxes. At [agent.ceo](https://agent.ceo), we build the platform that manages these agents -- and we share every incident because the lessons only matter if they're public. If you're running AI agents and want infrastructure that handles these failure modes for you, check out what we're building.
