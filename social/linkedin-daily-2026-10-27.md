---
platform: linkedin
status: draft
date: 2026-10-27
note: "Blog launch — Why Every Redeploy Cost Us 90 Seconds"
---

## Post: New Blog -- Why Every Redeploy Cost Us 90 Seconds

New deep-dive published today. The full architecture story behind a Kubernetes performance problem that cost us 90 seconds of downtime on every single deploy.

The setup: each of our AI agents runs in a pod with a 10Gi ReadWriteOnce PVC for persistent state. Pod security context sets fsGroup: 1000 so the agent process can write to the volume. Standard Kubernetes configuration that you will find in most production manifests.

The hidden cost: Kubernetes defaults fsGroupChangePolicy to "Always." Every time a pod mounts a volume, the kubelet recursively changes ownership of every file. After weeks of operation, those volumes accumulate thousands of files. Result: 60-90 seconds of recursive chown before the container process even starts.

The compounding factor: ReadWriteOnce PVCs cannot be mounted by two pods simultaneously, which forces deployment strategy: Recreate. Old pod terminates completely before new pod starts. That 90-second chown becomes pure serial downtime with zero overlap.

The fix: one field. fsGroupChangePolicy: OnRootMismatch. Checks only the volume root instead of recursing through every file. Applied across all agent manifests. Deploy disruption dropped from 10+ minutes across the fleet to under 10 seconds.

The irony: the kubelet was emitting an event on every mount suggesting exactly this fix. We just were not looking at kubelet events.

Read the full deep-dive: https://agent.ceo/blog/fsgroup-change-policy-onrootmismatch-redeploy-outage

#Kubernetes #fsGroup #DeepDive #AgentCEO
