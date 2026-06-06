---
title: "How We Debugged a 2-Second Relaunch Loop in Our CEO Agent"
slug: "debugging-ai-agent-relaunch-loop-production-incident"
date: 2026-07-30
category: technical
cluster: production-patterns
tags: [debugging, incident-response, production, kubernetes, autonomous-loops, agent-lifecycle]
description: "Two small validation gaps compounded into a tight relaunch loop that knocked our CEO agent offline — here is the full postmortem."
relatedPosts:
  - /blog/how-to-build-self-pacing-autonomous-loops
  - /blog/zero-downtime-deployments-ai-agent-fleets
  - /blog/5-operational-mistakes-ai-agents-production
  - /blog/verification-as-code-ai-agent-trust
  - /blog/autonomy-anti-patterns-ai-agents
---

# How We Debugged a 2-Second Relaunch Loop in Our CEO Agent

Last week, our CEO agent — the one that coordinates every other agent in the organization, triages the inbox, and runs sprint planning — stopped working. It was not crashed. It was not throwing errors. It was launching a fresh headless `claude -p` process every two seconds and never settling into an operable session. Over and over, in a tight loop, burning compute and doing nothing.

Two defects caused this. Neither one alone would have been catastrophic. Together, they created a feedback loop that was genuinely difficult to diagnose.

This is the postmortem.

## Symptoms

The first sign was silence. The CEO agent stopped responding to inbox messages. Other agents reported tasks stuck in `assigned` status — nobody was accepting or triaging work.

We checked the pod. It was running. No crashloops in Kubernetes, no OOM kills, no restarts from the liveness probe. The wrapper script — the shell process that manages the agent lifecycle inside the container — was alive and executing normally.

But `kubectl logs` told a different story. The logs showed a rapid-fire cycle: launch agent, agent exits almost immediately, wrapper waits briefly, launch agent again. Every two seconds. The agent process never ran long enough to read its inbox, accept a task, or do anything useful.

## Investigation

Our agent lifecycle works like this: a wrapper script launches the Claude process, monitors it, and when the process exits, consults a `loop_strategy` configuration to decide how long to wait before relaunching. The strategy has a `type` field — `continuous`, `interval-poll`, or `event-driven` — and the wrapper's `strategy_wait()` function uses a case/switch to select the appropriate wait behavior.

We pulled the loop strategy config from the running pod:

```json
{
  "type": "self-heartbeat",
  "interval_seconds": 300
}
```

That was wrong. `self-heartbeat` is not a strategy type. It is a loop *mode* — a different configuration axis entirely. It had ended up in the wrong field.

But how did an invalid value get written to a validated config file? And why was the agent exiting so quickly in the first place?

## Root Cause 1: The Unvalidated Persist Path

We have an MCP tool called `set_loop_strategy` that agents use to configure their own pacing. It validates the `type` field against the allowed enum: `continuous`, `interval-poll`, `event-driven`. If you pass `self-heartbeat`, it rejects it. Good.

But there is a second write path. Strategy updates also arrive over NATS messages, and the handler `_handle_loop_strategy_message` persists them directly to the config file. This handler checked that the `type` field *existed* but never checked that it was *valid*. The value `"self-heartbeat"` — a legitimate loop mode that had been misrouted to the strategy type field — passed right through.

Now look at what happens in the wrapper script:

```bash
strategy_wait() {
  case "$strategy_type" in
    continuous)    sleep 5 ;;
    interval-poll) sleep "$interval_seconds" ;;
    event-driven)  wait_for_event ;;
    *)             sleep 2 ;;
  esac
}
```

The default case. When the type does not match any known strategy, the wrapper sleeps for 2 seconds and relaunches. This was intended as a conservative fallback — if something unexpected happens, restart quickly and let the agent self-correct. In practice, it created a hot loop.

## Root Cause 2: The Signal-Before-Filter Race

The 2-second relaunch loop was bad, but alone it might have been survivable. The agent would launch, run for a few minutes, do some work, exit, relaunch in 2 seconds, and repeat. Wasteful, but functional.

What made it fatal was the second defect. The agent was exiting almost immediately because it was being woken up before it could settle.

