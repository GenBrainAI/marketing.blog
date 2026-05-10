---
platform: twitter
scheduled_date: 2026-09-09
thread_length: 7
day: 122
---

**Tweet 1/7:**
How do you unit test an AI agent? We have 4,100 tests across 6 agents. Here's our approach.

AI output is non-deterministic. Traditional assert(expected == actual) doesn't work. So we built something different.

**Tweet 2/7:**
Layer 1: Deterministic tests (2,400 of 4,100).

These don't test the LLM at all. They test everything around it -- tool execution, message routing, config parsing, git operations, file I/O.

If your agent can't read a file correctly, the LLM doesn't matter.

**Tweet 3/7:**
Layer 2: Contract tests (1,200 of 4,100).

We don't assert exact output. We assert structure. Did the agent return valid JSON? Does the blog post have frontmatter? Is the commit message under 72 chars? Does the PR have a description?

Shape over content.

**Tweet 4/7:**
Layer 3: Behavioral tests (400 of 4,100).

Given a known scenario, does the agent take the right action? We use cheap, fast models for test runs. Not "did it write good code" but "did it attempt to write code in the right file."

Action selection, not output quality.

**Tweet 5/7:**
Layer 4: Regression tests (100 of 4,100).

Every production bug becomes a test case. Agent merged to wrong branch? Test. Agent sent email without approval? Test. Agent exceeded token budget? Test.

These are our most valuable tests. Each one represents a real failure.

**Tweet 6/7:**
What we don't test: prose quality, creative output, subjective decisions.

We tried. Spent 3 weeks building LLM-as-judge evaluations. Flaky, expensive, low signal. Killed it. Human review handles subjective quality. Tests handle correctness.

**Tweet 7/7:**
4,100 tests. Zero are flaky. The secret: test the system, not the model.

AI agents are software systems that happen to include an LLM. Test them like software. At GenBrain AI, our CI runs in under 4 minutes.

Read more: https://agent.ceo/blog/testing-ai-agents
