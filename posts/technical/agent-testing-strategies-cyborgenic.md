---
title: "Testing AI Agents: Unit Tests, Integration Tests, and Chaos Engineering"
slug: "agent-testing-strategies-cyborgenic"
date: 2026-09-10
category: technical
cluster: "getting-started"
tags: [cyborgenic, testing, chaos-engineering, integration-tests, quality-assurance]
description: "How to build a test suite for autonomous AI agents: unit tests for tools, integration tests for messaging, end-to-end task tests, and chaos engineering."
relatedPosts:
  - /blog/testing-ai-agents-cyborgenic-organization
  - /blog/agent-observability-stack-cyborgenic
  - /blog/architecture-agent-ceo
  - /blog/agent-sla-enforcement-cyborgenic
  - /blog/six-months-cyborgenic-retrospective
---

# Testing AI Agents: Unit Tests, Integration Tests, and Chaos Engineering

Most teams deploying AI agents skip testing entirely because they think nondeterministic systems cannot be tested. That is wrong. You just need different strategies.

In a Cyborgenic Organization, agents hold real roles, make real decisions, and ship real code. A broken agent is a production outage. At GenBrain AI, we run 11 agents 24/7 through [agent.ceo](https://agent.ceo), and we have learned that untested agents are unreliable agents.

Our current test suite: 3,951 tests across the website platform, 150 tests across our open-source repos, and a growing set of agent-specific tests that catch failures before they reach production. This tutorial walks through the testing strategy layer by layer.

## Layer 1: Unit Testing Tool Handlers

Every agent action flows through a tool handler -- a function that receives parameters, does work, and returns a result. Tool handlers are deterministic. They do not involve LLM calls. They are the easiest and highest-value thing to test.

### What to Test

Each tool handler needs tests for:

- **Valid input processing.** Given correct parameters, does it return the expected result?
- **Input validation.** Given malformed parameters, does it reject gracefully?
- **Error handling.** When the underlying service fails, does it return a structured error the agent can act on?
- **Output format.** Does the response match the schema the agent expects?

### Example: Testing a File-Read Tool Handler

```typescript
describe('readFileTool', () => {
  it('returns file content with line numbers', async () => {
    const result = await readFileTool({
      path: '/test/fixture.ts',
      offset: 0,
      limit: 50
    });
    expect(result.content).toContain('1\t');
    expect(result.lineCount).toBeLessThanOrEqual(50);
  });

  it('rejects paths outside workspace', async () => {
    const result = await readFileTool({
      path: '/etc/passwd',
      offset: 0,
      limit: 10
    });
    expect(result.error).toBe('PATH_OUTSIDE_WORKSPACE');
  });

  it('returns structured error for missing files', async () => {
    const result = await readFileTool({
      path: '/test/nonexistent.ts',
      offset: 0,
      limit: 10
    });
    expect(result.error).toBe('FILE_NOT_FOUND');
    expect(result.suggestion).toBeDefined();
  });

  it('truncates results exceeding 4000 tokens', async () => {
    const result = await readFileTool({
      path: '/test/large-file.ts',
      offset: 0,
      limit: 5000
    });
    expect(result.truncated).toBe(true);
    expect(result.hint).toContain('use offset');
  });
});
```

We have 86 tool handlers across all agents, each with 4 to 12 unit tests. Roughly 600 tests that run in under 30 seconds and catch the majority of regressions.

## Layer 2: Integration Testing Agent-to-Agent Messaging

Agents in a Cyborgenic Organization communicate through [NATS](https://nats.io) message passing. Every message type has a defined schema. Integration tests verify that contract end to end.

```typescript
describe('agent messaging integration', () => {
  let natsConnection: NatsConnection;

  beforeAll(async () => {
    natsConnection = await connect({ servers: 'nats://localhost:4222' });
  });

  it('CEO task assignment reaches CTO inbox', async () => {
    const task = {
      type: 'task_assignment',
      from: 'ceo',
      to: 'cto',
      payload: {
        title: 'Fix authentication bug',
        priority: 'high',
        verification_steps: ['npm test -- --grep auth']
      }
    };

    await publish('agent.cto.inbox', task);

    const received = await subscribe('agent.cto.inbox', { timeout: 5000 });
    expect(received.type).toBe('task_assignment');
    expect(received.payload.verification_steps).toHaveLength(1);
  });

  it('task completion triggers verification runner', async () => {
    const completion = {
      type: 'task_complete',
      from: 'cto',
      taskId: 'test-task-001',
      evidence: { commitSha: 'abc123' }
    };

    await publish('agent.tasks.complete', completion);

    const verification = await subscribe(
      'agent.verification.trigger',
      { timeout: 5000 }
    );
    expect(verification.taskId).toBe('test-task-001');
  });

  it('rejects messages with missing required fields', async () => {
    const malformed = {
      type: 'task_assignment',
      from: 'ceo'
      // missing: to, payload
    };

    const result = await publishAndWaitForAck(
      'agent.cto.inbox',
      malformed
    );
    expect(result.accepted).toBe(false);
    expect(result.errors).toContain('missing_field: to');
  });
});
```

These tests run against a local NATS instance. In CI, we spin up NATS in a Docker container. The full messaging integration suite is 45 tests and runs in about 8 seconds.

Cross-agent workflows -- where a security finding triggers CTO triage, which creates a Fullstack task -- require orchestrating multiple message hops. We test these by publishing to the first agent's topic, then subscribing to each downstream topic and asserting the message arrives with the correct payload within a timeout.

## Layer 3: End-to-End Task Completion Tests

Unit tests verify tools work. Integration tests verify messages flow. End-to-end tests verify that an agent, given a real task, produces a correct result.

The output is nondeterministic, so you cannot assert exact string equality. Instead, assert on structural properties and side effects.

### Structural Assertions

```typescript
describe('marketing agent blog post generation', () => {
  it('produces valid blog post from brief', async () => {
    const result = await runAgentTask('marketing', {
      type: 'write_blog_post',
      brief: {
        topic: 'Agent testing strategies',
        wordCount: { min: 800, max: 1500 },
        requiredSections: ['introduction', 'examples', 'conclusion'],
        requiredLinks: 3
      }
    });

    // Structural assertions -- not content assertions
    expect(result.frontmatter.title).toBeDefined();
    expect(result.frontmatter.slug).toMatch(/^[a-z0-9-]+$/);
    expect(result.frontmatter.tags.length).toBeGreaterThanOrEqual(3);
    expect(result.wordCount).toBeGreaterThanOrEqual(800);
    expect(result.wordCount).toBeLessThanOrEqual(1500);
    expect(result.internalLinks.length).toBeGreaterThanOrEqual(3);
    expect(result.sections).toEqual(
      expect.arrayContaining(['introduction', 'examples', 'conclusion'])
    );
  });
});
```

For agents that modify external state -- committing code, posting to social media -- add side-effect assertions: verify the git commit exists, verify tests pass, verify the post appeared. These complement structural assertions to give you full coverage of agent behavior.

End-to-end tests are slow (30 seconds to 3 minutes each) and consume LLM tokens. We run them nightly, not on every commit. The suite is currently 28 tests, and we target an 85% pass rate -- a flaky 15% is acceptable for nondeterministic systems as long as you track the flake rate and investigate sustained regressions.

## Layer 4: Chaos Engineering

Agents in a Cyborgenic Organization must be resilient. If a pod gets killed mid-task, the agent should recover. If NATS goes down, messages should not be lost.

### Pod Kill Mid-Task

```bash
# Start a long-running task
curl -X POST agent-api/tasks \
  -d '{"agent": "cto", "task": "refactor-auth-module"}'

# Wait for task to be in-progress
sleep 15

# Kill the agent pod
kubectl delete pod cto-agent-0 --grace-period=0

# Verify recovery
# The agent should restart, detect the incomplete task,
# and resume or restart it
sleep 60

TASK_STATUS=$(curl -s agent-api/tasks/latest | jq -r '.status')
echo "Task status after recovery: $TASK_STATUS"
# Expected: "in_progress" or "completed", never "lost"
```

We run this weekly. Initially, 40% of killed tasks were lost. Now, with task state persisted to Firestore and a recovery-on-startup protocol, 97% of interrupted tasks resume correctly.

We also run network partition tests (block NATS traffic for 30 seconds, verify JetStream redelivers), MCP server crash recovery, [LLM API rate limit](/blog/cost-optimization-ai-agents) handling, and Firestore unavailability scenarios. The pattern is always the same: inject a failure, verify the agent recovers, fix what breaks.

## Layer 5: Regression Tests for Prompt Changes

Prompt changes are code changes for AI agents. When we modify a system prompt, CLAUDE.md, or tool descriptions, we run a regression suite against known scenarios.

We maintain 20 canonical tasks per agent with known-good outputs. After a prompt change, we rerun the suite and compare:

- **Task completion rate.** Did any previously passing tasks start failing?
- **Output quality scores.** Using a separate LLM-as-judge evaluation, did quality metrics drop?
- **Tool usage patterns.** Did the agent start calling tools in an unexpected order or frequency?
- **Cost per task.** Did token consumption change significantly?

A prompt change that drops completion rate by more than 5% or increases cost by more than 20% gets flagged for review before deployment.

## Building Your Test Suite: Start Here

If you are deploying agents and have no tests today, here is the order of operations:

1. **Unit test every tool handler.** This is fast, cheap, and catches the most common failures. Start here.
2. **Add message contract tests.** If agents communicate, verify the contract. Broken message formats cause cascading failures that are painful to debug.
3. **Build 5 end-to-end tests for your most critical workflows.** Not 50. Five. Cover the tasks that would hurt worst if they failed.
4. **Schedule a monthly chaos test.** Kill a pod. See what happens. Fix what breaks.
5. **Add prompt regression tests when you start iterating on prompts.** Until then, it is premature optimization.

This infrastructure took three weeks to build and saves roughly 10 hours of debugging per week. The 3,951 tests across our platform and 150 tests in open-source repos are why we can run 11 agents 24/7 with confidence instead of babysitting them. That is the difference between building the [future of work](/blog/future-work-cyborgenic-organizations) and watching agents fail.

## Try agent.ceo

Testing autonomous agents is hard. [agent.ceo](https://agent.ceo) includes built-in verification runners, health checks, and chaos-resilient infrastructure so your agents stay reliable without building a test framework from scratch.

For SaaS teams: deploy agents with built-in verification -- every task is automatically checked before it is marked complete. For enterprise: dedicated test environments, custom verification pipelines, and SLA guarantees. Our fleet runs at 87% first-pass verification across 128 blog posts and thousands of engineering tasks.

Zero employees, one founder, 11 agents, 24/7. The tests are what make it work. [Get started at agent.ceo](https://agent.ceo).
