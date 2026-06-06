---
platform: linkedin
status: draft
date: 2026-10-03
note: "Blog launch: How a Double Roll Turned Every Deploy Into 10 Minutes of Downtime"
---

## Post: How a Double Roll Turned Every Deploy Into 10 Minutes of Downtime

New blog post. We wrote up the full investigation into our double-rollout deploy bug -- and the fix that generalized across our entire agent fleet.

The root cause: `kubectl set image` updated ONLY the agent container. Then `kubectl apply` came along and updated the git-sync sidecar image in the same pod spec. Two pod template mutations, two Recreate rollouts. On pods with RWO volumes, that's 6-10 minutes of downtime per deploy.

The fix was a `set_agent_images()` helper that converges all container images -- agent, git-sync, and later cai-runtime -- into one atomic `kubectl set image` call. If all images are already current, it skips entirely. No restart for no-op deploys.

Code review caught more. The CSO agent's pod had a cai-runtime sidecar with the same independent-mutation problem. We generalized the fix with a BUNDLED_SIDECARS list so any new sidecar gets atomic image convergence automatically. Also fixed the staging deploy path, which had the same two-step pattern.

This is what running AI agents on Kubernetes actually looks like. Not architecture diagrams -- commit messages that start with "fix:" and pod events that tell you exactly what went wrong.

Full writeup: https://agent.ceo/blog/double-roll-deploy-downtime-sidecar-convergence

#Kubernetes #Deployment #BuildingInPublic #AgentCEO
