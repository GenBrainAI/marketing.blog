---
title: "Tutorial: How to Detect and Break Agent Retry Loops in Production"
slug: "detect-break-agent-retry-loops-production"
date: 2026-09-17
category: technical
cluster: "tutorials"
tags: [anti-loop, retry-detection, stuck-loops, cybernetic-loop, policy-gate, tutorial]
description: "A practical tutorial on building three layers of loop detection for AI agents — from counting recent failures to sliding-window stuck-loop detection — so your agents stop burning tokens on doomed retries."
relatedPosts:
  - /blog/cybernetic-learning-loop-agents-write-own-rules
  - /blog/hook-system-enforce-agent-discipline-runtime
  - /blog/ralph-loop-one-task-per-session-anti-drift
  - /blog/why-agents-should-escalate-not-loop
  - /blog/debugging-ai-agent-failures-cyborgenic
---

# How to Detect and Break Agent Retry Loops in Production

A fullstack agent spent 2 hours and 28 minutes stuck in the same thinking/tool-call cycle. 58,000 tokens burned. Zero shipping progress. The agent wasn't broken — it was *persistent*. It hit a wall, and because nothing told it to stop, it kept retrying the same failing operation with the confidence of someone who believes the sixth attempt will somehow work.

This is the failure mode that costs the most in production multi-agent systems. Not hallucinations. Not wrong answers. Just an agent stuck in a loop, burning money and time while looking busy.

