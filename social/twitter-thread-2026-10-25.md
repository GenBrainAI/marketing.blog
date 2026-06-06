---
platform: twitter
status: draft
date: 2026-10-25
note: "Concept — fsGroupChangePolicy performance problem"
---

## Thread: Your Kubernetes Volume Mount Takes 90 Seconds? Check fsGroupChangePolicy

Your Kubernetes pod takes 60-90 seconds to start and you cannot figure out why?

Check fsGroupChangePolicy. The default is silently killing your deploy speed.

---

Here is what happens: you set fsGroup in your pod security context (standard practice). Kubernetes defaults fsGroupChangePolicy to "Always."

That means on EVERY mount -- every deploy, every restart -- the kubelet recursively chowns every single file on the volume. O(files), not O(1).

---

A 10Gi PVC with thousands of files accumulated over weeks? 60-90 seconds of recursive chown before your container even starts.

Now add ReadWriteOnce PVCs. Those force strategy: Recreate. Old pod must die before new pod mounts. That chown is pure serial downtime.

---

We run 7+ AI agents on GKE. Every deploy meant 10+ minutes of total fleet disruption. Our CEO agent -- the one coordinating all other agents -- went dark for 90 seconds on every redeploy.

The kubelet was literally logging: "consider fsGroupChangePolicy: OnRootMismatch."

We were not reading kubelet events. Lesson learned.

---

Full breakdown: https://agent.ceo/blog/zero-downtime-deployments-ai-agent-fleets

#Kubernetes #PVC #DevOps #AgentCEO
