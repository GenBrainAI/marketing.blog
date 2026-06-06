---
title: "How a Double Roll Turned Every Deploy Into 10 Minutes of Downtime"
slug: "double-roll-deploy-downtime-sidecar-convergence"
date: 2026-10-03
category: marketing
cluster: case-studies
tags: [deployment, kubernetes, ci-cd, sidecar, downtime, case-study, building-in-public]
description: "Every deploy rolled our agent pods twice — once for the agent container, again for the git-sync sidecar. With Recreate strategy and RWO volumes, that meant 6-10 minutes of hard downtime per deploy. Here's how we fixed it with one atomic kubectl call."
relatedPosts:
  - /blog/human-gate-timeout-agent-fleet-idle-incident
  - /blog/zero-downtime-deployments-ai-agent-fleets
  - /blog/outer-loop-shell-script-keeps-agents-alive
  - /blog/three-agent-failure-modes-production-only
  - /blog/prompt-watchdog-daemon-keeps-agents-working
---

# How a Double Roll Turned Every Deploy Into 10 Minutes of Downtime

Every time we deployed a new build, every agent in our fleet restarted twice. Not once. Twice. The founder's browser would show the CEO agent's terminal disconnect, reconnect, disconnect again, and reconnect again. Two full pod restarts for every single CI run. On the CEO pod — which uses a ReadWriteOnce persistent volume and a Recreate rollout strategy — each restart meant the old pod had to fully terminate before the new one could mount the volume. Three minutes of hard downtime per roll. Two rolls per deploy. Six to ten minutes of terminal outage, every time we shipped anything.

This went on for a while before we figured out what was happening.

## The Architecture

Our agent fleet runs on GKE. Each agent runs as a Kubernetes deployment with at least two containers in the pod: the `agent` container (Claude Code CLI, the actual brain) and a `git-sync` sidecar that keeps the agent-hub repository synced to the pod's filesystem. Some agents also have a `cai-runtime` sidecar. All of these container images are built per CI run and tagged with the commit SHA and run ID.

The CEO agent uses a Recreate deployment strategy because it mounts a ReadWriteOnce (RWO) persistent volume for its working directory. RWO means only one pod can mount the volume at a time. Rolling updates are impossible — you cannot start the new pod until the old pod releases the volume. So every pod template change triggers a full stop-then-start cycle.

This is fine when it happens once. It is not fine when it happens twice in a row for the same deploy.

## How the Double Roll Happened

Our CI pipeline had two steps that both modified agent deployments, and they ran sequentially.

**Step 1: "Update agent images."** This step ran `kubectl set image deployment/agent-ceo agent=$NEW_IMAGE` for each agent. It updated ONLY the `agent` container to the new build tag. The git-sync sidecar was left untouched. Kubernetes saw the pod template change and triggered a Recreate rollout. Roll number one.

**Step 2: "Apply infra manifests."** After roll number one completed, a separate CI step ran. This step rewrote ALL container images in the deployment manifest YAML — including git-sync — to the current build tag, then ran `kubectl apply` with server-side apply. Since step 1 only updated the agent container, the git-sync sidecar was still running the image from the PREVIOUS build. The apply changed the git-sync image in the pod template. Kubernetes saw a second pod template change and triggered a second Recreate rollout. Roll number two.

The agent container was already on the correct image after step 1. The second roll was entirely caused by the git-sync sidecar catching up. The agent was not changing. Only the sidecar was. And it was triggering a full pod restart — with all the RWO volume unmount/mount overhead — for a container that just syncs a git repo.

## The Evidence

We caught this by examining CI build run 27036846962. The CEO deployment went from revision 1142 to 1143. Both revisions had the SAME agent container image. The only difference was the git-sync tag changing from the previous build's run ID to the current one. An entire Recreate rollout — old pod terminated, volume released, new pod scheduled, volume mounted, containers started, health checks passed — for a sidecar image bump that could have been bundled with the first roll.

Multiply this by every agent in the fleet. The CEO pod was worst because of the RWO constraint, but every agent experienced two restarts per deploy. The websocket terminal connections died twice. Any in-flight agent work was interrupted twice. The prompt watchdog had to re-inject twice. Two disruptions for the price of one deploy.

## The Fix

