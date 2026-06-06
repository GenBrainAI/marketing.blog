---
platform: twitter
status: draft
date: 2026-10-24
note: "Blog launch — CLAUDE.md Reconciler"
---

## Thread: New Blog -- CLAUDE.md Reconciler

Yesterday: config drift means agents run stale instructions.

Today: we shipped the fix. A three-phase reconciler that keeps every agent's behavior definition current. Automatically.

---

Phase 1: Version annotation. The behavior template gets a version string. When we generate a ConfigMap from the template, the version is embedded as a Kubernetes annotation on the ConfigMap.

Now every ConfigMap carries metadata about which template version it was built from.

---

Phase 2: Reconciler script. Compares each ConfigMap's version annotation against the current template version. If stale, it patches the ConfigMap with the latest content and updates the annotation.

One script. Deterministic. Idempotent. Run it twice, same result.

---

Phase 3: CronJob. Runs the reconciler every 10 minutes. Scans all org-* namespaces. Patches any stale ConfigMaps.

ConfigMap updates propagate to mounted volumes automatically -- no pod restart needed. Agents read fresh instructions on their next session start.

---

From "agents silently running outdated behavior" to "every agent gets updates within 10 minutes." Zero manual intervention.

Read the full case study: https://agent.ceo/blog/configmap-reconciler-claude-md-template-versioning

#ConfigMap #Reconciler #Kubernetes #AgentCEO
