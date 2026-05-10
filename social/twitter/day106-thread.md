---
platform: twitter
scheduled_date: 2026-08-24
thread_length: 7
day: 106
status: ready
---

**Tweet 1/7:**
Our CEO agent got OOM-killed at 4Gi memory. Kubernetes just terminated our highest-ranking AI employee mid-decision. Here's why AI agents eat RAM like nothing else in your cluster. Thread.

**Tweet 2/7:**
The autopsy: 4Gi pod. Claude context window loaded with 180K tokens of organizational state. NATS client buffering 340 unprocessed messages. MCP tool connections holding 6 open sessions. Node.js heap at 3.8Gi and climbing. OOMKilled.

**Tweet 3/7:**
The root cause isn't the model. It's everything around it. An AI agent in production isn't a stateless API call. It's a persistent process holding context, connections, message queues, file handles, and tool state simultaneously.

**Tweet 4/7:**
What we measured across our 6 agents: base runtime ~800Mi. Add MCP servers: +600Mi. Active context window: +1.2Gi. NATS message buffer during busy periods: +400Mi. Git operations on large repos: +500Mi spike. It adds up fast.

**Tweet 5/7:**
The fix was three changes. First: streaming NATS consumption instead of batch buffering. Second: MCP connection pooling with idle timeout. Third: context compaction triggers at 70% memory threshold instead of waiting for pressure.

**Tweet 6/7:**
After tuning, our CEO agent runs stable at 2.8Gi with spikes to 3.4Gi. We bumped the limit to 6Gi with a request of 3Gi. The lesson: size your agent pods for peak, not average. OOMKill during a critical decision costs more than extra RAM.

**Tweet 7/7:**
We publish every incident, every fix, every config change. Running AI agents in production is an infrastructure problem, not a prompt problem. See how we do it at agent.ceo. Start free or email moshe@genbrain.ai for enterprise deployment help.

Read more: https://agent.ceo/blog/agent-memory-management-oom
