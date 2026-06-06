---
title: "Tutorial: In-Cluster Deploys via Cloud Build — Ship Without GitHub Actions"
slug: "in-cluster-deploy-cloud-build-api-gke"
date: 2026-11-05
category: technical
cluster: tutorials
tags: [cloud-build, deploy, gke, kubernetes, ci-cd, tutorial]
description: "Step-by-step tutorial for building an in-cluster deploy pipeline that uses the Cloud Build API to build images and kubectl to roll them out — no GitHub Actions, no external CI, no human in the loop."
relatedPosts:
  - /blog/double-roll-deploy-downtime-sidecar-convergence
  - /blog/fsgroup-change-policy-onrootmismatch-redeploy-outage
  - /blog/image-pinning-latest-tag-customer-agent-drift
  - /blog/zero-downtime-deployments-ai-agent-fleets
  - /blog/outer-loop-shell-script-keeps-agents-alive
---

# Tutorial: In-Cluster Deploys via Cloud Build — Ship Without GitHub Actions

Your AI agents live inside GKE. Your build pipeline lives outside it — on GitHub Actions, or CircleCI, or whatever hosted CI you adopted before you had agents. Every deploy is a round-trip: push code out, wait for external CI to build it, pull the image back in, roll it out. That round-trip costs minutes, money, and a dependency your agents cannot control — a real drag on a cyborgenic organization where the agents do the shipping.

This tutorial walks through the two-script pipeline we built at GenBrain AI to eliminate that round-trip. One Python script submits builds to the Cloud Build API. One Bash script orchestrates the full cycle: build, deploy, rollback, status. An agent ships a fix with a single command and never leaves the cluster.

## Prerequisites

- GKE cluster with workload identity (or a service account) that has Cloud Build and GCS access
- Artifact Registry configured (e.g. `us-central1-docker.pkg.dev/{project}/{repo}`)
- `kubectl` access from inside the cluster (standard for pods with appropriate RBAC)
- Python 3.9+ with `google-cloud-build` and `google-cloud-storage` client libraries
- Dockerfiles for each component you want to build

## Step 1: The Build Submitter — `cluster_build.py`

The Python script does three things: package the source, upload it to GCS, and submit a Cloud Build job. It does not know about Kubernetes, deployments, or rollouts. Its only job is to produce a built image URI.

```python
# cluster_build.py — submit a build to Cloud Build API

def submit_build(component, project_id, repo_root):
    # 1. Package the source into a tarball
    context_tar = create_build_context(repo_root, component)

    # 2. Upload the tarball to a GCS staging bucket
    gcs_path = upload_to_gcs(context_tar, project_id)

    # 3. Submit the build to Cloud Build
    build = cloud_build_client.create_build(
        project_id=project_id,
        build={
            "source": {
                "storage_source": {
                    "bucket": staging_bucket,
                    "object": gcs_path,
                }
            },
            "steps": [{
                "name": "gcr.io/cloud-builders/docker",
                "args": ["build", "-t", image_tag, "."],
            }],
            "images": [image_tag],
        },
    )

    # 4. Poll for completion
    result = wait_for_build(build)
    return result.images[0]  # e.g. us-central1-docker.pkg.dev/agent-hub-ceo/agent-hub/gateway:sha-abc123
```

The tarball goes to GCS, not to Cloud Build directly. Cloud Build pulls the source from the bucket — you upload once, Cloud Build reads it, and the GCS object serves as an audit trail. The script polls for completion rather than using a callback. Inside a cluster, polling is simpler than setting up a webhook endpoint.

## Step 2: The Orchestrator — `cluster-deploy.sh`

The Bash script is the interface agents actually use. It handles git sync, dependency resolution, build invocation, deployment, rollback, and status checks.

### Basic Usage

```bash
scripts/cluster-deploy.sh gateway          # build + deploy the gateway
scripts/cluster-deploy.sh agent            # build agent-base + agent, deploy to all agent pods
scripts/cluster-deploy.sh worker           # build agent-base + worker
scripts/cluster-deploy.sh rollback gateway # rollback gateway to previous revision
scripts/cluster-deploy.sh status gateway   # check rollout status
```

One command, one argument. The agent does not need to know which Dockerfile to use, which registry to push to, or which deployments to update.

### Git Sync

The first thing the script does is sync to the latest code:

```bash
git fetch origin main
git checkout origin/main -- .
```

This ensures the build always uses the latest merged code, not whatever the agent has checked out locally. Agents work on branches. Deploys ship from main.

### Dependency Resolution

Not every component is independent. The agent image depends on `agent-base`. So does the worker image. And the fullstack image. If you rebuild `agent` without first rebuilding `agent-base`, you get a stale foundation.

The script encodes these dependencies:

```bash
# When building 'agent', 'worker', or 'fullstack',
# build agent-base first
if [[ "$component" =~ ^(agent|worker|fullstack)$ ]]; then
    echo "Building dependency: agent-base"
    python3 cluster_build.py agent-base
fi

# Then build the actual target
python3 cluster_build.py "$component"
```

An agent running `cluster-deploy.sh agent` does not need to remember the dependency chain. The script handles it.

### Component-to-Deployment Mapping

Each component targets specific Kubernetes resources. The script knows the mapping:

| Component | Kubernetes Targets | Container Name |
|-----------|-------------------|----------------|
| `gateway` | `deployment/api-gateway` | `gateway` |
| `agent` | All `agent-*` deployments + `agent-fullstack` statefulset | `agent` |
| `worker` | All `*-worker` deployments | `agent` |
| `fullstack` | `statefulset/agent-fullstack` or `deployment/agent-fullstack` | `agent` |
| `agent-base` | No deploy target (base image only) | -- |

The `agent` component is the most interesting. It targets every agent deployment in the cluster — CEO, CTO, Marketing, DevOps, all of them — plus the fullstack statefulset. One command updates the entire fleet.

### Smart Deploy Logic

The script does not blindly roll every matching deployment. It checks two things first:

**1. Already on target image?** If the deployment is running the exact image that was just built, skip it. No unnecessary restarts.

```bash
current_image=$(kubectl get deployment "$deploy" -n agents \
    -o jsonpath='{.spec.template.spec.containers[?(@.name=="agent")].image}')

if [[ "$current_image" == "$target_image" ]]; then
    echo "$deploy: already on target image, skipping"
    continue
fi
```

**2. Non-zero replicas?** Scaled-down agents (replicas: 0) get skipped — no point rolling a deployment that is not running.

For deployments that pass both checks:

```bash
kubectl set image deployment/"$deploy" \
    agent="$target_image" -n agents
kubectl rollout status deployment/"$deploy" \
    -n agents --timeout=120s
```

The configurable timeout (default 120 seconds) prevents the script from hanging if a rollout gets stuck.

### Post-Deploy Smoke Tests

For the gateway component, the script runs health checks after the rollout completes:

```bash
# Gateway smoke tests
for endpoint in /livez /ready /health; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "http://api-gateway.agents.svc/$endpoint")
    if [[ "$status" != "200" ]]; then
        echo "FAIL: $endpoint returned $status"
        exit 1
    fi
done
echo "Gateway smoke tests passed"
```

If any health endpoint fails, the script exits non-zero. The agent sees the failure and can decide whether to roll back or investigate.

## Step 3: Rollback

Deploys go wrong. The script supports rollback as a first-class operation:

```bash
scripts/cluster-deploy.sh rollback gateway
```

Under the hood, this runs:

```bash
kubectl rollout undo deployment/api-gateway -n agents
```

Kubernetes reverts to the previous revision. Verify with:

```bash
scripts/cluster-deploy.sh status gateway
# kubectl rollout status deployment/api-gateway -n agents
```

No image tags to remember. The agent detects a problem, rolls back, and verifies — all within the same script.

## Step 4: Putting It All Together

Here is a full deploy cycle. The DevOps agent discovers a gateway fix on main:

1. Agent runs `scripts/cluster-deploy.sh gateway`
2. Script syncs to latest main
3. `cluster_build.py` packages source, uploads tarball to GCS
4. Cloud Build job submitted, script polls until complete (~60-90s)
5. Built image: `us-central1-docker.pkg.dev/agent-hub-ceo/agent-hub/gateway:sha-abc123`
6. `kubectl set image` updates `deployment/api-gateway`
7. Rollout completes, smoke tests hit `/livez`, `/ready`, `/health` — all 200
8. Agent reports success

Total time: under three minutes. No GitHub Actions workflow queued. No external CI minutes consumed. The agent stayed inside the cluster the entire time.

For the `agent` component, the sequence includes the dependency chain:

```bash
scripts/cluster-deploy.sh agent
# 1. Builds agent-base first
# 2. Builds agent image on top of agent-base
# 3. Finds all agent-* deployments and agent-fullstack statefulset
# 4. Skips any already on the target image
# 5. Skips any with zero replicas
# 6. Rolls out to remaining deployments one by one
# 7. Waits for each rollout to complete
```

## Why This Beats GitHub Actions for Agent Organizations

The traditional CI path works fine when humans push code and machines build it. In an agent organization, routing through external CI adds friction that serves no one.

**Cost.** Cloud Build pricing is per-build-minute. GitHub Actions minutes come in tiers that do not map well to agent-driven, bursty build patterns.

**Latency.** GCS upload and Cloud Build submission take seconds. No queue, no runner allocation, no checkout step.

**RBAC simplicity.** The pod's service account already has Cloud Build and GCS access through workload identity. No GitHub tokens to rotate, no webhook secrets to manage.

**Agent autonomy.** Any agent with the right RBAC can build and deploy without leaving its pod. The deploy pipeline is a local script call.

## Adapt It to Your Cluster

The pattern is portable. Replace our component names with yours, swap in your registry, and adjust the Kubernetes target mappings. The core flow — tarball to GCS, submit to Cloud Build, poll for completion, `kubectl set image`, verify — works for any GKE cluster with Cloud Build access. The minimal version is just two operations: build the image, set the image. Everything else is operational polish you add as your fleet grows.

---

*In-cluster deploys are one piece of the autonomous operations stack at [agent.ceo](https://agent.ceo). Our AI agents build, deploy, monitor, roll back, and heal their own services — without human intervention. If you are building an agent organization on Kubernetes and want to see the full stack in action, [start at agent.ceo](https://agent.ceo).*
