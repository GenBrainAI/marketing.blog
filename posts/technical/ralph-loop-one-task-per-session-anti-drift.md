---
title: "The Ralph Loop: One Task Per Session as an Anti-Drift Pattern"
slug: "ralph-loop-one-task-per-session-anti-drift"
date: 2026-09-15
category: technical
cluster: architecture-deep-dives
tags: [ralph-loop, anti-drift, session-isolation, task-management, agent-architecture, deep-dive]
description: "Deep-dive into the Ralph Loop pattern — a structural approach to preventing AI agent drift by enforcing one task per session, fresh context per task, and zero invented work."
relatedPosts:
  - /blog/prevent-agent-drift-ground-truth-deltas
  - /blog/anatomy-agent-wakeup-cycle-first-60-seconds
  - /blog/hook-system-enforce-agent-discipline-runtime
  - /blog/cybernetic-learning-loop-agents-write-own-rules
  - /blog/agent-context-management
---

# The Ralph Loop: One Task Per Session as an Anti-Drift Pattern

Your agent finished its assigned task twenty minutes into a forty-minute session. It has context left. It has tools available. It has ambition. So it starts "improving" things — refactoring a module nobody asked it to touch, writing tests for a service owned by another agent, reorganizing imports across fourteen files. When the session ends, the git log shows six commits: one for the task, five for invented work that now needs review, may conflict with other agents' branches, and definitely was not on any backlog.

This is drift. Not the dramatic kind where an agent goes rogue. The quiet kind. The kind where an agent with spare cycles fills them with plausible-looking busywork that nobody requested and nobody will verify. At $15-45 per task session, that busywork has a real cost — and the merge conflicts it creates cost even more.

We solved it with a pattern we call the Ralph Loop, named after Geoffrey Huntley's concept. The rule is brutally simple: one task per session, fresh context per task, no invented work. The implementation is three files and a signal mechanism.

## The Architecture: Three Files and a Flag

The Ralph Loop lives in `/agent-data/ralph/` on every agent pod. The entire state machine is captured by three things:

- **`current-task.json`** — the single task the agent is working on right now. One file. One task. Not a queue, not a priority matrix, not a kanban board. One JSON object describing one unit of work.
- **`backlog.json`** — a priority-sorted queue of pending tasks, populated from external sources. The agent does not write to this file. The system populates it. The agent pops from it.
- **`completed/`** — a directory of archived completed tasks. When a task finishes, it moves here with its verification notes and artifacts attached. This is the audit trail.

There is also a signal file: `FRESH_START` at `/agent-data/ralph/FRESH_START`. When this file exists, the wrapper script strips the `--continue` flag from the next Claude session launch. Instead of resuming the old conversation, the agent starts clean. Fresh context window. No compacted memories from the previous task bleeding into the new one. No hallucinated state from three tasks ago surfacing as confident assertions about the current codebase.

That last point matters more than it sounds. Context compaction — where the LLM summarizes earlier conversation to free up token space — is lossy. Details get dropped. Nuance gets flattened. An agent that ran a database migration in task one, a CSS fix in task two, and is now working on an API endpoint in task three will sometimes "remember" database constraints that do not exist, or CSS class names it hallucinated during compaction. Fresh sessions eliminate the entire category.

## Task Sourcing: Where Work Comes From

The backlog does not appear from nowhere. When `_populate_ralph_backlog()` runs, it pulls from three sources in priority order:

1. **NATS-delivered JSON tasks** from the agent inbox. These are structured messages from other agents or the task management system, typically carrying full context: objective, acceptance criteria, deadline. Highest priority because they represent active organizational decisions.

2. **Legacy `.md` directive files** from the inbox directory. Older-format tasks that predate the structured JSON pipeline. The system still reads them for backward compatibility.

3. **TMS Pull** — a direct read from the shared task registry. This is the fallback that survives NATS failures. The system reads task files, filters by `assignee == ROLE_ID`, and only pulls tasks with status "assigned" or "accepted." If NATS is down and no directives are pending, the agent still finds its work.

The resulting backlog is sorted by priority: critical tasks surface first, then high, medium, low. An agent never decides what to work on. The backlog decides. The agent pops and executes.

## The Session Start Flow

When an agent wakes up, the sequence is deterministic:

1. `_get_ralph_current_task()` checks if `current-task.json` contains an in-progress task. If yes, the agent resumes it. No re-prioritization, no second-guessing. Finish what you started.

2. If no current task exists (previous task completed or first boot), `_pop_ralph_backlog_task()` takes the next item from `backlog.json`. The task moves from backlog to current. The backlog shrinks by one.

3. If the backlog is empty, `_populate_ralph_backlog()` scans all three task sources, builds a fresh priority-sorted queue, and pops the first item.

Each task becomes an `OrganizationalGoal` dataclass:

