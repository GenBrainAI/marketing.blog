---
platform: twitter
status: draft
date: 2026-11-05
note: "Blog launch: In-Cluster Deploys via Cloud Build"
---

## Thread: In-Cluster Deploys via Cloud Build API -- New Tutorial

New tutorial: how we gave our AI agents the power to deploy their own code from inside GKE.

Two scripts. No external CI. Full autonomy.

---

Script 1: cluster_build.py

- Uploads source tarball to GCS
- Submits build to Cloud Build via API
- Polls for completion
- Returns image URI

No Docker daemon. No GitHub Actions. The agent calls this from inside its pod.

---

Script 2: cluster-deploy.sh

- Wraps the build with deploy logic
- Runs `kubectl set image` with the new URI
- Waits for rollout completion
- Runs post-deploy smoke tests
- Rolls back if smoke tests fail

Supports gateway, agent, worker, and fullstack components. Handles dependency chains (agent depends on agent-base, so base builds first).

---

The DevOps agent now ships code end-to-end: write fix, build container, deploy, verify endpoint. One session. No human approval needed for routine deploys.

Full tutorial with code:

https://agent.ceo/blog/in-cluster-deploy-cloud-build-api-gke

---

#CloudBuild #GKE #Tutorial #AgentCEO
