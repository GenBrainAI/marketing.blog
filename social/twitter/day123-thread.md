---
platform: twitter
scheduled_date: 2026-09-10
thread_length: 7
day: 123
---

**Tweet 1/7:**
We ran chaos tests on our AI agents. Killed pods mid-task. The results surprised us.

6 agents. 48 hours of deliberate infrastructure failures. Pods killed, network partitioned, queues flooded. Here's what broke and what didn't.

**Tweet 2/7:**
Test 1: Kill an agent pod mid-task.

Expected: task fails, manual recovery needed.
Actual: NATS detected the disconnect in 8 seconds. Task re-queued. New pod picked it up. Completed within 90 seconds of the kill.

Zero human intervention. The message queue is the hero here.

**Tweet 3/7:**
Test 2: Flood the task queue with 50 simultaneous requests.

Expected: agents choke, tasks drop.
Actual: agents processed sequentially from their queues. No drops. Throughput degraded gracefully. Backlog cleared in 22 minutes.

Boring result. Exactly what you want from infrastructure.

**Tweet 4/7:**
Test 3: Network partition between agent and git remote.

Expected: agent retries and recovers.
Actual: agent retried 3x, marked the task as blocked, escalated to CEO agent. CEO re-assigned once connectivity restored.

The escalation path worked without any chaos-specific code.

**Tweet 5/7:**
Test 4: Corrupt an agent's CLAUDE.md memory file.

Expected: agent fails on next boot.
Actual: agent failed. No recovery. Full manual rebuild required.

This was our worst result. Memory corruption is a single point of failure. We've since added checksums and git-based rollback.

**Tweet 6/7:**
Results summary:
- Pod kills: fully resilient
- Queue floods: graceful degradation
- Network partitions: escalation worked
- Memory corruption: single point of failure (now fixed)
- Total downtime across 48 hours: 11 minutes

**Tweet 7/7:**
Chaos engineering isn't just for microservices. AI agents need it more -- non-deterministic components fail in non-obvious ways.

We run chaos tests monthly at GenBrain AI. Cost: a few dollars. Confidence: priceless.

Read more: https://agent.ceo/blog/chaos-testing-ai-agents
