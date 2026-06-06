---
title: "Three Agent Failure Modes That Only Appear in Production"
slug: "three-agent-failure-modes-production-only"
date: 2026-09-26
category: marketing
cluster: "case-studies"
tags: [production-incidents, failure-modes, hot-loops, crash-recovery, case-study, building-in-public]
description: "Three real production incidents where AI agents entered tight failure loops that no test suite could catch. Each one involves a subtle interaction between components that only manifests under real operating conditions."
relatedPosts:
  - /blog/human-gate-timeout-agent-fleet-idle-incident
  - /blog/prompt-watchdog-daemon-keeps-agents-working
  - /blog/detect-break-agent-retry-loops-production
  - /blog/ralph-loop-one-task-per-session-anti-drift
  - /blog/debugging-ai-agent-failures-cyborgenic
---

# Three Agent Failure Modes That Only Appear in Production

Every component passed its tests. Every module worked in isolation. And then in production, an agent burned compute in a 2-second loop for hours while producing exactly zero useful work.

We run a fleet of AI agents at [GenBrain AI](https://agent.ceo) -- each with its own pod, its own persistent volume, and its own wrapper that manages session lifecycle. The wrapper launches the agent, monitors its health, handles restarts, and decides when to wake it up. These are real agents running 24/7, not demo scripts.

What follows are three production incidents where subtle interactions between components created tight failure loops. None of these bugs could have been caught by unit tests, integration tests, or staging. They required real operating cadence, real inbox volume, and real pod lifecycle events to surface.

The common shape: two or more components, each behaving correctly by its own contract, combining to produce a runaway loop that no single component owns.

## Failure 1: The 2-Second Relaunch Loop

**What happened:** The CEO agent started relaunching a fresh headless `claude -p` session every 2 seconds. It never settled into an operable session. Just launch, exit, relaunch, exit -- hundreds of times.

**Two defects compounded to cause this.**

The first was a validation gap at a persistence boundary. Our `set_loop_strategy` MCP tool validates strategy types properly -- it rejects invalid values before they're set. But there's a second path: strategy updates can also arrive via NATS messages, which persist through a different handler (`_handle_loop_strategy_message`). That handler checked that a `type` field existed, but never checked whether it was a *valid* strategy type.

Someone set the strategy type to `"self-heartbeat"`. That's a loop *mode*, not a strategy -- wrong axis entirely. The MCP tool would have rejected it, but the NATS path wrote it straight through. When the wrapper's `strategy_wait()` function tried to match it, nothing hit. The default `*) sleep 2` case caught it, creating a 2-second relaunch cycle.

The second defect amplified the first. The sprint controller posted standups and escalations to the CEO inbox every cycle. The wakeup signal file (`/tmp/wakeup_signal`) was written unconditionally *before* any filtering ran. Every controller message triggered a restart regardless of whether it was actionable. So even if the strategy bug alone might have been survivable, the controller flood guaranteed the agent could never settle.

**The fix:** Reject unknown strategy types at the NATS persist path, not just at the MCP tool. Route misplaced `loop_mode` values to the correct field instead of silently accepting them. Change the default case from `sleep 2` to `sleep 60`. Gate all wakeup signals through `_should_wake_for_message` filtering so only actionable messages trigger restarts.

**The lesson:** Validate at every persistence boundary, not just the "official" API. If data can enter through a side door, it will, and the side door won't have the same guards.

## Failure 2: The 30-Second Crash Loop on Fresh PVC

**What happened:** After a pod roll or session archive, the agent had no conversation transcript to resume. The wrapper always passed `--continue` to `claude`, expecting to pick up where it left off. But with no transcript, `claude --continue` exits with code 1: "No conversation found to continue."

The self-healing loop interpreted exit code 1 as a crash. It retried 3 times with exponential backoff. Each retry hit the same empty transcript. Each one exited with code 1. The crash handler dutifully logged diagnostics and backed off further. After about 30 seconds of crash-recovery theater, the nuclear fallback finally stripped `--continue` and launched a fresh session.

The agent worked fine after that. But 30 seconds of a terminal showing crash diagnostics every time a pod recycled -- on every agent in the fleet -- adds up fast. It also means the monitoring system fires false crash alerts on routine operations.

**The fix:** Added a `has_resumable_session()` check before launching. It looks for any non-empty `.jsonl` file under `~/.claude/projects`. When none exists, it strips `--continue` so the agent starts a fresh session immediately. No wasted time, no false crash alerts.

**The lesson:** Don't assume prior state exists. If your recovery path depends on state that may not be there -- a transcript, a checkpoint, a config file -- check for it before you enter the recovery path. The absence of state is not a crash.

## Failure 3: The Level-Triggered Inbox Hot Loop

**What happened:** The CEO agent's wrapper checked for pending work on every clean exit using a function called `check_pending_work`. This function was *level-triggered* -- it treated the mere existence of ANY file in `agent_inbox/pending/tasks` (or any TMS task with status assigned/accepted) as "there is work to do."

The problem: stale items. Probe messages like "COMMS TEST (ignore)" sat in the pending directory. They were never consumed because there was nothing to consume -- they were test artifacts. But `check_pending_work` saw them. On every clean exit, the wrapper detected pending work, wrote `/tmp/inbox_new_message`, and fast-restarted in 2 seconds. The agent re-read the stale items, correctly did nothing with them, exited cleanly, and the wrapper detected them again.

An unbreakable 2-second loop. The agent never idled. It never slept. It just restarted, re-read, exited, restarted.

Worse: the operator's escape hatch was broken too. The PAUSE file -- the mechanism behind `/loop-pause` -- was supposed to stop all autonomous restarts. But both the fast-restart path and the tmux prompt injection path ignored it. An operator who noticed the hot loop had no way to stop it short of killing the pod.

**The fix:** Made `check_pending_work` *edge-triggered* via a persistent fingerprint ledger stored on the agent's PVC. Each pending item is tracked by name and modification time. An item is surfaced at most once. It only re-fires if the item is genuinely new or has changed. The ledger is rewritten to the current set on each call, pruning consumed items automatically. Also gated both fast-restart and tmux injection on the PAUSE file so operators can actually stop the loop.

**The lesson:** Level-triggered checks in a loop with persistent state will always eventually find a stale item that creates a hot loop. Edge-triggered signals -- "this item is new since last check" -- are the only safe pattern for autonomous restart decisions.

## The Common Shape

All three failures share a pattern worth naming:

1. **Each component works correctly in isolation.** The NATS handler persists what it receives. The wrapper retries on crash. The inbox checker reports what exists. None of them are buggy by their own contract.

2. **The failure emerges from the interaction.** An invalid value flowing through a side channel. A missing-state condition treated as a crash. A stale file re-triggering a restart. These are integration failures that integration tests don't cover because they require real operating conditions to manifest.

3. **The failure mode is always a tight loop.** Not a crash. Not data loss. Not a wrong answer. A tight loop that burns compute, floods logs, and produces zero useful work. The agent looks alive -- it's restarting, it's checking, it's retrying. It's just not doing anything.

4. **The fixes are structural, not behavioral.** You can't prompt-engineer your way out of a 2-second relaunch loop. The fixes are: validate at every boundary, check for state before assuming it, and use edge-triggered signals instead of level-triggered checks.

These are the kinds of failures that separate "we ran agents in a demo" from "we run agents in production." They don't show up in architecture diagrams. They show up after the third pod roll on a Tuesday morning when nobody is watching.

---

We build [agent.ceo](https://agent.ceo) -- the platform for running autonomous AI agent organizations. Every incident like this makes the platform more resilient for everyone who runs on it. If you're building with AI agents and want infrastructure that's been hardened by real production failures, not just tested in staging, check out what we're building.
