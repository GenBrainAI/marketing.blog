---
title: "Zero-Downtime Deployments for AI Agent Fleets: How We Eliminated Double-Roll Pod Restarts"
slug: "zero-downtime-deployments-ai-agent-fleets"
date: 2026-07-14
category: technical
cluster: production-patterns
tags: [deployment, kubernetes, zero-downtime, devops, ci-cd, agent-fleet, production]
description: "Every deploy was restarting our AI agent pods twice — causing 6-10 minutes of downtime per roll. Here's how we fixed it with one atomic kubectl call."
relatedPosts:
  - /blog/deploying-ai-agents-kubernetes
  - /blog/self-healing-connections-resilient-ai-agent-infrastructure
  - /blog/crash-resilient-ai-agents-cyborgenic
  - /blog/hardened-customer-org-provisioning-platform-update
  - /blog/monitoring-ai-agent-fleet
---

# Zero-Downtime Deployments for AI Agent Fleets: How We Eliminated Double-Roll Pod Restarts

Every deploy of our AI agent fleet was rolling each pod twice. We did not notice for weeks. Then we looked at the CEO agent's uptime graph and saw a pattern: two distinct downtime windows per deploy, ~3 minutes each, totalling 6-10 minutes of full outage every time we shipped. For a singleton agent with a ReadWriteOnce PVC, that means two complete websocket disconnections, two context reloads, two rounds of the session startup sequence. It was, to put it plainly, unacceptable.

This post explains what caused the double roll, how we fixed it, and how we test for it now so it never comes back.

## The Symptom: Two Rolls, One Deploy

Our agent fleet runs on GKE. Each agent is a Kubernetes Deployment with at least two containers: the `agent` container (Claude Code CLI + the agent's session) and a `git-sync` sidecar (keeps the agent's workspace in sync with its git repos). Some agents have additional sidecars — the CSO agent, for example, runs a `cai-runtime` container for its compliance scanning tools.

The CEO agent is the most sensitive workload. It is a singleton pod (`replicas: 1`) with a ReadWriteOnce persistent volume claim for its workspace. The deployment uses `strategy: Recreate` because RWO volumes cannot be mounted by two pods simultaneously. That means every pod template change triggers a full stop-then-start cycle — no rolling update, no graceful handoff. The old pod dies, the volume detaches, the new pod starts, the volume reattaches. About 3 minutes wall-clock.

We observed this happening twice per deploy. `kubectl get events` told the story:

```
LAST SEEN   TYPE     REASON              OBJECT                    MESSAGE
2m ago      Normal   ScalingReplicaSet   deployment/ceo-agent      Scaled down to 0
2m ago      Normal   ScalingReplicaSet   deployment/ceo-agent      Scaled up to 1
5m ago      Normal   ScalingReplicaSet   deployment/ceo-agent      Scaled down to 0
5m ago      Normal   ScalingReplicaSet   deployment/ceo-agent      Scaled up to 1
```

Two scale-downs, two scale-ups, one deploy. Something was mutating the pod template twice.

## The Root Cause: Two Steps, Two Mutations

Our deploy workflow had two steps that both touched container images:

**Step 1 — "Update agent images"**: A targeted `kubectl set image` call that updated only the `agent` container to the newly-built image:

```bash
kubectl set image deployment/ceo-agent \
  agent=gcr.io/genbrain/agent-cli:abc123
```

This triggers roll #1. The pod restarts with the new agent image. Good.

**Step 2 — "Apply infrastructure manifests"**: Server-side-apply of the full deployment manifests, which include ALL container specs — agent, git-sync, everything:

```bash
kubectl apply --server-side -f deploy/agents/ceo-agent.yaml
```

Here is the problem. The git-sync sidecar image is also rebuilt on every CI run. Its SHA changes every build. So when the manifest apply runs, Kubernetes sees a different `git-sync` image SHA than what is currently running (which was set during the previous deploy, not this one). It mutates the pod template. That triggers roll #2.

The timeline looked like this:

```
t=0    kubectl set image → agent container updated
t=0    Roll #1 starts (Recreate: pod killed, new pod starting)
t=3m   Roll #1 complete, CEO agent is back online
t=3m   kubectl apply → git-sync image updated in manifest
t=3m   Roll #2 starts (Recreate: pod killed AGAIN)
t=6m   Roll #2 complete, CEO agent is back online for real this time
```

Six minutes of downtime. Two websocket disconnections. Every single deploy.

For agents with `RollingUpdate` strategy, the damage was less visible — two overlapping rolls instead of two sequential outages — but it still doubled the pod churn across the fleet, wasted node resources, and made deploy times unpredictable.

## The Fix: Atomic Multi-Container Image Updates

The solution was straightforward once we understood the problem: bundle ALL container image updates into a single `kubectl set image` call, so the manifest apply becomes a no-op for images.

We wrote a `set_agent_images()` helper that compares each container's current image against the desired image, collects the stale ones, and issues one atomic update:

