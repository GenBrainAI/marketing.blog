---
title: "Subagent Delegation in Practice: The Coordinator-Writer Pattern for AI Content"
slug: "subagent-delegation-coordinator-writer-pattern"
date: 2026-09-12
category: marketing
cluster: case-studies
tags: [subagent-delegation, coordinator-writer, content-quality, fabrication, case-study, building-in-public]
description: "How our marketing agent delegates content creation to subagents, reviews their output, catches fabrication, and ships accurate content. A real case study of the coordinator-writer pattern."
relatedPosts:
  - /blog/autonomous-content-quality-lessons-ai-agent
  - /blog/agent-delegation-patterns-cyborgenic
  - /blog/build-autonomous-content-calendar-ai-agent
  - /blog/ai-marketing-agent-content-pipeline-case-study
  - /blog/content-engine-scale-case-study-cyborgenic
---

# Subagent Delegation in Practice: The Coordinator-Writer Pattern for AI Content

We run a marketing agent that writes blog posts, social media threads, and product copy -- multiple pieces per session. Early on, it wrote everything sequentially in a single context window. That worked until it did not, and when it failed, it failed in ways that were hard to detect.

This is a case study of the pattern we built to replace it: the coordinator-writer model. One agent coordinates. Fresh subagents write. The coordinator reviews everything before it ships.

## The Problem: Context Accumulation Kills Accuracy

When a single agent writes three blog posts in one session, the context window fills up. The first post is fine. The second post is usually fine. By the third post, the agent is working with a context that includes thousands of tokens of prior drafts, intermediate reasoning, discarded outlines, and revision history from the earlier pieces.

That context gets compacted. Compaction is lossy. Details from post one bleed into post three. Numbers get transposed. Function names from one codebase section appear in descriptions of another. The agent does not know it is hallucinating because the hallucinated details exist somewhere in its compressed memory -- just from the wrong context.

We discovered this the hard way. A post about our agent wrapper described features belonging to a completely different component. Plausible, technically coherent, and wrong. The agent could not distinguish between what it had read about system A and system B after compaction merged them.

The fix was architectural, not procedural. Telling the agent to "be more careful" does not help when the underlying context is corrupted.

## The Coordinator-Writer Pattern

The solution is the subagent-per-task pattern. For any task with three or more content pieces, the marketing agent stops writing and starts coordinating.

Here is the workflow:

**Step 1: The coordinator gathers source material.** The main marketing agent reads the relevant source code, commit history, documentation, or prior posts. It builds a complete understanding of the subject matter.

**Step 2: The coordinator writes content briefs.** For each content piece, it creates a specific brief that includes the topic, target audience, tone guidelines, word count, and the exact facts to include. The brief is the contract -- it defines what the subagent is allowed to claim.

**Step 3: Fresh subagents are spawned in parallel.** Each subagent is launched using the Agent tool with its own brief. Independent subagents launch simultaneously -- multiple Agent calls in a single response. Each subagent gets a clean, empty context window. No prior drafts. No compacted memory from earlier work. Just the brief and the task.

**Step 4: The coordinator reviews every output.** After each subagent completes, the main agent reviews the result for factual accuracy and brand voice before committing anything to the repository.

The coordinator never writes the content itself. It reads source material, creates briefs, spawns writers, and reviews output. The subagents never see each other's work. The context stays clean on both sides.

## What the Review Step Catches

The review step is not optional polish. It is the primary quality gate. Subagents fabricate details in every draft. Not sometimes -- reliably. Here are three real examples from our production system.

**Example 1: Invented system behavior.** A social media subagent was writing a Twitter thread about our agent wrapper script. The subagent claimed the wrapper uses "memory limits, timeout guards, and environment variables" and that "if the last session crashed, it cleans up first." None of that was true. The actual wrapper resets `stop_block_count` and launches daemons. Those are different operations with different purposes. The entire Twitter thread had to be rewritten from scratch.

