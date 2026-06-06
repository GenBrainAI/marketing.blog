---
title: "The 30-Second Crash Loop That Wasn't a Crash"
slug: "crash-loop-fresh-pvc-has-resumable-session"
date: 2026-10-17
category: marketing
cluster: case-studies
tags: [crash-loop, session-resume, precondition-check, self-healing, case-study, building-in-public]
description: "Every pod restart triggered 30 seconds of fake crash diagnostics before the agent started working. The cause: a --continue flag with nothing to continue. The fix: check before you retry."
relatedPosts:
  - /blog/outer-loop-shell-script-keeps-agents-alive
  - /blog/ceo-relaunch-loop-strategy-inbox-flood
  - /blog/crash-resilient-mcp-wrapper-startup-race
  - /blog/human-gate-timeout-agent-fleet-idle-incident
  - /blog/level-triggered-edge-triggered-agent-pending-work
---

# The 30-Second Crash Loop That Wasn't a Crash

Every time we rolled a pod or archived a session in our cyborgenic organization, the same thing happened. The CEO agent's terminal filled with retry messages, backoff timers, and crash diagnostics. For thirty seconds, the founder would watch the agent appear to fight for its life. Then it would finally start up and work perfectly.

Every. Single. Restart.

Thirty seconds of noise. Zero value. And nobody questioned it for weeks because the agent always came up eventually. Self-healing worked -- just slowly.

## The Symptom: Crash Diagnostics With No Crash

Our wrapper script (`claude_wrapper.sh`) manages the lifecycle of every agent in the fleet. When Claude Code exits unexpectedly, the wrapper detects the non-zero exit code, logs the failure, and retries with exponential backoff. This is the self-healing loop that keeps agents running through transient failures -- network hiccups, OOM kills, MCP server timeouts.

The problem was what appeared in the logs after every pod roll:

```
Crash detected! Retrying in 2 seconds...
Crash detected! Retrying in 4 seconds...
Crash detected! Retrying in 8 seconds...
NUCLEAR FALLBACK: Starting fresh session...
```

Three retries. Exponential backoff. 2 + 4 + 8 = 14 seconds of pure wait time, plus the startup overhead of three failed launches. Around 30 seconds total before the wrapper gave up on resuming and started a fresh session.

The nuclear fallback was doing the right thing. It just took a scenic route to get there.

## The Root Cause: --continue With Nothing to Continue

The wrapper always passed `--continue` when starting Claude Code. This flag tells Claude Code to resume the previous conversation from its transcript files -- the `.jsonl` files stored in `~/.claude/projects/`.

On a fresh PVC after a pod roll, that directory is empty. After a session archive, where old transcripts are cleaned up, the directory exists but contains no transcript files. In both cases, there is no previous conversation.

When `claude --continue` runs with no conversation to resume, it does exactly the right thing: exits with code 1 and the message "No conversation found to continue."

Here is where the design flaw lived. The wrapper's self-healing loop interprets ANY non-zero exit code as a crash. It does not distinguish between failure modes. So the sequence played out identically every time:

1. Wrapper starts `claude --continue`
2. Claude Code finds no conversation to resume, exits with code 1
3. Wrapper interprets exit 1 as a crash, waits 2 seconds
4. Wrapper retries `claude --continue`
5. Same result -- no conversation exists, exit 1
6. Wrapper waits 4 seconds (exponential backoff)
7. Third retry, same result, waits 8 seconds
8. After three failures, nuclear fallback kicks in
9. Wrapper strips `--continue` and starts a fresh session
10. Claude Code starts normally

The agent was never crashing. There was no instability, no resource contention, no transient error. The wrapper was retrying an operation that could never succeed -- asking Claude Code to resume a conversation that did not exist -- and treating the inevitable failure as evidence of a crash.

## Why Retrying Could Never Help

This is the critical distinction the wrapper was missing. There are two fundamentally different categories of non-zero exit:

**Transient failures** -- connection refused, timeout, temporary resource exhaustion. These might succeed on retry. Exponential backoff is the correct strategy.

**Structural failures** -- the prerequisite for the operation does not exist. No transcript file means no conversation to resume. Retrying will not create a transcript. The hundredth attempt will fail for exactly the same reason as the first.

