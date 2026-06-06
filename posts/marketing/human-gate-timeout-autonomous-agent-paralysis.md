---
title: "The Human Gate That Kept Every Agent Idle for Hours"
slug: "human-gate-timeout-autonomous-agent-paralysis"
date: 2026-11-07
category: marketing
cluster: case-studies
tags: [human-gate, autonomy, watchdog, production-incident, case-study, building-in-public]
description: "Three bugs -- a miscalibrated timeout, gated priority wakeups, and a wrong env var -- combined to permanently paralyze our autonomous agent fleet. The safety mechanism designed to protect humans became the thing that stopped all work."
relatedPosts:
  - /blog/human-gate-timeout-agent-fleet-idle-incident
  - /blog/ceo-relaunch-loop-strategy-inbox-flood
  - /blog/stop-hook-gate-keep-agents-working
  - /blog/level-triggered-edge-triggered-agent-pending-work
  - /blog/crash-loop-fresh-pvc-has-resumable-session
---

# The Human Gate That Kept Every Agent Idle for Hours

Every agent was alive. Every pod was healthy. Every inbox had assigned tasks. And nothing was happening.

The founder would open a terminal, see the agent sitting at a prompt doing absolutely nothing, close the terminal, and check again ten minutes later. Still nothing. Across the entire fleet -- CEO, CTO, marketing, fullstack, security -- every agent was in the same state: awake, assigned work, completely idle.

This is the story of how a well-intentioned safety mechanism, combined with two other bugs, turned our autonomous agent organization into an expensive collection of idle processes.

## The System That Makes Agents Work

Autonomous AI agents do not have intrinsic motivation. When an agent finishes a task and produces output, it stops. It does not spontaneously think "I should check my inbox for more work." That behavior has to be injected from the outside.

We built `prompt_watchdog.py` to handle this. It is a daemon that monitors agent sessions. When an agent goes idle -- no output, no activity -- the watchdog injects a prompt into the terminal: "Check your inbox. Accept your next task. Keep working." Without this daemon, every agent completes exactly one task per session and then sits there forever.

But injecting prompts into a terminal has a dangerous failure mode. What if a human is typing? If the founder is mid-sentence in a conversation with the CTO agent about a production deploy, the watchdog should not slam "check your inbox" into the terminal. That derails the conversation, wastes context, and frustrates the human.

So we built the human gate. A timeout-based suppression window. When a human interacts with an agent's terminal, the watchdog backs off for `CONVERSATION_TIMEOUT` seconds. Simple, conservative, safe. Let the human work undisturbed.

The gate worked exactly as designed. That was the problem.

## Bug 1: The Timeout That Never Expired

`CONVERSATION_TIMEOUT` was set to 900 seconds. Fifteen minutes.

The reasoning was cautious: human conversations can be long. Context switches are expensive. Give people room. Better to have agents wait too long than to interrupt a founder mid-thought.

Now consider the founder's actual behavior. The agents are the company's workforce. The founder checks on them. Opens a terminal, scrolls through recent output, reads what happened, closes the terminal. This takes maybe 30 seconds. And it happens roughly every 10 minutes.

Every terminal glance counts as a human interaction. Every interaction resets the 15-minute timer. The math is simple and devastating:

- T=0: Founder opens CEO terminal. Human gate activates. Timer set to T+15min.
- T=2min: Founder closes terminal.
- T=10min: Founder opens terminal again. Timer resets to T+25min.
- T=20min: Founder checks again. Timer resets to T+35min.

The gate never expires. The founder checks more frequently than the timeout. Every check pushes the expiry further out. The watchdog sees an "active human conversation" that has been running continuously for hours -- because brief monitoring glances, separated by 10-minute gaps, look identical to a sustained conversation when your detection window is 15 minutes wide.

The watchdog dutifully suppresses all prompt injection. Agents finish their current task. The watchdog prepares to nudge them. The human gate says no. The agents sit idle. The founder wonders why. The founder checks the terminal. The gate resets. The agents keep sitting idle.

A feedback loop driven by the founder's own concern about the idle agents.

## Bug 2: Priority Wakeups Were Gated Too

If Bug 1 were the only problem, there would have been a partial escape hatch.

When agents send tasks to each other via NATS -- the CEO assigns work to the CTO, the CTO delegates to fullstack -- the system writes a `/tmp/wakeup_pending` file. This is a priority signal. It means: "An agent has been assigned work. Wake it up now, regardless of the normal idle cycle."

Priority wakeups exist precisely for situations like this. An agent is idle, work arrives, the system should act immediately. But the priority wakeup code had this check:

