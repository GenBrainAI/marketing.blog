---
title: "How to Build an Observation Log That Makes AI Agents Self-Improving"
slug: "observation-log-self-improving-ai-agents"
date: 2026-09-24
category: technical
cluster: tutorials
tags: [observation-log, cybernetic-loop, self-improving, action-classification, outcome-detection, tutorial]
description: "A practical tutorial on designing a structured observation log that records significant agent actions and outcomes, enabling pattern detection, failure analysis, and automated policy generation."
relatedPosts:
  - /blog/cybernetic-learning-loop-agents-write-own-rules
  - /blog/detect-break-agent-retry-loops-production
  - /blog/hook-system-enforce-agent-discipline-runtime
  - /blog/prevent-agent-drift-ground-truth-deltas
  - /blog/ralph-loop-one-task-per-session-anti-drift
---

# How to Build an Observation Log That Makes AI Agents Self-Improving

An AI agent that cannot remember what it did yesterday is stuck making the same mistakes forever. But an agent that records every significant action and its outcome -- and feeds those records into a pattern detector -- starts writing its own rules. That is the difference between a tool and a system that learns.

At [agent.ceo](https://agent.ceo), we run seven AI agents 24/7. Each one records its significant actions into a structured observation log. A cybernetic learner reads those observations, detects patterns (repeated failures, stuck loops, recovery sequences), and compiles them into enforcement policies. The agents literally improve themselves.

This tutorial walks you through building that observation log from scratch. We will cover what to record, how to classify actions, how to detect outcomes automatically, and how the log feeds a self-improving system.

## The Core Design: Append-Only JSONL

The observation log is a single append-only JSONL file at `/agent-data/cybernetic/observations.jsonl`. Each line is one JSON object representing one significant action and its outcome.

Why JSONL? Three reasons: append-only writes are safe under concurrent access, line-oriented format makes streaming reads trivial, and you can `tail -f` the file to watch agent behavior in real time.

We cap the file at 10,000 observations (`MAX_OBSERVATIONS`). When the log exceeds this limit, the oldest entries are pruned. This keeps the file manageable while retaining enough history for meaningful pattern detection.

The log is written from three call sites:

- **`post_tool_use.py`** -- the success path, recording every significant tool call after it completes
- **`post_tool_use_failure.py`** -- a separate failure hook for tool executions that crash entirely before the normal hook fires
- **`autonomous_stop.py`** -- handles deferred outcome resolution (more on this below)

## Step 1: Filter for Significance

The first mistake teams make is logging everything. If you record every file read and every directory listing, you drown the signal in noise. Our `_is_significant()` function gates recording -- if it returns False, the action is silently ignored.

Here is what we consider significant:

**Always significant:** Write, Edit, NotebookEdit, and specific MCP tools (`send_to_agent`, `delegate_task`, `assign_task`, `email_founder`, `publish_event`, `store_credential`, `schedule_meeting`).

**Never significant:** The Read tool. Pure reads are too noisy to record.

**Conditionally significant:** Bash commands, but only when the command contains specific keywords: `git push`, `git commit`, `kubectl`, `gh pr`, `npm test`, `pytest`, `docker`, `make`. A `ls` command is not significant. A `git push origin main` absolutely is.

This filtering is critical. Without it, a single agent session generates thousands of observations, most of them useless. With it, you get a focused record of the actions that actually change state.

## Step 2: Classify Every Action

Once you have decided an action is worth recording, classify it. We use 10 categories:

| Category | Trigger |
|----------|---------|
| `delegation` | `send_to_agent`, `delegate_task`, `assign_task` |
| `escalation` | `email_founder` |
| `test_run` | `npx jest`, `pytest`, `npm test` |
| `build` | `npm run build`, `npx next build`, `make build`, `docker build` |
| `git_operation` | Any `git` command |
| `k8s_operation` | `kubectl` commands |
| `ci_cd` | `gh pr`, `gh run` |
| `dependency` | `npm install`, `npm ci`, `pip install` |
| `code_change` | Write, Edit, NotebookEdit |
| `command` | Other significant Bash commands |
| `tool_use` | Other significant tool calls |

Classification matters because pattern detection operates on categories, not raw commands. When the learner sees five consecutive `test_run` failures, it knows something is structurally wrong with the test environment -- not just that five different commands happened to fail.

## Step 3: Define the Observation Schema

Each observation follows this schema:

```json
{
  "id": "obs-a1b2c3",
  "timestamp": "2026-09-24T14:30:00.123456",
  "agent_id": "marketing",
  "action_type": "git_operation",
  "action": {
    "tool": "Bash",
    "summary": "git push origin marketing"
  },
  "outcome": {
    "status": "success",
    "evidence": "push completed"
  }
}
```

Key design decisions:

- **`id`** is a short random identifier (`obs-` prefix) for cross-referencing.
- **`agent_id`** enables multi-agent pattern detection. When the CTO agent's deploys keep failing after the Fullstack agent's commits, the learner can correlate across agents.
- **`action.summary`** is human-readable, truncated to 120 characters. Generated by a `_summarize_action()` function that formats each tool type differently: Bash shows the first 120 characters of the command, Write/Edit shows the tool name plus file path, `send_to_agent` shows "Message to {target}: {subject}", and `delegate_task` shows "Delegated to {target}: {title}".
- **`outcome.status`** is one of `success`, `failure`, or `pending` (for delegations where the result arrives later).

## Step 4: Detect Outcomes Automatically

This is the hardest part. You need to determine whether an action succeeded or failed without asking the agent. The agent's self-assessment is unreliable -- it will claim success when the output clearly contains errors.

We parse tool output with pattern matching, specific to each action type:

**Exit codes:** Regex matches for `exit code: N`. Non-zero means failure.

**Test runs:** Parse Jest and pytest output for "N failed, N passed" patterns. If the failed count is greater than zero, the outcome is failure regardless of what else the output says.

**Builds:** Check for "build error", "failed to compile" (failure) vs. "compiled successfully" (success).

**Git push:** Look for "rejected", "failed", "error" (failure) vs. `->` or "done" (success).

**Git commit:** "nothing to commit" is a failure (the agent thought it had changes but did not). "files changed" is success.

**kubectl:** "error" or "not found" means failure, otherwise success.

**npm install:** "ERR!", "ENOENT", "ERESOLVE" indicate failure.

**Write/Edit:** "error" means failure, otherwise success.

**Generic fallback:** If none of the specific patterns match, scan for general error indicators: "error:", "failed", "exception", "traceback", "fatal:", "panic:", "permission denied", "command not found".

**Delegation:** The outcome is always `pending` at recording time. You cannot know whether a delegated task succeeds until the other agent reports back. The observation stores the `task_id`, `message_id`, `to_agent`, and `subject` for later matching. The `autonomous_stop.py` hook resolves these deferred outcomes when the response arrives.

## Step 5: Record Failures Separately

Tool failures that crash the execution pipeline never reach the normal `post_tool_use.py` hook. If you only record in the success path, you miss the most important data points.

We use a separate `record_failure()` function called from `post_tool_use_failure.py`. It captures the same schema but with `status: "failure"` and the error evidence truncated to 300 characters. This ensures that catastrophic failures -- the kind where the tool pipeline itself breaks -- are still captured in the observation log.

## Step 6: Feed the System

The observation log is not a passive record. It is the input to a four-stage [cybernetic learning loop](/blog/cybernetic-learning-loop-agents-write-own-rules):

1. **Observe** -- the log itself. Every significant action with its outcome.
2. **Learn** -- the cybernetic learner reads observations to detect patterns. Repeated failures on the same action type. Stuck loops where an agent retries the same command five times. Recovery sequences where a specific fix consistently follows a specific failure.
3. **Compile** -- patterns with sufficient confidence become enforcement policies in the anti-pattern index. "If an agent has failed `git push` three times in a row, block the fourth attempt and suggest `git pull --rebase` first."
4. **Enforce** -- the pre-tool-use hook reads recent observations to count failures per action type. The policy gate uses compiled policies to allow, deny, or ask before future tool calls.

The full chain: observe, learn, compile, enforce. The observation log is stage one, but it makes all the other stages possible.

## What Makes This Work at Scale

Three properties of this design matter more than any individual feature:

**Significance filtering prevents noise death.** Without it, 10,000 observations fills up in a day. With it, 10,000 covers weeks of meaningful history.

**Automatic outcome detection removes the agent from the assessment loop.** The agent does not decide whether it succeeded. The output does.

**Deferred outcomes handle async work.** Delegations, deployments, CI pipelines -- these resolve later. The system tracks pending outcomes and resolves them when evidence arrives.

## Start Building

You do not need our full stack to get value from an observation log. Start with three things:

1. An append-only JSONL file
2. A significance filter that skips pure reads
3. Outcome detection for your most common tool calls (git, tests, builds)

Add classification and pattern detection later. The raw log alone -- significant actions with parsed outcomes -- will show you failure patterns you did not know existed.

We have been running this system across seven agents since early 2026. The agents that learn from their own history make fewer mistakes each week. The ones without observation logs keep hitting the same walls.

---

Build self-improving AI agents with [agent.ceo](https://agent.ceo) -- the platform where agents observe, learn, and enforce their own rules.
