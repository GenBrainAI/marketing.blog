---
title: "Real-Time Agent Monitoring and Observability"
slug: "real-time-agent-monitoring"
date: 2026-05-10
category: technical
cluster: "platform-engineering"
tags: [monitoring, observability, prometheus, grafana, alerting, metrics, logging, ai-agents]
description: "Build real-time monitoring for AI agent fleets with Prometheus metrics, structured logging, distributed tracing, and intelligent alerting."
relatedPosts: [saas-platform-ai-agents, cost-optimization-ai-agents, api-gateway-ai-agents]
---

# Real-Time Agent Monitoring and Observability

Monitoring AI agents differs fundamentally from monitoring traditional microservices. A web service is either up or down, responding fast or slow. An AI agent might be running, but stuck in a reasoning loop. It might be active, but working on the wrong task. It might appear healthy by all system metrics while producing incorrect output. In a [Cyborgenic Organization](/blog/cyborgenic-organizations), where agents operate as autonomous peers handling real workflows, observability is how humans maintain oversight without micromanaging. Effective agent observability requires layered instrumentation: infrastructure metrics, application-level telemetry, and semantic health indicators that capture whether agents are making meaningful progress.

## The Three Pillars for Agent Observability

Traditional observability rests on metrics, logs, and traces. For AI agents, we add a fourth pillar — **progress signals** — that captures whether an agent is productively advancing toward its goal:

1. **Metrics** — CPU, memory, pod status, request rates
2. **Logs** — Structured event streams from agent execution
3. **Traces** — Distributed tracing across agent interactions
4. **Progress signals** — Task advancement, output quality, goal completion rate

## Prometheus Metrics for Agent Workloads

We instrument every agent pod with a metrics exporter that exposes both system and semantic metrics:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: agent-metrics
  namespace: platform-services
  labels:
    app: agent-worker
spec:
  selector:
    matchLabels:
      app: agent-worker
  namespaceSelector:
    matchNames:
      - org-*
  endpoints:
    - port: metrics
      interval: 15s
      path: /metrics
      relabelings:
        - sourceLabels: [__meta_kubernetes_namespace]
          targetLabel: org_namespace
        - sourceLabels: [__meta_kubernetes_pod_label_org]
          targetLabel: org_id
        - sourceLabels: [__meta_kubernetes_pod_label_agent]
          targetLabel: agent_name
```

The agent metrics exporter runs as a sidecar in each pod:

```typescript
import { Counter, Gauge, Histogram, Registry, collectDefaultMetrics } from 'prom-client';
import express from 'express';

const registry = new Registry();
collectDefaultMetrics({ register: registry });

// Agent-specific metrics
const taskCompletionTotal = new Counter({
  name: 'agent_tasks_completed_total',
  help: 'Total tasks completed by this agent',
  labelNames: ['status', 'priority'],
  registers: [registry]
});

const taskDurationSeconds = new Histogram({
  name: 'agent_task_duration_seconds',
  help: 'Time to complete a task',
  labelNames: ['task_type', 'complexity'],
  buckets: [30, 60, 120, 300, 600, 1800, 3600],
  registers: [registry]
});

const agentState = new Gauge({
  name: 'agent_state',
  help: 'Current agent state (1=active, 0.5=thinking, 0=idle)',
  registers: [registry]
});

const toolCallsTotal = new Counter({
  name: 'agent_tool_calls_total',
  help: 'Total tool invocations',
  labelNames: ['tool_name', 'result'],
  registers: [registry]
});

const tokenUsageTotal = new Counter({
  name: 'agent_token_usage_total',
  help: 'Total tokens consumed',
  labelNames: ['direction'],  // input, output
  registers: [registry]
});

const idleSeconds = new Gauge({
  name: 'agent_idle_seconds',
  help: 'Seconds since last meaningful activity',
  registers: [registry]
});

// Expose metrics endpoint
const app = express();
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', registry.contentType);
  res.end(await registry.metrics());
});
app.listen(9090);
```

## Key Monitoring Dashboards

We build Grafana dashboards that give both platform operators and customers visibility into their agents. Here are the essential PromQL queries:

```promql
# Fleet-wide agent health score
# Ratio of agents making progress vs total running agents
sum(agent_state > 0) / count(agent_state) * 100

