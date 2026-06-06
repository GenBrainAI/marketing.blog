---
platform: linkedin
status: draft
date: 2026-10-26
note: "One line fix — fsGroupChangePolicy: OnRootMismatch"
---

## Post: One Line, 89 Seconds Saved Per Deploy

Yesterday I described the problem: Kubernetes recursively chowns every file on a PVC every time a pod mounts it. 60-90 seconds of pure startup delay per agent. Multiply by 7+ agents with ReadWriteOnce volumes forcing serial deploys. Minutes of downtime on every rollout.

The fix is one line in every pod spec:

fsGroupChangePolicy: OnRootMismatch

Instead of recursively walking every file on every mount (the "Always" default), OnRootMismatch checks only the volume root directory. If the root already has the correct group ownership, it skips the recursive walk entirely. O(1) instead of O(files).

We added this single line to every agent manifest in our fleet. Mount time dropped from 60-90 seconds to under 1 second. A rolling deployment across 7+ agents went from 10+ minutes of disruption to under 10 seconds.

The frustrating part: Kubernetes was already telling us about this. The kubelet events on every pod startup included a message suggesting we consider OnRootMismatch. We just were not looking at kubelet-level events -- we were focused on pod logs and container readiness.

One YAML field. No code changes. No architecture rethink. Just reading the event that Kubernetes was already emitting and acting on its advice.

Sometimes the biggest wins are the smallest changes.

Full technical story: https://agent.ceo/blog/zero-downtime-deployments-ai-agent-fleets

#Kubernetes #Performance #InfrastructureOptimization #AgentCEO
