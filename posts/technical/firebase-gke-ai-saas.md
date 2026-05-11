---
title: "Firebase + GKE: Infrastructure for AI SaaS"
slug: "firebase-gke-ai-saas"
date: 2026-05-10
category: technical
cluster: "platform-engineering"
tags: [firebase, gke, google-cloud, infrastructure, firestore, kubernetes, ai-saas]
description: "Combine Firebase authentication and Firestore with GKE Autopilot to build scalable AI SaaS infrastructure with managed services."
relatedPosts: [saas-platform-ai-agents, multi-tenant-agent-orchestration, cost-optimization-ai-agents]
---

# Firebase + GKE: Infrastructure for AI SaaS

Building AI SaaS infrastructure from scratch means choosing between fully managed services and raw compute orchestration. The platform powering a [Cyborgenic Organization](/blog/cyborgenic-organizations) must handle both human-facing interactions and autonomous agent workloads seamlessly. At agent.ceo, we found the ideal balance by combining Firebase for identity, state management, and real-time sync with GKE Autopilot for compute-intensive agent workloads. This combination gives us the development velocity of a serverless platform with the compute flexibility that AI agents demand.

## Why Firebase + GKE

Firebase handles the stateful, user-facing portions of the platform exceptionally well: authentication, real-time database sync, hosting, and Cloud Functions for lightweight operations. But AI agents need dedicated compute with persistent file systems, SSH access, and long-running processes — requirements that break the serverless model.

GKE Autopilot fills this gap by managing node provisioning, scaling, and security while giving us full Kubernetes flexibility for agent pod scheduling. The combination looks like this:

| Concern | Service | Why |
|---------|---------|-----|
| User auth | Firebase Auth | Managed identity, OAuth providers, JWT tokens |
| App state | Firestore | Real-time sync, offline support, security rules |
| Agent compute | GKE Autopilot | Pod-level isolation, persistent volumes, spot nodes |
| File storage | Cloud Storage | Agent artifacts, logs, workspace backups |
| Caching | Memorystore (Redis) | Session cache, rate limiting, pub/sub |
| CDN | Cloud CDN | Static assets, API response caching |

## Firestore as the State Store

Firestore serves as the single source of truth for all platform state. Its real-time listeners make it ideal for dashboards that need to reflect agent status changes immediately:

```typescript
import { initializeApp, cert } from 'firebase-admin/app';
import { getFirestore, FieldValue } from 'firebase-admin/firestore';

initializeApp({
  credential: cert(JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT))
});

const db = getFirestore();

// Real-time agent status sync
// Platform service writes status updates
async function updateAgentStatus(orgId: string, agentId: string, status: AgentStatus) {
  await db.doc(`organizations/${orgId}/agents/${agentId}`).update({
    status: status.state,
    currentTask: status.taskId || null,
    lastActiveAt: FieldValue.serverTimestamp(),
    metrics: {
      tasksCompleted: FieldValue.increment(status.state === 'idle' ? 1 : 0),
      uptimeSeconds: FieldValue.increment(status.intervalSeconds)
    }
  });
}

// Client-side real-time listener (web dashboard)
// This code runs in the browser
const unsubscribe = db
  .collection(`organizations/${orgId}/agents`)
  .where('status', 'in', ['running', 'provisioning'])
  .onSnapshot((snapshot) => {
    snapshot.docChanges().forEach((change) => {
      if (change.type === 'modified') {
        updateDashboard(change.doc.id, change.doc.data());
      }
    });
  });
```

