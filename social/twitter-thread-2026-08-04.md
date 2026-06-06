---
platform: twitter
status: draft
date: 2026-08-04
note: Monday Twitter thread. Cannot auto-post — no Twitter API keys provisioned.
---

## Thread: The Signal-Before-Filter Antipattern

1/ Our CEO agent got stuck in a relaunch loop for 47 minutes last month. Start, crash, restart, crash. Same failure every time.

The root cause is a pattern I see everywhere in distributed systems. Thread on the signal-before-filter antipattern:

---

2/ What happened: NATS subscription fired before the config validator initialized. Invalid ConfigMap hit the planner raw. Unhandled exception. Pod restart. NATS replayed the message. Loop.

Two conditions required: bad config + premature signal delivery.

---

3/ The general pattern: a process starts up and receives input before its validation/filtering layer is ready.

The input that should be rejected hits raw processing. Something breaks. The process restarts. The input replays. Your retry logic becomes your failure mode.

---

4/ Where you'll see this:
- Message queues with replay hitting services mid-startup
- Event-driven systems where subscriptions activate before auth middleware
- Init containers that emit before downstream readiness
- Any startup sequence where "listen" happens before "validate"

---

5/ The fix is a strict ordering rule: filters initialize before signals arrive. Never the reverse.

For us: validate config at admission time (before it enters the cluster) + defer NATS subscriptions until all validators are ready. Either fix alone breaks the loop.

---

6/ Full postmortem with the timeline, config diffs, and the two-part fix:

https://agent.ceo/blog/debugging-ai-agent-relaunch-loop-production-incident

#DistributedSystems #SoftwareEngineering #AIAgents #Postmortem #BuildInPublic
