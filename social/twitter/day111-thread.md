---
platform: twitter
scheduled_date: 2026-08-29
thread_length: 7
day: 111
status: ready
---

**Tweet 1/7:**
Your AI agent needs 6Gi of RAM. No, that's not a typo. Everyone budgets for the model API call and forgets about the 14 other processes keeping an agent alive in production. Here's the real resource bill. Thread.

**Tweet 2/7:**
Baseline agent process: 800Mi. Now add what production requires. MCP server connections (3-5 active): 600Mi. Git working tree for a medium repo: 200Mi. NATS client with message history: 300Mi. Monitoring and health probes: 100Mi. Already at 2Gi.

**Tweet 3/7:**
But that's idle. Under load: context window hydration pulls organizational memory, task history, and relevant docs into working memory. That's 1-2Gi depending on task complexity. Git operations on large repos spike 500Mi. NATS bursts add 400Mi.

**Tweet 4/7:**
Our per-agent resource spec after 110 days of tuning: request 3Gi, limit 6Gi. CPU request 500m, limit 2000m. These numbers come from actual production profiling, not guessing. We tracked p50, p95, and p99 memory usage for 8 weeks.

**Tweet 5/7:**
The mistake everyone makes: setting request = limit. Your agent idles at 2Gi but spikes to 5Gi during complex tasks. If you set both to 3Gi, it OOM-kills during spikes. If you set both to 6Gi, your scheduler wastes 4Gi of reserved RAM per pod.

**Tweet 6/7:**
Multiply by agents: 6 agents at 3Gi request = 18Gi minimum cluster RAM just for agent pods. Add system services, monitoring, NATS, and ingress: 8Gi. Our production cluster runs 32Gi total. Fits on two 16Gi Hetzner nodes at $40/month each.

**Tweet 7/7:**
Production AI agents are infrastructure-heavy, model-light. Budget accordingly. We publish our exact Kubernetes specs and resource profiles. Everything is at agent.ceo. Start free or email moshe@genbrain.ai for help sizing your deployment.

Read more: https://agent.ceo/blog/agent-resource-sizing-production
