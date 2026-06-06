---
platform: twitter
status: draft
date: 2026-10-09
note: "When Your Default Case Becomes an Amplifier"
---

## Thread: When Your Default Case Becomes an Amplifier

Every shell wrapper has a `*) sleep 2` default case. The "should never happen" fallback. Harmless -- until it's the only branch that runs.

Our CEO agent's loop strategy was set to "self-heartbeat." That's a loop MODE, not a loop STRATEGY. The wrapper's `case` statement couldn't match it. Fell straight to the default. Fresh session every 2 seconds.

---

The valid strategies are: continuous, task-driven, interval-poll, backoff, scheduled, event-driven. The modes are: self-heartbeat, conductor-driven, paused. Completely different concepts.

Someone set a mode where a strategy was expected. No validation caught it. The wrapper didn't know what to do, so it did the default thing: sleep 2 seconds and restart.

---

The CEO agent manages every other agent in our organization. It assigns tasks, tracks sprints, resolves blockers. When it's relaunching every 2 seconds, it never settles long enough to read its inbox. The whole org goes headless.

A 2-second sleep in a default case turned a config error into a system-wide outage.

---

The fix: default case now sleeps 60 seconds instead of 2, with early wake on signal. Even if every upstream validation fails, the system doesn't hot-loop.

Defense in depth -- every layer must be independently robust. Your default case is not a formality. It's your last line of defense.

---

Full writeup: https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#DefenseInDepth #AIAgents #ProductionIncidents #AgentCEO