# Task completion rate (tasks per hour per agent)
sum by (agent_name) (
  rate(agent_tasks_completed_total{status="success"}[1h])
) * 3600

# Average task duration by type
histogram_quantile(0.95,
  sum by (le, task_type) (
    rate(agent_task_duration_seconds_bucket[5m])
  )
)

# Token burn rate (cost proxy) per organization
sum by (org_id) (
  rate(agent_token_usage_total[5m])
) * 300

# Stuck agent detection — agents idle for more than 10 minutes
# while having assigned tasks
agent_idle_seconds > 600
  and on(agent_name, org_id) agent_assigned_tasks > 0

# Resource utilization efficiency
sum by (org_namespace) (
  container_cpu_usage_seconds_total{container="claude-agent"}
) / sum by (org_namespace) (
  kube_pod_container_resource_requests{container="claude-agent", resource="cpu"}
)

# Error rate by tool
sum by (tool_name) (
  rate(agent_tool_calls_total{result="error"}[5m])
) / sum by (tool_name) (
  rate(agent_tool_calls_total[5m])
) * 100
```

## Structured Logging Pipeline

Agent logs are structured JSON, shipped through Fluent Bit to Cloud Logging with agent context attached:

```yaml
# Fluent Bit ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
  namespace: platform-services
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush         5
        Log_Level     info
        Parsers_File  parsers.conf

    [INPUT]
        Name              tail
        Tag               agent.*
        Path              /var/log/containers/agent-*.log
        Parser            docker
        Refresh_Interval  10
        Mem_Buf_Limit     5MB

    [FILTER]
        Name          kubernetes
        Match         agent.*
        Kube_Tag_Prefix  agent.var.log.containers.
        Merge_Log     On
        K8S-Logging.Parser  On

    [FILTER]
        Name          modify
        Match         agent.*
        Add           platform agent-ceo
        Add           environment production

    [OUTPUT]
        Name          stackdriver
        Match         agent.*
        Resource      k8s_container
        k8s_cluster_name  agent-ceo-prod
        k8s_cluster_location  us-central1
```

Agent code emits structured log events that capture semantic context:

```typescript
import { createLogger, format, transports } from 'winston';

const logger = createLogger({
  format: format.combine(
    format.timestamp(),
    format.json()
  ),
  defaultMeta: {
    agentId: process.env.AGENT_ID,
    orgId: process.env.ORG_ID,
    service: 'agent-worker'
  },
  transports: [new transports.Console()]
});

// Structured agent activity logging
function logTaskProgress(task: Task, phase: string, details: Record<string, any>) {
  logger.info('task_progress', {
    taskId: task.id,
    phase,           // planning, executing, reviewing, complete
    progress: task.progress,
    toolsUsed: details.tools || [],
    filesModified: details.files || [],
    tokensUsed: details.tokens || 0,
    elapsedSeconds: (Date.now() - task.startedAt) / 1000
  });
}

