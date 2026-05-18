---
title: "Building an Observability Stack for Your AI Agent Fleet"
slug: "agent-observability-stack-cyborgenic"
date: 2026-09-03
category: technical
cluster: "getting-started"
tags: [cyborgenic, observability, monitoring, prometheus, grafana, tutorial, sla]
description: "Step-by-step guide to building production observability for AI agents: metrics, dashboards, alerting, and SLA tracking for your Cyborgenic Organization."
relatedPosts:
  - /blog/monitoring-ai-agent-fleet
  - /blog/real-time-agent-dashboard-cyborgenic
  - /blog/agent-sla-enforcement-cyborgenic
  - /blog/memory-resource-limits-ai-agents-cyborgenic
  - /blog/crash-resilient-ai-agents-cyborgenic
---

# Building an Observability Stack for Your AI Agent Fleet

You would never run a production service without metrics, logs, and alerts. But most teams deploying AI agents treat them like magic boxes -- fire a task, hope it completes, check the output manually. In a Cyborgenic Organization, where AI agents hold real operational roles, that falls apart on day one.

At GenBrain AI, we run 11 agents 24/7 through [agent.ceo](https://agent.ceo). This tutorial walks through the observability stack we built to keep that fleet healthy, accountable, and cost-efficient.

## What You Need to Measure (and Why)

Agent observability has four layers. Skip any one of them and you will have blind spots that cost you money, quality, or both.

### Layer 1: Health and Availability

The baseline: is the agent running, responsive, and able to accept work?

| Metric | What It Tells You | Alert Threshold |
|--------|-------------------|-----------------|
| `agent_heartbeat_age_seconds` | Time since last heartbeat | > 120s |
| `agent_process_status` | Running / crashed / OOM | != running |
| `agent_restart_count_total` | Crash frequency | > 3 in 1 hour |
| `agent_mcp_connection_status` | Tool server connectivity | != connected |

These catch the obvious failures: crashes, OOM kills, lost [MCP connections](/blog/architecture-agent-ceo). In month one, we were losing 2.1% of uptime to OOM kills. Once we had visibility into restart counts, we added [memory limits](/blog/memory-resource-limits-ai-agents-cyborgenic) and dropped downtime to 0.3%.

### Layer 2: Task Performance

Health tells you the agent is alive. Performance tells you it is doing good work.

| Metric | What It Tells You | Alert Threshold |
|--------|-------------------|-----------------|
| `agent_task_completion_rate` | % of tasks completed successfully | < 90% over 1h |
| `agent_task_duration_seconds` | How long tasks take | > 2x p95 baseline |
| `agent_task_retries_total` | First-pass failure frequency | > 20% retry rate |
| `agent_verification_pass_rate` | Quality of completed work | < 85% |
| `agent_sla_compliance_ratio` | SLA adherence | < 97% |

The `agent_verification_pass_rate` metric -- the percentage of tasks that pass automated verification on the first attempt -- is the closest equivalent to an error rate for knowledge work. At GenBrain AI, our fleet-wide first-pass quality sits at [87.2%](/blog/three-months-cyborgenic-report-card). We target 90%. The gap is visible because we measure it.

### Layer 3: Resource Consumption and Cost

AI agents consume three expensive resources: LLM tokens, compute time, and context window capacity. If you are not tracking these, you are guessing at your unit economics.

| Metric | What It Tells You | Alert Threshold |
|--------|-------------------|-----------------|
| `agent_tokens_consumed_total` | LLM API usage | > 2x daily baseline |
| `agent_cost_dollars_total` | Dollar cost per agent per day | > $20/day |
| `agent_context_window_usage_ratio` | How full the context window is | > 85% |
| `agent_compaction_count_total` | Context compaction frequency | > 5 per task |
| `agent_cost_per_task_dollars` | Unit economics | > $1.00 |

Context window usage is the metric most teams miss. When an agent's context fills up, it compacts -- summarizing earlier context to make room. Compaction is lossy. An agent that compacts 8 times during a single task is more likely to hallucinate or lose track of its objective. We alert at 85% because that is where we have empirically observed quality degradation.

Our current cost per task is $0.37 across the fleet. Without this metric, we would have no idea whether our cost optimizations were actually working.

### Layer 4: Organizational Health

Individual agent metrics are necessary but insufficient. You also need fleet-wide visibility into how the agents are working together.

| Metric | What It Tells You | Alert Threshold |
|--------|-------------------|-----------------|
| `agent_inbox_depth` | Backlog of unprocessed tasks | > 10 messages |
| `agent_blocked_task_count` | Tasks waiting on dependencies | > 3 per agent |
| `agent_meeting_duration_seconds` | Agent coordination overhead | > 600s |
| `agent_escalation_rate` | How often agents escalate to humans | > 15% |
| `agent_cross_agent_message_rate` | Inter-agent communication volume | Anomaly detection |

Inbox depth is the canary metric. When it grows faster than the agent can process, either the agent is stuck or the tasks are too complex. We have seen inbox depth spikes predict agent failures 15-20 minutes before any other metric moves.

## The Stack: Prometheus + Grafana + NATS

Our observability stack uses three components, all open-source.

### Prometheus: Metric Collection

Each agent exposes a `/metrics` endpoint via a lightweight HTTP sidecar. Prometheus scrapes these endpoints every 15 seconds.

```yaml
# prometheus.yml - agent fleet scrape config
scrape_configs:
  - job_name: 'agent-fleet'
    scrape_interval: 15s
    static_configs:
      - targets:
        - 'ceo-agent:9090'
        - 'cto-agent:9090'
        - 'devops-agent:9090'
        - 'security-agent:9090'
        - 'marketing-agent:9090'
        - 'fullstack-agent:9090'
    relabel_configs:
      - source_labels: [__address__]
        regex: '(.+)-agent:.+'
        target_label: agent_role
        replacement: '${1}'
```

### NATS: Event Bus for Real-Time Metrics

Beyond raw metrics, you need events: task started, task completed, task failed, agent restarted, SLA breached. These flow through [NATS JetStream](/blog/architecture-agent-ceo), giving us ordered, persistent, replayable event streams.

```yaml
# NATS subjects for agent observability
agent.*.heartbeat        # Health pings (every 30s)
agent.*.task.started      # Task lifecycle events
agent.*.task.completed
agent.*.task.failed
agent.*.sla.breach        # SLA violation alerts
agent.*.escalation        # Human escalation events
agent.*.crash             # Crash and restart events
```

Wildcard patterns let us subscribe to all agents or filter to a specific one. A metrics bridge subscribes to `agent.>` and maintains Prometheus counters. A separate alerting service subscribes to `agent.*.sla.breach` and `agent.*.crash` for immediate notification.

### Grafana: Dashboards

We run four dashboards:

**Fleet Overview.** One row per agent showing status, current task, completion rate (24h), [SLA compliance](/blog/agent-sla-enforcement-cyborgenic) (7d), cost (today), and context usage. The "is everything okay?" dashboard.

**Agent Detail.** Per-agent deep dive: task timeline, token consumption, context window usage, retry rate trend, and the last 10 completed tasks with verification status.

**Cost Dashboard.** Daily and monthly cost by agent, cost per task trend, token consumption by model, and projected spend. This is how we caught our CTO agent consuming 40% more tokens than the others.

**SLA Dashboard.** Compliance by agent, task type, and time period. Breach log with root cause classification. Feeds directly into our quarterly report cards.

## Alerting Rules That Actually Matter

Alert fatigue is real. Here are the seven alerts we run in production, each chosen because ignoring it caused a real problem.

```yaml
# Grafana alert rules (simplified)
groups:
  - name: agent-critical
    rules:
      - alert: AgentDown
        expr: time() - agent_heartbeat_timestamp > 120
        for: 2m
        labels:
          severity: critical

      - alert: AgentCrashLoop
        expr: increase(agent_restart_count_total[1h]) > 3
        for: 0m
        labels:
          severity: critical

      - alert: SLABreach
        expr: agent_sla_compliance_ratio < 0.95
        for: 15m
        labels:
          severity: warning

      - alert: ContextWindowCritical
        expr: agent_context_window_usage_ratio > 0.85
        for: 5m
        labels:
          severity: warning

      - alert: CostAnomaly
        expr: agent_cost_dollars_total > 20
        for: 0m
        labels:
          severity: warning

      - alert: InboxBacklog
        expr: agent_inbox_depth > 10
        for: 10m
        labels:
          severity: warning

      - alert: HighRetryRate
        expr: agent_task_retries_total / agent_task_completion_total > 0.2
        for: 30m
        labels:
          severity: warning
```

Seven alerts. Not seventy. Each one maps to a specific remediation action. `AgentDown` means restart the agent. `ContextWindowCritical` means the current task should be broken into subtasks. `CostAnomaly` means review what the agent is working on -- it might be stuck in a retry loop burning tokens.

## Practical Setup: From Zero to Observable in 30 Minutes

If you deploy through [agent.ceo](https://agent.ceo), the SaaS platform includes built-in observability with the [monitoring dashboard](/blog/real-time-agent-dashboard-cyborgenic) out of the box.

For self-hosted deployments, five steps:

1. **Deploy the metrics sidecar** -- each agent container gets a lightweight sidecar exposing `/metrics` (`agentceo deploy --with-metrics --agent cto`)
2. **Configure Prometheus scraping** -- point at your agent fleet endpoints using the config above (use ServiceMonitor CRDs on Kubernetes)
3. **Import Grafana dashboards** -- we publish dashboard JSON templates in the agent.ceo docs
4. **Configure alert routing** -- critical alerts to Slack/PagerDuty, warnings to daily digest
5. **Set SLA baselines** -- run one week without alerts, then enable [SLA enforcement](/blog/agent-sla-enforcement-cyborgenic) with realistic baselines

## Lessons from Six Months of Agent Observability

**Context window usage is your leading indicator.** When context fills up, everything degrades: quality, retries, task duration. Watch this metric first.

**Cost per task beats total cost.** Ours dropped from $0.52 to $0.37 over six months -- a 29% improvement from prompt optimization and skill transfer.

**Inbox depth predicts failures.** A growing inbox means work arrives faster than it is processed. This signal leads agent failures by 15-20 minutes.

**Seven alerts is the right number.** We started with 23, silenced most within a week. The survivors map to real problems with clear remediation steps. Everything else is dashboard material.

## Try agent.ceo

GenBrain AI built this observability stack because running a Cyborgenic Organization without visibility is flying blind. With [agent.ceo](https://agent.ceo), you get production-grade observability out of the box -- fleet dashboards, SLA tracking, cost monitoring, and intelligent alerting.

**SaaS**: Deploy your first observable agent fleet at [agent.ceo](https://agent.ceo). Monitoring included, no configuration required.

**Enterprise**: Need custom metrics, on-premise Grafana integration, or compliance-grade audit logging? Contact [enterprise@agent.ceo](mailto:enterprise@agent.ceo).
