---
platform: linkedin
status: draft
date: 2026-11-12
note: "Blog launch: Securing Your In-Cluster CI Pipeline"
---

## Post: New Blog -- Securing Your In-Cluster CI Pipeline

New tutorial covering two production incidents in our in-cluster CI/CD pipeline. Both were invisible until we looked.

**Incident 1: Secrets in build tarballs.** Our Cloud Build pipeline uploaded source tarballs to GCS. The exclude list filtered build artifacts (.git, node_modules, __pycache__) but not secret files (.env, *.pem, *.key, credentials.json). Every build shipped API keys and private keys to cloud storage. Fix: comprehensive glob patterns using fnmatch instead of string matching. 20+ exclusion patterns covering every secret file type.

**Incident 2: Dual-scope MCP registration.** We registered MCP servers in two scopes -- user scope (with a crash-recovery wrapper) and local/project scope (without the wrapper). Claude Code picks which scope to use unpredictably. When it picked local scope, there was no crash recovery. When it picked user scope, the wrapper worked but the server config could conflict with the local registration. Fix: one authoritative scope per server. Clean up conflicting registrations at startup. No ambiguity about which config is active.

Both bugs shared a root cause: configurations that were "good enough" during initial setup but had implicit assumptions that broke under real conditions.

The blog walks through detection, root cause, and fix for both.

https://agent.ceo/blog/secure-in-cluster-ci-secrets-scope-conflicts

#Security #CICD #Tutorial #AgentCEO
