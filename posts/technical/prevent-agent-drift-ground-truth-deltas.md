---
title: "How to Prevent Agent Drift with Ground-Truth Deltas"
slug: "prevent-agent-drift-ground-truth-deltas"
date: 2026-09-10
category: technical
cluster: tutorials
tags: [agent-drift, ground-truth, session-start, hooks, multi-agent, tutorial]
description: "Practical tutorial on implementing session start hooks that sync agent state with reality: ground-truth deltas, the Ralph Loop pattern, and preventing redundant work in multi-agent fleets."
relatedPosts:
  - /blog/anatomy-agent-wakeup-cycle-first-60-seconds
  - /blog/hook-system-enforce-agent-discipline-runtime
  - /blog/writing-agent-instructions-claude-md-scale
  - /blog/daily-operations-ai-agent-fleet-cyborgenic
  - /blog/agent-state-recovery-patterns-cyborgenic
---

# How to Prevent Agent Drift with Ground-Truth Deltas

The most expensive bug in multi-agent systems is an agent that does not know what changed while it was sleeping.

It does not throw an error. It does not crash. It wakes up, reads its last-known state, and starts working — confidently, efficiently, on something that another agent already finished three hours ago. Or worse, it overwrites a founder fix with the stale version it still remembers. You do not find out until someone audits the git log and asks why commit `a3f8e1c` undid the work from commit `b7d2a09`.

We call this **agent drift**, and it is the single most common failure mode in production multi-agent fleets. This tutorial shows you how to eliminate it with a session start hook that takes two seconds to run.

## The Problem: Stale Context After Sleep

An agent's session ends. Maybe the pod restarted. Maybe the context window filled and the session compacted. Maybe it simply finished its task and went idle.

While it sleeps, the world moves:

- Another agent pushes commits to `origin/main` that change the codebase the sleeping agent was working on.
- The founder manually fixes a production bug, overriding work the agent had in flight.
- New directives arrive via NATS or the task management system, changing priorities.
- ConfigMaps update, environment variables shift, secrets rotate.
- Tasks the agent was planning to pick up get completed by someone else.

The agent wakes up. It has no idea any of this happened. Its internal state says "I was working on feature X, I got halfway through, time to finish." So it finishes — creating a merge conflict with the agent that already shipped feature X, or reverting the founder's hotfix because its local branch does not have it.

This is not a hypothetical. We see it weekly in any fleet running more than three agents.

## The Solution: Ground-Truth Delta

The fix is a `session_start` hook — a script that fires within two seconds of an agent waking up, before it reads its instructions, before it checks its inbox, before it decides what to work on.

The hook checks what changed since the agent's last active session and surfaces a structured block:

```
GROUND-TRUTH DELTA — what changed while you were away
────────────────────────────────────────────────────
Commits on origin/main since 2026-09-09T14:32:00Z:
  b7d2a09 fix(api): patch auth bypass in /v1/tokens (founder)
  c1e8f33 feat(kb): add embedding cache layer (cto-agent)

New directives:
  [PRIORITY] Ship billing integration before Thursday demo

Task state changes:
  task-a8f3e1d2: "Implement token rotation" → completed by cto-agent
────────────────────────────────────────────────────
```

The agent reads this block and immediately knows: do not touch the auth code (founder fixed it), do not start token rotation (already done), and billing is now the top priority. Two seconds of computation. Zero wasted work.

## What the Delta Checks

A production-grade delta hook queries five sources:

**1. Git history.** `git log --oneline --since="<last_session_timestamp>" origin/main` reveals every commit that landed while the agent slept. Pay special attention to commits authored by the founder — those represent manual interventions that override any agent's in-flight work.

**2. Directive changes.** Check the agent's directive file or control config for updates. If priorities shifted, the agent needs to know before it resumes yesterday's task.

**3. Configuration state.** ConfigMap checksums, environment variable diffs, secret rotation timestamps. An agent that assumes `DB_HOST` still points to the same database after a pod restart is an agent about to corrupt data.

**4. Task management state.** Query the TMS for tasks that changed status since last session — completed by peers, newly assigned, or marked blocked. This is how you prevent two agents from working the same task.

**5. Inbox messages.** Check for high-priority messages that arrived during sleep. A "STOP — do not deploy" message from the CEO is useless if the agent does not read it until after it deploys.

## The Ralph Loop Pattern

Our most battle-tested implementation of anti-drift is the Ralph Loop. The core principle: **one task per session, fresh context per task, no invented work.**

The agent's current task lives at `/agent-data/ralph/current-task.json`. On session start, the hook reads this file. If it contains a task, that is the agent's sole objective. No improvisation, no "while I am at it" side quests.

The backlog lives at `/agent-data/ralph/backlog.json`. Tasks flow in from three sources: NATS-delivered JSON payloads, files dropped in the inbox pending directory, and TMS assignments. The session start hook picks the highest-priority item from the backlog and writes it to `current-task.json`.

When a task completes, the hook archives it automatically and pulls the next item. Between tasks, the agent compacts its context — shedding all the accumulated state from the previous task so the next one starts clean.

This is anti-drift by design. The agent never wakes up and asks itself "what should I work on?" It reads `current-task.json` and does that. The delta hook ensures that task is still valid before work begins.

## Implementation Guide

Here is a minimal session start hook in Python:

```python
#!/usr/bin/env python3
"""session_start.py — Ground-truth delta hook."""

import subprocess, json, sys
from datetime import datetime, timezone
from pathlib import Path

TIMESTAMP_FILE = Path("/agent-data/.last_session_timestamp")

def get_last_timestamp():
    if TIMESTAMP_FILE.exists():
        return TIMESTAMP_FILE.read_text().strip()
    return "24 hours ago"

def get_git_delta(since):
    result = subprocess.run(
        ["git", "log", "--oneline", f"--since={since}", "origin/main"],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def main():
    since = get_last_timestamp()
    now = datetime.now(timezone.utc).isoformat()

    git_delta = get_git_delta(since)

    if git_delta:
        print(f"GROUND-TRUTH DELTA — changes since {since}", file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        print(f"Commits on origin/main:\n{git_delta}", file=sys.stderr)
        print("=" * 50, file=sys.stderr)

    # Update timestamp for next session
    TIMESTAMP_FILE.write_text(now)

if __name__ == "__main__":
    main()
```

Wire this into your Claude Code configuration as a session start hook. Output goes to `stderr`, which Claude Code surfaces as system-level context the agent sees before anything else. The timestamp file lives on a persistent volume so it survives pod restarts.

Store the timestamp after computing the delta, not before. If the hook crashes mid-run, the next session will re-check the same window rather than silently skipping it.

## What Changes

Before ground-truth deltas, agents wasted significant compute on redundant or conflicting work. An agent would spend 40 minutes implementing a feature, push it, and discover the CTO agent had already merged an equivalent implementation two hours earlier. The founder would fix a critical bug at 2 AM and wake up to find an agent had reverted it during its morning session.

After implementing the delta hook across our fleet, redundant work dropped to near zero. The pattern also changed how agents reason about their own work. Instead of "I was doing X, let me continue," the thinking became "X may or may not still be relevant — let me check the delta first." That shift from assumption to verification is the entire point.

Two seconds of computation at session start prevents hours of wasted work downstream. If you are running more than one agent, you need this hook.

---

*Ground-truth deltas are one building block of the cyborgenic operating system at [agent.ceo](https://agent.ceo). See how autonomous agents coordinate, verify, and self-correct — without stepping on each other's work.*
