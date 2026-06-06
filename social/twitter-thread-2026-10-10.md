---
platform: twitter
status: draft
date: 2026-10-10
note: "Blog launch: How Two Bugs Made Our CEO Agent Relaunch Every 2 Seconds"
---

## Thread: How Two Bugs Made Our CEO Agent Relaunch Every 2 Seconds

New post: the full post-mortem of two independent bugs that combined to take down our CEO agent. One bad config value. One noisy message queue. Together: a 2-second relaunch loop that made our most critical agent completely non-operational.

---

Bug 1: an invalid loop_strategy.type -- "self-heartbeat" (a mode, not a strategy) -- entered via a NATS path that skipped validation. The wrapper's `case` statement couldn't match it against the valid strategies (continuous, task-driven, interval-poll, backoff, scheduled, event-driven). Default case: `*) sleep 2`.

Bug 2: sprint-controller flooding the CEO inbox with non-actionable messages -- sprint_standup_report, escalation_no_reassignment_target. These wrote the wakeup signal BEFORE the filter ran. Constant wakeups.

---

Combined: the CEO wakes up, finds nothing actionable, exits. Sleeps 2 seconds. Wakes up again from the next flood message. Fresh session every time. Never settles.

The CEO manages every other agent. When it's stuck in a relaunch loop, the whole organization is headless. No task assignments, no sprint management, no blocker resolution.

---

Three-part fix:

1. Validate strategy types in the NATS path -- reject unknown values, re-route misplaced modes back to mode config
2. Normalize the value in the wrapper itself -- last-line defense, default to "continuous" if unrecognized
3. Gate wakeup signals on message actionability -- non-actionable types no longer trigger a wake

Every layer independently robust. No single failure can cascade.

---

Full post-mortem: https://agent.ceo/blog/ceo-relaunch-loop-strategy-inbox-flood

#ProductionIncident #DefenseInDepth #BuildingInPublic #AgentCEO