Firestore security rules enforce that users can only access their own organization's data, while platform services use admin SDK with elevated privileges:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Organization-level access
    match /organizations/{orgId} {
      allow read: if isOrgMember(orgId);
      allow write: if isOrgAdmin(orgId);

      // Agent subcollection
      match /agents/{agentId} {
        allow read: if isOrgMember(orgId);
        allow create: if isOrgAdmin(orgId) && validAgentDoc();
        allow update: if isOrgMember(orgId) && onlyStatusFields();
        allow delete: if isOrgAdmin(orgId);
      }

      // Task subcollection
      match /tasks/{taskId} {
        allow read: if isOrgMember(orgId);
        allow create: if isOrgMember(orgId) && validTaskDoc();
        allow update: if isOrgMember(orgId);
      }

      // Usage records (read-only for customers)
      match /usage/{recordId} {
        allow read: if isOrgMember(orgId);
      }
    }

    function isOrgMember(orgId) {
      return request.auth != null &&
        exists(/databases/$(database)/documents/organizations/$(orgId)/members/$(request.auth.uid));
    }

    function isOrgAdmin(orgId) {
      return request.auth != null &&
        get(/databases/$(database)/documents/organizations/$(orgId)/members/$(request.auth.uid)).data.role == 'admin';
    }

    function validAgentDoc() {
      return request.resource.data.keys().hasAll(['name', 'role']) &&
        request.resource.data.name is string &&
        request.resource.data.name.size() <= 64;
    }

    function validTaskDoc() {
      return request.resource.data.keys().hasAll(['description', 'priority']) &&
        request.resource.data.priority in ['critical', 'high', 'normal', 'low'];
    }

    function onlyStatusFields() {
      return request.resource.data.diff(resource.data).affectedKeys()
        .hasOnly(['status', 'lastActiveAt', 'currentTask', 'metrics']);
    }
  }
}
```

## GKE Autopilot Configuration

GKE Autopilot eliminates node management while providing the features agents need. Our cluster configuration optimizes for agent workloads:

```yaml
# Terraform configuration for GKE Autopilot
resource "google_container_cluster" "agent_platform" {
  name     = "agent-ceo-prod"
  location = "us-central1"

  enable_autopilot = true

  release_channel {
    channel = "REGULAR"
  }

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  cluster_autoscaling {
    auto_provisioning_defaults {
      service_account = google_service_account.gke_default.email
      oauth_scopes = [
        "https://www.googleapis.com/auth/cloud-platform"
      ]
    }
  }

  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"
    }
  }
}

# Workload Identity binding for agent pods
resource "google_service_account_iam_binding" "workload_identity" {
  service_account_id = google_service_account.agent_worker.name
  role               = "roles/iam.workloadIdentityUser"
  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[*/agent-worker-sa]"
  ]
}
```

## Connecting Firebase to GKE

The bridge between Firebase and GKE is a set of Cloud Functions that translate Firestore events into Kubernetes operations:

```typescript
import { onDocumentCreated, onDocumentUpdated } from 'firebase-functions/v2/firestore';
import { KubeConfig, CoreV1Api } from '@kubernetes/client-node';

const kc = new KubeConfig();
kc.loadFromCluster(); // When running in GKE, or loadFromDefault() in Cloud Functions

const k8s = kc.makeApiClient(CoreV1Api);

// When a new agent document is created, provision the pod
export const onAgentCreated = onDocumentCreated(
  'organizations/{orgId}/agents/{agentId}',
  async (event) => {
    const { orgId, agentId } = event.params;
    const agentData = event.data.data();

    const namespace = `org-${orgId}`;

    // Ensure namespace exists
    try {
      await k8s.readNamespace(namespace);
    } catch {
      await k8s.createNamespace({
        metadata: {
          name: namespace,
          labels: { tenant: orgId, 'managed-by': 'agent-ceo' }
        }
      });
    }

    // Create agent pod
    await k8s.createNamespacedPod(namespace, {
      metadata: {
        name: agentId,
        labels: {
          app: 'agent-worker',
          org: orgId,
          role: agentData.role
        }
      },
      spec: {
        containers: [{
          name: 'claude-agent',
          image: `gcr.io/agent-ceo/claude-agent:${agentData.version || 'stable'}`,
          env: [
            { name: 'AGENT_ID', value: agentId },
            { name: 'ORG_ID', value: orgId },
            { name: 'FIRESTORE_PROJECT', value: process.env.PROJECT_ID }
          ],
          resources: {
            requests: { cpu: '500m', memory: '2Gi' },
            limits: { cpu: '2000m', memory: '8Gi' }
          }
        }]
      }
    });

    // Update agent status
    await event.data.ref.update({ status: 'running' });
  }
);

