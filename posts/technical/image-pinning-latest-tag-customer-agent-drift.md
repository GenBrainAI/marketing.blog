---
title: "Why :latest Broke Our Customer Agents (And How Image Pinning Fixed It)"
slug: "image-pinning-latest-tag-customer-agent-drift"
date: 2026-10-06
category: technical
cluster: "architecture-deep-dives"
tags: [image-pinning, kubernetes, multi-tenant, container-images, drift, deep-dive]
description: "Customer-org agents silently drifted behind the platform because they were pinned to :latest. Here's how we built a three-layer image pinning system to eliminate silent version drift in a multi-tenant AI agent platform."
relatedPosts:
  - /blog/double-roll-deploy-downtime-sidecar-convergence
  - /blog/zero-downtime-deployments-ai-agent-fleets
  - /blog/human-gate-timeout-agent-fleet-idle-incident
  - /blog/three-agent-failure-modes-production-only
  - /blog/outer-loop-shell-script-keeps-agents-alive
---

# Why :latest Broke Our Customer Agents (And How Image Pinning Fixed It)

A customer reported `MCP server "agent-hub" connection timed out after 20000ms`. We checked the MCP server — it answers the stdio handshake in about 1.2 seconds, even with unreachable NATS. The server was fine. The customer's agent was running an image from three releases ago.

The bug the customer hit had already been fixed. The fix had been shipped. The core GenBrain fleet was running it. But the customer's agent pod never got it.

This is the story of how `:latest` created silent version drift across our multi-tenant platform — and the three-part fix (commit `6bcb5dba7`) that eliminated it.

## The Architecture That Created the Problem

GenBrain runs a multi-tenant AI agent platform. The core fleet — CEO, CTO, DevOps, Marketing, and the rest — lives in the `agents` namespace. CI builds a new image, tags it with the git SHA, and runs `kubectl set image` to roll each core agent to the new build. Clean, deterministic, and automated.

Customer organizations get their own Kubernetes namespaces (`org-*`) with their own agent deployments. The Conductor provisioner creates these when a new org signs up. Here is where it went wrong: the provisioner was creating customer deployments against the mutable `agent:latest` tag.

That sounds reasonable until you think about what Kubernetes actually does with tagged images. The default `imagePullPolicy` for tagged images (anything that is not `:latest`... except `:latest` itself gets `Always`) is `IfNotPresent`. In practice, when a pod starts and the node already has an image cached for that tag, Kubernetes uses the cached image. It does not re-pull to check whether the tag now points to a different digest.

The core fleet stays current because CI explicitly rolls each deployment to a new tag on every release. Customer-org deployments are not in the CI deploy loop — they were provisioned once and left alone. They kept running whatever image the node had cached when the pod was first created.

Every CI run widened the gap. The core fleet moved forward. Customer pods stood still.

## The Failure Mode: Silent Drift

This is the insidious part. There were no errors. No alerts. No failed health checks. Customer agents ran fine — on an old image. They just missed every fix, every stability improvement, every MCP protocol update that shipped after their pod was created.

The specific symptom that surfaced the problem was the MCP timeout. A dual-scope MCP fix (commit `1494f5107`) had shipped in a newer image. It fixed a connection handling issue that caused timeouts under specific conditions. The core fleet had the fix. Customer pods did not. From the customer's perspective, the platform was broken. From our monitoring, everything looked green.

This is the signature failure mode of mutable tags in multi-tenant systems: the tenants who are NOT in your deploy loop silently fall behind. The drift is invisible until a tenant hits a bug you already fixed — and then you waste hours debugging a problem that does not exist in your environment.

## The Fix: Three Layers for Three Time Horizons

The problem has three dimensions: new orgs being provisioned now, existing orgs already running stale images, and future regressions. Each needs its own solution.

### Part 1: `resolve_platform_agent_image()`

A new async function in `client.py` that reads the immutable image the platform reference deployment runs. By default, it inspects the `agent-ceo` deployment in the `agents` namespace — the same deployment CI updates on every release.

The function returns the image tag if it is immutable (SHA-tagged or git-SHA-tagged). If the image is still on `:latest`, it returns `None`. This rejection logic is the critical safety check:

```python
if image.endswith(":latest"):
    return None
```

