---
platform: linkedin
status: draft
date: 2026-10-02
note: "The Hidden Cost of Non-Atomic CI/CD Mutations"
---

## Post: The Hidden Cost of Non-Atomic CI/CD Mutations

Every deploy was rolling our agent pods twice. We didn't notice for weeks.

Here's what happened. Our CI pipeline had two steps that mutated the same Kubernetes resource independently. Step 1: `kubectl set image` to update the agent container. Step 2: `kubectl apply` the full manifest, which also changed the git-sync sidecar image. Two mutations to the same pod template. Two Recreate rollouts.

With the Recreate strategy, each rollout fully terminates the old pod before starting the new one. On our CEO agent pod -- which uses a ReadWriteOnce (RWO) volume -- each roll takes about 3 minutes of downtime. Two rolls = 6-10 minutes of terminal outage per deploy. The websocket connection died twice. For a deploy that should have taken 3 minutes.

The fix: bundle all container image updates into one atomic `kubectl set image` call that covers both the agent container and the git-sync sidecar. After convergence, the manifest apply is a no-op for images. One rollout instead of two.

Simple in hindsight. Invisible until you watch the pod events and count the restarts.

If your CI/CD pipeline has multiple steps that can independently mutate the same resource, you probably have the same problem. Check your pod rollout history.

https://agent.ceo/blog/zero-downtime-deployments-ai-agent-fleets

#Kubernetes #CICD #DevOps #AgentCEO
