---
platform: twitter
scheduled_date: 2026-10-10
thread_length: 6
day: 153
---

**Tweet 1/6:**
The anti-pattern that kills multi-agent systems: spawning when you should message.

We made this mistake at GenBrain AI. It cost us weeks of wasted compute. Here's what we learned.

**Tweet 2/6:**
The temptation: every new task gets a fresh agent. Clean context. No baggage. Feels right.

The problem: you lose all accumulated knowledge. The new agent re-discovers what the old one already knew. You pay for the same learning twice.

**Tweet 3/6:**
When to spawn: the task is independent. A one-off report. A content piece with no shared state. Parallelizable work where isolation is a feature.

When to message: the task builds on existing context. The agent has domain knowledge. Continuity matters more than cleanliness.

**Tweet 4/6:**
Real example from our system:

Wrong: spawning a new marketing agent for every blog post. Each one re-learned our voice, our content pillars, our internal linking strategy.

Right: messaging the persistent marketing agent. It already knows the brand. Ship faster.

**Tweet 5/6:**
The rule we follow now at GenBrain AI:

Spawn for parallelism. Message for continuity. Meet for consensus.

If you're spawning because "it's cleaner," you're probably wasting tokens and losing knowledge.

**Tweet 6/6:**
Multi-agent coordination is a design problem, not a compute problem. The right pattern depends on whether you need isolation or continuity.

We documented all 3 patterns and when to use each.

Read more: https://agent.ceo/blog/spawn-vs-message-anti-pattern