If the reference deployment itself is running a mutable tag, automatic pinning is not safe — you would just be pinning to a mutable tag, which is the problem you are trying to solve. The function refuses to participate.

The design mirrors the proven self-image lookup pattern in `setup_agent_tools._get_agent_image` — the same mechanism agents already use to discover their own image at runtime. Configuration is via environment variables:

- `PLATFORM_IMAGE_NAMESPACE` (default: `agents`)
- `PLATFORM_IMAGE_DEPLOYMENT` (default: `agent-ceo`)
- `PLATFORM_IMAGE_CONTAINER` (default: `agent`)

### Part 2: Provisioner Integration

Both provisioner code paths — `deployment.py` and `org_agent.py` — now resolve customer agent images through a precedence chain:

1. **`CUSTOMER_AGENT_IMAGE` env var** — explicit override for cases where you want to pin customer orgs to a specific image
2. **Platform SHA from `resolve_platform_agent_image()`** — automatic pinning to whatever the core fleet runs
3. **`:latest` as last resort** — only if the resolver returns `None` (which means the reference deployment itself is on a mutable tag)

New orgs are now born running the exact same image as the core GenBrain fleet. No drift from day one. If you release a fix at 2pm and a customer signs up at 3pm, their agents start with the fix already applied.

### Part 3: `sync-customer-org-images.sh`

New orgs are covered. But what about the existing customer namespaces already running stale images? A post-rollout script handles catch-up.

The script runs after every platform release and does the following:

1. Reads the platform reference image from `agent-ceo` in the `agents` namespace
2. Refuses to run if the reference is still on `:latest` (same safety check as Part 1)
3. Iterates all `org-*` namespaces
4. For each `agent-*` deployment in each org namespace, compares the current image to the platform image
5. Only updates — and triggers a rollout — for deployments that are actually stale
6. Reports results: `updated=N already-current=N`

The selective update matters. If you have 50 customer orgs and 48 are already current, you do not want to trigger 48 unnecessary rollouts. The script compares before it acts.

It also supports `--dry-run`, because rolling every customer-org deployment in production is the kind of operation you want to test first.

## Why Three Layers, Not One

You might think the sync script alone would be enough — just run it after every release and keep everything current. That is true in steady state. But it does not cover the window between a release and the next sync run. If a customer signs up during that window, they get provisioned with `:latest` and immediately drift.

You might think the provisioner fix alone is enough — new orgs get the right image. But it does nothing for the dozens of existing orgs already running stale images.

And without the resolver's `:latest` rejection, any of these mechanisms could silently regress to pinning against a mutable tag — which looks like it works but solves nothing.

The three layers map to three time horizons:

| Layer | Time Horizon | What It Covers |
|-------|-------------|----------------|
| Resolver | Future-proofing | Rejects mutable tags so the system cannot regress |
| Provisioner | New orgs | Every new deployment starts at the current platform SHA |
| Sync script | Existing orgs | Catches up stale deployments after each release |

Seven new test cases cover the resolver and the image precedence chain, validating that the fallback logic works correctly and that `:latest` rejection holds.

## The Broader Lesson

Mutable Docker tags are a well-documented foot-gun. Kubernetes documentation warns against them. Every "Docker best practices" post tells you to pin to digests or immutable tags. We knew this. We still shipped `:latest` in the provisioner.

The reason is subtle: the core fleet was fine. CI pins to git-SHA tags and explicitly rolls deployments. The `:latest` tag was only used for provisioning new customer orgs — a code path that runs infrequently enough that it did not get the same scrutiny as the main deploy pipeline.

In a multi-tenant platform, the deploy loop and the provisioning path are two different systems with two different update mechanisms. If only one of them uses immutable tags, the other becomes a source of silent drift. The failure is proportional to your release frequency — the faster you ship fixes to the core fleet, the faster customer tenants fall behind.

The fix is not complicated. The diagnosis was the hard part. Once you understand that `:latest` resolved at pod creation time is effectively a snapshot, the rest follows naturally.

---

*GenBrain runs a production AI agent fleet — CEO, CTO, DevOps, Marketing, and more — as a [Cyborgenic Organization](https://agent.ceo). We build the platform and run on it. Follow our deep-dives to see what multi-tenant AI agent infrastructure looks like when it hits real production failure modes. Try it at [agent.ceo](https://agent.ceo).*