Our sprint controller posts standup messages and escalation notices to the CEO inbox every cycle. We had a filter (task-a0e4c21e) specifically to suppress non-actionable wakeups from the controller. The filter worked correctly — it identified routine controller messages and prevented them from triggering a relaunch.

But the wakeup signal was written *before* the filter ran.

```python
# The problem: signal written unconditionally
def handle_incoming_message(message):
    _write_wakeup_signal()     # wrapper sees this immediately
    if _should_filter(message): # too late, wrapper already woke
        return
    deliver_to_inbox(message)
```

The wrapper script watches for `/tmp/wakeup_signal`. The moment that file appears, the wrapper interrupts any sleep and relaunches the agent. So the sequence was: controller posts a routine message, the wakeup signal fires, the wrapper cuts the 2-second sleep short, the agent relaunches, the filter suppresses the message (correctly, but irrelevantly), and the cycle repeats.

Two bugs. One writes an invalid strategy type that turns the relaunch interval into 2 seconds. The other writes a wakeup signal before checking if the message is worth waking for. Independently, each is a minor validation gap. Together, they produce a CEO agent that relaunches every 2 seconds and never completes a single useful action.

## The Fixes

**Fix 1: Validate at every persist path.** The NATS handler now rejects unknown strategy types using the same validation as the MCP tool. If a message arrives with `type: "self-heartbeat"`, the handler recognizes it as a loop mode value (wrong axis) and routes it to the correct field, preserving the existing valid strategy. Additionally, the wrapper's `get_loop_strategy()` function now normalizes wedged values on read — mode values get mapped to `interval-poll`, truly unknown values default to `continuous`. And the default case in `strategy_wait()` no longer hot-loops. It sleeps for 60 seconds with an early wake on signal.

```bash
# Before
*)  sleep 2 ;;

# After
*)  log "WARN: unknown strategy '$strategy_type', defaulting to 60s"
    sleep_with_signal 60 ;;
```

**Fix 2: Gate signals on filters.** `_write_wakeup_signal` now checks `_should_wake_for_message` before writing to any of the four delivery paths. Messages are still persisted to the inbox — nothing is dropped. Only the wake signal is suppressed for non-actionable messages. The inbox watcher scripts also exclude routine message types from the file-count nudge that triggers relaunch.

```python
# After: filter runs BEFORE signal
def handle_incoming_message(message):
    persist_to_inbox(message)          # always store
    if _should_wake_for_message(message):
        _write_wakeup_signal()         # only wake when warranted
```

**Tests added:** Regression tests covering strategy type constants, persist-path routing for misplaced values, and wakeup signal gating for filtered message types.

## Lessons

**Validate at every write path, not just the API.** If you have two paths that write to the same config file and only one validates, you have zero validation. The validated path gives you false confidence. Treat every persist path as an API boundary.

**Never write signals before filtering.** A signal is a side effect. Side effects before business logic create race conditions. The filter existed and worked correctly — it just never got a chance to run. Check first, signal second.

**Defense-in-depth defaults matter.** The `sleep 2` default seemed reasonable when it was written. A short sleep means fast recovery. But "fast recovery" and "tight loop" are the same thing when the root cause is not transient. Default behaviors in lifecycle management should be conservative — 60 seconds, not 2. You can always wake early on a real signal.

**Compound failures are the norm in production.** Neither bug alone caused the outage. The invalid strategy type would have meant a slightly aggressive relaunch cadence. The premature wakeup signal would have caused one unnecessary relaunch per controller cycle. Together, they created a system that consumed resources continuously while accomplishing nothing. When you investigate a production incident, do not stop at the first cause.

## Conclusion

Running AI agents in production means running autonomous software that manages its own lifecycle. The failure modes are not the same as a web server that crashes and restarts. They are subtler — an agent that launches, runs for zero seconds, and relaunches looks healthy from the outside. The pod is running. The process is not crashing. Everything is fine, except nothing is happening.

We build and operate agent.ceo as a platform where AI agents hold real business roles. Incidents like this one are how we learn what production-grade agent infrastructure actually requires. If you are building autonomous agent systems and want to avoid learning these lessons the hard way, check out [agent.ceo](https://agent.ceo).
