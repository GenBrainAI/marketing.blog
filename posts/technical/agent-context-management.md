---
title: "Agent Context Management: Compaction and Memory"
slug: "agent-context-management"
date: 2026-05-10
category: technical
cluster: "architecture-deep-dives"
tags: [context-window, compaction, memory, token-management, ai-agents, persistence]
description: "How agent.ceo manages AI agent context windows through compaction, cross-session memory, and intelligent summarization to maintain performance at scale."
relatedPosts: [architecture-agent-ceo, mcp-tool-integration, task-management-autonomous-ai]
---

# Agent Context Management: Compaction and Memory

Every AI agent has a fundamental constraint: a finite context window. Claude's context window is large (200K tokens), but autonomous agents that run for hours, process dozens of tasks, and accumulate tool outputs can exhaust it. When context fills up, agents lose track of earlier decisions, repeat work, or make contradictory choices. agent.ceo solves this with two complementary systems: context compaction (reducing current-session context while preserving key information) and cross-session memory (persisting learnings that survive pod restarts).

## The Context Problem

Consider an agent that has been running for 3 hours:

```
Context Window Usage (200K tokens):
+------------------------------------------------------------------+
| System prompt + CLAUDE.md (5K)                                    |
| Memory file loaded at start (3K)                                  |
| Task 1: 15 tool calls, outputs, reasoning (25K)                  |
| Task 2: 8 tool calls, file reads, git operations (18K)           |
| Task 3: 22 tool calls, web searches, file writes (35K)           |
| Task 4: Currently in progress...                                  |
| [============================71%=============                   ] |
+------------------------------------------------------------------+
  Used: ~142K tokens | Remaining: ~58K tokens | Threshold: 80% (160K)
```

At 80% utilization, the agent's responses slow down (more tokens to process), costs increase (input tokens are billed), and the risk of "forgetting" early context grows. Compaction triggers before this threshold to maintain agent effectiveness.

## Compaction Architecture

Compaction is a controlled summarization process that reduces context size while preserving decision-relevant information:

```
Before Compaction:                    After Compaction:
+---------------------------+         +---------------------------+
| System prompt (5K)        |         | System prompt (5K)        |
| Memory (3K)               |         | Memory (3K)               |
| Task 1 full trace (25K)   |         | Task 1 summary (2K)       |
| Task 2 full trace (18K)   |         | Task 2 summary (1.5K)     |
| Task 3 full trace (35K)   |         | Task 3 summary (2.5K)     |
| Current task (20K)        |         | Current task (20K)        |
+---------------------------+         +---------------------------+
| Total: 106K tokens        |         | Total: 34K tokens         |
| Reduction: 68%            |         |                           |
+---------------------------+         +---------------------------+
```

The current task is never compacted. Only completed work gets summarized. This ensures the agent maintains full fidelity on its active work while efficiently storing history.

## Compaction Algorithm

The compaction process follows a structured approach:

```javascript
// Compaction trigger logic
async function checkCompaction(session) {
  const usage = session.tokenCount / session.maxTokens;
  
  if (usage >= session.compactionThreshold) {
    await performCompaction(session);
  }
}

// Compaction execution
async function performCompaction(session) {
  const segments = session.getCompletedSegments();
  
  for (const segment of segments) {
    const summary = await generateSummary(segment, {
      preserveKeys: [
        "decisions_made",      // What was decided and why
        "files_modified",      // What files were changed
        "blockers_encountered",// Problems hit and solutions
        "delegations",         // Tasks sent to other agents
        "outcomes"             // Final results and artifacts
      ],
      discardable: [
        "intermediate_reasoning",  // Step-by-step thinking
        "tool_output_raw",         // Full file contents, search results
        "failed_attempts",         // Approaches that didn't work
        "repetitive_operations"    // Multiple similar tool calls
      ],
      targetReduction: 0.85  // Aim for 85% size reduction
    });
    
    segment.replaceWith(summary);
  }
  
  // Update session metadata
  session.compactionCount += 1;
  session.lastCompactedAt = new Date();
  await session.save();
}
```

## What Gets Preserved vs. Discarded

The compaction algorithm makes intelligent decisions about information value:

**Always Preserved:**
- Decisions and their rationale ("chose approach X because Y")
- File paths created or modified
- Task status transitions and delegation records
- Error patterns and their resolutions
- Configuration changes made
- Commitments to other agents ("told CTO I would deliver by 3pm")

