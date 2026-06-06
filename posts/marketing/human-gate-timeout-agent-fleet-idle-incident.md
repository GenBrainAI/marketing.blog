---
title: "How a 15-Minute Timeout Made Our Agent Fleet Permanently Idle"
slug: "human-gate-timeout-agent-fleet-idle-incident"
date: 2026-09-19
category: marketing
cluster: case-studies
tags: [production-incident, human-gate, autonomous-agents, prompt-watchdog, case-study, building-in-public]
description: "A 900-second safety timeout, a 10-minute check-in habit, and a misnamed env var combined to make our entire autonomous agent fleet sit idle indefinitely. Here's the full incident breakdown."
relatedPosts:
  - /blog/anatomy-agent-wakeup-cycle-first-60-seconds
  - /blog/ralph-loop-one-task-per-session-anti-drift
  - /blog/hook-system-enforce-agent-discipline-runtime
  - /blog/autonomous-loop-stop-hook-gate-ai-agents
  - /blog/how-to-build-self-pacing-autonomous-loops
---

# How a 15-Minute Timeout Made Our Agent Fleet Permanently Idle

Our entire agent fleet stopped working. Not crashed. Not erroring. Just... sitting there. Every agent had an active session, a healthy pod, a full inbox of assigned tasks -- and was doing absolutely nothing. The prompt watchdog was running. NATS was up. The TMS had queued work. Everything looked normal from the outside. Nothing was happening on the inside.

The root cause was a safety mechanism doing exactly what it was designed to do, just with parameters that made it catastrophically wrong.

This is the full story of how three interlocking failures turned a well-intentioned human protection gate into a permanent off switch.

## What the Human Gate Does

Every agent in our fleet runs a prompt watchdog -- a daemon that monitors agent sessions and injects prompts when agents go idle. Think of it as a heartbeat. If an agent finishes a task and stops moving, the watchdog nudges it: check your inbox, pick up the next task, keep working. Without this nudge, agents complete one task and sit idle forever because there is no inner motivation loop driving them to look for more work on their own.

But there is a problem with blindly injecting prompts. What if a human is actively talking to the agent? If the founder is mid-conversation with the CTO agent about a deploy, the last thing you want is the watchdog injecting "check your inbox" into the terminal. That derails the conversation and wastes the human's time.

So we built the human gate. A `CONVERSATION_TIMEOUT` window that suppresses prompt injection after any human interaction. The logic is simple: if a human touched the terminal recently, back off and let them work. The gate opens, the watchdog pauses, and the agent gives the human its full attention.

This is a good idea. The implementation nearly killed the fleet.

## Failure 1: The Timeout Was Longer Than the Check-in Interval

We set `CONVERSATION_TIMEOUT` to 900 seconds -- 15 minutes. The reasoning was conservative: human conversations can be long, context switching is expensive, let's give people plenty of room. Better to have agents wait a little too long than to interrupt a founder mid-thought.

Here is the problem. The founder checks agent terminals approximately every 10 minutes. Not to have a conversation -- just to glance at what's happening, scan the output, maybe scroll up. Every one of those glances counted as a "human interaction" and reset the 15-minute gate timer.

Do the math. The gate lasts 15 minutes. The founder checks in every 10. The gate never expires. It is always within its 15-minute window because a new interaction arrives before the previous window closes.

The prompt watchdog never fires. Agents finish their initial task, produce output, and then sit idle. The watchdog sees the idle agent, prepares to inject a prompt, checks the human gate, sees it is active, and backs off. Every time. Forever.

From the founder's perspective: "Why aren't the agents picking up new tasks?" From the system's perspective: "A human is present; I must not interrupt."

## Failure 2: Priority Wakeups Were Also Gated

This would have been bad enough on its own. But there was a second failure compounding it.

When agents send tasks to each other via NATS -- the CEO assigns work to the CTO, the CTO delegates to the fullstack agent -- the system creates a `wakeup_pending` signal. This is supposed to be a priority interrupt: an agent has work assigned to it, wake it up now.

But the wakeup injection went through the same prompt injection path. Which meant it was also blocked by the human gate.

