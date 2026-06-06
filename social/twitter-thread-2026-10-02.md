---
platform: twitter
status: draft
date: 2026-10-02
note: "The Hidden Cost of Non-Atomic CI/CD Mutations"
---

## Thread: The Hidden Cost of Non-Atomic CI/CD Mutations

Every deploy was rolling our agent pods twice. Two Recreate rollouts per deploy. Double the downtime. We didn't notice for weeks.

Here's the anatomy of a non-atomic CI/CD mutation.

---

Our CI had two steps that independently mutated the same pod template:

Step 1: `kubectl set image` -- updates the agent container.
Step 2: `kubectl apply` -- applies the full manifest, which also changes the git-sync sidecar image.

Two mutations. Two rollouts. Same pod.

---

With the Recreate strategy, each rollout fully terminates the old pod before starting the new one. Our CEO pod uses a ReadWriteOnce (RWO) volume, so each roll is ~3 min of downtime.

Two rolls = 6-10 minutes of terminal outage. The websocket died twice. For a deploy that should take 3 minutes.

---

The fix: bundle all container image updates into one atomic `kubectl set image` call -- agent container AND git-sync sidecar in one shot.

After convergence, the manifest apply is a no-op for images. One rollout instead of two. Done.

---

If your CI pipeline has multiple steps that can independently mutate the same Kubernetes resource, check your pod rollout history. You might be paying double.

https://agent.ceo/blog/zero-downtime-deployments-ai-agent-fleets

#Kubernetes #CICD #DevOps #AgentCEO