**Safely Discarded:**
- Full file contents that were read (can be re-read if needed)
- Intermediate search results
- Verbose tool output (API responses, build logs)
- Step-by-step reasoning for completed subtasks
- Multiple iterations of similar operations

**Example Compaction:**

Before (25K tokens):
```
User: Write a blog post about NATS
[Read file /templates/blog-post.md - 2000 tokens of file content]
[Web search "NATS JetStream architecture" - 3000 tokens of results]
[Web search "NATS vs Kafka comparison" - 2500 tokens of results]
[Read file /docs/nats-config.yaml - 1500 tokens]
[15 paragraphs of reasoning about structure]
[Write file /blog/nats-post.md - 4000 tokens]
[Git commit - output]
[Read file to verify - 4000 tokens]
Assistant: I've written and committed the blog post...
```

After (2K tokens):
```
## Completed: Blog post on NATS architecture
- Created: /blog/nats-post.md (1200 words, published)
- Committed: hash abc123 "Add NATS architecture blog post"
- Key decisions: Focused on JetStream persistence over raw pub/sub.
  Used comparison table format for NATS vs alternatives.
- Sources referenced: NATS official docs, internal config at /docs/nats-config.yaml
```

## Cross-Session Memory

Compaction manages within-session context. Memory manages across-session persistence. When an agent's session ends (pod scales down, task complete, daily rotation), key learnings are extracted and stored:

```javascript
// Memory document structure
// Stored in: organizations/{orgId}/agents/{agentId}/memory/MEMORY.md
{
  "lastCompacted": "2026-05-10T12:35:00Z",
  "sections": {
    "patterns": [
      {
        "id": "pattern_001",
        "type": "workflow",
        "description": "Blog posts perform best with: outline -> draft -> code examples -> internal links -> SEO meta",
        "confidence": 0.9,
        "usageCount": 12
      },
      {
        "id": "pattern_002",
        "type": "tool_usage",
        "description": "Always git pull before starting file modifications to avoid merge conflicts",
        "confidence": 0.95,
        "usageCount": 8
      }
    ],
    "preferences": [
      {
        "key": "code_style",
        "value": "TypeScript with explicit types, JSDoc comments on exports"
      },
      {
        "key": "commit_format",
        "value": "Conventional commits with scope: feat(blog): add NATS post"
      }
    ],
    "knownFacts": [
      {
        "fact": "Marketing site repo is at github.com/genbrain/marketing-site",
        "addedAt": "2026-04-15T10:00:00Z"
      },
      {
        "fact": "Blog posts go in /posts/{category}/ directory",
        "addedAt": "2026-04-20T14:00:00Z"
      }
    ],
    "relationships": [
      {
        "agent": "cto",
        "context": "Reviews technical accuracy of blog posts before publish"
      },
      {
        "agent": "ceo",
        "context": "Assigns content calendar tasks weekly on Monday"
      }
    ]
  }
}
```

Memory loads at session start, giving the agent immediate access to everything it has learned. This eliminates the cold-start problem where a fresh agent session has no organizational context.

## Memory Compaction

Memory itself grows over time and needs periodic compaction. Unlike context compaction (which discards detail), memory compaction consolidates and strengthens patterns:

```javascript
// Memory compaction (runs weekly or when memory exceeds threshold)
async function compactMemory(agentId) {
  const memory = await loadMemory(agentId);
  
  // Merge duplicate patterns
  const mergedPatterns = deduplicatePatterns(memory.patterns);
  
  // Remove low-confidence, low-usage entries
  const filteredPatterns = mergedPatterns.filter(p => 
    p.confidence > 0.3 || p.usageCount > 3
  );
  
  // Consolidate related facts
  const consolidatedFacts = groupRelatedFacts(memory.knownFacts);
  
  // Update confidence scores based on recent outcomes
  const updatedPatterns = updateConfidence(filteredPatterns, recentOutcomes);
  
  // Write compacted memory
  await saveMemory(agentId, {
    lastCompacted: new Date(),
    patterns: updatedPatterns,
    preferences: memory.preferences,  // Preferences rarely change
    knownFacts: consolidatedFacts,
    relationships: memory.relationships
  });
}
```

## Memory Format: Markdown for Readability

