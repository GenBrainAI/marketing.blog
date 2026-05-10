---
title: "Deploying AI Agents to Kubernetes"
slug: "deploying-ai-agents-kubernetes"
date: 2026-05-10
category: technical
cluster: "getting-started"
tags: [kubernetes, deployment, infrastructure, containers, k8s, tutorial]
description: "Deploy autonomous AI agents to Kubernetes clusters. Learn pod configuration, resource limits, networking, and scaling for production agent workloads."
relatedPosts: [getting-started-agent-ceo, first-ai-agent-team, monitoring-ai-agent-fleet]
---

# Deploying AI Agents to Kubernetes

Every AI agent on agent.ceo runs in its own Kubernetes pod, giving it an isolated development environment with full access to Claude Code CLI. This guide explains how agents are deployed to Kubernetes, how to configure resource allocation, and how to manage agent workloads at scale.

Whether you are running on GKE, EKS, or AKS, this tutorial covers everything you need to know about the infrastructure powering your autonomous agent fleet.

## How agent.ceo Uses Kubernetes

Each agent operates as an independent pod with:

- **Its own filesystem**: Agents clone repos and work in isolation
- **Claude Code CLI**: The AI runtime that powers agent reasoning and actions
- **Tool access**: Configured integrations mounted as environment variables
- **Network policies**: Controlled access to external services
- **Resource limits**: CPU and memory boundaries to control costs

This architecture ensures agents cannot interfere with each other and provides the security isolation needed for production workloads. Learn more in our [architecture overview](/blog/architecture-agent-ceo).

## Prerequisites

To follow this guide, you need:

- An agent.ceo account with a connected team (see [Getting Started](/blog/getting-started-agent-ceo))
- Basic familiarity with Kubernetes concepts (pods, deployments, services)
- Access to your Kubernetes cluster (for custom configurations)

Note: agent.ceo manages the Kubernetes infrastructure for you by default. This guide is for teams that want to understand or customize the deployment.

## Step 1: Understand the Default Deployment

When you deploy an agent through the dashboard, agent.ceo automatically creates a Kubernetes deployment:

```yaml
# Auto-generated agent deployment (simplified)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-code-reviewer
  namespace: agentceo-agents
  labels:
    app: agent-ceo
    agent-role: code-reviewer
    team: core-engineering
spec:
  replicas: 1
  selector:
    matchLabels:
      agent-id: agent-code-reviewer
  template:
    metadata:
      labels:
        agent-id: agent-code-reviewer
        agent-role: code-reviewer
    spec:
      containers:
        - name: agent-runtime
          image: agentceo/agent-runtime:latest
          resources:
            requests:
              cpu: "500m"
              memory: "2Gi"
            limits:
              cpu: "2000m"
              memory: "8Gi"
          env:
            - name: AGENT_ROLE
              value: "code-reviewer"
            - name: AGENT_TEAM
              value: "core-engineering"
            - name: GITHUB_TOKEN
              valueFrom:
                secretRef:
                  name: agent-github-token
          volumeMounts:
            - name: agent-workspace
              mountPath: /workspace
            - name: agent-config
              mountPath: /etc/agent
      volumes:
        - name: agent-workspace
          emptyDir:
            sizeLimit: 20Gi
        - name: agent-config
          configMap:
            name: agent-code-reviewer-config
```

[Screenshot: Kubernetes dashboard showing agent pods running in the agentceo-agents namespace]

## Step 2: Configure Resource Limits

Different agent roles require different resources. A code review agent needs less memory than one that runs full test suites. Configure resources based on workload:

```yaml
# Resource profiles for different agent types
resource_profiles:
  code-reviewer:
    cpu_request: "500m"
    cpu_limit: "2000m"
    memory_request: "2Gi"
    memory_limit: "8Gi"
    storage: "10Gi"

  security-analyst:
    cpu_request: "1000m"
    cpu_limit: "4000m"
    memory_request: "4Gi"
    memory_limit: "16Gi"
    storage: "30Gi"

  devops-engineer:
    cpu_request: "500m"
    cpu_limit: "2000m"
    memory_request: "2Gi"
    memory_limit: "8Gi"
    storage: "20Gi"

  backend-developer:
    cpu_request: "1000m"
    cpu_limit: "4000m"
    memory_request: "4Gi"
    memory_limit: "16Gi"
    storage: "50Gi"
```

Apply custom resource profiles through the CLI:

```bash
# Set resource profile for an agent
agentceo agent configure CodeReviewer \
  --cpu-limit 2000m \
  --memory-limit 8Gi \
  --storage-limit 10Gi
```

## Step 3: Set Up Namespace Isolation

For security, agent.ceo deploys agents in isolated namespaces with network policies:

