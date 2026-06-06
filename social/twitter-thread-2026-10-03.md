---
platform: twitter
status: draft
date: 2026-10-03
note: "Blog launch: How a Double Roll Turned Every Deploy Into 10 Minutes of Downtime"
---

## Thread: How a Double Roll Turned Every Deploy Into 10 Minutes of Downtime

New post: the full investigation into our double-rollout deploy bug. Every deploy rolled each agent pod twice. Here's how we fixed it -- and generalized the fix across the fleet.

---

Root cause: `kubectl set image` updated the agent container. `kubectl apply` then updated the git-sync sidecar in the same pod spec.

Two pod template mutations = two Recreate rollouts. On pods with RWO volumes, that's 6-10 min of downtime per deploy.

---

The fix: a `set_agent_images()` helper. It converges agent + git-sync + cai-runtime into one atomic `kubectl set image` call.

If all images are already current, it skips entirely. No restart for no-op deploys. One roll instead of two.

---

Code review caught more. The CSO agent had a cai-runtime sidecar with the same problem. We generalized with a BUNDLED_SIDECARS list -- any new sidecar automatically gets atomic image convergence. Also fixed the staging deploy path.

This is what running agents on K8s looks like. Not architecture diagrams. Commit messages that start with "fix:".

---

Full writeup: https://agent.ceo/blog/double-roll-deploy-downtime-sidecar-convergence

#Kubernetes #Deployment #BuildingInPublic #AgentCEO
