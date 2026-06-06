---
title: "Tutorial: How to Keep CLI Tools Current in Long-Lived Kubernetes Pods"
slug: "auto-update-cli-long-lived-kubernetes-pods"
date: 2026-10-29
category: technical
cluster: "tutorials"
tags: [kubernetes, auto-update, cli, self-healing, tutorial, building-in-public]
description: "A practical tutorial on building a time-gated, PVC-stamped self-updater for CLI tools baked into Docker images — so long-running pods stay current without redeployment or downtime."
relatedPosts:
  - /blog/outer-loop-shell-script-keeps-agents-alive
  - /blog/crash-resilient-mcp-wrapper-startup-race
  - /blog/image-pinning-latest-tag-customer-agent-drift
  - /blog/fsgroup-change-policy-onrootmismatch-redeploy-outage
  - /blog/zero-downtime-deployments-ai-agent-fleets
---

# Tutorial: How to Keep CLI Tools Current in Long-Lived Kubernetes Pods

Your Docker image bakes a CLI tool at build time. The Dockerfile runs an installer script, captures whatever version is latest that day, and the binary ships with the image. Clean. Reproducible. And immediately stale.

In the [agent.ceo](https://agent.ceo) fleet, agent pods run for days or weeks between image rebuilds. Claude Code releases new versions frequently. Our agents were falling further behind with every passing day.

The obvious fix is "just redeploy." But obvious fixes carry hidden costs.

## Why Redeployment Is Not the Answer

Redeploying an agent pod is not a zero-cost operation. Each redeployment triggers a cascade:

- **fsGroupChangePolicy overhead**: Without `OnRootMismatch`, Kubernetes recursively re-chowns the entire PVC on mount. Gigabytes of session history means minutes of startup delay.
- **Recreate strategy interruption**: ReadWriteOnce PVCs force Recreate strategy. The old pod dies before the new one starts. That is downtime.
- **Session loss**: A running session gets killed. Context is lost. The agent cold-starts, re-reads its inbox, rebuilds understanding of whatever task it was mid-way through.

Redeploying on every CLI release means eating all three costs on a cadence you do not control. We needed a way to update the binary in place, between sessions, without redeployment.

## The Design: A Time-Gated, PVC-Stamped Self-Updater

The solution is a shell script -- `update_claude_cli.sh` -- that runs at the top of the agent's relaunch loop, between sessions. It checks whether enough time has passed since the last update attempt, and if so, re-runs the canonical installer that the Docker image already ships.

Three design principles drive every decision in this script.

### Principle 1: Stamp on PVC, Not in Memory

The update interval is tracked by a timestamp file on the PVC:

```bash
STAMP_FILE="/agent-data/claude-session/.last_claude_update"
```

Not an in-memory timer. Not a variable that resets when the wrapper restarts. A file on persistent storage. The timestamp survives pod restarts, session relaunches, OOM kills. Pod dies and comes back -- stamp file is still there. No redundant updates. No lost state.

### Principle 2: Best-Effort, Never Blocking

The script never exits non-zero. Never. A failed update -- transient network issue, npm registry timeout, corrupted download -- leaves the currently working binary in place. The agent starts its next session with the old version. On the next eligible loop iteration (after the cadence interval expires), it tries again.

If the update mechanism can break the agent, you have traded one problem (stale CLI) for a worse one (dead agent).

### Principle 3: Between Sessions Only

The wrapper (`claude_wrapper.sh`) calls the updater at the top of the relaunch loop -- after the previous session exits, before the next one starts. The new binary installs into `~/.local` and takes effect on the next launch. A live session is never disrupted.

```bash
# In claude_wrapper.sh, at the top of the relaunch loop:
# (before starting a new claude session)
update_claude_cli.sh  # best-effort, never blocks
```

No mid-session binary swaps. No corrupted processes. The next session picks up the new version.

## The Implementation

Here is how each piece works.

### Environment Variables

Everything is overridable for testing:

```bash
CLAUDE_UPDATE_INTERVAL_HOURS=48   # default cadence
STAMP_FILE="/agent-data/claude-session/.last_claude_update"
INSTALLER="/app/install_cli.sh"   # canonical install path from Docker image
```

The 48-hour default means agents check for updates roughly every two days. Aggressive enough to stay current. Conservative enough to avoid unnecessary churn.

### Safety Guards

Before attempting any update, the script runs through a series of guards:

1. **CLI vendor check**: Only runs for `CLI_VENDOR=claude-code`. If the pod runs a different CLI tool, the script exits cleanly. You do not want a Claude updater accidentally firing in a pod running something else.

2. **Running process check**: `pgrep -x claude` -- if a Claude process is currently running, skip. The normal call path (top of the relaunch loop) means no Claude process should be running. But this guards against stray callers or manual invocations.

3. **Installer existence check**: Verifies that the installer script (`/app/install_cli.sh`) actually exists in the image. If someone ships an image without it, the script exits cleanly instead of failing noisily.

### The Cadence Check

The core timing logic:

```bash
now=$(date +%s)
last=$(cat "$STAMP_FILE" 2>/dev/null || echo 0)
age_hours=$(( (now - last) / 3600 ))
if [[ "$last" -gt 0 && "$age_hours" -lt "$INTERVAL_HOURS" ]]; then
    log "skip — last update ${age_hours}h ago (< ${INTERVAL_HOURS}h interval)"
    exit 0
fi
```

If the stamp file does not exist (first run), `last` defaults to `0`, and the check falls through -- triggering an update. If the interval has not elapsed, exit. Simple arithmetic. No cron jobs. No external schedulers.

### Stamp the Attempt, Not the Success

This is the subtlety that prevents retry storms:

```bash
# Stamp the attempt time BEFORE running the installer
date +%s > "$STAMP_FILE"
```

If the installer fails (network timeout, registry down), the stamp file already records the attempt. The next relaunch loop sees "updated 0 hours ago" and skips. You do not get a pod hammering a broken registry on every session restart.

A failing installer retries after the full cadence interval, not on every loop. npm down for two hours? Your agent tries once, fails, moves on. Tries again 48 hours later. No retry storm. No log spam.

### Time-Bounded Installation

Network-dependent installers can hang. Unresponsive CDN, DNS timeout, half-open TCP connection -- any of these can block the installer indefinitely, which means the agent never starts its next session.

```bash
if command -v timeout &>/dev/null; then
    timeout 300 bash "$INSTALLER"
else
    bash "$INSTALLER"
fi
```

Five minutes maximum. If the installer has not finished in 300 seconds, it gets killed. The old binary is still in place. The agent starts its session. If the `timeout` command is not available in the image (some minimal base images strip it), the script runs unbounded rather than skipping the update entirely. Pragmatic degradation.

### Version Reporting

Observability matters. The script captures before and after versions:

```bash
before="$(claude --version 2>/dev/null | head -1)"
# ... run installer ...
after="$(claude --version 2>/dev/null | head -1)"
if [[ "$before" != "$after" ]]; then
    log "updated: ${before:-unknown} -> ${after:-unknown}"
else
    log "already latest (${after:-unknown})"
fi
```

When you run a fleet, you need to know which version each pod is running and when it changed. `updated: 1.0.23 -> 1.0.24` in the pod logs tells you exactly when the transition happened. Trivially greppable.

### Force Mode

Sometimes you need to skip the cadence check. Critical bug fix upstream. Security patch. You want every agent updated now.

```bash
update_claude_cli.sh --force   # bypass cadence check
```

Force mode skips the time check but preserves every other safety guard. It still checks for running processes. It still time-bounds the installer. It still stamps the attempt. Force does not mean unsafe.

## The Pattern: Generalizing Beyond Claude Code

This tutorial uses Claude Code, but the pattern applies to any CLI tool baked into a Docker image. `kubectl`, `helm`, `terraform`, `gh` -- any binary that ships new versions faster than you rebuild images.

The six principles:

1. **Stamp on PVC, not in memory** -- the update timer must survive pod restarts
2. **Best-effort, never fail** -- a broken update must leave the working binary intact
3. **Between sessions** -- update when the tool is not in use
4. **Time-bound the installer** -- network-dependent installs need a timeout
5. **Stamp the attempt, not the success** -- prevents retry storms on persistent failures
6. **Log version transitions** -- always report before/after for observability

Miss any one of these and you will discover the failure mode in production. Skip the PVC stamp and your pod updates on every restart. Skip the timeout and a hanging installer blocks your workload. Stamp only success and a persistent failure retries on every loop. We hit all of these before arriving at the current design.

## What This Buys You

Our agents now stay within 48 hours of the latest Claude Code release. No redeployment. No downtime. No session interruption. When a new version ships with a fix we need, every agent in the fleet picks it up organically within two days -- or immediately with `--force`.

The script is 80 lines of bash. No external dependencies. No daemon. No cron job. Just a function call at the right point in the lifecycle, with the right set of guards.

Infrastructure that disappears into the background and just works.

---

*We run a fleet of AI agents as a real company at [agent.ceo](https://agent.ceo). Every tutorial on this blog comes from production code, production failures, and production fixes. If you are building with AI agents in Kubernetes, we have probably hit your bug already.*
