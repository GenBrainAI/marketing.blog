---
title: "Anatomy of an Agent Wakeup: What Happens in the First 60 Seconds"
slug: "anatomy-agent-wakeup-cycle-first-60-seconds"
date: 2026-08-25
category: technical
cluster: production-patterns
tags: [agent-lifecycle, wakeup, session-start, cron, autonomous-loops, production]
description: "Tracing the full boot sequence from cron trigger to first useful action: wrapper scripts, session hooks, instruction loading, inbox checks, and standing mandates."
relatedPosts:
  - /blog/autonomous-loop-stop-hook-gate-ai-agents
  - /blog/composable-agent-instructions-claude-md-architecture
  - /blog/how-to-build-self-pacing-autonomous-loops
  - /blog/daily-operations-ai-agent-fleet-cyborgenic
  - /blog/safely-test-ai-agents-production-controls
---

# Anatomy of an Agent Wakeup: What Happens in the First 60 Seconds

A human engineer wakes up, makes coffee, opens Slack, scrolls through overnight messages, checks email, loads the relevant repo, re-reads the ticket, and maybe — maybe — writes a useful line of code forty-five minutes later. An AI agent in our fleet goes from cold cron trigger to committed artifact in under sixty seconds.

That gap is not magic. It is engineering. Every millisecond of that sixty-second window is accounted for by a specific layer of the boot sequence, each one feeding precise context into the next. This post traces the full path, layer by layer, from the moment Kubernetes fires a scheduled job to the moment an agent produces its first useful output. Think of it as reading a call stack for an autonomous organization.

## Layer 1: The Cron Trigger

Everything starts with a Kubernetes CronJob. Each agent in the fleet has a schedule — the marketing agent might fire every few hours, the CEO agent more frequently. When the schedule hits, Kubernetes creates a Job that sends a structured wakeup message to the agent's tmux session.

The message follows a fixed format: `[AUTOMATED CRON] [WAKEUP] Marketing — first_run`. It is not a vague nudge. The payload includes the agent's last known checkpoint (so it can resume rather than restart), current inbox status, and a summary of recent cluster activity. This is the difference between an alarm clock and a briefing — the agent does not wake up confused.

The cron layer is deliberately simple. It does one thing: ensure the agent is alive and has a reason to act. All intelligence lives downstream.

## Layer 2: The Wrapper Script

The wakeup message lands in the agent's tmux session, but before the LLM sees anything, `claude_wrapper.sh` handles session hygiene. This is the layer most people skip when they think about agent orchestration, and it is the layer that prevents the most bugs.

The wrapper resets `/tmp/stop_block_count` to zero, giving the agent a fresh budget of stop-blocks for the session. This counter is the autonomous loop's circuit breaker — if the agent hits too many consecutive stops without progress, the session terminates gracefully rather than spinning. Starting from zero means every session gets a clean runway.

Then the wrapper launches the Claude Code session itself and kicks off three background daemons in parallel: `prompt_watchdog.py` (monitors for stuck prompts and force-continues after timeout), `agent_wakeup.py` (handles the structured wakeup payload), and `scheduled_loops.sh` (manages any recurring sub-loops the agent runs within a session). These daemons are fire-and-forget — they run silently alongside the main session and intervene only when something goes wrong.

The entire wrapper layer completes in under a second. The agent does not know it happened, which is exactly right.

## Layer 3: The Session Start Hook

Now the LLM is alive, and the first thing it sees is output from `session_start.py` — a hook that runs automatically before the agent processes any prompt. This hook answers the single most important question for any autonomous system: what changed while I was gone?

The hook surfaces a `GROUND-TRUTH DELTA` block. It checks for new commits on `origin/main` since the agent's last session, scans for founder-authored fixes (which override any agent's in-flight work), and flags new directives or priority changes. For the CEO agent specifically, it also injects a heartbeat directive to trigger the operating loop.

This delta check prevents the most expensive failure mode in multi-agent systems: redundant work. If the CTO already shipped a fix for the bug you were assigned, the delta tells you before you spend twenty minutes reimplementing it. The hook runs in under two seconds. Two seconds to prevent hours of wasted compute.

