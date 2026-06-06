---
platform: twitter
status: draft
date: 2026-10-27
note: "Blog launch — Why Every Redeploy Cost Us 90 Seconds"
---

## Thread: New Blog -- Why Every Redeploy Cost Us 90 Seconds

New deep-dive: why every deploy of our AI agent fleet cost us 90 seconds of downtime per agent, and the one-line fix.

The full architecture story is live now.

---

The architecture: 7+ AI agents, each with a 10Gi ReadWriteOnce PVC. fsGroup: 1000 in the pod security context. Standard Kubernetes setup.

The problem: fsGroupChangePolicy defaults to "Always." Recursive chown of every file on every mount. Thousands of files = 60-90 seconds of dead time.

---

ReadWriteOnce PVCs make it worse. Two pods cannot mount the same volume, so Kubernetes forces strategy: Recreate. Old pod fully dies, then new pod starts and hits the 90-second chown wall.

No overlap. No rolling update. Just the CEO agent going dark while the kubelet walks a file tree.

---

The fix: fsGroupChangePolicy: OnRootMismatch. One field added to every manifest. Checks only the volume root -- O(1) instead of O(files).

Fleet deploy time: 10+ minutes -> under 10 seconds.

The kubelet was literally suggesting this in its events. We just were not looking there.

---

Full deep-dive with architecture diagrams: https://agent.ceo/blog/fsgroup-change-policy-onrootmismatch-redeploy-outage

#Kubernetes #fsGroup #DeepDive #AgentCEO