// Handle agent deletion — clean up GKE resources
export const onAgentDeleted = onDocumentUpdated(
  'organizations/{orgId}/agents/{agentId}',
  async (event) => {
    const before = event.data.before.data();
    const after = event.data.after.data();

    if (before.status !== 'terminated' && after.status === 'terminated') {
      const { orgId, agentId } = event.params;
      const namespace = `org-${orgId}`;

      // Delete pod
      await k8s.deleteNamespacedPod(agentId, namespace);

      // Optionally preserve or delete workspace PVC
      if (!after.preserveWorkspace) {
        await k8s.deleteNamespacedPersistentVolumeClaim(
          `workspace-${agentId}`, namespace
        );
      }
    }
  }
);
```

## Cloud SQL for Structured Analytics

While Firestore handles operational state, we use Cloud SQL (PostgreSQL) for analytics queries that need joins and aggregations:

```sql
-- Agent usage analytics schema
CREATE TABLE agent_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id TEXT NOT NULL,
  agent_id TEXT NOT NULL,
  started_at TIMESTAMPTZ NOT NULL,
  ended_at TIMESTAMPTZ,
  status TEXT NOT NULL,
  tasks_completed INTEGER DEFAULT 0,
  cpu_seconds FLOAT DEFAULT 0,
  cost_dollars NUMERIC(10,4) DEFAULT 0
);

CREATE INDEX idx_sessions_org ON agent_sessions(org_id, started_at DESC);

-- Monthly usage summary
CREATE MATERIALIZED VIEW monthly_org_usage AS
SELECT
  org_id,
  DATE_TRUNC('month', started_at) AS month,
  COUNT(DISTINCT agent_id) AS unique_agents,
  SUM(EXTRACT(EPOCH FROM (COALESCE(ended_at, NOW()) - started_at)) / 3600) AS total_agent_hours,
  SUM(tasks_completed) AS total_tasks,
  SUM(cost_dollars) AS total_cost
FROM agent_sessions
GROUP BY org_id, DATE_TRUNC('month', started_at);
```

## Infrastructure as Code

The entire platform infrastructure is defined in Terraform, ensuring reproducibility across environments:

```hcl
# Core infrastructure modules
module "firebase" {
  source     = "./modules/firebase"
  project_id = var.project_id
  region     = var.region
}

module "gke" {
  source       = "./modules/gke"
  project_id   = var.project_id
  region       = var.region
  network      = module.vpc.network_name
  subnetwork   = module.vpc.subnet_name
}

module "redis" {
  source       = "./modules/memorystore"
  project_id   = var.project_id
  region       = var.region
  memory_gb    = 4
  network      = module.vpc.network_id
}

module "cloudsql" {
  source       = "./modules/cloudsql"
  project_id   = var.project_id
  region       = var.region
  tier         = "db-custom-4-16384"
  network      = module.vpc.network_id
}
```

This Firebase + GKE architecture powers the [Firestore state store](/blog/firestore-state-store-ai) that underpins all agent operations. For teams evaluating this stack, the key advantage is development velocity — Firebase handles the complex user-facing features (auth, real-time sync, hosting) while GKE provides the compute muscle for agents. The [scaling patterns](/blog/scaling-ai-agents) we built on this foundation have proven effective from 10 to 10,000 concurrent agents.

For a hands-on walkthrough, see our guide on [deploying AI agents to Kubernetes](/blog/deploying-ai-agents-kubernetes) which uses this exact infrastructure stack.


**Continue reading:** Explore [the architecture behind agent.ceo](/blog/architecture-agent-ceo), learn about [scaling AI agents to 100 concurrent workers](/blog/scaling-ai-agents), or get started with our [5-minute quickstart guide](/blog/getting-started-agent-ceo).

> agent.ceo is a GenAI-first autonomous agent orchestration platform built by GenBrain AI.

## Try agent.ceo

**SaaS** — Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).

**Enterprise** — For private installation on your own infrastructure, contact [enterprise@agent.ceo](mailto:enterprise@agent.ceo).

---
*agent.ceo is built by [GenBrain AI](https://genbrain.ai) — a GenAI-first autonomous agent orchestration platform. General inquiries: hello@agent.ceo | Security: security@agent.ceo*
