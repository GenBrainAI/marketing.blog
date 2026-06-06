---
title: "The Hook System: How 35 Python Scripts Enforce Agent Discipline at Runtime"
slug: "hook-system-enforce-agent-discipline-runtime"
date: 2026-09-01
category: technical
cluster: production-patterns
tags: [hooks, enforcement, policy-gate, cybernetic, anti-patterns, production]
description: "Deep-dive into the Claude Code hook system that makes agent rules compulsive: session lifecycle, policy gates, observation, human interaction tracking, and the cybernetic learning loop."
relatedPosts:
  - /blog/autonomous-loop-stop-hook-gate-ai-agents
  - /blog/writing-agent-instructions-claude-md-scale
  - /blog/anatomy-agent-wakeup-cycle-first-60-seconds
  - /blog/safely-test-ai-agents-production-controls
  - /blog/incident-learning-loop-ai-agent-platform
---

# The Hook System: How 35 Python Scripts Enforce Agent Discipline at Runtime

Rules in text files are suggestions. Rules in hooks are laws.

That distinction is the single most important lesson we learned running a fleet of autonomous AI agents in production. You can write the most detailed CLAUDE.md in the world — spell out every policy, every guardrail, every thou-shalt-not — and a sufficiently long autonomous session will eventually drift past one of them. Not out of malice. Out of probability. An agent running for hours, burning through context, compacting and resuming, will at some point forget that it should not push to `main`. Or it will skip test evidence because the task felt trivial. Or it will mark a delegated task as complete without verifying the artifact.

We solved this the way operating systems solve it: not by asking nicely, but by intercepting the syscall.

## The Hook Lifecycle

Claude Code supports lifecycle hooks — scripts that fire at specific moments in the agent's execution. The moments that matter: session start, before each tool use, after each tool use, on user prompt submission, and when the autonomous loop considers stopping. We run 35+ Python scripts across these five event types. Together they form a behavioral enforcement layer that sits between the agent's intent and the outside world.

The hooks are not advisory. They are structural. When `pre_tool_use.py` returns `"deny"`, the tool call does not execute. There is no override. The agent receives the denial reason and must find another path. This is what makes "never push to main" compulsive rather than aspirational.

## Category 1: Session Lifecycle — `session_start.py`

Every agent session begins the same way. `session_start.py` fires within the first two seconds and outputs context to stderr, which Claude Code surfaces as system-level input to the model. This is how we kickstart autonomous operation without a human typing "go."

The hook implements what we call the ground-truth delta. It checks git for commits that landed since the agent's last session — work from other agents, founder hotfixes, configuration changes. The delta block prevents a common failure mode: an agent waking up and re-doing work that another agent already shipped while it was sleeping.

Beyond the delta, the session hook surfaces the agent's current task queue, organizational goals, and any standing directives from the CEO agent. The agent does not need to remember these things across sessions. The hook reconstructs them from durable state every time. Memory is unreliable; hooks are not.

## Category 2: Policy Gate — `pre_tool_use.py`

This is the most critical hook in the system. It intercepts every tool call before execution — every `Bash` command, every MCP invocation, every file write — and checks it against a compiled anti-pattern index.

The gate returns one of three decisions: `allow`, `deny`, or `ask`. Each decision carries a reason string that the agent sees. A denied `git push origin main` comes back with an explanation: "Direct push to main is prohibited. Commit to your feature branch instead." The agent adapts. It does not argue with a hook.

The anti-pattern index is not a static list. It is compiled from observed failures (more on this in the cybernetic learning section). But the structural patterns are stable: no pushes to protected branches, no `--force` flags without explicit authorization, no commits without test evidence, no `--no-verify` to skip pre-commit hooks.

Violation state is tracked in `VIOLATION_STATE_FILE`. Repeated violations escalate. The system has environment-level kill switches — `POLICY_GATE_ENABLED` and `STRIKE_TRACKING_ENABLED` — so we can disable enforcement in development or during controlled experiments. In production, both are always on.

## Category 3: Observation — `post_tool_use.py` and `cybernetic_observer.py`

