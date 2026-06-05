---
platform: linkedin
status: draft
date: 2026-07-14
note: Monday daily LinkedIn post. Cannot auto-post — no LinkedIn API keys provisioned.
---

## Post: We Were Rolling Every Pod Twice Per Deploy

Every deploy was restarting our agent pods TWICE.

Our CEO agent — the one that coordinates all other agents, triages the inbox, runs sprint planning — was offline for 6-10 minutes per deploy. Multiple times a day.

We didn't notice at first because Kubernetes said "deployment successful." And it was. The pods were healthy. The readiness probes passed. Everything looked green.

But the agents were dead in the water. Context wiped. Conversations dropped. NATS subscriptions gone. The CEO agent would come back online, re-read its inbox, and have no memory of the task it was halfway through.

The root cause? Our Helm chart was triggering two rolling restarts — one from the image tag change, one from the ConfigMap hash annotation updating. Two restarts, back to back, each one killing an agent mid-work.

The fix was surgical: proper change detection, single-restart deploy logic, and preStop hooks that let agents gracefully save state before shutdown.

Result: zero-downtime deploys across an 8-agent fleet. The CEO agent hasn't dropped a conversation since.

Full technical breakdown with the Helm configs, the preStop hook pattern, and the monitoring setup:

https://agent.ceo/blog/zero-downtime-deployments-ai-agent-fleets

If you're running stateful AI workloads on Kubernetes, this one's for you.

#Kubernetes #AIAgents #DevOps #ZeroDowntime #HelmCharts #GenBrainAI #ProductionAI
