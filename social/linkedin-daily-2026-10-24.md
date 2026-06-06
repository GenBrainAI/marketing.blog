---
platform: linkedin
status: draft
date: 2026-10-24
note: "Blog launch — CLAUDE.md Reconciler"
---

## Post: New Blog -- CLAUDE.md Reconciler

New case study today. Yesterday we described the config drift problem: customer org agents running stale behavior definitions because ConfigMap updates don't propagate to existing orgs. Today, the fix.

We built a three-phase reconciler.

Phase 1: Version annotation. The shared behavior template carries a version string. When a ConfigMap is generated from the template, the version is embedded as a Kubernetes annotation. Every ConfigMap now carries metadata about which template version it was built from.

Phase 2: Reconciler script. It iterates over all org-* namespaces, reads each ConfigMap's version annotation, and compares it against the current template version. If the annotation is missing or outdated, the script patches the ConfigMap with the latest template content and updates the annotation. The operation is deterministic and idempotent -- running it twice produces the same result.

Phase 3: CronJob. The reconciler runs every 10 minutes, scanning all org-* namespaces automatically. No manual intervention, no deployment pipeline changes, no operator involvement.

The key insight that made this practical: Kubernetes propagates ConfigMap updates to mounted volumes automatically. When the reconciler patches a ConfigMap, the mounted file inside the pod updates without a restart. Agents pick up fresh instructions on their next session start.

We went from "agents silently running behavior definitions that could be months old" to "every agent is within 10 minutes of the latest template." Zero touch.

Full case study: https://agent.ceo/blog/configmap-reconciler-claude-md-template-versioning

#ConfigMap #Reconciler #Kubernetes #AgentCEO
