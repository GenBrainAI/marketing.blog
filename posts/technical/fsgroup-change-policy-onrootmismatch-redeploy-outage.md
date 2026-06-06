---
title: "Why Every Redeploy Cost Us 90 Seconds: The fsGroup Recursive chown Problem"
slug: "fsgroup-change-policy-onrootmismatch-redeploy-outage"
date: 2026-10-27
category: technical
cluster: architecture-deep-dives
tags: [kubernetes, fsgroup, pvc, redeploy, performance, deep-dive]
description: "Every CI/CD rollout caused 60-90 seconds of agent downtime per pod — because Kubernetes was recursively chown-ing every file on every volume mount. One line fixed it."
relatedPosts:
  - /blog/double-roll-deploy-downtime-sidecar-convergence
  - /blog/zero-downtime-deployments-ai-agent-fleets
  - /blog/outer-loop-shell-script-keeps-agents-alive
  - /blog/image-pinning-latest-tag-customer-agent-drift
  - /blog/three-agent-failure-modes-production-only
---

# Why Every Redeploy Cost Us 90 Seconds: The fsGroup Recursive chown Problem

The CEO agent — the most critical agent in our cyborgenic organization — went completely dark on every deploy. No inbox processing. No task assignments. No escalation handling. For over a minute. Every single time.

We had been living with this for long enough that it felt normal. A deploy triggers a pod restart. Pod restarts take time. Time means downtime. That is just how Kubernetes works, right?

Wrong. We were burning 60-90 seconds per pod on something that should take under one second.

## The Clue Was in the Kubelet Events

During a routine rollout, a kubelet event surfaced that we had never paid attention to:

```
VolumePermissionChangeInProgress: Setting volume ownership for
pvc-...agent-data... is taking longer than expected, consider OnRootMismatch
```

Kubernetes was telling us exactly what was wrong. It was even telling us the fix. We just had not been watching kubelet events closely enough.

## What fsGroup Actually Does

Each agent pod in our fleet mounts a 10Gi ReadWriteOnce PVC called `agent-data`. This volume holds everything that persists across restarts: session transcripts, context files, git repos, cached state. The pod spec sets `securityContext.fsGroup: 1000` so the `appuser` process can read and write the volume.

When `fsGroup` is set, Kubernetes needs to ensure that every file on the volume is owned by the specified group. The question is *how* it does this. That is controlled by the `fsGroupChangePolicy` field, and the default is brutal.

### `Always` — The Default

With `fsGroupChangePolicy: Always` (or when the field is omitted, which defaults to `Always`), kubelet recursively `chown`s **every file on the volume on every mount**. Every file. Every directory. Every symlink. Every time the pod starts.

On a fresh PVC with a handful of files, this is invisible. On a 10Gi PVC with thousands of session transcripts, multiple cloned git repositories, and accumulated context files — the kind of PVC that every long-running agent accumulates — this recursive walk takes 60-90 seconds.

That is 60-90 seconds where the pod is in `ContainerCreating` state. The containers have not started. The agent is not running. The volume is being walked, file by file, applying `chown` to everything it finds.

### `OnRootMismatch` — The Fix

With `fsGroupChangePolicy: OnRootMismatch`, kubelet only checks whether the **volume root directory** has the correct group ownership. If the root is already owned by group 1000 — which it will be after the very first mount — the recursive walk is skipped entirely.

The complexity drops from O(files) to O(1). The mount time drops from 60-90 seconds to under one second.

## Why It Hurt So Much

Our agents use `strategy: Recreate` for their deployments. This is not a choice we made for fun — it is forced by the storage architecture. Each agent mounts a ReadWriteOnce PVC. ReadWriteOnce means exactly one pod can mount the volume at a time. You cannot do a rolling update because that requires two pods running simultaneously, and the second pod would fail to mount the volume.

So `Recreate` does this:

1. Kill the old pod
2. Wait for the old pod to fully terminate
3. Detach the volume from the old node
4. Start the new pod
5. Attach and mount the volume
6. Wait for the new pod to be ready

Step 5 is where the `fsGroup` policy kicks in. With `Always`, that step includes a full recursive `chown` of the volume. So the total downtime per agent is:

