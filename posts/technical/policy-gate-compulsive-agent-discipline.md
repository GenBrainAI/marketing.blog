---
title: "Tutorial: How to Build a Policy Gate That Makes Agent Discipline Compulsive"
slug: "policy-gate-compulsive-agent-discipline"
date: 2026-10-01
category: technical
cluster: tutorials
tags: [policy-gate, pre-tool-use, anti-pattern-index, strike-system, enforcement, tutorial]
description: "A practical tutorial on building a pre-tool-use policy gate that intercepts every agent action, checks it against a learned anti-pattern index, and enforces graduated consequences — making policy compliance structural, not advisory."
relatedPosts:
  - /blog/observation-log-self-improving-ai-agents
  - /blog/cybernetic-learning-loop-agents-write-own-rules
  - /blog/detect-break-agent-retry-loops-production
  - /blog/hook-system-enforce-agent-discipline-runtime
  - /blog/outer-loop-shell-script-keeps-agents-alive
---

# Tutorial: How to Build a Policy Gate That Makes Agent Discipline Compulsive

You can write the perfect set of instructions. You can explain every rule, every guardrail, every anti-pattern. And after enough context compactions, enough long-running sessions, enough task switches — your agent will forget one of them.

This is not a character flaw. It is a property of bounded context windows. The fix is not better instructions. The fix is a gate that sits between the agent's intent and the outside world, checking every action before it executes. Not sometimes. Every time.

We run a pre-tool-use policy gate on every agent in our fleet. It intercepts every tool call, evaluates it against a compiled index of anti-patterns the agents have learned from their own failures, and decides: allow, deny, or ask. This tutorial walks through the exact architecture.

## The Hook Interface

The gate runs as a PreToolUse hook in Claude Code — it fires before every tool call. The hook receives input via stdin as JSON:

```json
{
  "tool_name": "Bash",
  "tool_input": {"command": "kubectl rollout restart deployment --all -n agents"},
  "tool_use_id": "toolu_abc123",
  "session_id": "sess_xyz789"
}
```

The hook writes its decision to stdout, also as JSON:

```json
{
  "hookSpecificOutput": {
    "permissionDecision": "deny",
    "permissionDecisionReason": "Mass fleet restart blocked. Restart individual deployments instead.",
    "additionalContext": ""
  }
}
```

Three decisions: `"allow"` lets it execute, `"deny"` blocks it (the agent sees the reason), `"ask"` pauses for human judgment. Exit code 0 means the decision is in the JSON. Exit code 2 is a hard block — stderr gets shown to the agent.

## Step 1: Skip What Cannot Hurt You

The first thing the gate does is nothing — for the right tools. Evaluating read-only tools against a policy index wastes time on actions that cannot cause harm:

```python
SKIP_TOOLS = {
    "Read", "Glob", "Grep", "WebSearch", "WebFetch",
    "ListMcpResourcesTool", "ReadMcpResourceTool",
    "TaskList", "TaskGet", "AskUserQuestion"
}

if tool_name in SKIP_TOOLS:
    return allow()
```

An agent reads hundreds of files per session. If each read costs even 50ms of policy evaluation overhead, you are adding minutes of latency for zero safety benefit.

## Step 2: Build the Multi-Layer Gate

After skipping read-only tools, the gate evaluates a stack of policy layers. First match wins — order matters. Hardest safety rules go first.

- **Layer 1: Deploy gate** — blocks direct kubectl deployment modifications. That is what CI/CD is for.
- **Layer 2: TMS delegation gate** — requires a TMS task before tmux delegation. Prevents untracked work.
- **Layer 3: Fleet restart guard** — blocks mass `kubectl rollout restart`. One deployment is fine. Every deployment in a namespace is how you take down a fleet.
- **Layer 4: Test evidence gate** — currently disabled. The founder turned it off because it blocked legitimate work without catching real bugs. Not every gate idea survives production.
- **Layer 5: Anti-pattern index evaluation** — checks the tool call against a compiled index of patterns learned from the agents' own failures.

Each layer returns a decision or `None` (no match, pass to next):

```python
for gate in [deploy_gate, tms_delegation_gate, fleet_restart_guard,
             test_evidence_gate, anti_pattern_evaluation]:
    result = gate(tool_name, tool_input)
    if result is not None:
        return result
return allow()  # No gate matched — tool is safe
```

## Step 3: Load and Cache the Anti-Pattern Index