Commit `5e3d1110d` introduced a `set_agent_images()` shell helper that converges ALL container images in a single atomic `kubectl set image` call:

```bash
set_agent_images() {
    local ref="$1" agent_image="$2" ns="agents"
    kubectl get "$ref" -n "$ns" || return 0
    local args="" cur
    # Check agent container
    cur=$(kubectl get "$ref" -n "$ns" \
      -o jsonpath='{...containers[?(@.name=="agent")].image}')
    [ "$cur" != "$agent_image" ] && args="$args agent=$agent_image"
    # Check git-sync sidecar (if present)
    if kubectl get "$ref" -n "$ns" \
      -o jsonpath='{...containers[*].name}' | grep -qw git-sync; then
        cur=$(kubectl get "$ref" -n "$ns" \
          -o jsonpath='{...containers[?(@.name=="git-sync")].image}')
        [ "$cur" != "$GITSYNC_IMAGE" ] && \
          args="$args git-sync=$GITSYNC_IMAGE"
    fi
    # Only update if something changed
    if [ -z "$args" ]; then
        echo "  $ref: already on target images, skipping"
    else
        kubectl set image "$ref" $args -n "$ns"
    fi
}
```

The key design decisions:

**One atomic mutation.** Both the agent image and the git-sync image update in a single `kubectl set image` call. One pod template change. One rollout. When the later `kubectl apply` of manifests runs, the images are already correct — the apply is a no-op for the pod template, and no second roll triggers.

**Current-state check before update.** The function reads each container's current image and only includes it in the update if it differs from the target. If every container is already on the correct tag — say, a CI re-run or a no-op deploy — nothing happens. No restart for a deploy that changed nothing.

**Graceful handling of missing sidecars.** Not every agent has a git-sync container. The function checks for its presence before trying to update it. Workloads that do not exist are skipped entirely.

## The Follow-Up

Code review of the initial fix (commit `797d8e1f6`) revealed two more problems hiding behind the same pattern.

First, the CSO agent has a `cai-runtime` sidecar that was also being updated by the manifest apply step — causing the same double roll. We generalized `set_agent_images()` to converge ALL per-build sidecars via a `BUNDLED_SIDECARS` list rather than hardcoding just git-sync.

Second, the staging deploy path had the identical bug. It only updated the agent container in its `kubectl set image` step, leaving sidecars for the manifest apply to catch. Same fix, same result.

## The General Pattern

This is a specific instance of a CI/CD anti-pattern that shows up everywhere: multiple pipeline steps mutating the same resource non-atomically. When step A changes field X and step B changes field Y, and both fields live in the same template that triggers a rollout, you get redundant restarts. The fix is always convergence — bundle all mutations into one step so subsequent steps are no-ops.

The severity depends on your rollout strategy. On a rolling update deployment, a redundant rollout is annoying but mostly invisible — old pods keep serving while new pods come up. On a Recreate strategy with RWO volumes, every unnecessary rollout is minutes of hard downtime. The same CI bug ranges from "slightly wasteful" to "catastrophic" depending on what it is deploying to.

We ran with this bug for weeks. It was not that we did not notice the downtime — we noticed it every deploy. We just assumed it was inherent to the Recreate strategy. "Deploys take a while because the volume has to unmount." True, but they should take a while ONCE, not twice. The assumption that downtime was expected prevented us from questioning whether the amount of downtime was expected.

## The Takeaway

If your deploys touch the same Kubernetes resource from multiple pipeline steps, check whether you are triggering redundant rollouts. Look at your deployment's revision history after a deploy — if you see two revisions where you expected one, you have this bug. And if you are running Recreate with RWO volumes, every redundant rollout is costing you minutes of real downtime that your users can see.

The fix is almost always the same: converge your mutations. Update all containers in one call. Apply all labels in one patch. Set all env vars in one step. Make every subsequent step a no-op for the fields it would otherwise mutate.

We ship these war stories because building production agent infrastructure is full of problems that look like platform limitations until you realize they are pipeline bugs. The interesting engineering is not in the architecture — it is in the deploy script that accidentally restarts your fleet twice.

---

We build [agent.ceo](https://agent.ceo) — the platform for running autonomous AI agent organizations. If you are building production agent systems and want to skip some of the deployment mistakes we have already made, check out what we are shipping.
