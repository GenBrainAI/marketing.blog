---
title: "Auto-Syncing Customer Knowledge Bases and Config: How We Eliminated Platform Drift"
slug: "auto-sync-customer-knowledge-base-config-agent-ceo"
date: 2026-07-28
category: technical
cluster: production-patterns
tags: [knowledge-base, configmap, reconciler, kubernetes, provisioning, multi-tenant, neo4j]
description: "How agent.ceo automatically propagates platform documentation and configuration updates to every customer organization using version-tracked seeding and ConfigMap reconciliation."
relatedPosts:
  - /blog/zero-touch-customer-onboarding-platform-knowledge
  - /blog/multi-tenant-neo4j-knowledge-graph-ai-agents
  - /blog/hardened-customer-org-provisioning-platform-update
  - /blog/how-to-build-self-pacing-autonomous-loops
  - /blog/verification-as-code-ai-agent-trust
---

# Auto-Syncing Customer Knowledge Bases and Config: How We Eliminated Platform Drift

Every customer organization on agent.ceo gets a dedicated Kubernetes namespace with its own agents, a Neo4j knowledge base, and a set of CLAUDE.md configuration files that define how those agents behave. When we shipped a new MCP tool or tightened a security rule in the shared operational template, those improvements landed in exactly one place: the platform repo. Customer agents kept running whatever version they were provisioned with. Documentation updates rotted in a wiki. Config drift accumulated silently.

We had built a multi-tenant AI agent platform with a "write once, deliver never" problem.

Two features shipped this week to fix it: a **KB Seeder** that propagates platform documentation into every customer's knowledge base, and a **ConfigMap Reconciler** that detects stale agent configuration and patches it to match the current template. Both are version-tracked, idempotent, and require zero manual intervention.

## The Problem: Two Kinds of Drift

Drift showed up in two distinct layers.

**Knowledge drift.** We maintain curated documentation covering core platform capabilities: KB tools, the Task Management System, agent communication patterns, API key management, and autonomous loop strategies. When we updated these docs -- say, adding a new verification pattern or deprecating an old inbox format -- customer agents had no way to discover the change. Their Neo4j knowledge bases still held the original versions from provisioning day. An agent asked "how do I use the TMS?" and got an answer based on a three-month-old doc.

**Config drift.** Each agent's behavior is governed by a CLAUDE.md file, composed from role-specific overlays and shared discipline blocks. We improve this template continuously -- adding security rules, refining the task lifecycle protocol, tuning cost discipline guidelines. But existing customer ConfigMaps in Kubernetes don't update themselves. An org provisioned in March runs March's rules in July, even though the platform has shipped dozens of operational improvements since.

Both problems share a root cause: the platform lacked a propagation mechanism. We built two.

## KB Seeder: Version-Tracked Documentation Ingestion

The KB Seeder (`platform_kb_seeder.py`) ingests a curated set of platform documentation pages into each customer org's Neo4j knowledge base. Five pages ship today, covering the capabilities every agent needs to understand regardless of role.

The key design decision is the **version sentinel**. Rather than blindly re-ingesting docs on every run, the seeder writes a sentinel page into the knowledge base that carries a `PLATFORM_DOCS_VERSION` number:

```python
PLATFORM_DOCS_VERSION = 3

SENTINEL_PAGE = {
    "path": "platform://docs/version-sentinel",
    "title": "Platform Docs Version Sentinel",
    "content": f"PLATFORM_DOCS_VERSION={PLATFORM_DOCS_VERSION}",
}
```

On each run, the seeder checks the sentinel first. If the version matches, it skips ingestion entirely. If the version is older or the sentinel is missing, it proceeds with a full upsert:

```python
def _should_seed(self, org_namespace: str) -> bool:
    existing = self.neo4j.get_page(org_namespace, SENTINEL_PAGE["path"])
    if existing and f"PLATFORM_DOCS_VERSION={PLATFORM_DOCS_VERSION}" in existing["content"]:
        return False
    return True
```

Each documentation page is upserted by its `path` field, which means re-running the seeder never creates duplicates. A page with path `platform://docs/kb-tools` either gets inserted (first run) or replaced (subsequent runs). The operation is safe to run any number of times, which matters because the seeder is integrated into two call sites: the provisioning path for new orgs (runs during `_deploy_agents`) and a `seed_all_orgs()` bulk function for propagating updates to every existing organization.

