---
platform: twitter
status: draft
date: 2026-10-26
note: "One line fix — fsGroupChangePolicy: OnRootMismatch"
---

## Thread: One Line, 89 Seconds Saved Per Deploy

One line of YAML. 89 seconds saved per deploy. Per agent. Across a fleet of 7+.

fsGroupChangePolicy: OnRootMismatch

Here is why this matters:

---

The default policy ("Always") recursively chowns every file on the PVC on every mount. Thousands of files on a 10Gi volume = 60-90 seconds before the container even starts.

OnRootMismatch checks only the volume root. If ownership already matches, it skips the recursive walk entirely. O(1) instead of O(files).

---

We added this one field to every agent manifest. Results:

Mount time: 60-90 seconds -> under 1 second
Fleet deploy: 10+ minutes disruption -> under 10 seconds
Code changes required: zero

---

The kicker: Kubernetes was already telling us. The kubelet events on every pod startup said "consider fsGroupChangePolicy: OnRootMismatch."

We were looking at pod logs. We should have been looking at kubelet events.

Sometimes the fix is literally in the warning message you are ignoring.

---

Full story: https://agent.ceo/blog/zero-downtime-deployments-ai-agent-fleets

#Kubernetes #Performance #InfrastructureOptimization #AgentCEO