```bash
set_agent_images() {
  local deployment="$1"
  local namespace="${2:-agents}"
  local -a updates=()

  # Compare current vs desired for each container
  for container in agent git-sync cai-runtime; do
    local desired="${IMAGE_MAP[$container]:-}"
    [ -z "$desired" ] && continue

    # Check if this deployment even has this container
    local current
    current=$(kubectl get deployment "$deployment" -n "$namespace" \
      -o jsonpath="{.spec.template.spec.containers[?(@.name=='$container')].image}" \
      2>/dev/null) || continue
    [ -z "$current" ] && continue

    if [ "$current" != "$desired" ]; then
      updates+=("$container=$desired")
    fi
  done

  if [ ${#updates[@]} -eq 0 ]; then
    echo "All images current for $deployment — no restart needed"
    return 0
  fi

  echo "Updating ${#updates[@]} container(s) for $deployment: ${updates[*]}"
  kubectl set image "deployment/$deployment" -n "$namespace" "${updates[@]}"
}
```

The key insight: `kubectl set image` accepts multiple `container=image` pairs in a single call. One call, one pod template mutation, one roll.

After this runs, the subsequent `kubectl apply` sees that all images already match the manifest. No mutation. No second roll.

We generalized this for every agent deployment, including agents with extra sidecars:

```bash
# IMAGE_MAP is populated from CI build outputs
declare -A IMAGE_MAP=(
  [agent]="gcr.io/genbrain/agent-cli:${BUILD_SHA}"
  [git-sync]="gcr.io/genbrain/git-sync:${BUILD_SHA}"
  [cai-runtime]="gcr.io/genbrain/cai-runtime:${BUILD_SHA}"
)

# Apply to each agent deployment
for deployment in ceo-agent cto-agent cso-agent marketing-agent; do
  set_agent_images "$deployment" "agents"
done
```

The CSO agent has all three containers. The marketing agent has only `agent` and `git-sync`. The helper handles both cases — it skips containers that do not exist in the deployment spec.

## Testing It: Mock-Kubectl Harness

We did not want to discover regression by watching the CEO agent go down twice in production. So we built a mock-kubectl test harness that validates the bundling logic:

```bash
# Test cases for set_agent_images()
test_bundles_both_when_both_stale()    # agent + git-sync both outdated → one call
test_bundles_only_stale_ones()         # agent current, git-sync stale → git-sync only
test_no_restart_when_both_current()    # both match desired → no kubectl call at all
test_agent_only_when_no_git_sync()     # deployment has no git-sync sidecar → agent only
test_skips_missing_workloads()         # deployment doesn't exist → skip, don't error
```

The mock intercepts `kubectl set image` and `kubectl get deployment` calls, records the arguments, and asserts on the expected bundling behavior. Each test case verifies that exactly one `kubectl set image` call is made (or zero, when no update is needed) with exactly the right set of container-image pairs.

This runs in CI on every change to the deploy scripts. The double-roll bug is now structurally impossible to reintroduce without a test failure.

## Results

Before the fix:
- **~6-10 minutes** of CEO agent downtime per deploy (two Recreate rolls)
- **2 websocket disconnections** per deploy, each requiring full session reconnection
- **Double pod churn** across the fleet on every deploy

After the fix:
- **~3 minutes** of CEO agent downtime per deploy (one Recreate roll)
- **1 websocket disconnection** per deploy
- **50% reduction** in deploy-related pod restarts fleet-wide
- **Zero** double-roll incidents since the fix shipped

The CEO agent's deploy downtime dropped from the worst case of 10 minutes to a consistent 3 minutes. For an agent that processes founder messages, coordinates the entire organization, and manages sprint cycles, that difference matters.

## Lessons

**1. Audit your deploy pipeline for sequential mutations.** If you have separate steps that each modify the pod template — even different fields — each one triggers a roll. Kubernetes does not batch mutations across separate API calls. You have to.

**2. Recreate strategy amplifies every mistake.** With RollingUpdate, a double mutation causes extra pod churn but limited downtime. With Recreate (forced by RWO PVCs or singleton constraints), every mutation is a full outage. If you run Recreate workloads, your deploy pipeline needs to be surgical.

**3. Sidecar images change more often than you think.** We assumed git-sync was "infrastructure" that rarely changed. In reality, it was rebuilt every CI run, and its SHA changed every time. Any container that shares a CI pipeline with your main app will drift on every build.

**4. Test the deploy, not just the app.** Our application tests were green. Our infrastructure manifests were valid. The bug lived in the interaction between two correct steps executed in sequence. The mock-kubectl harness tests the deploy logic itself — something most teams skip.

This fix is part of our broader work on [production resilience for AI agent fleets](/blog/self-healing-connections-resilient-ai-agent-infrastructure). Running agents in Kubernetes introduces operational patterns that don't exist in traditional deployments — singleton pods with stateful volumes, long-lived websocket connections, and context windows that take minutes to rebuild after a restart. We have written about the [foundations of deploying agents to Kubernetes](/blog/deploying-ai-agents-kubernetes), how we handle [crash resilience](/blog/crash-resilient-ai-agents-cyborgenic), and how we [monitor the fleet](/blog/monitoring-ai-agent-fleet) to catch issues like this one before they compound.

Every minute of unnecessary downtime is a minute where an agent is not processing work, not responding to the founder, not coordinating with other agents. In a [Cyborgenic Organization](https://agent.ceo), uptime is productivity. We treat deploy pipelines with the same rigor we treat application code — because in production, they are application code.

---

*GenBrain AI builds autonomous AI agent organizations. See how we run a full company with AI agents at [agent.ceo](https://agent.ceo).*
