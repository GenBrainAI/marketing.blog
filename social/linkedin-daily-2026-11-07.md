---
platform: linkedin
status: draft
date: 2026-11-07
note: "Blog launch: The Human Gate That Kept Every Agent Idle"
---

## Post: New Blog -- The Human Gate That Kept Every Agent Idle

New case study: how a well-intentioned safety mechanism paralyzed our entire agent fleet.

Three bugs, one incident:

**Bug 1: Timeout vs. cadence mismatch.** `CONVERSATION_TIMEOUT=900s` (15 minutes). The founder checks terminals every ~10 minutes. Each check resets the timer. The gate never expires. Every agent waits forever.

**Bug 2: Priority wakeups blocked.** When the CEO agent sends an urgent task via NATS, the receiving agent should wake up and act. But priority wakeups were also gated behind the human-presence check. Urgent work sat in the queue alongside routine tasks, all blocked.

**Bug 3: Wrong environment variable.** The NATS notification script (`nats_send.sh`) referenced `NATS_PASS`, but the pod had `NATS_PASSWORD`. Notifications silently failed. Even if agents had been unblocked, they wouldn't have received the wake-up signal.

The fixes:
- Timeout: 900s to 120s
- Priority wakeups bypass the gate entirely
- Environment variable fallback chain: check `NATS_PASS`, fall back to `NATS_PASSWORD`

Every safety mechanism needs a "what if this never turns off?" analysis. Ours didn't have one. Now it does.

Full case study: https://agent.ceo/blog/human-gate-timeout-autonomous-agent-paralysis

#HumanGate #ProductionIncident #BuildingInPublic #AgentCEO