The anti-pattern index lives in `anti_pattern_index.json`. Each entry describes a learned failure pattern:

```json
{
  "id": "retry-same-kubectl-5x",
  "match": {
    "tool_name": "Bash",
    "action_type": "k8s_operation",
    "input_field": "command",
    "pattern": "kubectl.*apply|kubectl.*create",
    "min_recent_failures": 3
  },
  "action": "block_suggest",
  "reason": "Repeating a failing kubectl command. Check the error output first.",
  "alternative": "Run kubectl describe on the resource to diagnose before retrying.",
  "confidence": 0.82,
  "stats": {"matches": 47, "true_positives": 41}
}
```

The gate loads this file with mtime-based caching — only re-reads when the file changes. If the index file does not exist, the gate compiles it on-the-fly from raw observations as a fallback. In normal operation, `compile_anti_patterns.py` builds the index from observations that cross a 0.6 confidence threshold.

## Step 4: Implement Three-Dimensional Pattern Matching

Matching is not a single string comparison. Three checks must all pass:

**Dimension 1: Tool name filter.** Does this pattern apply to this tool? A pattern targeting Bash should not fire on file writes. Fast, cheap, eliminates most patterns immediately.

**Dimension 2: Action type context.** The gate classifies the call via `_classify_action_type()` into categories like `git_operation`, `k8s_operation`, `delegation`, `file_write`. Some patterns also set `min_recent_failures` — only triggering after N recent failures of the same type to prevent false positives on first attempts.

**Dimension 3: Input field matching.** Two strategies: exact string match (fast path, substring check) and regex pattern match (compiled and cached). One important detail: the gate strips commit message content from git commands before matching. Without this, `git commit -m "fix: kubectl apply issue"` would false-positive on patterns watching for `kubectl apply`.

## Step 5: Implement the Graduated Strike System

Not every violation deserves the same response. First time might be legitimate. Fifth time is a loop. The strike system tracks per-pattern violation counts and escalates:

| Strike Count | Response | Effect |
|---|---|---|
| First violation | **warn** | `additionalContext` injected, tool still executes |
| Repeated violations | **block_suggest** | Tool denied, suggested alternative shown |
| Persistent violations | **block_autotest** | Tool denied, agent can generate a test to prove the action is safe |

The exception: builtin `"block"` patterns always deny regardless of strike level. `kubectl rollout restart --all` is never okay, first time or fiftieth.

Strike state is persisted atomically (temp file + rename) — survives crashes, restarts, and session boundaries. An agent cannot reset its strike count by restarting.

## Step 6: Log Everything

Every gate activation is recorded to `policy_gate_log.jsonl`, capped at 5,000 entries. Each entry records: pattern_id, action taken, tool_name, tool_input_summary (first 200 chars), reason, and timestamp.

This log is how you debug the gate itself. When an agent reports a false positive, you check the log, find the pattern ID, and adjust. Without this log, policy gate debugging is guesswork.

## Step 7: Add the Kill Switch

```python
if os.environ.get("POLICY_GATE_ENABLED") == "false":
    sys.exit(0)  # Allow everything
```

Set `POLICY_GATE_ENABLED=false` to disable the entire gate. All tools are allowed — the hook exits immediately with code 0. You will need this when debugging whether a problem is the gate or the agent.

## The Full Chain: From Failure to Prevention

The policy gate is one piece of a larger [cybernetic loop](/blog/cybernetic-learning-loop-agents-write-own-rules):

1. **Observations** -- every tool outcome recorded to `observations.jsonl`
2. **Pattern detection** -- the cybernetic learner detects recurring failure patterns
3. **Compilation** -- `compile_anti_patterns.py` compiles patterns above 0.6 confidence into the index
4. **Enforcement** -- the pre-tool-use hook loads the index and gates every tool call

No human writes the rules. The agents' own mistakes write the rules. The gate makes following them compulsive. That is the difference between telling an agent "don't retry failing commands" and making it structurally impossible after three attempts.

## Start Building

The full policy gate is under 400 lines of Python. The hook interface is stdin/stdout. No framework, no dependency. Just a script that says yes or no before every tool call.

If you are running autonomous agents in production and relying on instructions alone, you are one long session away from a policy violation. Build the gate. Make discipline compulsive.

We run this across every agent at [agent.ceo](https://agent.ceo). If you want to see a fully autonomous AI organization -- policy gates, cybernetic learning, self-improving agents -- check it out.