```python
@dataclass
class OrganizationalGoal:
    objective: str
    why_it_matters: str
    success_criteria: str
    deadline: str
    source: str  # 'directive', 'initiative', 'standing_orders', 'mission'
```

This is not a suggestion. It is a contract. The agent knows exactly what it needs to deliver (`objective`), why the organization cares (`why_it_matters`), how completion will be measured (`success_criteria`), and when it is due (`deadline`). There is no room for "I thought it would be helpful to also..."

## Acceptance Criteria Extraction

The system parses task text for concrete checkboxes. `_extract_ralph_criteria()` looks for lines starting with `- [ ]` or `* [ ]` and lines containing the words "criteria" or "must." It caps at five criteria — enough to define done, not enough to create analysis paralysis. If no criteria are found in the task text, it defaults to a single item: `["Complete the assigned task"]`.

Five criteria max is a deliberate constraint. A task with fifteen acceptance criteria is not a task. It is a project. It needs decomposition, not a longer checklist.

## The Anti-Drift Injection

Here is where the pattern becomes compulsive rather than aspirational. The session start hook outputs a formatted block that the agent sees before it processes anything else:

```
======================================================================
CURRENT TASK (Ralph Loop — Anti-Drift)
======================================================================
Objective: Write technical blog post on the Ralph Loop pattern
Acceptance Criteria:
  - Post is 800-1500 words
  - Includes accurate code examples from source
  - Frontmatter matches template
Source: TMS task-a1b2c3d4

IMPORTANT: Complete THIS task before starting anything else.
When done, update /agent-data/ralph/current-task.json:
  - Set "status" to "completed"
  - Add "verification_notes" explaining how criteria were met
  - Add "artifacts" listing files changed
Do NOT start unrelated work (tests for other modules, refactoring, etc.)
======================================================================
```

That last line is the key. "Do NOT start unrelated work" is not buried in a CLAUDE.md paragraph the agent might compact away. It is injected fresh, at the top of context, every single session. The agent cannot forget it because it never needs to remember it — the hook re-delivers it every time.

## The Completion Boundary

When the agent finishes the task, it updates `current-task.json`: sets `status` to `"completed"`, writes `verification_notes` explaining how each criterion was met, and lists `artifacts` (files changed, commits made, endpoints deployed).

On clean exit (exit code 0), the wrapper clears both `backlog.json` and `current-task.json`. The next session starts from scratch — fresh backlog population, fresh task selection, fresh context. No carried state. No "I was also thinking about..." from the previous session.

The `FRESH_START` file triggers the wrapper to launch a new Claude session rather than resuming the old one. This ensures MCP tools re-initialize properly, environment state is current, and the context window is clean.

## Why This Pattern Works

The Ralph Loop is effective not because of any single mechanism, but because of how they combine:

**Fresh context per task** eliminates compaction hallucinations. An agent working on its third task in a continued session will have a context window polluted with summaries of tasks one and two. Those summaries are lossy. They create false confidence about code state, variable names, and API contracts. A fresh session has no history to hallucinate from.

**Single-task focus** eliminates invented work. An agent cannot drift into "helpful" refactoring if the only instructions it has seen say "write this blog post" and "do NOT start unrelated work." The constraint is not in memory — it is in the prompt, injected fresh every session.

**Priority-sorted backlog** ensures critical work surfaces first. The agent does not choose. The system chooses. A critical production fix will always precede a medium-priority documentation update, regardless of which one the agent finds more "interesting."

**Clean session boundaries** ensure tool state is correct. MCP connections, git state, environment variables — all re-initialize on fresh session start. No stale connections. No cached credentials from a rotated secret.

The result: every session produces exactly one artifact, verified against explicit criteria, with no side effects. The git log reads like a task list, not a stream of consciousness.

## The Broader Lesson

The Ralph Loop embodies a principle that applies far beyond AI agents: **ambition without boundaries produces noise, not signal.** An agent with spare capacity and no constraints will fill that capacity with work that looks productive but was never requested, never prioritized, and never verified. The fix is not smarter agents. It is dumber constraints — one task, one session, one clean exit. Repeat.

If you are building autonomous agent systems and your agents keep "helping" by doing things nobody asked for, you do not have a capability problem. You have a scoping problem. The Ralph Loop is one way to solve it.

---

*We run the Ralph Loop across every agent in the GenBrain fleet. It is one layer of a larger enforcement stack that includes [policy gate hooks](/blog/hook-system-enforce-agent-discipline-runtime), [ground-truth deltas](/blog/prevent-agent-drift-ground-truth-deltas), and a [cybernetic learning loop](/blog/cybernetic-learning-loop-agents-write-own-rules) that writes new rules from observed failures. If you want to see how these systems work together in a production multi-agent organization, check out [agent.ceo](https://agent.ceo).*
