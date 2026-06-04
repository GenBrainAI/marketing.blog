---
title: "How to Write Tasks That AI Agents Can Actually Complete"
slug: "how-to-write-tasks-ai-agents-can-complete"
date: 2026-06-04
category: technical
cluster: "tutorials"
tags: [ai-agents, tasks, acceptance-criteria, delegation, tutorial, productivity, verification]
description: "Most agent failures aren't agent failures — they're task-writing failures. Here's how to write tasks with concrete verbs, done conditions, and scope limits that agents can actually complete."
relatedPosts:
  - /blog/how-to-evaluate-ai-agent-did-the-job
  - /blog/why-agents-should-escalate-not-loop
  - /blog/verification-as-code-ai-agent-accountability-cyborgenic
  - /blog/agent-delegation-patterns-cyborgenic
---

# How to Write Tasks That AI Agents Can Actually Complete

You gave an agent a clear task. It came back with something you didn't ask for, or got stuck in a loop, or hallucinated a solution that doesn't work. You're starting to wonder if the agent is the problem.

It's probably not. Most agent failures aren't agent failures. They're task-writing failures.

We've learned this the hard way. GenBrain AI is the company behind [agent.ceo](https://agent.ceo), where an entire organization of AI agents ships real work every day — code, content, deployments, customer responses. When an agent delivers the wrong thing, we almost always trace it back to the task description. The agent did exactly what it was told. It was just told the wrong thing.

Here's what we've learned about writing tasks that agents can actually complete.

## Start with the verb

Vague goals produce vague results. Good tasks start with a concrete action verb, not an aspiration.

**Bad:**
- "Improve the onboarding flow"
- "Look into the performance issue"
- "Handle the email backlog"

**Good:**
- "Add a progress bar to the signup wizard showing steps 1-4"
- "Profile the /api/search endpoint and identify queries taking >500ms"
- "Reply to the 12 unanswered support emails in the inbox with our standard troubleshooting template"

See the difference? The bad versions describe a direction. The good versions describe an action you can picture someone doing. An agent can execute "add a progress bar." It cannot execute "improve."

The verb forces you to think about what you actually want. If you can't pick a verb, you don't know what you want yet — and that's a planning problem, not a delegation problem.

## Write the done condition before the task

Before you describe what to do, describe what done looks like. This is the single highest-leverage habit for agent task writing.

**Vague criteria vs. specific criteria:**

| Vague | Specific |
|-------|----------|
| "The API should work" | "POST /api/widgets returns 201 with a valid JSON body containing an `id` field" |
| "Write a good blog post" | "Publish a 900-word post to /blog/ with 3+ internal cross-links and a CTA to agent.ceo" |
| "Fix the login bug" | "Users with email+password can log in and receive a JWT. Verify with `curl -X POST /auth/login`" |

When you write the done condition first, two things happen. First, you catch ambiguity before the agent starts working. Second, you give the agent a concrete target to verify its own output against. Agents that know what "done" looks like self-correct. Agents that don't will wander.

This maps directly to [verification as code](/blog/verification-as-code-ai-agent-accountability-cyborgenic) — the practice of encoding your acceptance criteria as executable checks, not prose descriptions.

## One task, one independently verifiable outcome

"Build the analytics dashboard" is not a task. It's a project. When you hand a project-sized chunk to an agent, it will either oversimplify (build something trivially incomplete) or overcomplicate (spend hours gold-plating one corner while ignoring the rest).

Break it down. Each task should have exactly one outcome you can verify independently.

**Instead of:** "Build the analytics dashboard"

**Write:**
1. "Create a `/api/analytics/events` endpoint that returns the last 7 days of page-view events as JSON. Verify: `curl /api/analytics/events` returns a 200 with an array of event objects."
2. "Build a React component `EventChart` that renders a line chart from the events API. Verify: component renders in Storybook with mock data."
3. "Add the EventChart component to the /dashboard page, wired to the live API. Verify: visiting /dashboard shows the chart with real data."
4. "Add a date-range picker that filters the chart to the selected range. Verify: selecting 'Last 30 days' updates the chart data."

Each sub-task can be completed, verified, and merged independently. If the agent gets stuck on task 3, you still have tasks 1 and 2 shipped and working. This is the core of [effective delegation patterns](/blog/agent-delegation-patterns-cyborgenic) — small, verifiable units of work.

## Include what NOT to do

Agents are eager. They want to deliver. Without constraints, they'll add features you didn't ask for, refactor code you didn't want touched, or pick an approach that conflicts with your architecture.

Explicit constraints save hours of rework:

- "Do NOT add any new npm dependencies"
- "Do NOT modify the database schema — use the existing tables"
- "Do NOT implement authentication — that's a separate task"
- "Use the existing Button component from /components/ui, do NOT create a new one"

Think of constraints as guardrails. They don't limit the agent's creativity on the actual task — they prevent it from wandering into adjacent territory. The best tasks have 2-3 constraints that rule out the most likely wrong directions.

## The 30-second test

Here's the test we use before assigning any task: can you describe how you'd verify the result in 30 seconds or less?

- "I'll curl the endpoint and check the response" — good, assign it.
- "I'll open the page and see if the chart shows up" — good, assign it.
- "I'll run the test suite and check it passes" — good, assign it.
- "I'll... read through the code and see if it looks right?" — not ready. The task is too vague.

If you can't verify it in 30 seconds, one of two things is true: the task is too big (decompose it), or the done condition is too vague (sharpen it). Either way, don't delegate it yet.

This connects directly to [how you evaluate whether an agent did the job](/blog/how-to-evaluate-ai-agent-did-the-job). Evaluation isn't a separate phase — it's baked into the task from the start. And when verification fails, the right response is [escalation, not looping](/blog/why-agents-should-escalate-not-loop).

## Write better tasks, get better agents

The agents are good enough. The frontier models can code, write, analyze, and execute multi-step plans. The bottleneck is almost never capability — it's clarity. A well-written task with a concrete verb, a specific done condition, tight scope, explicit constraints, and a 30-second verification plan will succeed with almost any competent agent.

A vague task will fail with any of them.

On [agent.ceo](https://agent.ceo), every task has acceptance criteria and verification steps built in — so "done" means done. See how structured task management keeps a whole org of agents productive.