The wrapper treated both identically. Every non-zero exit got the same retry loop with the same backoff timers. It was the equivalent of retrying a "file not found" error and hoping the file materializes on the fourth attempt.

## The Fix: Precondition Checking (Commit aef74842d)

The fix added a `has_resumable_session()` function that checks BEFORE launching Claude Code whether there is actually a conversation to resume:

```bash
has_resumable_session() {
    local projects_dir="/home/appuser/.claude/projects"
    [[ -d "$projects_dir" ]] || return 1
    local found
    found=$(find "$projects_dir" -name "*.jsonl" \
            -type f -size +0c -print -quit 2>/dev/null)
    [[ -n "$found" ]]
}
```

Four design decisions in eight lines:

1. **Check the directory exists.** If `~/.claude/projects/` is missing entirely (fresh PVC), return false immediately. No filesystem scan needed.
2. **Look for `.jsonl` files.** Claude Code stores transcripts in JSON Lines format. These are the files `--continue` needs to resume.
3. **Require non-empty files.** The `-size +0c` flag skips zero-byte files. An empty `.jsonl` is not a valid conversation -- it is a leftover from an interrupted write or a failed initialization. Passing `--continue` with only empty transcripts would fail just as reliably as passing it with no transcripts at all.
4. **Exit on first match.** The `-print -quit` combination stops scanning the moment it finds one valid file. No need to enumerate the entire directory tree. On a PVC with dozens of project subdirectories, this avoids unnecessary I/O.

The wrapper's start path now uses this check before deciding whether to pass `--continue`:

```bash
elif ! has_resumable_session; then
    echo "No resumable conversation found — starting fresh Claude session..."
    local fresh_flags
    fresh_flags=$(echo "$CLAUDE_FLAGS" | sed 's/--continue//')
    claude $fresh_flags
```

When `has_resumable_session()` returns false, the wrapper strips `--continue` from the flags and starts a fresh session immediately. No crash loop. No retry. No backoff. No nuclear fallback. The agent is operational in under two seconds instead of thirty.

When the function returns true -- meaning valid transcripts exist -- the wrapper passes `--continue` as before, and the agent resumes its previous conversation. The happy path is unchanged.

## What Changed Operationally

Before the fix, every pod roll and every session archive produced 30 seconds of false crash diagnostics. In a fleet of seven agents, a rolling restart meant 3.5 minutes of cumulative wasted time. More importantly, it meant 3.5 minutes where agents were not processing tasks, not reading inboxes, not responding to escalations.

After the fix, cold starts are indistinguishable from warm starts in terms of speed. The wrapper makes the right decision on the first attempt. The logs show a clean "No resumable conversation found -- starting fresh" instead of three rounds of crash diagnostics followed by a nuclear fallback.

The false crash reports also disappeared from our monitoring. We had been filtering them out mentally -- "oh, that's just the startup noise" -- which is exactly the kind of normalization that makes you miss a real crash when one finally happens.

## The Broader Lesson: Retry Loops Should Classify Exits

Self-healing retry loops are essential for production agent infrastructure. Agents crash. MCP servers lose connections. Kubernetes evicts pods. You need a loop that detects failure and retries.

But "retry everything the same way" is a trap. Exit code 1 with "no conversation found" is structurally different from exit code 1 with "connection refused." The first will never succeed on retry -- the precondition is missing, and no amount of waiting will create it. The second might succeed -- the connection might come back.

The general principle: **check the precondition before attempting the operation, not after it fails.** A precondition check is cheaper than a retry, more informative than an error message, and eliminates an entire class of false alarms.

For retry loops specifically, the design rule is: **classify the exit, then choose the strategy.** Some exits should trigger retry with backoff. Some exits should trigger immediate fallback. Some exits should trigger an alert. Treating them all as "crash, retry" wastes time on the structural failures and masks real crashes in a flood of false positives.

We applied this fix to both the deployed `wrappers/` copy and the legacy `/app` copy so that every agent in the fleet gets the same clean startup behavior.

Thirty seconds of fake crashes, fixed by eight lines of bash that ask one question: is there actually something to resume?

---

Running autonomous AI agents in production means encountering failure modes that do not exist in demos or sandboxes. At [agent.ceo](https://agent.ceo), we build the platform that manages these agents -- and we share every incident because the lessons only matter if they are public. If you are running AI agents and want infrastructure that handles these failure modes for you, check out what we are building.
