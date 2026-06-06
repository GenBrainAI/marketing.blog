---
title: "Your Agents Run Old Instructions Until You Restart Them: How We Built a CLAUDE.md Reconciler"
slug: "configmap-reconciler-claude-md-template-versioning"
date: 2026-10-24
category: marketing
cluster: case-studies
tags: [configmap, reconciler, versioning, kubernetes, multi-tenancy, case-study, building-in-public]
description: "When you update shared agent behavior rules, every existing customer org keeps running the old version. We built a three-phase reconciler that detects stale CLAUDE.md ConfigMaps, regenerates them, and patches them in place -- no pod restarts, no manual intervention."
relatedPosts:
  - /blog/zero-touch-customer-onboarding-platform-knowledge
  - /blog/image-pinning-latest-tag-customer-agent-drift
  - /blog/shared-neo4j-property-tenant-isolation-knowledge-graph
  - /blog/outer-loop-shell-script-keeps-agents-alive
  - /blog/crash-loop-fresh-pvc-has-resumable-session
---

# Your Agents Run Old Instructions Until You Restart Them: How We Built a CLAUDE.md Reconciler

You ship a critical behavior fix -- "never push to main without approval" -- and feel good about it. New customer orgs pick it up immediately. But every existing org? Their agents keep running without that rule. Silently. Indefinitely. Until someone manually recreates their ConfigMaps.

That was our situation. And the longer the platform ran, the worse it got.

## The Problem: Silent Version Drift

GenBrain runs customer org agents in Kubernetes. Each agent gets a CLAUDE.md file -- its behavior instructions -- mounted as a ConfigMap volume. These instructions are built from a shared template (`shared-customer-platform-ops.md`) combined with role-specific overlays.

When we update the shared template, the build pipeline uses it for new orgs. But existing orgs keep whatever version of CLAUDE.md was baked into their ConfigMap at creation time. There is no mechanism to propagate changes backward.

This is not a theoretical risk. Consider:

- You add a rule that agents must verify deployments before marking tasks complete. New orgs get the rule. Existing orgs skip verification.
- You tighten security constraints around secret handling. New orgs comply. Existing orgs operate under the old, looser policy.
- You fix a prompt injection mitigation in the shared template. New orgs are protected. Existing orgs are not.

Every customer org onboarded before the update is running stale instructions. The platform team has no visibility into which orgs are current and which are behind. And the drift compounds with every template update.

## Why Not Just Recreate All ConfigMaps?

We could have written a script that blasts through every org namespace and regenerates every ConfigMap. But that approach has problems.

First, you do not know which ConfigMaps actually need updating. Running a full regeneration on hundreds of namespaces when only the shared template changed is wasteful and noisy.

Second, you need a way to track whether a ConfigMap is current. Without versioning, you cannot distinguish "regenerated five minutes ago with the latest template" from "created six months ago and never touched."

Third, this should not require human intervention. If the platform team has to remember to run a script every time they update the shared template, someone will forget. And the drift will resume.

We needed something that tracks versions, detects drift, and fixes it automatically.

## The Solution: A Three-Phase Reconciler

We built this in commit `59a4100`. Three phases: version the template, reconcile on demand, automate with a CronJob.

### Phase 1: Template Versioning

The shared template (`shared-customer-platform-ops.md`) now carries a version annotation in its first line:

```html
&lt;!-- platform_ops_version: 3 --&gt;
```

A parser function extracts this version number:

```python
def _parse_platform_ops_version() -> int:
    try:
        first_line = _PLATFORM_OPS_TEMPLATE_PATH.read_text().split("\n", 1)[0]
        if "platform_ops_version:" in first_line:
            return int(first_line.split("platform_ops_version:")[1].strip().rstrip(" ->"))
    except (FileNotFoundError, ValueError):
        pass
    return 0
```

When a ConfigMap is created for a new org agent, the version number is embedded as a Kubernetes annotation: `agent.ceo/platform-ops-version: "3"`. This is the version tag that makes drift detection possible.

### Phase 2: The Reconciler Script

`scripts/reconcile_org_claude_md.py` is a Python script that does the actual work:

1. Reads the current template version via `_parse_platform_ops_version()`
2. Lists all `org-*` namespaces via `kubectl get ns`
3. For each namespace, lists deployments to find agent roles
4. For each agent, reads its CLAUDE.md ConfigMap and checks the version annotation
5. If the ConfigMap version is lower than the current template version, it regenerates the CLAUDE.md using the existing builder functions (`_build_org_admin_claude_md`, `_build_org_role_claude_md`, etc.)
6. Patches the ConfigMap with the new content and updates the version annotation

The script includes safety checks. Before patching, it validates that the generated CLAUDE.md contains a "Platform Capabilities" section. If the output looks malformed, it skips the patch and reports the failure.

Operational flags make this practical for both manual runs and automation:

- `--dry-run` previews what would change without applying anything
- `--force` regenerates even if the version matches (useful after fixing a bug in a builder function)
- Target specific namespaces or pass `--all` for every `org-*` namespace

After a run, you get a summary: "X updated, Y skipped (already current)."

### Phase 3: The CronJob

A Kubernetes CronJob (`cronjob-claude-md-reconcile.yaml`) runs the reconciler every 10 minutes:

- **Schedule:** `*/10 * * * *`
- **Scope:** all `org-*` namespaces
- **Service account:** `agent-workload` (needs ConfigMap read/patch across org-* namespaces)
- **Concurrency:** `Forbid` -- no overlapping runs
- **Timeout:** `activeDeadlineSeconds: 300` (5 minutes)
- **Resources:** 50m CPU / 128Mi memory (request), 200m CPU / 256Mi memory (limit)

Lightweight, bounded, and self-policing.

## How Updates Reach Running Agents

Here is the part that makes this work without downtime: Kubernetes automatically propagates ConfigMap changes to mounted volumes. The kubelet periodically syncs ConfigMap content -- typically within about 60 seconds. The agent's CLAUDE.md refreshes in place. No pod restart. No deploy. No rollout.

The next time the agent reads its instructions -- at session start, after compaction, or on any context reload -- it gets the updated version.

## The Full Lifecycle

Here is what happens end to end when the platform team ships a behavior update:

1. Platform team updates `shared-customer-platform-ops.md` and bumps the version from 3 to 4
2. New orgs provisioned after the update get version 4 automatically -- the builder reads the current template
3. Within 10 minutes, the CronJob runs, detects that existing org ConfigMaps still have version 3
4. The reconciler regenerates CLAUDE.md for each stale agent and patches the ConfigMap with version 4
5. Within about 60 seconds, the kubelet propagates the update to the mounted volume
6. The agent reads fresh instructions on its next session start -- no human intervention at any point

From template update to every agent in the fleet running the new instructions: under 12 minutes. Zero manual steps.

## What We Tested

Thirteen new tests cover the implementation: 4 for version parsing and annotation handling, 9 for reconciler logic (dry-run behavior, force mode, namespace targeting, skip-when-current, patch-when-stale, validation failures). All 61 tests in the suite pass.

The version parser handles edge cases: missing files return version 0, malformed version lines return 0, trailing whitespace and comment markers are stripped correctly. The reconciler handles partial failures gracefully -- if one namespace errors, it continues with the rest and includes the failure in the summary.

## The Takeaway

Configuration drift in multi-tenant agent platforms is not a maybe. It is a certainty. Every shared template update that does not propagate to existing tenants creates a silent fork. The longer you wait to address it, the more orgs diverge, and the harder it becomes to reason about what any given agent is actually doing.

The fix is not complicated. Version your templates. Annotate your ConfigMaps. Run a reconciler on a schedule. Kubernetes already handles the last mile -- ConfigMap volume mounts update automatically. You just need to give it the right content to propagate.

We went from "hope someone remembers to update the ConfigMaps" to "every agent in the fleet converges to the latest template within 12 minutes." Thirteen tests, one CronJob, zero human intervention.

---

**GenBrain AI builds the platform behind [agent.ceo](https://agent.ceo) -- where AI agents run as employees with real roles, real accountability, and instructions that stay current.** If you are building multi-tenant agent infrastructure and want to stop managing drift by hand, check out what we are shipping.
