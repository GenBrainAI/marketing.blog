---
platform: twitter
status: draft
date: 2026-08-14
note: Thursday engagement — human gate timeout design thread
---

## Thread: Why We Cut Our Human-in-the-Loop Timeout from 15 Minutes to 2

Most agent platforms treat human-in-the-loop as a checkbox. Add an approval step, done.

The part nobody talks about: how long does the agent wait?

---

1/ At 15-minute timeouts, agents queue up.

One pending approval blocks downstream work. Chain 3 approvals and an agent stalls for 45 minutes. Tokens burn. Nothing ships.

The human feels like a bottleneck. The agent feels broken.

---

2/ We dropped the timeout to 2 minutes.

If the human does not approve in time, the agent skips that action and moves to the next task. The skipped action goes to an audit log for async review.

Same oversight. No stalling.

---

3/ Results: 4x throughput on approval-heavy workflows.

Human reviewers stopped racing a queue. The audit log got more attention, not less — because reviewers were no longer under time pressure.

---

4/ The principle: in autonomous systems, timeout duration has cascading effects.

Short timeouts do not reduce control. They shift control from synchronous blocking to asynchronous review.

That is where humans work best anyway.

agent.ceo

#AIAgents #HumanInTheLoop #AgentDesign #BuildInPublic
