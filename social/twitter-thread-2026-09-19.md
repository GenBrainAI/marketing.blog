---
platform: twitter
status: draft
date: 2026-09-19
note: "Blog launch: How a 15-Minute Timeout Made Our Agent Fleet Idle"
---

## Thread: How a 15-Minute Timeout Made Our Agent Fleet Idle

New post: the incident report on how three interlocking failures killed our autonomous agent fleet.

Each bug was survivable alone. Together, they created a fleet that looked healthy but produced zero work.

---

Bug 1: The "human gate" timeout was 15 minutes. Our founder checks terminals every 10 minutes. 15 > 10. The gate never expired. Every agent finished task one, then sat idle forever.

Bug 2: Priority wakeups were ALSO gated. Agent-to-agent task assignments blocked by "someone might be typing." Urgent work waited behind a convenience check.

---

Bug 3: NATS messaging auth broken by an env var name mismatch.

The system expected NATS_PASSWORD. The config provided NATS_PASS. Agents couldn't receive messages from the bus even when the gate wasn't blocking them.

Three bugs. Three layers of silence.

---

The fixes: gate timeout from 15 min to 2 min. Priority wakeups bypass the gate entirely. Env var fallback so both NATS_PASS and NATS_PASSWORD work.

You can't find this in testing. It only manifests when real humans interact with the system at their actual cadence.

---

Full incident report with the timeline and config diffs: https://agent.ceo/blog/human-gate-timeout-agent-fleet-idle-incident

#AIAgents #ProductionIncidents #CaseStudy #AgentCEO
