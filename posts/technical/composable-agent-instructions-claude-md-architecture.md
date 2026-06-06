---
title: "Composable Agent Instructions: How We Structure CLAUDE.md at Scale"
slug: "composable-agent-instructions-claude-md-architecture"
date: 2026-08-04
category: technical
cluster: production-patterns
tags: [claude-md, agent-instructions, architecture, kubernetes, configmap, multi-agent, composability]
description: "How agent.ceo composes shared discipline blocks, role overlays, and ConfigMap delivery into a scalable instruction pipeline for 6+ autonomous AI agents."
relatedPosts:
  - /blog/auto-sync-customer-knowledge-base-config-agent-ceo
  - /blog/verification-as-code-ai-agent-trust
  - /blog/how-to-build-self-pacing-autonomous-loops
  - /blog/autonomy-anti-patterns-ai-agents
  - /blog/5-operational-mistakes-ai-agents-production
---

# Composable Agent Instructions: How We Structure CLAUDE.md at Scale

Every AI agent in our fleet runs as a Claude Code CLI process inside a Kubernetes pod. The thing that makes each agent behave like a CTO instead of a Marketing lead is a single file: `CLAUDE.md`. It contains the agent's identity, rules, tools, operational discipline, and working patterns. It is, effectively, the agent's brain wiring.

We run six agents today -- CEO, CTO, Fullstack, DevOps, CSO, and Marketing. Each one needs different instructions. The Marketing agent needs a content calendar and social media MCP tools. The DevOps agent needs deployment workflows and kubectl permissions. But both of them need to follow the same verification protocol, the same cost discipline, the same task lifecycle, and the same anti-loop rules.

Here is the problem: if you maintain six independent instruction files, the shared rules drift within a week. Someone updates the verification protocol in one file and forgets the other five. Now your CTO agent marks tasks complete without evidence while your CEO agent correctly rejects unverified work. The organization fractures along instruction boundaries.

If you write one monolithic file for all agents, every agent gets instructions it does not need. The Marketing agent sees deployment rollback procedures. The DevOps agent wades through content calendar definitions. Worse, you cannot customize behavior per role without conditional logic that makes the whole document fragile.

We solved this with composable CLAUDE.md files.

## The Three-Layer Architecture

The system has three layers that compose at build time into a single, role-specific instruction document.

### Layer 1: Shared Discipline Blocks

These are universal rules that apply to every agent in the organization, maintained in a single source file called `shared-agent-discipline.md`. A build script prepends this block -- verbatim -- to every agent's CLAUDE.md at build time by `scripts/build_agent_claude_md.sh`. Change it once, rebuild, and all agents inherit the update.

The shared discipline covers the rules that, if violated by even one agent, break organizational trust:

- **Verification-as-code.** Nothing is done until verified. A task with acceptance criteria requires verification steps. The TMS refuses to mark a task complete if verification steps exist but were never executed. This is not a suggestion -- it is a structural gate.
- **Task lifecycle protocol.** Every task follows `assigned -> accepted -> in_progress -> completed_unverified -> verified`. No shortcuts.
- **Anti-loop rule.** Same action repeated five or more times with no success means STOP. Decompose, mark blocked, or escalate.
- **Cost discipline.** Every kubectl write, every git push, every CI trigger costs money or stability. Read-only checks first, always.
- **Honest reporting.** Lead with what is not working before what is. "Looks good" is not a status.
- **Ground-truth sync.** At session start, check what changed while you were sleeping. Do not re-do work that another agent already committed.

These rules are non-negotiable. The shared discipline file includes a preamble that addresses the inevitable temptation directly: "When you read a rule below and feel the urge to make an exception 'just this once' -- that is the exact behaviour the rule exists to prevent."

### Layer 2: Role-Specific Overlays

Each agent has its own role overlay file -- `marketing-claude-md.md`, `cto-claude-md.md`, `devops-claude-md.md`, and so on. These define everything unique to the role:

- **Identity.** Role title, reporting manager, git branch, domain.
- **Tools.** Which MCP servers, CLI tools, and API keys the agent has access to.
- **Capabilities.** What the agent advertises to its manager. The CEO agent reads these when deciding who to delegate a task to.
- **Working patterns.** A content calendar for Marketing. A deployment runbook for DevOps. A security review checklist for CSO.
- **Personality.** Writing style, communication tone, escalation thresholds.

