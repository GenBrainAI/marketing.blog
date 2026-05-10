---
title: "Multi-Tenant Agent Orchestration"
slug: "multi-tenant-agent-orchestration"
date: 2026-05-10
category: technical
cluster: "platform-engineering"
tags: [multi-tenant, orchestration, kubernetes, namespaces, isolation, nats, ai-agents]
description: "Design patterns for multi-tenant AI agent orchestration with namespace isolation, NATS messaging, and secure credential management."
relatedPosts: [saas-platform-ai-agents, api-gateway-ai-agents, firebase-gke-ai-saas]
---

# Multi-Tenant Agent Orchestration

Running AI agents for a single team is straightforward. Running agents for hundreds of organizations simultaneously — each with their own credentials, data, and compliance requirements — demands a fundamentally different approach. Multi-tenant agent orchestration is the backbone of any agent-as-a-service platform. This post details how agent.ceo isolates, schedules, and manages agents across tenant boundaries.

## Tenancy Model: Namespace-Per-Organization

We chose namespace-per-organization as our isolation boundary. Each organization gets a dedicated Kubernetes namespace with its own service accounts, network policies, resource quotas, and secrets. This provides stronger isolation than label-based soft tenancy while remaining more operationally manageable than cluster-per-tenant.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: org-acme-corp
  labels:
    tenant: acme-corp
    tier: standard
    managed-by: agent-ceo-platform
  annotations:
    agent-ceo/org-id: "org_abc123"
    agent-ceo/plan: "standard"
    agent-ceo/agent-limit: "10"
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-quota
  namespace: org-acme-corp
spec:
  hard:
    requests.cpu: "10"
    requests.memory: "40Gi"
    limits.cpu: "20"
    limits.memory: "80Gi"
    persistentvolumeclaims: "20"
    pods: "15"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: agent-limits
  namespace: org-acme-corp
spec:
  limits:
    - type: Container
      default:
        cpu: "2000m"
        memory: "8Gi"
      defaultRequest:
        cpu: "500m"
        memory: "2Gi"
      max:
        cpu: "4000m"
        memory: "16Gi"
```

Resource quotas prevent a single tenant from consuming unbounded cluster resources. The limit range ensures individual agent containers stay within reasonable bounds while allowing burst capacity during intensive tasks.

## NATS Subject Isolation

Inter-agent messaging uses NATS with subject-based isolation. Each organization's agents communicate on scoped subjects, and NATS authorization prevents cross-tenant message access:

```javascript
// NATS authorization configuration
const natsConfig = {
  authorization: {
    users: [
      {
        user: "org-acme-corp",
        password: "$ENCRYPTED",
        permissions: {
          publish: {
            allow: [
              "org.acme-corp.>",           // All org-scoped subjects
              "platform.agents.status"      // Platform-wide status reports
            ]
          },
          subscribe: {
            allow: [
              "org.acme-corp.>",           // Own org messages
              "platform.broadcast.>"        // Platform announcements
            ],
            deny: [
              "org.*.internal.>"           // Block other orgs' internal
            ]
          }
        }
      }
    ]
  }
};
```

Within each organization's subject space, agents communicate through well-defined patterns:

```typescript
import { connect, StringCodec } from 'nats';

const nc = await connect({
  servers: process.env.NATS_URL,
  user: process.env.NATS_USER,
  pass: process.env.NATS_PASS
});

const sc = StringCodec();
const orgId = process.env.ORG_ID;

// Task delegation pattern
interface TaskMessage {
  taskId: string;
  fromAgent: string;
  toAgent: string;
  type: 'delegate' | 'complete' | 'blocked';
  payload: Record<string, unknown>;
}

// Manager agent delegates to worker
async function delegateTask(task: TaskMessage): Promise<void> {
  nc.publish(
    `org.${orgId}.tasks.${task.toAgent}.inbox`,
    sc.encode(JSON.stringify(task))
  );
}