If the policy gate is the bouncer, the observation hooks are the security cameras.

`post_tool_use.py` fires after every tool execution. Its primary job: detect when tools return empty results and inject continuation guidance. This sounds minor, but it prevents a surprisingly common failure mode where the agent receives an empty response from a command, interprets it as "nothing to do," and drops to a prompt — waiting for human input that will never come in an autonomous session.

The hook also tracks three critical state dimensions: test evidence (did the agent actually run tests before claiming completion?), TMS delegation state (did the agent delegate a task and then mark its own task complete without waiting for results?), and MCP health state (are the tools the agent depends on actually responding?).

`cybernetic_observer.py` operates at a higher level. It records significant agent actions and their outcomes to `/agent-data/cybernetic/observations.jsonl` — an append-only JSONL log. This is the raw audit trail. Every tool call that modifies state, every deployment, every inter-agent message. The log is not for human reading. It is for the learning loop.

## Category 4: Human Interaction Tracking — `user_prompt_submit.py`

This hook solves a specific problem: autonomous agents interrupting human conversations. When a human submits a prompt, `user_prompt_submit.py` records the timestamp to `/tmp/last_human_interaction`. The autonomous stop hook reads this file and skips its blocking behavior if the interaction was recent.

The result: when a founder is actively chatting with an agent, the autonomous loop control stands down. The agent behaves like an interactive assistant. When the human leaves, the autonomous machinery takes over again. The transition is seamless because the hooks manage it, not the agent's judgment.

## Category 5: Autonomous Loop Control — `autonomous_stop.py`

Left unchecked, an autonomous agent will run forever, burning tokens and accomplishing nothing. `autonomous_stop.py` is the circuit breaker. It manages a stop-block counter with `MAX_STOP_BLOCKS=3`, calling `_should_block_for_pending_work()` to check whether there is genuine remaining work before allowing the session to continue.

When the agent has completed its tasks, reported results, and has no pending inbox items, the hook lets the session terminate gracefully. When the agent is mid-task, it blocks the stop and the session continues. Three consecutive blocks with no measurable progress triggers termination anyway — the agent is stuck, and more tokens will not unstick it.

## Category 6: The Cybernetic Learning Loop

Here is where it gets interesting. The hooks do not just enforce rules — they generate new ones.

The loop has four stages. `cybernetic_observer.py` records actions and outcomes — the raw observation data. `cybernetic_learner.py` runs the LEARN stage, extracting patterns from those observations: "Agent X pushed to main three times this week before the gate caught it" becomes a pattern. `compile_anti_patterns.py` aggregates learned patterns into the anti-pattern index that `pre_tool_use.py` consults on every tool call. And `generate_anti_pattern_test.py` auto-generates test cases for newly discovered anti-patterns, ensuring the gate actually catches them.

The cycle is: observe action, record outcome, learn pattern, compile into index, gate blocks future violations. The system gets stricter over time, but only in response to observed failures. It is not a ratchet — patterns that stop appearing in the observation log eventually age out of the index.

## How It All Composes

For a single tool call, the full hook stack executes in sequence:

1. `pre_tool_use.py` checks the compiled anti-pattern index. Returns `allow`, `deny`, or `ask`.
2. If allowed, the tool executes normally.
3. `post_tool_use.py` records the outcome, detects empty results, tracks test evidence and delegation state.
4. `cybernetic_observer.py` logs the action to the append-only observation file for future learning.

Four hooks. One tool call. The agent never sees the machinery unless it tries to do something it should not — and then it sees a denial reason, not a crash.

## The Point

The best enforcement system is the one nobody notices. Our agents do not think about hooks. They think about their tasks — writing code, publishing content, managing deployments. The hooks run in the background, silently ensuring that "never push to main" is never violated, that test evidence exists before completion claims, that the observation log captures what actually happened.

Thirty-five scripts. Five lifecycle events. One principle: if a rule matters enough to write down, it matters enough to enforce at runtime.

The full hook system, along with the rest of our agent orchestration platform, runs at [agent.ceo](https://agent.ceo). If you are building autonomous agent systems and want rules that stick, start with the hooks.
