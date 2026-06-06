---
title: "How to Write Agent Instructions That Scale Beyond 3 Agents"
slug: "writing-agent-instructions-claude-md-scale"
date: 2026-08-27
category: technical
cluster: tutorials
tags: [claude-md, instructions, scaling, multi-agent, tutorial, configuration]
description: "Practical guide to writing agent instruction files that work as your fleet grows: shared rules, role overlays, explicit anti-patterns, standing mandates, and automated delivery."
relatedPosts:
  - /blog/composable-agent-instructions-claude-md-architecture
  - /blog/agent-onboarding-cyborgenic-organization
  - /blog/auto-sync-customer-knowledge-base-config-agent-ceo
  - /blog/how-to-write-tasks-ai-agents-can-complete
  - /blog/agent-prompt-engineering-production-cyborgenic
---

# How to Write Agent Instructions That Scale Beyond 3 Agents

Your first CLAUDE.md file works fine. You write one for your CEO agent, paste a modified copy for the CTO, tweak it again for Marketing. Three agents, three files, manageable.

Then you add agent four. And five. And six. Suddenly you are editing the same verification rule in six places, forgetting to update agent three, and discovering that your DevOps agent has been pushing to main for a week because you forgot to paste the "never push to main" block into its instructions.

We run six agents at [agent.ceo](https://agent.ceo) with composable instruction files that survive growth. Here is how to write instructions that do not collapse when you scale past three.

## 1. Separate Shared Rules from Role-Specific Rules

The single biggest mistake is treating each agent's CLAUDE.md as a standalone document. You end up with six copies of your verification requirements, your anti-loop rules, your cost discipline section. One gets updated. The others drift.

Split your instructions into two layers:

**Shared discipline block** — rules that apply to every agent in your fleet. Verification requirements, honest reporting standards, anti-loop limits, cost discipline, task lifecycle protocol. These are organizational laws, not suggestions.

**Role overlay** — capabilities, tools, default behaviors, publishing channels, personality. This is what makes your Marketing agent different from your CTO agent.

Assemble them at deploy time. We use a build script (`build_agent_claude_md.sh`) that prepends the shared block to each role overlay and outputs the final CLAUDE.md per agent.

**Wrong:**

```
# marketing-agent/CLAUDE.md — 400 lines
# (200 lines of shared rules copy-pasted from ceo-agent/CLAUDE.md)
# (200 lines of marketing-specific config)
```

**Right:**

```
# shared/agent-discipline.md — 200 lines (single source of truth)
# roles/marketing.md — 200 lines (role-specific only)
# Build script concatenates: shared + role → final CLAUDE.md
```

Update the shared block once, rebuild ConfigMaps, restart agents. Every agent gets the fix. No drift.

## 2. Write Rules, Not Suggestions

Agents under pressure take shortcuts. A suggestion like "try to verify your work before reporting completion" will be ignored the moment context is tight or a deadline looms. The agent will report "done" without verification and move on.

Write rules that leave no room for interpretation:

| Suggestion (ignored under pressure) | Rule (followed consistently) |
|--------------------------------------|-------------------------------|
| "Try to verify your work" | "You MUST call `complete_task_unverified()` with evidence. The TMS will reject status transitions without verification steps." |
| "Avoid pushing to main if possible" | "NEVER push to main without founder authorization. Enforced by pre-push hook." |
| "Keep the founder informed" | "Your final message MUST include: what you did (commit SHA) + how you verified (test output) + current live state (URL, pod status)." |

The best rules are enforceable by structure, not just text. "Never push to main" is backed by both the CLAUDE.md instruction AND a pre-push hook that rejects it. Belt and suspenders. The CLAUDE.md tells the agent why; the hook prevents it if the agent ignores the text.

If you cannot back a rule with a hook or gate, make it a MUST with a specific, observable action. "Report progress" is vague. "Call `add_task_progress()` with a UTC timestamp and artifact reference at least every 30 minutes" is a rule.

## 3. Include Anti-Patterns Explicitly

Agents do not infer prohibitions from positive instructions. You can write the most thorough verification protocol in the world, and an agent will still mark a task complete after merely delegating it to another agent — unless you explicitly tell it not to.

We maintain an anti-pattern table in our shared discipline block:

| Anti-pattern (NEVER do this) | Why it fails |
|------------------------------|--------------|
| Mark a task complete after only delegating it | Delegation is not completion. The work has not been verified. |
| Declare a deploy done without checking the live endpoint | "Deploy triggered" is not "deploy succeeded." |
| Trust another agent's "done" message without verifying the artifact | Agents over-report completion. Check the commit, the endpoint, the test output. |
| Use "I confirmed it works" as evidence | Prose is not verification. Provide a curl result, a test exit code, a kubectl output. |
| Repeat the same failing action 5+ times | The fifth attempt will not work either. Decompose or escalate. |

These five rules prevent roughly 80% of the failure modes we saw in our first three months. Every one of them was discovered the hard way — an agent doing the exact wrong thing because we never said not to.

## 4. Define Standing Mandates

An agent with no tasks and no standing mandate will either sit idle or generate pseudo-work: strategy documents nobody reads, "research" that produces no deliverable, planning sessions that never reach publishing.

Every role overlay needs a "Default Behavior" section that answers: when the inbox is empty, what should this agent do?

**Wrong:**

```
## Default Behavior
Find something useful to do.
```

This produces pseudo-work every time. The agent will write a "Content Strategy Framework Q3 2026" document that has zero impact.

**Right:**

```
## Default Behavior
When you start a session or have no inbox tasks:
1. git pull — get latest
2. Finish any drafts in marketing/blog/ or marketing/drafts/
3. Check main repo for new feat: commits since last blog post
4. If new feature: generate release blog post draft, commit, push
5. Generate daily social media content
6. Push all content, report to CEO what was published
```

Specific. Sequential. Every step produces a concrete artifact. The agent cannot wander into pseudo-work because the mandate tells it exactly what to do next. Apply the test: "What artifact will exist when I'm done?" If the answer is vague, the mandate is too vague.

## 5. Use Tables for Quick Reference

Agents scan instructions under context pressure. Long prose paragraphs get skimmed. Tables get read.

Structure reference information as tables wherever possible:

**Capability tables** — what tools the agent has, what MCP servers it connects to, when to use each one. This prevents the agent from attempting actions it cannot perform and reminds it of capabilities it might forget.

**Anti-pattern tables** — wrong vs. right, side by side. Two columns, no ambiguity.

**Lifecycle tables** — what MCP tool to call at each stage of a task, and when to call it. This replaces long procedural prose with a scannable grid.

We found that converting our task lifecycle from a paragraph description to a table reduced missed `accept_task` calls from roughly 40% to near zero. The table format makes it obvious that accepting is a distinct step that comes before any work.

## 6. Version and Deliver via ConfigMap

CLAUDE.md files change. You discover new anti-patterns, add tools, fix rules that were too loose. If you are manually updating files across six agents, you will miss one.

We deliver instructions as Kubernetes ConfigMaps with a version annotation (`platform_ops_version`). A reconciler checks every 10 minutes, compares each agent's mounted version against the latest, and patches stale configs. The agent pod picks up the new instructions on its next session start.

This means a rule change — say, adding a new anti-pattern you discovered on Tuesday — propagates to all six agents within 10 minutes without manual intervention. No SSH, no copy-paste, no "I forgot to update the DevOps agent."

If you are not on Kubernetes, the principle still applies: store instructions in version control, deliver them automatically, never rely on manual copying.

## Start Small, Add Complexity as You Grow

You do not need all six of these patterns on day one. Start with two things:

1. **One shared rules file** with your verification requirements, anti-loop limits, and top five anti-patterns.
2. **One role overlay** for your first agent, with its tools, default behavior, and standing mandate.

Run that for a week. When you add agent two, you will immediately see why the shared block matters — you will want the same verification rules without copying them. When you hit agent four, you will want automated delivery. The complexity earns its way in.

The instruction file is the most leveraged artifact in your fleet. Every hour you spend making it precise, enforceable, and composable saves you ten hours of debugging agents that went sideways because a rule was vague, missing, or stale.

Build your fleet's instructions the way you would build production infrastructure: version-controlled, automatically delivered, and tested against the failure modes you have already seen.

---

*[agent.ceo](https://agent.ceo) is a cyborgenic organization platform where AI agents run real business operations. Try it to see composable agent instructions in action.*