At [GenBrain AI](https://agent.ceo), we enforce a blunt rule: **same action repeated five or more times with no success — STOP.** Decompose into smaller steps, mark the task BLOCKED with a specific reason, or escalate. But a rule in a CLAUDE.md file is a suggestion. What you need is *enforcement*. This tutorial covers the three detection layers we built to catch loops before they eat your budget.

## Why Agents Loop

Agents are trained to be persistent. That's usually good — you want an agent that pushes through transient errors. But persistence without success detection becomes pathology. A missing Kubernetes secret won't materialize on attempt twelve. A broken CI pipeline won't fix itself between retries. The agent just knows it hasn't succeeded yet, so it tries again.

You need detection at three levels: real-time (catch it now), pattern-based (learn from recent history), and structural (detect sustained stuck loops). Here's how to build each one.

## Layer 1: Recent Failure Counting

The fastest detection layer runs on every single tool call, before execution. It answers one question: "Has this type of action been failing a lot recently?"

The implementation lives in a pre-tool-use hook. Before the agent executes any tool call, the hook reads the last 10 entries from an `observations.jsonl` file — a structured log where every tool call outcome gets recorded.

```python
def _count_recent_failures(action_type, limit=10):
    """Count failures for this action type in last N observations."""
    recent = read_observations(limit=limit)
    return sum(
        1 for obs in recent
        if obs["action_type"] == action_type
        and obs["outcome"]["status"] == "failure"
    )
```

Action types are classified by a `_classify_action_type()` function into categories: `git_operation`, `k8s_operation`, `ci_cd`, `code_change`, `command`, and `tool_use`. This grouping matters — you don't want to count a failed `git push` against an unrelated `kubectl apply`. But you do want five failed `git push` attempts to trigger an intervention, even if they targeted different branches.

The policy gate uses a `min_recent_failures` threshold in its pattern matching. A pattern only triggers when the agent has already failed N times at the same type of action. This prevents false positives on first failures while catching genuine loops early.

This layer is cheap and real-time. It catches the most obvious loops — the agent hammering the same operation type and failing every time.

## Layer 2: Repeated Failure Pattern Detection

The second layer runs during a learning phase rather than on every tool call, looking at a broader window to find systemic failure patterns.

```python
def _detect_repeated_failures():
    """Flag action types with 3+ failures and >= 50% failure rate."""
    # Group observations by action_type
    # If fail_count >= 3 AND failures > successes → generate learning
```

The threshold is conservative: at least 3 failures AND a failure rate of 50% or higher. An action that fails twice but succeeds eight times is normal operational noise.

When a pattern is detected, the system generates a learning with a calculated confidence score:

```
confidence = min(0.9, 0.3 + (fail_count * 0.1))
```

This starts at 0.4 for a single failure and caps at 0.9 after 6 failures. The learning includes an actionable rule — something like: *"Caution: k8s_operation has an 80% failure rate. Consider alternative approaches."*

Learnings exceeding 0.6 confidence get promoted into the anti-pattern index, where the pre-tool-use hook enforces them. Below 0.6, the system watches but doesn't intervene.

## Layer 3: Stuck Loop Detection

This is the heavy hitter. Layer 3 catches the scenario from the opening of this post — an agent grinding through the same action type for an extended period with zero successes.

The detection uses a sliding window approach with three constants:

```python
LOOP_WINDOW_SIZE = 15      # observations per window
LOOP_MIN_REPEATS = 5       # minimum same-type actions in window
MIN_WINDOW_COUNT = 2       # must appear in multiple windows
```

The algorithm slides a 15-observation window across the observation log. Within each window, it checks: does the same `action_type` appear 5 or more times? And critically — are there *zero* successes for that action type in the window? Even one success resets the detection, because the agent might actually be making progress.

A single window match isn't enough to generate a learning. The pattern must be confirmed in at least 2 windows, which prevents false positives from short bursts of retries that the agent self-corrects from.

When confirmed, the system generates a **high-confidence** learning:

```
confidence = min(0.95, 0.6 + (windows_seen * 0.05))
```

Starting at 0.65 and climbing fast, these learnings almost always exceed the 0.6 threshold for anti-pattern promotion — which means they get enforced immediately. The actionable rule is direct: *"When `[action_type]` repeats 5 or more times with no success: STOP immediately. Switch strategy: decompose the task into smaller steps, try a different approach, or escalate."*

One important detail: the detector excludes metadata action types like `task_reflection` and `unknown`. These aren't real agent actions — they're bookkeeping. You don't want to flag an agent for "looping" on internal reflection steps.

## The Enforcement Chain

Detection without enforcement is a dashboard nobody looks at. Here's how the three layers connect into an automated intervention pipeline:

1. **Observe.** Every tool call outcome gets recorded to `observations.jsonl` (capped at 10,000 entries to prevent unbounded growth).
2. **Learn.** The cybernetic learner runs periodically, detecting repeated failures (Layer 2) and stuck loops (Layer 3) from the observation history.
3. **Index.** Patterns with confidence at or above 0.6 get compiled into the anti-pattern index — a fast-lookup structure the hooks can query.
4. **Gate.** The pre-tool-use hook checks every incoming tool call against the anti-pattern index and runs Layer 1's recent failure count.
5. **Decide.** The policy gate returns one of three verdicts: **allow** (proceed normally), **deny** (block the action entirely), or **ask** (prompt the agent for justification before allowing it).

The "ask" verdict is the most interesting. It forces the agent to articulate *why* this attempt will be different from the last five. If the agent provides a genuine reason ("I changed the namespace" or "I fixed the secret first"), the action proceeds. If it can't, the gate teaches the agent to escalate instead of retry.

## What Breaking the Loop Looks Like

When the system intervenes, the agent has three paths forward — and "try again" is not one of them:

- **Decompose.** Break the stuck task into smaller steps. Often the agent was attempting a compound operation where one sub-step was failing. Splitting it isolates the broken part.
- **Block and document.** Mark the task BLOCKED with a *specific* reason — "Neo4j at 0 replicas, cannot test writes," not "having trouble."
- **Escalate.** Hand the problem to a manager agent or the human founder with enough context to actually unblock it.

The wrapper script also tracks consecutive crashes and backs off exponentially — if the agent itself is crashing and restarting into the same broken state, the backoff prevents it from consuming resources during a systemic outage.

## Implementation Checklist

To build this for your own agent system:

1. **Add structured observation logging.** Every tool call gets an entry: action type, outcome status, timestamp. Cap the file size.
2. **Classify action types.** Group similar operations so your failure counting catches patterns across slight variations of the same underlying action.
3. **Build a pre-tool-use hook** with recent failure counting (Layer 1). This alone catches most loops.
4. **Add periodic pattern detection** for repeated failures (Layer 2) and stuck loops (Layer 3). Feed results into an anti-pattern index.
5. **Wire the policy gate** to the anti-pattern index. Start with "ask" verdicts — let agents justify retries before you start hard-blocking.
6. **Enforce the rule in your agent instructions:** same action, 5 or more times, no success — STOP.

The 58,000-token loop from our opening? With these three layers running, it would have been caught within the first 15 observations — roughly 10 minutes in, not 148 minutes. That's the difference between a production system and a demo.

---

*GenBrain AI builds the infrastructure for running AI agent organizations in production. The loop detection system described here runs on every agent in our fleet. See it in action at [agent.ceo](https://agent.ceo).*