```
pod termination + volume detach + container pull + RECURSIVE CHOWN + container startup
```

Everything except the recursive chown is fast — a few seconds each. The recursive chown was the dominant cost by an order of magnitude.

## The Fleet Math

We run 7+ agents in the fleet. A CI/CD deployment hits every agent. At 90 seconds of chown per agent, that is over 10 minutes of total fleet disruption during a rollout. The CEO agent is down for 90 seconds. The CTO agent is down for 90 seconds. Marketing, DevOps, CSO, QA — all sequentially eating their own 90-second chown penalty.

During those 90 seconds per agent, nothing happens. No inbox processing. No NATS messages consumed. No task state transitions. No health checks passing. The agent is a black hole.

## The One-Line Fix

The fix was one line per manifest, applied to every agent workload in the fleet:

```yaml
securityContext:
  fsGroup: 1000
  fsGroupChangePolicy: OnRootMismatch
```

That is it. The entire change was adding `fsGroupChangePolicy: OnRootMismatch` to every pod security context. Every deployment, every statefulset, every template.

The commit (`5d842de12`) touched:

- **CEO and CTO** — the core deployments
- **CSO, DevOps, Marketing, Investment, QA** — individual agent manifests
- **Fullstack** — the statefulset
- **Super-agent-pool** — the burst-capacity pool
- **statefulset-agent-template** — so every future customer org inherits the fix automatically
- **Dev environment** — so development clusters get the same behaviour

After the first deploy with this change (which does the initial chown, setting the volume root correctly), every subsequent redeploy skips the recursive walk. The volume root is already owned by group 1000. Mount time: sub-second.

## What This Does Not Fix

Two things remain:

**The Recreate strategy is structural.** Each agent runs a single `claude --continue` session. That session cannot run in two pods simultaneously — it is a single process with local state. Even if the PVC were ReadWriteMany, you still could not run two instances of the same agent session in parallel. So `Recreate` is forced by the application semantics, not just the storage class. There will always be *some* downtime per deploy.

**The double-roll problem is separate.** In some CI/CD configurations, `kubectl set image` triggers one rollout and `kubectl apply --server-side --force-conflicts` triggers another. That means each agent restarts twice per deploy instead of once. Fixing fsGroup halves the pain of each restart, but the double restart itself is tracked as a separate follow-up. (See our earlier post on [double-roll deploy downtime](/blog/double-roll-deploy-downtime-sidecar-convergence) for that story.)

## The Lesson

The default is not always safe. Kubernetes defaults to `Always` for `fsGroupChangePolicy` because it is the most conservative option — it guarantees correct permissions regardless of how the volume was previously used. But "conservative" and "correct" are not the same as "fast" or "appropriate for your workload."

If you run stateful workloads on Kubernetes with persistent volumes and `fsGroup`, check your `fsGroupChangePolicy`. If you do not set it explicitly, you are paying the recursive chown tax on every single pod restart. On small volumes, you will never notice. On volumes that accumulate data over time — logs, transcripts, repos, caches — the cost grows linearly with the number of files and will eventually dominate your restart latency.

The kubelet was even warning us. We just were not listening.

## Key Takeaways

- **`fsGroupChangePolicy: Always` (the default)** recursively `chown`s every file on every mount. Cost grows with file count.
- **`fsGroupChangePolicy: OnRootMismatch`** checks only the volume root. O(1) after first mount.
- **ReadWriteOnce PVCs + Recreate strategy** make this especially painful — there is no overlap to mask the mount latency.
- **Watch kubelet events.** Kubernetes often tells you exactly what is wrong. `VolumePermissionChangeInProgress` is not informational — it is a performance alarm.
- **Audit your defaults.** The most expensive bugs are the ones that ship as default behaviour.

---

*GenBrain AI runs a fleet of autonomous agents that build, deploy, and manage software — including themselves. Every second of downtime is a second where no agent is thinking. That is why we obsess over restart latency.*

*Want to see how a cybernetic organization actually works? Visit [agent.ceo](https://agent.ceo) and watch our agents operate in real time.*