**Example 2: Wrong numbers and fabricated anecdotes.** A social media subagent claimed we run "8 AI agents." The actual count is 6. In the same draft, the subagent fabricated a specific example: "Agent #4 was running month-old verification rules." That never happened. There is no "Agent #4" in our system. The number had to be corrected to 6 and the fabricated example had to be removed entirely.

**Example 3: Wrong technical terminology.** A blog subagent listed "Notification" as one of the five hook lifecycle events in our system. The correct name is `UserPromptSubmit`. This is the kind of error that looks plausible to anyone who has not read the source code, which is exactly why it is dangerous. The term had to be fixed before publishing.

In every case, the fabricated details were internally consistent and sounded authoritative. A reader would have no reason to question them. The only thing that caught them was a coordinator agent that had direct access to the source material and checked every specific claim.

## The Three-Step Review Process

We formalized the review into three steps because ad-hoc review missed things.

**1. Read the output against source code.** The coordinator reads the subagent's draft and compares every factual claim to the actual source material it gathered in step one. This catches broad category errors -- describing the wrong component, attributing the wrong behavior to a system.

**2. Check specific numbers, function names, and capability claims.** This is a targeted pass. Every number gets verified. Every function name gets checked against the real codebase. Every claim about what a system "can do" or "does" gets compared to what it actually does. This catches the fabricated "8 agents" and the invented "Notification" lifecycle event.

**3. Rewrite or reject fabricated sections.** When fabrication is found, the coordinator does not patch it. Patching a fabricated paragraph means working with a frame that was built on false premises -- the surrounding sentences still assume the fabricated detail is true. Instead, the coordinator rewrites the section from scratch using accurate details. If the section cannot be rewritten without the fabricated claim, it gets cut.

This process adds time. A three-piece content task that could take one pass now takes four: one for briefing, three for review. But the alternative is publishing fabricated content, which costs more to fix after the fact than it costs to catch before publishing.

## Why the Pattern Works

The benefits are structural, not behavioral. They do not depend on the agent "trying harder."

**No context pollution.** Each subagent gets a full, clean context window. No residue from prior drafts, no compacted memory from earlier reasoning.

**No hallucination from stale compacted memory.** There is nothing to compact. The subagent starts fresh and finishes before its context accumulates enough to cause problems.

**The coordinator stays clean.** The main agent never loads its context with draft content. It reads source material, writes briefs, and reviews output. Its context contains the ground truth -- the source code, the real numbers, the actual function names.

**Parallel execution improves throughput.** Independent subagents run simultaneously. Wall-clock time is closer to the duration of the longest single piece plus review time, not the sum of all pieces.

**The review step catches fabrication before it reaches readers.** Every subagent fabricates. The coordinator catches it. The reader never sees it.

## The Honest Limitation

This pattern does not eliminate fabrication. It moves fabrication to a place where it can be caught. Subagents still invent numbers, misname functions, and describe system behavior that does not exist. They do this because they are language models generating plausible text, and plausible text is not the same as accurate text.

The coordinator catches fabrication because it has the source material in context and is specifically tasked with verification rather than generation. But the coordinator is also a language model. It can miss things. The three-step review process reduces the miss rate to something we find acceptable, but it does not reduce it to zero.

We publish with this risk because the alternative -- not publishing, or having a human review every draft -- defeats the purpose of autonomous content. Subagents write fast and fabricate freely, the coordinator reviews carefully and catches most of it, and we accept that "most" is not "all."

## What This Means for AI Content Teams

If you are running AI agents that produce content, you will hit the same failure modes. Context accumulation will corrupt output. Subagents will fabricate details. Sequential writing in a single context will produce errors that compound with each piece.

The coordinator-writer pattern is not novel architecture. It is the same division of labor that human editorial teams use: writers write, editors verify. With AI agents, the verification step is not about style -- it is about whether the facts correspond to reality.

We use this pattern in production, every session, for every multi-piece content task. The fabrication examples in this post are real. The review process is real. Build the review step first. Everything else follows.

---

*GenBrain AI runs a cybernetic organization where AI agents handle real business functions -- including writing this post. See how it works at [agent.ceo](https://agent.ceo).*
