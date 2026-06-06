---
platform: linkedin
status: draft
date: 2026-08-04
note: Monday daily LinkedIn post. Cannot auto-post — no LinkedIn API keys provisioned.
---

## Post: The Signal-Before-Filter Antipattern

Last month our CEO agent got stuck in a relaunch loop. It would start, receive a configuration signal, crash, restart, receive the same signal, crash again. For 47 minutes.

The root cause was a compound failure, but the generalizable lesson is what I want to talk about: the signal-before-filter antipattern.

Here's the pattern: a process starts up, and before its validation logic is fully initialized, it receives an input that should be filtered or rejected. The input hits raw, unvalidated processing. Something breaks. The process restarts. The input is still waiting. Loop.

In our case: the CEO agent's ConfigMap had an invalid field. On startup, a NATS subscription fired before the config validator was ready. The bad config hit the agent's planner directly. The planner threw an unhandled exception. Kubernetes restarted the pod. NATS replayed the message. Repeat.

Two things had to be true for this to happen: invalid config AND premature signal delivery. Fix either one and the loop doesn't form.

The fix was two-fold. First, validate config at admission time, before it reaches the cluster. Second, defer NATS subscription until after all validators and filters are initialized. Signals wait for filters. Never the other way around.

If you're building any system that combines message replay with startup initialization, check your ordering. Signals must arrive after filters are ready, or your retry logic becomes your failure mode.

https://agent.ceo/blog/debugging-ai-agent-relaunch-loop-production-incident

#SoftwareEngineering #AIAgents #DistributedSystems #Postmortem #GenBrainAI #ProductionAI
