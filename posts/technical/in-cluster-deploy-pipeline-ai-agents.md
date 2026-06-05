---
title: "How Our AI Agents Deploy Themselves: An In-Cluster Build Pipeline"
slug: "in-cluster-deploy-pipeline-ai-agents"
date: 2026-06-08
category: technical
cluster: "infrastructure"
tags: [deployment, ci-cd, cloud-build, gke, kubernetes, in-cluster, ai-agents, infrastructure, automation]
description: "We replaced GitHub Actions with an in-cluster build pipeline that lets AI agents trigger Cloud Build, push images, and roll out deployments from inside GKE — no external CI needed."
relatedPosts: ["autonomous-deployment", "deploying-ai-agents-kubernetes", "self-healing-infrastructure", "ai-powered-devops", "cicd-pipeline-analysis"]
---

# How Our AI Agents Deploy Themselves: An In-Cluster Build Pipeline

Here is a question that will sound strange if you have never run a [Cyborgenic Organization](/blog/cyborgenic-organizations): who deploys your AI agents? If the answer is "a human clicks merge and GitHub Actions takes it from there," you have a bottleneck shaped like a person. We did too. Then we gave the agents a build pipeline they can run themselves, from inside the cluster, with zero external dependencies. Now an agent that fixes a bug can also ship the fix — without waiting for anyone.

## The Problem: CI/CD Was Not Built for Agents

Our original setup was standard. Push to a branch, open a PR, merge to main, GitHub Actions builds a Docker image, pushes to Artifact Registry, and a deploy step rolls it out to GKE. This works fine when humans are the only actors. It breaks down when your workforce is six AI agents running inside the same Kubernetes cluster they are deploying to.

Three problems surfaced fast:

**Latency.** An agent that discovers a bug, writes a fix, and pushes a commit still has to wait 8-12 minutes for GitHub Actions to notice, queue, build, and push. The agent sits idle, burning tokens, watching a pipeline it cannot control.

**Cost.** GitHub Actions minutes are not free at scale. We were burning roughly 3,000 minutes per month on agent-triggered builds — builds that were running on external infrastructure while perfectly good compute sat unused inside our GKE cluster. That is paying twice for the same capacity.

**Access friction.** Agents inside GKE do not have an easy way to trigger GitHub Actions workflows. You can use the API, but now you are managing GitHub tokens, webhook callbacks, and polling for completion status. The agent needs to know when the image is ready so it can roll it out. That is a surprising amount of glue code for something that should be simple: build this, deploy it.

We wanted something an agent could invoke with a single command — and that ran entirely inside the cluster where the agent already lives.

## The Solution: `cluster-deploy.sh` + `cluster_build.py`

We built a two-piece pipeline. A bash script handles orchestration and rollout. A Python script handles build submission. Together, they let any agent build and deploy any component with one command:

```bash
./cluster-deploy.sh gateway
```

That is it. One line. The agent does not need to know about Docker registries, build configs, or rollout strategies. The script handles all of it.

### How the Build Works

When an agent runs `cluster-deploy.sh gateway`, here is what happens under the hood:

**Step 1: Context packaging.** The Python build submitter (`cluster_build.py`) tars up the repository context — the source code, Dockerfile, and build configuration for the target component. This tarball becomes the build source.

```python
# cluster_build.py packages and submits the build
def submit_build(component, project_id, repo_root):
    # Tar the repo context
    context_tar = create_build_context(repo_root, component)

    # Upload to GCS staging bucket
    gcs_path = upload_to_gcs(context_tar, project_id)

    # Submit to Cloud Build API
    build = cloud_build_client.create_build(
        project_id=project_id,
        build={
            "source": {"storage_source": {"bucket": bucket, "object": gcs_path}},
            "steps": [{"name": "gcr.io/cloud-builders/docker", "args": ["build", "-t", image_tag, "."]}],
            "images": [image_tag],
        },
    )
    return wait_for_build(build)
```

**Step 2: Cloud Build execution.** The tarball gets uploaded to a GCS staging bucket, then submitted to the Cloud Build API. Cloud Build pulls the source, builds the Docker image according to the component's Dockerfile, and pushes the finished image to Artifact Registry. All of this runs on Google's managed build infrastructure — we do not need dedicated build nodes in our cluster.

**Step 3: Rollout.** Once the build completes, the bash script uses `kubectl set image` to update the deployment with the new image tag. Kubernetes handles the rolling update — the same [Kubernetes deployment patterns](/blog/deploying-ai-agents-kubernetes) we use for all agent pods — draining old pods and starting new ones.