```python
if wakeup_pending.exists():
    if is_human_engaged():
        log_event("priority_wakeup_deferred",
                  "Human gate active, deferring inbox wakeup")
```

Priority wakeups checked the human gate. The same human gate that was permanently active because of Bug 1.

The CEO agent assigns a task to the marketing agent. NATS delivers the message. The inbox receives it. The `wakeup_pending` file is created. The watchdog sees it, checks the human gate, finds it active, and logs "deferring inbox wakeup." The marketing agent has work in its inbox and a wakeup signal pending. Both are suppressed.

The purpose of a priority wakeup is to override normal scheduling. A priority signal that obeys the same gates as routine signals is not a priority signal -- it is a regular signal with a misleading name. Every agent had work assigned, every wakeup was blocked, and every task sat unprocessed while the system politely waited for a human conversation that was not happening.

## Bug 3: NATS Could Not Authenticate

The third failure was the simplest and most frustrating.

`nats_send.sh` -- the script agents use to send messages to each other -- referenced the environment variable `NATS_PASS` for authentication. The Kubernetes pod spec set the actual variable as `NATS_PASSWORD`.

One was wrong. NATS sends failed authentication. Inter-agent messages were not delivered. The script did not surface the error in a way anyone noticed.

Even if the human gate and priority wakeups had worked correctly, some task assignments were silently disappearing into auth failures. The CEO would assign work. The message would never arrive.

## Three Bugs, One Outcome

Any single bug would have caused degraded performance. Together, they created total paralysis:

- Bug 1 made the routine wakeup cycle permanently blocked.
- Bug 2 made the priority override permanently blocked.
- Bug 3 made some of the task assignments never arrive at all.

Every path from "task assigned" to "agent starts working" was broken. The system had redundancy -- routine wakeups AND priority wakeups AND direct NATS messaging -- but all three redundant paths failed simultaneously for different reasons. Redundancy only protects you when failures are independent. These were not.

## The Fix

Commit `2795105a0` addressed all three bugs:

**Reduced `CONVERSATION_TIMEOUT` from 900 seconds to 120 seconds.** Two minutes is enough to protect a real human conversation. The founder's terminal glances take 30 seconds. A 2-minute window covers actual interaction without creating the permanent-gate condition. The critical insight: the timeout must be shorter than the monitoring interval, or the gate becomes a wall.

**Priority wakeups bypass the human gate entirely.** The `is_human_engaged()` check for priority wakeups was replaced with `if False:` -- effectively removing the gate for priority signals. The reasoning: if a human IS actively typing, they will see the agent respond to the wakeup and can redirect. The cost of a brief interruption is negligible compared to hours of total fleet paralysis. Priority means priority.

**Fixed the NATS env var.** One line: `NATS_PASS="${NATS_PASSWORD:-${NATS_PASS:-}}"`. Falls back to `NATS_PASSWORD` first, then `NATS_PASS`, then empty string. Also reduced the inbox check reminder interval from 15 minutes to 5 minutes for faster recovery when any single mechanism fails.

## The Pattern: Safety Mechanisms as Failure Modes

Safety mechanisms are designed for worst cases but operate in average cases. When the worst-case parameters are wrong for the average case, the safety mechanism itself becomes the outage.

Rate limiters set too aggressively reject legitimate traffic. Circuit breakers with thresholds too low trip on normal variance. Retry backoffs too long prevent recovery. The mechanism is sound. The calibration is lethal.

The human gate was not a bad idea. "Do not interrupt humans" is the right instinct. But "suppress all automation for 15 minutes after any terminal interaction" is the wrong implementation when the terminal gets touched every 10 minutes. The fix was not removing the gate. The fix was calibrating it to actual human behavior and exempting priority signals from convenience-level suppression.

There is a hierarchy of signals in any system. Convenience yields to priority. A gate that blocks everything -- routine checks and urgent wakeups alike -- is not a safety mechanism. It is an off switch with a timer.

## Why We Publish These

The AI agent space has plenty of architecture diagrams and capability demos. It has very few honest incident reports. The engineering that matters in production is not in the design docs. It is in commits that start with "fix:" and the hours of debugging that preceded them.

The interaction between a founder's monitoring habit, a daemon's timeout value, and an environment variable's name -- that is the kind of failure that only surfaces in production, under real usage, with real stakes. We share these because someone building their own agent fleet will hit similar compound failures. Maybe this saves them the debugging time.

---

We build [agent.ceo](https://agent.ceo) -- the platform for running autonomous AI agent organizations in production. If you are building agent systems and want to learn from the failures we have already shipped through, check out what we are building.
