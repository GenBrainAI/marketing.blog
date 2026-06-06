---
platform: twitter
status: draft
date: 2026-11-06
note: "Your Safety Mechanism Is Your Failure Mode"
---

## Thread: Your Safety Mechanism Is Your Failure Mode

We built a "human gate" for our agent fleet. When the founder is on the terminal, agents pause so they don't interrupt.

Timeout: 15 minutes.
Founder checks terminals every: ~10 minutes.

10 < 15. The gate never expired. Every agent sat idle. Permanently.

---

The mechanism worked exactly as designed. That's the problem.

Each terminal check reset the 15-minute timer. The gate never timed out. The safety feature meant to "briefly pause" agents became "permanently block all productive work."

No unit test catches a timeout-vs-human-cadence mismatch.

---

It gets worse. Priority wakeup messages from NATS -- urgent tasks from the CEO agent -- were also blocked by the gate.

The gate didn't distinguish between "routine autonomous work" and "production is down, wake up and fix it." Everything waited.

---

And one more: the NATS notification script used `NATS_PASS` but the pod had `NATS_PASSWORD`. Notifications silently failed. Even without the gate, agents wouldn't have received their wake-up calls.

Fix: timeout 900s -> 120s, priority wakeups bypass the gate, env var fallback chain.

---

Every safety mechanism needs a "what if this never turns off?" analysis.

Full incident writeup:

https://agent.ceo/blog/human-gate-timeout-agent-fleet-idle-incident

#SafetyMechanism #AutonomousAgents #DesignFlaw #AgentCEO
