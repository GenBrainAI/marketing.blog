---
platform: linkedin
status: draft
date: 2026-10-25
note: "Concept — fsGroupChangePolicy performance problem"
---

## Post: Your Kubernetes Volume Mount Takes 90 Seconds? Check fsGroupChangePolicy

Here is a Kubernetes performance problem that almost nobody talks about until it bites them.

You have a PVC. Maybe 10Gi. Your pod spec sets fsGroup: 1000 so the container process can write to the volume. Standard practice. What you probably do not know: Kubernetes defaults fsGroupChangePolicy to "Always." That means on every single mount -- every pod restart, every deploy, every node migration -- the kubelet recursively chowns every file on that volume.

A fresh volume? No problem. A volume with thousands of files accumulated over weeks of agent operation? 60 to 90 seconds of pure startup delay before your container even begins running.

Now combine this with ReadWriteOnce PVCs, which force strategy: Recreate on deployments. The old pod must fully terminate before the new pod can mount the volume. That 90-second chown is pure serial downtime. No overlap. No rolling update. Just dead time.

We discovered this running a fleet of 7+ AI agents on GKE. Every deploy meant 10+ minutes of total fleet disruption. The CEO agent -- the one coordinating all others -- would go dark for 90 seconds on every redeploy.

The worst part? The kubelet was literally logging the answer in its events: "applied fsGroup, consider fsGroupChangePolicy: OnRootMismatch."

We were not looking at kubelet events. We should have been.

Read the full story: https://agent.ceo/blog/zero-downtime-deployments-ai-agent-fleets

#Kubernetes #PVC #DevOps #AgentCEO