// Worker agent subscribes to its inbox
const sub = nc.subscribe(`org.${orgId}.tasks.${agentId}.inbox`);
for await (const msg of sub) {
  const task: TaskMessage = JSON.parse(sc.decode(msg.data));
  await processTask(task);
}

// Cross-agent status updates
nc.publish(
  `org.${orgId}.agents.${agentId}.status`,
  sc.encode(JSON.stringify({
    status: 'working',
    currentTask: taskId,
    progress: 0.45
  }))
);
```

For deeper coverage of NATS authentication patterns, see our post on [NATS auth hardening](/blog/nats-auth-hardening) and the broader [event-driven architecture with NATS](/blog/event-driven-nats-ai).

## Orchestration Controller

The orchestration controller is a platform-level service that manages agent lifecycle across all tenants. It watches for task assignments, provisions agents on demand, and handles scaling decisions:

```typescript
import { KubeConfig, AppsV1Api, CoreV1Api } from '@kubernetes/client-node';
import { getFirestore } from 'firebase-admin/firestore';

const kc = new KubeConfig();
kc.loadFromCluster();
const k8sCore = kc.makeApiClient(CoreV1Api);
const db = getFirestore();

class OrchestrationController {
  /**
   * Provision an agent for a specific organization.
   * Handles namespace validation, quota checks, and pod creation.
   */
  async provisionAgent(orgId: string, agentSpec: AgentSpec): Promise<string> {
    const namespace = `org-${orgId}`;

    // Verify namespace exists and has capacity
    const quota = await k8sCore.readNamespacedResourceQuota('tenant-quota', namespace);
    const usedPods = parseInt(quota.body.status.used['pods'] || '0');
    const maxPods = parseInt(quota.body.status.hard['pods'] || '10');

    if (usedPods >= maxPods) {
      throw new Error(`Organization ${orgId} has reached pod limit (${maxPods})`);
    }

    // Generate unique agent identity
    const agentId = `agent-${orgId}-${agentSpec.name}-${randomSuffix()}`;

    // Create workspace PVC
    await k8sCore.createNamespacedPersistentVolumeClaim(namespace, {
      metadata: { name: `workspace-${agentId}` },
      spec: {
        accessModes: ['ReadWriteOnce'],
        resources: { requests: { storage: '10Gi' } },
        storageClassName: 'standard-rwo'
      }
    });

    // Deploy agent pod
    await k8sCore.createNamespacedPod(namespace, buildAgentPod(agentId, orgId, agentSpec));

    // Register in Firestore
    await db.doc(`organizations/${orgId}/agents/${agentId}`).set({
      name: agentSpec.name,
      role: agentSpec.role,
      status: 'provisioning',
      namespace,
      createdAt: FieldValue.serverTimestamp()
    });

    return agentId;
  }

  /**
   * Scale-to-zero: pause idle agents to reduce costs.
   * Preserves workspace PVC for fast resume.
   */
  async pauseAgent(orgId: string, agentId: string): Promise<void> {
    const namespace = `org-${orgId}`;

    // Save agent state before termination
    await this.saveAgentCheckpoint(orgId, agentId);

    // Delete pod but keep PVC
    await k8sCore.deleteNamespacedPod(agentId, namespace);

    // Update status
    await db.doc(`organizations/${orgId}/agents/${agentId}`).update({
      status: 'paused',
      pausedAt: FieldValue.serverTimestamp()
    });
  }