```bash
# After build completes, roll out the new image
kubectl set image deployment/${COMPONENT} \
  ${COMPONENT}=${REGISTRY}/${COMPONENT}:${NEW_TAG} \
  -n agents
```

The agent gets real-time feedback at every stage.

### Dependency Resolution

Not all components are independent. Our `agent` image depends on `agent-base` — the base image that includes the CLI runtime, shared libraries, and configuration tooling. If you rebuild `agent` without first rebuilding `agent-base`, you get stale dependencies.

The pipeline handles this automatically:

```bash
# cluster-deploy.sh knows the dependency graph
declare -A DEPENDENCIES=(
  ["agent"]="agent-base"
  ["worker"]="agent-base"
)

# Before building 'agent', check if agent-base needs rebuilding
if needs_rebuild "${DEPENDENCIES[$component]}"; then
  echo "Building dependency: agent-base"
  build_component "agent-base"
fi
build_component "$component"
```

An agent running `cluster-deploy.sh agent` does not need to remember that `agent-base` comes first. The script checks, rebuilds if necessary, and chains the builds in the correct order.

### Supported Components

The pipeline supports five component targets, covering the entire stack:

| Component | Description |
|-----------|-------------|
| `gateway` | API gateway — routing, auth, rate limiting |
| `agent-base` | Base image for all agent pods |
| `agent` | Individual agent images (CEO, CTO, Marketing, etc.) |
| `worker` | Background task workers |
| `fullstack` | Frontend dashboard and admin UI |

Each component has its own Dockerfile and build context within the monorepo. The pipeline knows where to find them.

### Rollback

Things go wrong. When they do, an agent can roll back just as easily:

```bash
./cluster-deploy.sh rollback gateway
```

This reverts the deployment to the previous image tag. The agent can also check deployment status before deciding whether a rollback is needed:

```bash
./cluster-deploy.sh status gateway
# Output: gateway: 3/3 replicas ready, image: gateway:abc1234, last deploy: 2m ago
```

Combined with our [self-healing infrastructure](/blog/self-healing-infrastructure) patterns, this means an agent can detect a bad deploy through health checks, trigger a rollback, and report the issue — all without human intervention.

## What This Looks Like in Practice

Here is a real sequence. Our CTO agent discovered a bug in the gateway's auth middleware:

1. CTO agent reads the error logs, identifies the root cause, writes a fix
2. CTO agent commits the fix to its branch, merges to main
3. CTO agent runs `cluster-deploy.sh gateway`
4. Pipeline builds the new gateway image (~90 seconds)
5. Pipeline rolls out the new image to the gateway deployment
6. CTO agent verifies the fix by curling the affected endpoint
7. CTO agent reports the resolution to the CEO agent via NATS

Total time from bug discovery to verified fix in production: under four minutes. No human involved at any step. No external CI pipeline queued. No GitHub Actions minutes consumed.

This is what [autonomous deployment](/blog/autonomous-deployment) looks like when agents own the full loop.

## Why This Matters

Giving agents the ability to build and deploy is not a convenience feature. It is a structural requirement for autonomous operations.

Without it, every deploy is a handoff. The agent does the intellectual work — finding the bug, writing the fix, reasoning about the change — and then waits for an external system to do the mechanical work. That handoff introduces latency, cost, and failure modes that have nothing to do with the quality of the agent's work.

With the in-cluster pipeline, the agent's authority matches its responsibility. If an agent is accountable for a service's health (and in a [Cyborgenic Organization](/blog/cyborgenic-organizations), it is), it should be able to act on that accountability without waiting in a queue.

The [CI/CD pipeline analysis](/blog/cicd-pipeline-analysis) we did earlier this year showed that most pipeline time is wasted on setup, caching, and queuing — not actual building. By moving the build trigger inside the cluster, we eliminated the queuing and setup overhead entirely. The GCS upload and Cloud Build submission take seconds, not minutes.

We are working toward [AI-powered DevOps](/blog/ai-powered-devops) where agents own the full operational lifecycle: detect, diagnose, fix, build, deploy, verify. The in-cluster build pipeline is the piece that closes the loop between "agent wrote a fix" and "fix is running in production."

## Try It Yourself

If you are running AI agents on Kubernetes and still relying on external CI to deploy them, consider what you are paying — in time, money, and complexity — for that indirection. The agents are already inside the cluster. The cluster already has the compute. The build APIs already exist.

The question is not whether agents should deploy themselves. The question is why they are still waiting for permission.

---

*Running AI agents that manage their own infrastructure is one of the core capabilities of the [agent.ceo](https://agent.ceo) platform. If you want to see what a fully autonomous agent organization looks like — where agents build, deploy, monitor, and heal their own services — [get started at agent.ceo](https://agent.ceo).*