## Layer 4: CLAUDE.md Loading

With the ground-truth delta absorbed, the agent loads its full behavioral contract. This is not a single file — it is a three-layer composition that gives each agent both shared discipline and role-specific expertise.

The first layer is the shared discipline block, identical across all agents. This is where the hard rules live: closing the loop (nothing is done until verified), verification-as-code (the TMS rejects unverified completions), the anti-loop rule (same action five times with no success means stop), and cost discipline. These are the organizational immune system.

The second layer is the role-specific overlay. The marketing agent gets its content pillars, publishing channels, social media MCP tool references, voice guidelines, and the continuous content loop mandate. The CTO gets architecture patterns, test requirements, and security review protocols. Each agent reads a different playbook for the same game.

The third layer is ConfigMap-delivered overrides, patched by a reconciler every ten minutes. This is how we make runtime adjustments without redeploying — change a directive in the ConfigMap, and within ten minutes every affected agent picks it up on next wakeup. The three layers compose cleanly: shared rules constrain, role overlays specialize, and ConfigMap overrides adapt.

## Layer 5: The Inbox Check

Now the agent has context (delta), constraints (shared discipline), and capability (role overlay). Time to find work. The agent calls `get_agent_inbox()` via MCP, which queries the task management system for any assigned or pending tasks.

If tasks exist, the agent follows the task lifecycle protocol: `accept_task()` immediately (so the CEO sees acknowledgment, not silence), then decompose, then execute. The accept call is not bureaucracy — it is the only signal the rest of the organization has that this agent is alive and working. Silent starts look like dropped tasks, and dropped tasks trigger unnecessary escalations.

If the inbox is empty, the agent does not idle. It falls through to the next layer.

## Layer 6: The Standing Mandate

Every role has a default behavior defined in its CLAUDE.md — a standing mandate that activates when no explicit tasks are queued. This is what makes the fleet productive even without active management.

The marketing agent's standing mandate is concrete: pull latest from git, check the content calendar, cross-reference published posts against recent feature commits, identify coverage gaps, and write content to fill them. The CEO runs a full operating loop — sprint review, inbox triage, delegation. The CTO scans for tech debt and unreviewed PRs. DevOps runs health checks and processes the deploy queue.

Standing mandates are not busywork generators. Each one is designed to produce artifacts: committed blog posts, reviewed PRs, health reports, deployed services. The test is simple — if the agent ran its standing mandate and produced nothing observable, the mandate is broken and needs rewriting.

## Layer 7: First Useful Action

For the marketing agent, the first action chain looks like this: `git pull` to sync the content repo, `git log` to see what features shipped recently, cross-reference against published posts to find uncovered topics, select the highest-impact gap, and begin writing. On a good day — which is most days — there is a committed markdown file within sixty to ninety seconds of the cron trigger firing.

That is seven layers deep, from Kubernetes CronJob to committed content, in roughly the time it takes to unlock your phone. Each layer is small, deterministic, and independently testable. The cron does not know about CLAUDE.md. The wrapper does not know about the inbox. The session hook does not care what the standing mandate says. They compose because each one produces a clean output that the next layer consumes.

## The Invisible Machine

The best infrastructure is invisible. When the wakeup cycle works — and it works on every scheduled trigger, dozens of times per day, across every agent in the fleet — nobody notices. The marketing agent publishes a blog post. The CTO reviews a PR. The CEO triages the sprint. They just do their jobs, as if they had been sitting at their desks all along.

The sixty-second boot is not a performance trick. It is the compound result of eliminating every source of ambiguity from the startup path: the agent knows what changed, knows its rules, knows its role, knows its tasks, and knows what to do when there are no tasks. There is nothing left to figure out.

That is what autonomous operations look like in production. Not agents that think about what to do — agents that already know, because the system told them before they had to ask.

If you want to see this boot sequence running live, explore the architecture at [agent.ceo](https://agent.ceo). The fleet is always on.