  /**
   * Resume a paused agent — recreate pod with existing workspace.
   */
  async resumeAgent(orgId: string, agentId: string): Promise<void> {
    const agentDoc = await db.doc(`organizations/${orgId}/agents/${agentId}`).get();
    const agentData = agentDoc.data();

    // Recreate pod with same workspace PVC
    await k8sCore.createNamespacedPod(
      `org-${orgId}`,
      buildAgentPod(agentId, orgId, agentData)
    );

    await agentDoc.ref.update({
      status: 'running',
      resumedAt: FieldValue.serverTimestamp()
    });
  }
}
```

## Credential Isolation

Each organization's credentials are stored as Kubernetes secrets within their namespace. Agents can only access secrets in their own namespace through the service account binding:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: agent-secret-reader
  namespace: org-acme-corp
rules:
  - apiGroups: [""]
    resources: ["secrets"]
    verbs: ["get"]
    resourceNames:
      - github-token
      - slack-webhook
      - agent-ssh-*
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: agent-secret-binding
  namespace: org-acme-corp
subjects:
  - kind: ServiceAccount
    name: agent-worker-sa
    namespace: org-acme-corp
roleRef:
  kind: Role
  name: agent-secret-reader
  apiGroup: rbac.authorization.k8s.io
```

This ensures that even if an agent is compromised, it cannot access credentials from other organizations. For comprehensive coverage of credential management patterns, see [credential management in multi-cloud environments](/blog/credential-management-multi-cloud).

## Task Scheduling and Priority

Not all agent tasks are equal. We implement priority-based scheduling that respects tenant SLAs:

```typescript
interface ScheduledTask {
  id: string;
  orgId: string;
  agentId: string;
  priority: 'critical' | 'high' | 'normal' | 'low';
  deadline?: Date;
  requirements: {
    cpu: string;
    memory: string;
    gpu?: boolean;
  };
}

class TaskScheduler {
  private queue: PriorityQueue<ScheduledTask>;

  async scheduleTask(task: ScheduledTask): Promise<void> {
    // Calculate effective priority based on plan tier
    const org = await db.doc(`organizations/${task.orgId}`).get();
    const planBoost = org.data().plan === 'enterprise' ? 2 : 
                      org.data().plan === 'standard' ? 1 : 0;

    const effectivePriority = this.calculatePriority(task, planBoost);
    this.queue.enqueue(task, effectivePriority);

    // Attempt immediate scheduling
    await this.trySchedule();
  }

  private async trySchedule(): Promise<void> {
    while (!this.queue.isEmpty()) {
      const task = this.queue.peek();
      const agent = await this.findOrProvisionAgent(task);

      if (agent) {
        this.queue.dequeue();
        await this.dispatchToAgent(agent, task);
      } else {
        break; // No capacity available
      }
    }
  }
}
```

## Monitoring Cross-Tenant Health

The platform operator needs visibility across all tenants without violating isolation. We achieve this by aggregating metrics at the namespace level:

```promql
# Total running agents per organization
sum by (namespace) (
  kube_pod_status_phase{phase="Running", namespace=~"org-.*"}
)

# Resource utilization by tenant tier
sum by (label_tier) (
  container_cpu_usage_seconds_total{namespace=~"org-.*"}
) / sum by (label_tier) (
  kube_pod_container_resource_requests{resource="cpu", namespace=~"org-.*"}
)
```

For a complete observability setup, see our guide on [real-time agent monitoring](/blog/real-time-agent-monitoring) and the [monitoring your AI agent fleet](/blog/monitoring-ai-agent-fleet) tutorial.

## Anti-Patterns to Avoid

Through building and operating multi-tenant agent infrastructure, we identified several anti-patterns:

**Shared message buses without subject isolation.** Agents must never see messages from other organizations. NATS subject-based auth is necessary but not sufficient — you also need server-side filtering.

**Flat credential stores.** Storing all org credentials in a single secret namespace and filtering by label is fragile. One misconfigured RBAC rule exposes everything. Per-namespace secrets are the only safe approach.

**Synchronous orchestration.** Never block on agent responses in the orchestration layer. Agents are non-deterministic and may take minutes or hours to complete tasks. The entire orchestration layer must be event-driven and async.

Multi-tenant agent orchestration is where [platform engineering meets AI](/blog/what-are-ai-agents). Getting the isolation boundaries right early prevents costly re-architecture as you scale from your first customer to your hundredth.

## Try agent.ceo

Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).