```yaml
# Network policy restricting agent communication
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: agent-network-policy
  namespace: agentceo-agents
spec:
  podSelector:
    matchLabels:
      app: agent-ceo
  policyTypes:
    - Ingress
    - Egress
  egress:
    # Allow access to GitHub API
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0
      ports:
        - protocol: TCP
          port: 443
    # Allow DNS resolution
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
  ingress:
    # Only allow traffic from agent.ceo control plane
    - from:
        - namespaceSelector:
            matchLabels:
              app: agent-ceo-control-plane
```

This ensures agents can only communicate with approved external services (GitHub, Slack, etc.) and cannot access other services in your cluster.

## Step 4: Configure Persistent Storage

By default, agent workspaces use ephemeral storage (emptyDir). For agents that need to persist state between restarts, configure persistent volumes:

```yaml
# Persistent volume claim for agent workspace
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: agent-workspace-pvc
  namespace: agentceo-agents
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: ssd
```

```bash
# Enable persistent storage for an agent
agentceo agent configure BackendDev \
  --persistent-storage true \
  --storage-class ssd \
  --storage-size 50Gi
```

Persistent storage is recommended for agents that:
- Work with large repositories (monorepos)
- Build Docker images
- Run integration test suites
- Cache dependency installations

## Step 5: Configure Auto-Scaling

For teams with variable workloads, configure horizontal pod autoscaling:

```yaml
# HPA for agent workloads
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: code-reviewer-hpa
  namespace: agentceo-agents
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: agent-code-reviewer
  minReplicas: 1
  maxReplicas: 5
  metrics:
    - type: External
      external:
        metric:
          name: agent_queue_depth
          selector:
            matchLabels:
              agent-role: code-reviewer
        target:
          type: AverageValue
          averageValue: "3"
```

```bash
# Enable auto-scaling through the CLI
agentceo agent scale CodeReviewer \
  --min-replicas 1 \
  --max-replicas 5 \
  --scale-metric queue-depth \
  --scale-threshold 3
```

This scales your code review agent from 1 to 5 replicas when the PR queue grows, ensuring fast response times during busy periods.

[Screenshot: Grafana dashboard showing agent pod count scaling from 1 to 3 during a PR surge]

## Step 6: Set Up Health Checks

Agent pods include health checks to ensure reliability:

```yaml
# Health check configuration
livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 2

startupProbe:
  httpGet:
    path: /health/startup
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 30
```

If an agent becomes unresponsive, Kubernetes automatically restarts the pod. The agent resumes work from its last checkpoint, ensuring no tasks are lost.

## Step 7: Deploy to Your Own Cluster (Self-Hosted)

For organizations that require agents to run in their own infrastructure, agent.ceo supports self-hosted deployment:

```bash
# Install the agent.ceo operator in your cluster
kubectl apply -f https://agent.ceo/install/operator.yaml

# Configure the operator with your agent.ceo API key
kubectl create secret generic agentceo-api-key \
  --namespace agentceo-system \
  --from-literal=api-key=your-api-key-here

# Deploy agents to your cluster
agentceo cluster register \
  --name production-cluster \
  --kubeconfig ~/.kube/config \
  --context my-gke-cluster
```

[Screenshot: Terminal output showing successful operator installation and cluster registration]

Self-hosted deployments support GKE, EKS, AKS, and any conformant Kubernetes cluster running version 1.26 or higher.

## Step 8: Monitor Deployment Health

After deploying, verify your agents are running correctly:

```bash
# Check all agent pods
kubectl get pods -n agentceo-agents -l app=agent-ceo

# View agent logs
kubectl logs -n agentceo-agents -l agent-role=code-reviewer --tail=50

# Check resource usage
kubectl top pods -n agentceo-agents

# View events for troubleshooting
kubectl get events -n agentceo-agents --sort-by='.lastTimestamp'
```

For ongoing monitoring, integrate with your existing observability stack. See our [monitoring guide](/blog/monitoring-ai-agent-fleet) for detailed instructions.

## Production Deployment Checklist

Before deploying agents to production, verify:

- [ ] Resource limits are set appropriately for each agent role
- [ ] Network policies restrict agent access to approved services only
- [ ] Secrets are stored in Kubernetes secrets or an external vault
- [ ] Health checks are configured and tested
- [ ] Auto-scaling thresholds are set based on expected workload
- [ ] Logging and monitoring are connected to your observability stack
- [ ] Backup and recovery procedures are documented
- [ ] Cost alerts are configured for unexpected scaling events

## Cost Considerations

Agent pods consume cluster resources. Estimate costs based on:

- **CPU**: Most agents need 0.5-2 vCPU sustained, with bursts to 4 vCPU
- **Memory**: 2-16 GB depending on workload (large repos need more)
- **Storage**: 10-50 GB per agent for workspace and caches
- **Network**: Minimal for API calls; more for cloning large repos

Use [spot/preemptible instances](/blog/cost-optimization-ai-agents) for non-critical agents to reduce costs by 60-80%.

## Try agent.ceo

Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).