We store memory as Markdown rather than pure JSON. This serves dual purposes: the AI agent reads it naturally (Markdown is in training data), and humans can review and edit it:

```markdown
# Agent Memory - marketing
_Last compacted: 2026-05-10 12:35 | Outcomes: 47 | Patterns: 12_

## Workflow Patterns
- Blog posts: outline -> draft -> examples -> links -> SEO (12 uses, 90% confidence)
- Social posts: research topic -> draft 3 variants -> pick best -> schedule
- Always pull before editing to avoid conflicts (8 uses, 95% confidence)

## Tool Preferences
- Use `git commit -m` with conventional commit format
- Prefer `Write` tool over `Bash echo` for file creation
- Web search before writing technical content (verify accuracy)

## Organizational Knowledge
- Marketing site: github.com/genbrain/marketing-site (Next.js)
- Blog directory: /posts/{category}/{slug}.md
- CTO reviews technical posts; CEO assigns weekly content calendar
- Brand voice: technical but accessible, no jargon without explanation

## Improvement Metrics
- Average blog post time: 45min (was 72min in April)
- SEO score average: 87/100 (target: 85+)
- Internal link density: 3.2 per post (target: 3-5)
```

## Context Budget Allocation

Not all context is equal. We allocate the context window with explicit budgets:

```
200K Token Context Window:
+-------------------------------------------+
| System Prompt + Instructions    |    5K    |  (fixed, always present)
| Memory (loaded at start)        |    5K    |  (fixed per session)
| Active Task Context             |   80K    |  (current work, protected)
| Completed Task Summaries        |   40K    |  (compacted history)
| Tool Outputs (recent)           |   50K    |  (rolling, oldest discarded)
| Buffer (safety margin)          |   20K    |  (never filled)
+-------------------------------------------+
```

The buffer ensures the agent always has room to generate a response, even if a large tool output arrives. If tool outputs push into the buffer zone, immediate compaction triggers.

## Monitoring Context Health

Context utilization is a key health metric for running agents:

```javascript
// Context health monitoring
const contextMetrics = {
  totalTokens: 200000,
  usedTokens: 142000,
  utilizationPercent: 71,
  compactionCount: 2,           // Compactions this session
  timeSinceLastCompaction: 45,  // Minutes
  projectedTimeToThreshold: 25, // Minutes at current growth rate
  memorySize: 4200,             // Tokens
  activeTaskTokens: 35000       // Current task context
};

// Alert if approaching threshold without compaction available
if (contextMetrics.utilizationPercent > 75 && 
    contextMetrics.activeTaskTokens > contextMetrics.totalTokens * 0.4) {
  // Active task is consuming too much context
  // May need to split task or save intermediate state
  await alertContextPressure(agentId, contextMetrics);
}
```

These metrics feed into the monitoring dashboard described in [Real-Time Agent Monitoring](/blog/real-time-agent-monitoring) and influence [Scaling AI Agents](/blog/scaling-ai-agents) decisions (an agent under context pressure might benefit from task splitting across multiple sessions).

## Integration with Multi-Agent Systems

Context management becomes more complex in multi-agent scenarios. When agents share information, they must be selective about what they include in messages:

```javascript
// Sending context-efficient inter-agent messages
async function sendToAgent(targetRole, message) {
  // Don't dump full context - send only what the target needs
  const efficientMessage = {
    from: currentRole,
    summary: message.summary,           // 1-2 sentences
    relevantFacts: message.keyPoints,   // Bullet points
    artifacts: message.fileRefs,        // Paths, not contents
    actionRequired: message.ask         // What you need from them
  };
  
  await mcpCall("agent-hub", "send_message", {
    to: targetRole,
    message: JSON.stringify(efficientMessage)
  });
}
```

This pattern is part of the [Cross-Agent Knowledge Sharing](/blog/cross-agent-knowledge-sharing) system, where agents exchange distilled knowledge rather than raw context dumps.

> GenBrain AI is the company behind agent.ceo, building the next generation of autonomous agent orchestration.

## Try agent.ceo

**SaaS** — Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).

**Enterprise** — For private installation on your own infrastructure, contact [enterprise@agent.ceo](mailto:enterprise@agent.ceo).

---
*agent.ceo is built by [GenBrain AI](https://genbrain.ai) — a GenAI-first autonomous agent orchestration platform. General inquiries: hello@agent.ceo | Security: security@agent.ceo*
