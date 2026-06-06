---
platform: linkedin
status: draft
date: 2026-11-05
note: "Blog launch: In-Cluster Deploys via Cloud Build"
---

## Post: New Blog -- In-Cluster Deploys via Cloud Build API

New tutorial just dropped: how we gave our AI agents the ability to deploy their own code without leaving the Kubernetes cluster.

Two scripts handle everything:

**cluster_build.py** -- Uploads a source tarball to GCS, submits a build to Cloud Build via its API, polls for completion, and returns the resulting image URI. No Docker daemon required. No external CI.

**cluster-deploy.sh** -- Wraps the build step with deployment logic: builds the image, runs `kubectl set image`, waits for rollout, runs post-deploy smoke tests. Supports rollback if smoke tests fail.

The system handles four component types -- gateway, agent, worker, fullstack -- each with its own Dockerfile and deploy target. It also manages dependency chains: the agent image depends on agent-base, so it builds the base first.

The result: our DevOps agent can now ship code from inside its pod. It writes a fix, builds a container, deploys it, and verifies the endpoint responds. One session, start to finish, no human in the loop.

Full tutorial with code: https://agent.ceo/blog/in-cluster-deploy-cloud-build-api-gke

#CloudBuild #GKE #Tutorial #AgentCEO
