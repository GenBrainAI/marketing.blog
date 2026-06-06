---
platform: twitter
status: draft
date: 2026-11-12
note: "Blog launch: Securing Your In-Cluster CI Pipeline"
---

## Thread: Securing Your In-Cluster CI Pipeline -- New Tutorial

New tutorial: two production incidents in our CI/CD pipeline. Both invisible until we looked.

Incident 1: Cloud Build tarballs excluded .git and node_modules but NOT .env, *.pem, *.key, credentials.json. Every build uploaded secrets to GCS.

---

Fix for secrets: switch from string matching to fnmatch glob patterns. 20+ exclusion patterns covering every secret file type. *credentials*.json catches what "credentials.json" as a prefix never would.

---

Incident 2: MCP servers registered in two scopes -- user (with crash-recovery wrapper) and local (without). Claude Code picks unpredictably. Local scope = no crash recovery. User scope = potential config conflicts.

Fix: one authoritative scope per server. Clean up conflicts at startup.

---

Both bugs shared a root cause: configs that were "good enough" during setup but had implicit assumptions that broke under real conditions.

Full walkthrough with detection, root cause, and fixes:

https://agent.ceo/blog/secure-in-cluster-ci-secrets-scope-conflicts

#Security #CICD #Tutorial #AgentCEO
