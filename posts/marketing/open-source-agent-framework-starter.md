---
title: "Open Source: Agent Framework Starter Kit"
slug: "open-source-agent-framework-starter"
date: 2026-05-10
category: marketing
cluster: "open-source"
tags: [open-source, agent-framework, python, starter-kit, multi-agent, cyborgenic-organizations]
description: "GenBrain AI open-sources agent-framework-starter — a minimal Python starter kit for building AI agent teams with multi-agent orchestration, NATS messaging, and task management."
relatedPosts: [first-ai-agent-team, getting-started-agent-ceo, what-are-ai-agents, nats-jetstream-ai-agents]
---

# Open Source: Agent Framework Starter Kit

Building a cyborgenic organization should not require six months of infrastructure work before your first agent does anything useful. The gap between "I want AI agents working as a team" and "I have AI agents working as a team" is too wide. Today we are closing it.

[**agent-framework-starter**](https://github.com/GenBrainAI/agent-framework-starter) is a minimal Python starter kit for building AI agent teams. Multi-agent orchestration, NATS messaging, and task management — everything you need to go from zero to a functioning agent team in five minutes.

## What It Is

The starter kit is an opinionated, minimal framework for standing up a team of AI agents that can:

- **Communicate** via NATS JetStream with durable inboxes and reliable delivery
- **Delegate tasks** between agents with tracking, acknowledgment, and completion verification
- **Orchestrate work** through a manager agent that assigns tasks based on agent capabilities
- **Manage state** with persistent task queues that survive agent restarts

It is not a toy. It is a stripped-down version of the same architecture that powers [GenBrain AI's cyborgenic organization](/blog/future-work-cyborgenic-organizations) — the company where AI agents fill real roles and ship real work every day. We removed the GenBrain-specific business logic and kept the structural foundation.

## Why We Built This

We talk to teams building multi-agent systems every week. The same conversation happens repeatedly:

"We have agents that work individually. We cannot get them to work together."

The problem is never the individual agent's capability. GPT-4, Claude, Gemini — they are all capable enough. The problem is coordination. How does Agent A tell Agent B to do something? How does Agent B report back? What happens when Agent C fails halfway through a task? Who tracks what is done and what is not?

These are [solved problems](/blog/what-are-ai-agents) in distributed systems engineering. But most teams building AI agents are not distributed systems engineers. They are ML engineers, product builders, and startup founders who want agents that collaborate — not a graduate course in message queue design.

The starter kit packages the coordination layer so you can focus on what your agents actually do.

## Five-Minute Quickstart

```bash
# Clone the repo
git clone https://github.com/GenBrainAI/agent-framework-starter
cd agent-framework-starter

# Start NATS and the example agent team
docker compose up -d

# Your agent team is running:
#   - manager agent (orchestrates work)
#   - worker-alpha (general tasks)
#   - worker-beta (general tasks)

# Assign a task
python cli.py assign "Review the README for typos"
```

That is it. Three agents running, communicating over NATS, with task assignment and completion tracking. From `git clone` to working agent team in under five minutes.

## What Is Inside

The repository is structured for clarity, not cleverness:

```
agent-framework-starter/
  agents/
    base.py          # Base agent class with NATS connectivity
    manager.py       # Orchestrator that delegates tasks
    worker.py        # Worker agent template
  messaging/
    inbox.py         # Per-agent durable inbox
    tasks.py         # Task queue with ack/nack/retry
    events.py        # Event broadcasting
  config/
    agents.yaml      # Agent definitions and capabilities
    nats.yaml        # NATS connection and stream config
  docker-compose.yml # One-command local setup
  cli.py             # Command-line task assignment
```

**Base Agent** — Every agent extends `BaseAgent`, which handles NATS connection, inbox subscription, heartbeat, and graceful shutdown. You write the `handle_task()` method. The framework handles everything else.

**Manager Agent** — Routes tasks to available workers based on declared capabilities. Tracks task state. Handles timeouts and retries. Escalates failures. This is the pattern described in our [multi-agent architecture](/blog/multi-agent-architecture-patterns) documentation, implemented and ready to run.

**Task Management** — Tasks flow through a defined lifecycle: assigned, accepted, in-progress, completed, or failed. Each transition is recorded. Nothing gets lost.

## Designed for Extension

The starter kit is deliberately minimal. It gives you the coordination skeleton. You add the intelligence.

Common extensions we expect teams to build:

- **Specialized workers** — Replace the generic worker with agents that have domain expertise: code review, data analysis, content generation, customer support
- **LLM integration** — The base agent template includes hooks for connecting any LLM provider. Bring your own model, API key, and prompt strategy
- **Custom routing** — The manager's task routing is pluggable. Route by skill, by load, by priority, or by whatever logic your organization needs
- **Persistence** — Swap the default in-memory state for PostgreSQL, Redis, or whatever your stack uses
- **Observability** — Add OpenTelemetry traces, Prometheus metrics, structured logging

The goal is to get you to "agents collaborating" fast, then get out of your way as you build something production-grade.

## From Starter Kit to Cyborgenic Organization

The starter kit is the first step. The path from here to a full [cyborgenic organization](/blog/future-work-cyborgenic-organizations) looks like this:

1. **Start with the kit** — Get familiar with agent communication and task delegation patterns
2. **Define real roles** — Replace generic workers with agents that own specific functions in your organization
3. **Add NATS patterns** — Integrate the [nats-agent-patterns](https://github.com/GenBrainAI/nats-agent-patterns) library for production-grade messaging
4. **Deploy to production** — Move from Docker Compose to your actual infrastructure
5. **Scale to agent.ceo** — When you need enterprise orchestration, [agent.ceo](https://agent.ceo) provides the full platform: scheduling, verification, cross-agent knowledge sharing, and more

We built agent.ceo to run GenBrain AI. We are open-sourcing the foundation so you can [build your first agent team](/blog/first-ai-agent-team) without starting from scratch.

## Get Started

**GitHub:** [github.com/GenBrainAI/agent-framework-starter](https://github.com/GenBrainAI/agent-framework-starter)

Clone it. Run the quickstart. Build your first agent team today. If you are new to AI agents, start with our guide on [what AI agents actually are](/blog/what-are-ai-agents) and then come back here to build one.

Star the repo. File issues. Contribute patterns. The more teams building cyborgenic organizations, the faster this future arrives.

> GenBrain AI is the company behind agent.ceo, building the next generation of autonomous agent orchestration.

## Try agent.ceo

**SaaS** — Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).

**Enterprise** — For private installation on your own infrastructure, contact [enterprise@agent.ceo](mailto:enterprise@agent.ceo).

---
*agent.ceo is built by [GenBrain AI](https://genbrain.ai) — a GenAI-first autonomous agent orchestration platform. General inquiries: hello@agent.ceo | Security: security@agent.ceo*
