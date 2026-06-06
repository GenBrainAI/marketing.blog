---
platform: linkedin
status: draft
date: 2026-10-09
note: "When Your Default Case Becomes an Amplifier"
---

## Post: When Your Default Case Becomes an Amplifier

Every shell wrapper has a default case. The `*) sleep 2` at the bottom of the `case` statement. The "this should never happen" branch. Harmless, right?

Until it's the only branch that runs.

Our CEO agent's outer loop wrapper uses a `case` statement to select the loop strategy -- continuous, task-driven, interval-poll, backoff, scheduled, event-driven. Each strategy has defined behavior. The default case is the safety net: if the value doesn't match anything, sleep 2 seconds and restart.

Someone set the CEO's loop_strategy.type to "self-heartbeat." That's a loop MODE (like conductor-driven or paused), not a loop STRATEGY. The wrapper's case statement couldn't match it. Every iteration fell through to `*) sleep 2`.

The result: our CEO agent -- the one that manages every other agent in the organization -- was relaunching every 2 seconds. Fresh session, 2-second sleep, fresh session, 2-second sleep. Completely non-operational.

The fix was simple. The default case now sleeps 60 seconds instead of 2, with early wake on signal. Even if every validation layer upstream fails, the system doesn't hot-loop itself into uselessness.

Defense in depth means every layer must be independently robust. Your validation layer should catch bad values. But your default case should not amplify the failure when validation misses one.

The "should never happen" case is the one that matters most -- because when it does happen, nothing else is protecting you.

https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#DefenseInDepth #AIAgents #ProductionIncidents #AgentCEO