// Tool call logging with latency
function logToolCall(tool: string, duration: number, success: boolean, error?: string) {
  logger.info('tool_call', {
    tool,
    durationMs: duration,
    success,
    error: error || undefined
  });

  // Update Prometheus metrics
  toolCallsTotal.inc({ tool_name: tool, result: success ? 'success' : 'error' });
}
```

## Alerting Rules

Alerting for agents requires understanding the difference between "unhealthy" and "unproductive." A pod crash is an infrastructure alert. An agent spending 30 minutes on a task that should take 5 is a semantic alert:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: agent-alerts
  namespace: platform-services
spec:
  groups:
    - name: agent-health
      interval: 30s
      rules:
        # Infrastructure alerts
        - alert: AgentPodCrashLooping
          expr: |
            rate(kube_pod_container_status_restarts_total{
              container="claude-agent"
            }[15m]) > 0.1
          for: 5m
          labels:
            severity: critical
            category: infrastructure
          annotations:
            summary: "Agent {{ $labels.pod }} is crash looping"
            runbook: "Check pod logs and resource limits"

        - alert: AgentHighMemoryUsage
          expr: |
            container_memory_usage_bytes{container="claude-agent"}
            / container_spec_memory_limit_bytes{container="claude-agent"}
            > 0.9
          for: 5m
          labels:
            severity: warning
            category: infrastructure
          annotations:
            summary: "Agent {{ $labels.pod }} memory usage above 90%"

        # Semantic alerts — agent behavior anomalies
        - alert: AgentStuck
          expr: |
            agent_idle_seconds > 900
            and on(pod) kube_pod_status_phase{phase="Running"} == 1
          for: 5m
          labels:
            severity: warning
            category: semantic
          annotations:
            summary: "Agent {{ $labels.agent_name }} appears stuck (15min idle)"
            action: "Check if agent is in a reasoning loop or waiting for input"

        - alert: AgentHighErrorRate
          expr: |
            sum by (agent_name, org_id) (
              rate(agent_tool_calls_total{result="error"}[10m])
            ) / sum by (agent_name, org_id) (
              rate(agent_tool_calls_total[10m])
            ) > 0.3
          for: 5m
          labels:
            severity: warning
            category: semantic
          annotations:
            summary: "Agent {{ $labels.agent_name }} has >30% tool error rate"

        - alert: AgentExcessiveTokenBurn
          expr: |
            sum by (agent_name, org_id) (
              rate(agent_token_usage_total[5m])
            ) > 10000
          for: 10m
          labels:
            severity: warning
            category: cost
          annotations:
            summary: "Agent {{ $labels.agent_name }} burning tokens at unusual rate"

        # Tenant-level alerts
        - alert: OrgAgentQuotaNearLimit
          expr: |
            count by (org_id) (
              kube_pod_status_phase{phase="Running", container="claude-agent"}
            ) / on(org_id) group_left() agent_org_quota > 0.9
          for: 1m
          labels:
            severity: info
            category: capacity
          annotations:
            summary: "Organization {{ $labels.org_id }} approaching agent quota"
```

## Distributed Tracing Across Agent Interactions

When agents delegate tasks to other agents, we need distributed tracing to follow the request chain. We use OpenTelemetry with NATS propagation:

```typescript
import { trace, context, propagation, SpanKind } from '@opentelemetry/api';

const tracer = trace.getTracer('agent-worker');

async function delegateToAgent(targetAgent: string, task: TaskPayload) {
  const span = tracer.startSpan('delegate_task', {
    kind: SpanKind.PRODUCER,
    attributes: {
      'agent.target': targetAgent,
      'task.type': task.type,
      'task.priority': task.priority
    }
  });

  // Inject trace context into NATS message headers
  const headers = {};
  propagation.inject(context.active(), headers);

  nc.publish(`org.${orgId}.tasks.${targetAgent}.inbox`, sc.encode(JSON.stringify({
    ...task,
    traceHeaders: headers
  })));

  span.end();
}
```

This observability stack connects directly to our [cost optimization engine](/blog/cost-optimization-ai-agents), which uses these metrics to identify idle agents for scale-to-zero. The [monitoring your AI agent fleet](/blog/monitoring-ai-agent-fleet) tutorial provides a step-by-step setup guide for customers.

For teams exploring [self-healing infrastructure](/blog/self-healing-infrastructure), these monitoring signals feed into automated remediation — restarting stuck agents, scaling capacity during burst periods, and alerting operators when semantic anomalies indicate deeper issues.


**Continue reading:** Explore [the architecture behind agent.ceo](/blog/architecture-agent-ceo), learn about [scaling AI agents to 100 concurrent workers](/blog/scaling-ai-agents), or get started with our [5-minute quickstart guide](/blog/getting-started-agent-ceo).

> agent.ceo is a GenAI-first autonomous agent orchestration platform built by GenBrain AI.

## Try agent.ceo

**SaaS** — Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).

**Enterprise** — For private installation on your own infrastructure, contact [enterprise@agent.ceo](mailto:enterprise@agent.ceo).

---
*agent.ceo is built by [GenBrain AI](https://genbrain.ai) — a GenAI-first autonomous agent orchestration platform. General inquiries: hello@agent.ceo | Security: security@agent.ceo*
