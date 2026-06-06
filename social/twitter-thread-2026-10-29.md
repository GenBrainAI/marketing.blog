---
platform: twitter
status: draft
date: 2026-10-29
note: "Blog launch — How to Keep CLI Tools Current in Long-Lived K8s Pods"
---

## Thread: New Blog -- How to Keep CLI Tools Current in Long-Lived K8s Pods

New tutorial: how we keep CLI tools current in long-lived Kubernetes pods without redeploying.

No operator. No sidecar. A shell script and a timestamp file.

---

The mechanism: a PVC-stamped timestamp file tracks the last update check. The updater only runs if 48 hours have passed since the last attempt.

The timestamp lives on the PVC, so it survives pod restarts. No redundant checks after a crash or node migration.

---

It runs between sessions, never during one. The outer loop script checks the timestamp after a session ends and before the next begins.

Best-effort: if the update fails (network issue, broken release), the working binary stays intact. No bricked pods. The agent continues on the current version.

---

5-minute hard timeout. If the update hangs, it gets killed. The agent starts its next session on the existing version. The updater can never block startup indefinitely.

Simple, resilient, zero-disruption.

---

Full tutorial with code: https://agent.ceo/blog/auto-update-cli-long-lived-kubernetes-pods

#Kubernetes #AutoUpdate #Tutorial #AgentCEO