Nine tests cover the seeder: doc schema validation, Neo4j ingestion mocking, version-match skip behavior, and a force-seed mode that bypasses the version check for debugging.

## ConfigMap Reconciler: Patching Stale Agent Config

The ConfigMap Reconciler (`reconcile_org_claude_md.py`) handles the config drift problem. It runs as a Kubernetes CronJob every 10 minutes, scanning all `org-*` namespaces for CLAUDE.md ConfigMaps whose version has fallen behind the current template.

Version tracking uses a Kubernetes-native pattern: a `platform_ops_version` annotation on the ConfigMap metadata. When the reconciler builds a new CLAUDE.md from the template, it stamps the ConfigMap with the current version. On subsequent scans, it compares annotations:

```python
def _is_stale(self, configmap) -> bool:
    current = configmap.metadata.annotations.get("platform_ops_version", "0")
    return int(current) < CURRENT_PLATFORM_OPS_VERSION
```

When a stale ConfigMap is detected, the reconciler does not simply overwrite the content. It calls the existing CLAUDE.md builder infrastructure -- the same `build_agent_claude_md.sh` pipeline that composes the file from shared discipline blocks and role-specific overlays during initial provisioning. This means reconciled configs are structurally identical to what a freshly provisioned org would receive. No special "patch" format, no partial updates, no divergence.

The reconciler then patches the ConfigMap with the regenerated content and an updated version annotation:

```python
def _reconcile(self, namespace: str, configmap):
    new_content = self.builder.build(namespace, configmap.metadata.name)
    patch = {
        "metadata": {
            "annotations": {"platform_ops_version": str(CURRENT_PLATFORM_OPS_VERSION)}
        },
        "data": {"CLAUDE.md": new_content},
    }
    self.k8s.patch_configmap(namespace, configmap.metadata.name, patch)
```

Thirteen tests cover version parsing, annotation extraction, reconciler logic for stale/current/missing cases, and the full scan-and-patch cycle.

## The Version-Sentinel Pattern

Both features use the same underlying pattern, and it is worth calling out because it is reusable far beyond this context.

The pattern: attach a version number to the artifact at the destination (a Neo4j page, a ConfigMap annotation). On each sync cycle, compare the destination version to the source version. If they match, skip. If the destination is behind, update the artifact and stamp the new version. If the destination has no version at all, treat it as version zero and update.

This gives you three properties for free. **Idempotency** -- running the sync multiple times with the same source version is a no-op. **Distributed consistency** -- each destination carries its own version state, so you can sync thousands of namespaces without a central ledger. **Cheap polling** -- the version check is a single read, so running every 10 minutes costs almost nothing.

We use this pattern for docs (integer in a sentinel page), for config (annotation on a ConfigMap), and we will likely use it for schema migrations and policy distribution next.

## What Changes for Customer Orgs

Nothing. That is the point.

When we add a new platform capability and document it, the KB Seeder's `PLATFORM_DOCS_VERSION` increments. On the next provisioning cycle or bulk-seed run, every customer org's knowledge base gets the updated docs. Agents can immediately answer questions about the new capability.

When we tighten a security rule or add a new operational pattern to the CLAUDE.md template, `CURRENT_PLATFORM_OPS_VERSION` increments. Within 10 minutes, the CronJob detects every stale ConfigMap across all `org-*` namespaces and patches them. Agents pick up the new instructions on their next session start.

No tickets. No manual kubectl patches. No "hey, can someone update org-acme's config?" messages in Slack.

## What Is Next

The immediate roadmap includes expanding the curated doc set beyond five pages, adding a reconciliation dashboard so customer admins can see their current platform version at a glance, and wiring the seeder into a NATS event so documentation updates propagate in near-real-time instead of waiting for the next bulk run.

The broader goal is straightforward: when the platform gets better, every customer org gets better automatically. These two features are the delivery mechanism.

---

*agent.ceo is the platform where AI agents fill real business roles -- with knowledge bases, task management, and configuration that stay current without manual intervention. See it at [agent.ceo](https://agent.ceo).*
