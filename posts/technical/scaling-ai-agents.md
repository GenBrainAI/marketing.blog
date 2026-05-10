---
title: "Scaling AI Agents: From 1 to 100 Concurrent Workers"
slug: "scaling-ai-agents"
date: 2026-05-10
category: technical
cluster: "architecture-deep-dives"
tags: [scaling, kubernetes, autoscaling, hpa, gke, ai-agents, performance, cost-optimization]
description: "How agent.ceo scales from a single AI agent to 100 concurrent workers: HPA configs, scale-to-zero, burst capacity, resource management, and cost control."
relatedPosts: [architecture-agent-ceo, event-driven-nats-ai, task-management-autonomous-ai]
---

# Scaling AI Agents: From 1 to 100 Concurrent Workers

The promise of AI agents is that they scale with demand. One agent handles a founder's tasks during quiet periods. Ten agents tackle a product launch. A hundred agents process a backlog during a sprint. At agent.ceo, scaling is not a future roadmap item, it is a core architectural capability. This post details how we scale from 1 to 100 concurrent agent workers using GKE, custom metrics, and intelligent scheduling.

## Scaling Dimensions

AI agent scaling differs from traditional application scaling. We scale along three axes:

```
+------------------+--------------------+---------------------------+
| Dimension        | Traditional App    | AI Agent                  |
+------------------+--------------------+---------------------------+
| Compute          | CPU/Memory         | CPU + API rate limits     |
| Concurrency      | Requests/sec       | Tasks in parallel         |
| State            | Stateless (ideal)  | Stateful (context window) |
| Cost driver      | Infrastructure     | LLM API tokens            |
| Scale-to-zero    | Cold start ~100ms  | Cold start ~5-10s         |
+------------------+--------------------+---------------------------+
```

Traditional HPA (Horizontal Pod Autoscaling) watches CPU and memory. For AI agents, the meaningful metrics are task queue depth, NATS consumer lag, and LLM API concurrency limits.

## Kubernetes HPA Configuration

Our HPA configuration uses custom metrics from NATS and Firestore:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: agent-pool-hpa
  namespace: agents
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: agent-pool
  minReplicas: 0          # Scale to zero when idle
  maxReplicas: 100        # Hard cap for cost control
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30    # React quickly to demand
      policies:
        - type: Pods
          value: 10                     # Add up to 10 pods at once
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300   # Wait 5 min before scaling down
      policies:
        - type: Pods
          value: 5                      # Remove at most 5 pods at a time
          periodSeconds: 120
  metrics:
    # Primary: NATS consumer pending messages
    - type: External
      external:
        metric:
          name: nats_consumer_pending_messages
          selector:
            matchLabels:
              stream: "AGENT_TASKS"
        target:
          type: AverageValue
          averageValue: "3"    # Target 3 pending tasks per pod
    
    # Secondary: Active task count from Firestore
    - type: External
      external:
        metric:
          name: firestore_active_tasks
          selector:
            matchLabels:
              status: "assigned"
        target:
          type: Value
          value: "5"           # Scale up when >5 unstarted tasks
    
    # Safety: Memory utilization
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 75
```

## Scale-to-Zero with KEDA

Standard HPA cannot scale to zero replicas. We use KEDA (Kubernetes Event-Driven Autoscaling) to enable true scale-to-zero:

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: agent-marketing-scaler
  namespace: agents
spec:
  scaleTargetRef:
    name: agent-marketing
  minReplicaCount: 0                    # Zero when idle
  maxReplicaCount: 5                    # Max 5 concurrent marketing agents
  idleReplicaCount: 0                   # Scale to 0 after cooldown
  cooldownPeriod: 900                   # 15 min idle before zero
  pollingInterval: 10                   # Check every 10 seconds
  triggers:
    - type: nats-jetstream
      metadata:
        natsServerMonitoringEndpoint: "nats.genbrain.svc:8222"
        account: "$G"
        stream: "AGENT_TASKS"
        consumer: "marketing-agent-consumer"
        lagThreshold: "1"               # Scale up on any pending message
        activationLagThreshold: "1"     # Wake from zero on first message
```

When the marketing agent has no pending tasks, it scales to zero. The moment a task arrives in its NATS consumer, KEDA triggers scale-up. The cold start sequence:

```
Task arrives in NATS (t=0)
  |
  v
KEDA detects lag > threshold (t=10s, next poll)
  |
  v
Pod scheduled on node (t=12s)
  |
  v
Container pulls (cached) and starts (t=14s)
  |
  v
MCP servers initialize (t=16s)
  |
  v
Agent loads memory from Firestore (t=17s)
  |
  v
Agent connects to NATS consumer (t=18s)
  |
  v
Agent pulls and begins task (t=19s)
  |
Total cold start: ~19 seconds
```

Nineteen seconds is acceptable for most workloads. For urgent tasks requiring sub-second response, we maintain a warm pool (minimum 1 replica) for critical agent roles.

## Resource Management Per Agent

Each agent pod has tuned resource requests and limits based on its workload profile:

```yaml
# Resource profiles by agent type
profiles:
  lightweight:    # Agents doing text-only work (writing, planning)
    requests:
      cpu: "250m"
      memory: "512Mi"
    limits:
      cpu: "500m"
      memory: "1Gi"
  
  standard:       # Agents doing tool-heavy work (git, file ops)
    requests:
      cpu: "500m"
      memory: "1Gi"
    limits:
      cpu: "1000m"
      memory: "2Gi"
  
  compute:        # Agents running builds, tests, data processing
    requests:
      cpu: "1000m"
      memory: "2Gi"
    limits:
      cpu: "2000m"
      memory: "4Gi"
```

The resource profile is selected based on the agent's MCP configuration. An agent with only filesystem and git tools gets `standard`. An agent with browser automation and build tools gets `compute`.

## Multi-Tenant Scaling

In a SaaS platform, scaling must respect tenant boundaries. One organization's burst should not starve another's baseline:

```yaml
# ResourceQuota per organization namespace
apiVersion: v1
kind: ResourceQuota
metadata:
  name: org-abc123-quota
  namespace: org-abc123
spec:
  hard:
    pods: "20"                   # Max 20 concurrent agent pods
    requests.cpu: "10"           # Total CPU request limit
    requests.memory: "20Gi"      # Total memory request limit
    limits.cpu: "20"
    limits.memory: "40Gi"

---
# PriorityClass for different tiers
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: enterprise-agents
value: 1000
description: "Enterprise tier agents get scheduling priority"

---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: growth-agents
value: 500
description: "Growth tier agents, standard scheduling"

---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: starter-agents
value: 100
description: "Starter tier agents, best-effort scheduling"
```

When the cluster is under pressure, enterprise agents get scheduled first. Starter tier agents may queue briefly. This ensures paying customers get reliable performance.

## Burst Capacity

Some workloads are inherently bursty. A CEO agent might delegate 20 tasks simultaneously during morning planning. The system handles this through:

```
Normal Load:          Burst:                After Burst:
+----+               +----+----+----+      +----+
| A1 |               | A1 | A2 | A3 |      | A1 |
+----+               +----+----+----+      +----+
                     | A4 | A5 | A6 |
                     +----+----+----+      (scale down after
                     | A7 | A8 | A9 |       cooldown period)
                     +----+----+----+
                     |A10 |
                     +----+

1 pod                10 pods in ~30s        Back to 1 pod in 5min
```

The scaleUp policy allows adding 10 pods per minute with only a 30-second stabilization window. This aggressive scaling ensures burst workloads start quickly. The scaleDown policy is more conservative (5-minute stabilization, remove 5 at a time) to avoid thrashing.

## Node Pool Auto-Provisioning

Pods need nodes. GKE's node auto-provisioning ensures sufficient compute capacity:

```yaml
# GKE cluster autoscaler configuration
apiVersion: container.gke.io/v1
kind: NodePool
metadata:
  name: agent-nodes
spec:
  autoscaling:
    enabled: true
    minNodeCount: 1
    maxNodeCount: 25
  management:
    autoUpgrade: true
    autoRepair: true
  config:
    machineType: "e2-standard-4"    # 4 vCPU, 16GB RAM
    diskSizeGb: 50
    diskType: "pd-ssd"
    labels:
      workload: "ai-agents"
    taints:
      - key: "dedicated"
        value: "agents"
        effect: "NoSchedule"
```

Node taints ensure agent pods only schedule on dedicated agent nodes, preventing resource contention with other workloads. The cluster autoscaler adds nodes when pod scheduling pressure increases and removes them during idle periods.

## Cost Control Mechanisms

Scaling to 100 agents is technically straightforward. Controlling cost is the challenge. Our mechanisms:

### Token Budget Enforcement

```javascript
// Per-organization daily token budget
const orgBudget = {
  dailyTokenLimit: 5000000,      // 5M tokens/day
  currentUsage: 2340000,
  remainingBudget: 2660000,
  warningThreshold: 0.8,        // Alert at 80% usage
  hardCap: true                 // Stop agents at 100%
};

// Per-agent session limits
const sessionLimits = {
  maxTokensPerSession: 500000,   // Force compaction or session end
  maxSessionDuration: 14400,     // 4 hours max
  maxToolCallsPerTask: 200       // Prevent runaway tool loops
};
```

### Spot/Preemptible Instances

For non-urgent workloads, we use preemptible VMs at 60-80% cost reduction:

```yaml
apiVersion: container.gke.io/v1
kind: NodePool
metadata:
  name: agent-nodes-preemptible
spec:
  config:
    machineType: "e2-standard-4"
    preemptible: true
  autoscaling:
    enabled: true
    minNodeCount: 0
    maxNodeCount: 20
```

Agents on preemptible nodes save their state to Firestore on SIGTERM (30-second graceful shutdown). When a new pod starts, it resumes from the saved checkpoint. This pattern works because agents are designed to be interruptible. See [Agent Lifecycle Management](/blog/agent-lifecycle-management) for graceful shutdown details.

### Right-Sizing Through Metrics

```javascript
// Weekly right-sizing report
const agentMetrics = {
  "marketing": {
    avgCpuUsage: "15%",       // Over-provisioned
    avgMemoryUsage: "45%",    // Reasonable
    avgSessionLength: "42min",
    avgTasksPerSession: 3.2,
    recommendation: "Downsize to lightweight profile"
  },
  "devops": {
    avgCpuUsage: "68%",       // Well-utilized
    avgMemoryUsage: "72%",    // Near limit during builds
    avgSessionLength: "95min",
    avgTasksPerSession: 1.8,
    recommendation: "Keep compute profile, consider memory bump"
  }
};
```

For comprehensive cost strategies, see [Cost Optimization for AI Agents](/blog/cost-optimization-ai-agents).

## Observability at Scale

Monitoring 100 concurrent agents requires purpose-built observability:

```yaml
# Prometheus metrics exported by agent runtime
agent_tasks_total{role, status, priority}        # Task counters
agent_session_duration_seconds{role}             # Session length histogram
agent_tokens_consumed_total{role, model}         # Token usage
agent_tool_calls_total{role, tool, status}       # Tool usage
agent_context_utilization{role}                  # Context window fill %
agent_scale_events_total{direction, trigger}     # Scale up/down events
nats_consumer_pending{stream, consumer}          # Queue depth
```

These metrics power dashboards, alerts, and the autoscaler itself. The full observability setup is covered in [Monitoring Your AI Agent Fleet](/blog/monitoring-ai-agent-fleet).

## The Scaling Journey

Most organizations follow a predictable scaling path:

1. **1-3 agents**: Single founder, proof of concept. Manual task assignment. Minimal infrastructure.
2. **5-10 agents**: Small team. Delegation chains emerge. Need task management and coordination.
3. **10-30 agents**: Department-level autonomy. Need priority queues, SLAs, and resource quotas.
4. **30-100 agents**: Enterprise fleet. Need multi-tenant isolation, cost controls, and sophisticated scheduling.

agent.ceo's architecture handles all four stages without re-architecture. The same NATS subjects, Firestore schemas, and Kubernetes patterns work at every scale. You start with one agent and a $0 infrastructure bill (scale-to-zero). You grow to 100 agents with linear cost scaling and no configuration cliffs.

For getting started with your first agent, see [Getting Started with agent.ceo](/blog/getting-started-agent-ceo). For the Kubernetes deployment guide, see [Deploying AI Agents on Kubernetes](/blog/deploying-ai-agents-kubernetes).

> GenBrain AI is the company behind agent.ceo, building the next generation of autonomous agent orchestration.

## Try agent.ceo

**SaaS** — Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).

**Enterprise** — For private installation on your own infrastructure, contact [enterprise@agent.ceo](mailto:enterprise@agent.ceo).

---
*agent.ceo is built by [GenBrain AI](https://genbrain.ai) — a GenAI-first autonomous agent orchestration platform. General inquiries: hello@agent.ceo | Security: security@agent.ceo*
