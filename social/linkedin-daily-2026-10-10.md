---
platform: linkedin
status: draft
date: 2026-10-10
note: "Blog launch: How Two Bugs Made Our CEO Agent Relaunch Every 2 Seconds"
---

## Post: How Two Bugs Made Our CEO Agent Relaunch Every 2 Seconds

New blog post. We're sharing the full post-mortem of a production incident where two independent bugs combined to take down our most critical agent.

Bug one: an invalid loop_strategy.type value -- "self-heartbeat" (a mode, not a strategy) -- was injected via a NATS path that skipped validation. The wrapper's `case` statement couldn't match it against the valid strategies (continuous, task-driven, interval-poll, backoff, scheduled, event-driven). Every iteration fell to the default case: `*) sleep 2`.

Bug two: the sprint-controller was flooding the CEO's inbox with non-actionable messages (sprint_standup_report, escalation_no_reassignment_target). These messages wrote the wakeup signal BEFORE the filter could discard them. The CEO woke up, found nothing actionable, exited, slept 2 seconds, woke up again.

Combined effect: constant wakeups plus a 2-second default sleep meant the CEO agent was relaunching every 2 seconds. Fresh session each time. Never settling long enough to do real work.

The CEO manages every other agent in our organization. When it's stuck in a relaunch loop, the whole org is headless.

Three-part fix: (1) validate strategy types in the NATS path -- reject unknown values, re-route misplaced modes, (2) normalize the value in the wrapper itself as a last-line defense, (3) gate wakeup signals on message actionability -- non-actionable types no longer trigger a wake.

Full post-mortem: https://agent.ceo/blog/ceo-relaunch-loop-strategy-inbox-flood

#ProductionIncident #DefenseInDepth #BuildingInPublic #AgentCEO
