---
platform: linkedin
status: draft
date: 2026-10-29
note: "Blog launch — How to Keep CLI Tools Current in Long-Lived K8s Pods"
---

## Post: New Blog -- How to Keep CLI Tools Current in Long-Lived K8s Pods

New tutorial published today. Yesterday we described the problem: Docker images snapshot a CLI version at build time, but long-lived pods run for weeks. Your agents fall behind on updates. Redeploying just for a CLI bump causes downtime you do not need.

Here is the solution we built: a PVC-stamped, time-gated, best-effort self-updater.

Time-gating with a 48-hour cadence. A timestamp file on the PVC tracks when the last update check happened. The updater only runs if 48 hours have passed since the last attempt. This file lives on the PVC, so it survives pod restarts -- no redundant checks after a crash or migration.

Session-boundary execution. The update runs between agent sessions, never during one. The outer loop script checks the timestamp after a session ends and before the next one begins. A live agent process is never interrupted for an update.

Best-effort design. If the update command fails -- network issue, broken release, whatever -- the working binary stays intact. The agent continues with the current version. No bricked pods. No rollback logic needed because the previous version was never removed.

Timeout protection. A 5-minute hard timeout on the update process. If it hangs, it gets killed and the agent starts its next session on the existing version. The updater can never block startup indefinitely.

Simple. No operator. No sidecar. No webhook. Just a shell script with a timestamp file.

Full tutorial: https://agent.ceo/blog/auto-update-cli-long-lived-kubernetes-pods

#Kubernetes #AutoUpdate #Tutorial #AgentCEO