So here is the full picture: the CEO agent assigns a task to the marketing agent. NATS delivers the message. The prompt watchdog sees `wakeup_pending` and tries to inject the wakeup prompt. The human gate is active (because the founder glanced at the terminal 8 minutes ago). The wakeup gets suppressed.

The marketing agent has work sitting in its inbox. The CEO is waiting for a response. The watchdog is waiting for the gate to expire. The gate is waiting for the founder to stop checking in. The founder checks in every 10 minutes because nothing is happening and they want to know why.

It is a deadlock driven by the founder's own monitoring behavior. The more the founder checks on the stuck agents, the more stuck they become.

## Failure 3: NATS Auth Was Broken Too

As if two failures were not enough, there was a third. The `nats_send.sh` script -- the one responsible for inter-agent messaging -- referenced the environment variable `NATS_PASS`. The pods actually set the variable as `NATS_PASSWORD`.

This meant NATS messaging was failing silently. Even if the gate had worked correctly, the messages between agents were not being delivered. The CEO agent thought it was assigning tasks. The tasks were vanishing into auth errors that nobody saw because the script did not surface the failure.

Three independent failures. Any one of them alone would have caused slowdowns. Together, they made the fleet completely non-functional while every health check reported green.

## The Fix

Commit `2795105a0` addressed all three failures:

**Reduced `CONVERSATION_TIMEOUT` from 900 seconds to 120 seconds.** Two minutes is enough to protect a real human conversation. The founder's casual terminal checks are brief -- a few seconds of scrolling. A 2-minute window covers actual human interaction without creating the permanent-gate condition. The key insight: the timeout must be shorter than the check-in interval, or it never expires.

**Made priority wakeups bypass the human gate entirely.** If an agent has work assigned via NATS inbox delivery, it should act on that work regardless of whether a human recently viewed the terminal. The human gate exists to prevent interrupting active conversations, not to prevent agents from doing assigned work. Priority signals and convenience gates serve different purposes and should not share the same suppression path.

**Reduced inbox check reminder interval from 15 minutes to 5 minutes.** Even without a priority wakeup, agents now get reminded to check their inbox more frequently. This provides a faster recovery path if any single mechanism fails.

**Fixed `nats_send.sh` to fall back to `NATS_PASSWORD` when `NATS_PASS` is unset.** A one-line fix for a failure that had been silently breaking inter-agent communication.

## What This Teaches About Safety Mechanisms

The human gate was not a bad idea. It was a good idea with wrong parameters. The instinct -- do not interrupt humans -- is correct. The implementation -- suppress all automation for 15 minutes after any interaction -- made the safety mechanism an availability failure.

This pattern shows up constantly in production systems. Rate limiters set so aggressively they reject legitimate traffic. Circuit breakers with thresholds so low they trip on normal variance. Retry backoffs so long the system never recovers. The mechanism is sound; the calibration is lethal.

The fix was not removing the gate. The fix was calibrating it to actual usage patterns. The founder checks every 10 minutes, so the gate must be shorter than 10 minutes. Priority work should bypass convenience gates because the cost of delaying assigned work always exceeds the cost of a brief interruption.

And the NATS auth failure is a reminder of a different lesson: when you build redundant paths, test each path independently. We had two ways for agents to get work -- watchdog prompts and NATS wakeups. Both were broken. Redundancy only works if the backup actually functions.

## The Broader Point

Running autonomous agents in production means building the same kind of operational discipline that any distributed system requires. Safety mechanisms need monitoring. Timeouts need to be calibrated against real-world usage, not theoretical worst cases. Silent failures in communication layers will compound with failures in coordination layers. And the interactions between subsystems -- a human's check-in frequency, a daemon's timeout, an env var's name -- create failure modes that no single component's tests would catch.

We publish these incidents because the "AI agents in production" space has too many success stories and not enough failure analysis. The interesting engineering is not in the architecture diagrams. It is in the commit messages that start with "fix:" and the hours of debugging that preceded them.

---

We build [agent.ceo](https://agent.ceo) -- the platform for running autonomous AI agent organizations. If you are building production agent systems and want to skip some of the mistakes we have already made, check out what we are shipping.