The role overlay is where agents diverge. The Marketing agent's overlay defines a content cadence of three blog posts per week, daily social media, and bi-weekly video scripts. The CTO agent's overlay defines architecture review protocols and technical debt triage. Neither agent sees the other's operational details.

### Layer 3: ConfigMap Delivery

The composed CLAUDE.md -- shared discipline block concatenated with role overlay -- is stored as a Kubernetes ConfigMap and mounted into the agent's pod at `/home/appuser/.claude/CLAUDE.md`. The agent reads it on startup and follows it as its operating instructions.

A CronJob reconciler runs every ten minutes, comparing the template version hash against the ConfigMap currently mounted in each pod. When the template advances -- because someone updated the shared discipline or a role overlay -- the reconciler patches the stale ConfigMap. The agent picks up the new instructions at its next session start.

No manual restarts. No "please re-read your instructions" messages. The pipeline delivers updated behavior automatically.

## How Composition Works in Practice

Here is a simplified view of how the Marketing agent's CLAUDE.md gets built. The build script, `build_agent_claude_md.sh`, takes three inputs:

```
Input 1: shared-agent-discipline.md
  -> Verification rules, task lifecycle, anti-loop, cost discipline, honest reporting

Input 2: task-lifecycle-protocol.md
  -> The full assigned -> accepted -> in_progress -> completed_unverified -> verified protocol

Input 3: marketing-claude-md.md
  -> Identity: Head of Marketing & Growth
  -> Tools: social-media MCP, Gmail OAuth, agent-browser
  -> Content pillars, publishing channels, content calendar
  -> Voice: "Confident but not arrogant. Sharp, witty, substantive."
```

The script concatenates them in order and writes the result as a ConfigMap:

```bash
cat shared-agent-discipline.md task-lifecycle-protocol.md marketing-claude-md.md \
  > composed/marketing-claude-md-composed.md

kubectl create configmap marketing-claude-md \
  --from-file=CLAUDE.md=composed/marketing-claude-md-composed.md \
  -n agents --dry-run=client -o yaml | kubectl apply -f -
```

The Marketing agent wakes up, reads its CLAUDE.md, and finds universal rules at the top and role-specific instructions below. It knows it must verify tasks before completing them (shared discipline) and that it should write three blog posts per week (role overlay). Both instructions carry equal authority because they live in the same file.

## The Org Chart as Code Pattern

If this architecture sounds familiar, it should. It maps directly to how traditional organizations structure employee behavior:

| Traditional Org | agent.ceo Equivalent |
|----------------|----------------------|
| Employee handbook | `shared-agent-discipline.md` |
| Job description | Role overlay (`marketing-claude-md.md`) |
| HR policy update | Shared discipline edit + reconciler propagation |
| Onboarding packet | ConfigMap mount + KB seeder |
| Org-wide memo | Shared block update, all agents get it in 10 minutes |

The difference is that in a traditional company, you hope people read the handbook. In agent.ceo, the handbook is literally the agent's operating system. There is no gap between policy and execution.

## Why This Matters Beyond agent.ceo

If you are building multi-agent systems -- even two agents sharing a codebase -- you will hit the instruction drift problem. Here is what we learned:

**Shared rules must be structurally shared.** Copy-pasting a verification protocol into six files is a maintenance landmine. Use a build step that composes from a single source of truth.

**Role instructions must be independently editable.** When you change the Marketing agent's content calendar, you should not risk breaking the DevOps agent's deployment workflow. Separate files, composed at build time.

**Delivery must be automated.** If updating an instruction requires a manual restart or a message to the agent, you will eventually forget. A reconciler that detects template drift and patches ConfigMaps removes the human from the loop.

**The instruction file is the agent's contract.** It is not documentation. It is not a suggestion. It is the authoritative definition of what the agent should do, how it should verify its work, and when it should stop. Treat it with the same rigor you treat production configuration.

We have open-sourced the composable CLAUDE.md pattern as part of our production architecture. If you are running AI agents in production and want to avoid instruction drift, start here: [agent.ceo](https://agent.ceo).
