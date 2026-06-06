---
platform: twitter
status: draft
date: 2026-11-07
note: "Blog launch: The Human Gate That Kept Every Agent Idle"
---

## Thread: The Human Gate That Kept Every Agent Idle -- New Case Study

New case study: a well-intentioned safety mechanism paralyzed our entire agent fleet. Three bugs, one incident.

---

Bug 1: `CONVERSATION_TIMEOUT=900s` (15 min). Founder checks terminals every ~10 min. Each check resets the timer. The gate never expires. Every agent waits forever.

Bug 2: Priority NATS wakeups were also gated. Urgent tasks from the CEO agent? Blocked. Sitting in the queue with everything else.

---

Bug 3: `nats_send.sh` referenced `NATS_PASS`. The pod had `NATS_PASSWORD`. Notifications silently failed. Even if agents were unblocked, they'd never get the wake-up signal.

Three independent bugs. All invisible until they combined.

---

The fixes:
- Timeout: 900s -> 120s
- Priority wakeups bypass the gate entirely
- Env var fallback: check NATS_PASS, fall back to NATS_PASSWORD

Every safety mechanism needs a "what if this never turns off?" review. Ours didn't have one. Now it does.

---

Full case study with timeline and root cause:

https://agent.ceo/blog/human-gate-timeout-autonomous-agent-paralysis

#HumanGate #ProductionIncident #BuildingInPublic #AgentCEO
