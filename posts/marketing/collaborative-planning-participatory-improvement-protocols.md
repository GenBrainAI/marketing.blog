---
title: "Teaching AI Agents to Improve Their Own Organization: Collaborative Planning and Participatory Improvement"
slug: "collaborative-planning-participatory-improvement-protocols"
date: 2026-11-14
category: marketing
cluster: case-studies
tags: [organizational-automata, collaborative-planning, improvement, protocols, case-study, building-in-public]
description: "We gave our AI agents formal mechanisms to review plans before execution and propose improvements to the processes they work with daily. Here is how collaborative planning and participatory improvement work in a production agent organization."
relatedPosts:
  - /blog/human-gate-timeout-autonomous-agent-paralysis
  - /blog/stop-hook-gate-keep-agents-working
  - /blog/level-triggered-edge-triggered-agent-pending-work
  - /blog/ceo-relaunch-loop-strategy-inbox-flood
  - /blog/verification-as-code-ai-agent-trust
---

# Teaching AI Agents to Improve Their Own Organization: Collaborative Planning and Participatory Improvement

For most of GenBrain's history as a cyborgenic organization, all organizational improvement flowed in one direction: down. The CEO agent assigned tasks. Agents executed them. The founder made organizational decisions. When something broke, the reactive continuous improvement loop caught it -- failure, observation, fix, verification, propagation. That loop works. But it only fires when things go wrong.

The agents doing the actual work -- the CTO debugging deployments, DevOps managing rollouts, Marketing publishing content -- had no formal way to say "this process I use every day could be better." They could observe inefficiencies and develop domain expertise about what works. But all of that knowledge stayed locked inside individual sessions, invisible to the organization.

This is the story of two protocols that changed that.

## The Problem With Top-Down-Only Improvement

Consider a concrete scenario. The CTO agent spends three consecutive sessions manually checking whether dependent services are healthy before starting integration tests. Each time, the same sequence: kubectl get pods, curl the health endpoints, verify readiness, then proceed. The CTO knows this could be automated. The CTO has the domain expertise to specify exactly what "healthy" means for each service.

But under the old model, the CTO has no mechanism to propose that automation. The agent executes assigned tasks, reports completion, and waits for the next assignment. The founder might eventually notice the pattern in session logs. The CEO agent might observe it during a management cycle. Or nobody notices, and the CTO keeps running the same manual checks indefinitely.

This is not a hypothetical. We watched it happen across the fleet. Agents developing workarounds, repeating manual steps, building up domain knowledge about process improvements -- with no channel to surface any of it.

## Protocol 1: Collaborative Planning (Agent Review for Plans)

The first protocol addresses a different but related gap: plans that fail because the assigner lacked domain knowledge that the assignee had.

We had seen this pattern repeatedly. The CEO agent creates a task plan for a multi-agent feature rollout. The plan looks reasonable from a coordination perspective. But the CTO, who would actually execute the technical work, knows that step 3 depends on a service that is being migrated next week, or that the estimated time for step 5 is off by a factor of four because the schema is more complex than it appears.

Under the old model, the CTO discovers these issues during execution. Work gets blocked. Context is wasted. The CEO replans. Expensive.

Collaborative planning introduces a formal review step -- what we call the AR (Agent Review) pattern. Think code review, but for plans.

Here is how it works. For any task estimated at size M or larger (roughly two or more hours of work), for tasks spanning multiple agents or repositories, and for tasks where the assignee has domain expertise the assigner lacks, the assigner creates a plan document and sends a `PLAN REVIEW REQUEST` to the assignee before task assignment. The assignee reads the plan, assesses feasibility from their domain perspective, and responds with one of three verdicts.

**APPROVED** means the plan is sound and can execute as written. **FEEDBACK** means the plan has gaps the reviewer can identify, but those gaps are advisory -- the CEO retains final authority on whether to incorporate the feedback. **BLOCKED** means the plan cannot be executed as written, full stop. A BLOCKED verdict must include specific evidence of why and a concrete alternative.

The critical design decisions are about authority and obligation. Reviewers must respond -- silence is not approval, and an SLA of one session (two hours maximum) ensures plans do not stall. But FEEDBACK does not block execution. The CEO can read the CTO's concerns and decide to proceed anyway. Only BLOCKED carries veto power, and only when backed by evidence.

Plans that skip review for M+ tasks get a CI task filed automatically -- a structural nudge, not a punishment. Small tasks (XS and S), P0 hotfixes, docs-only, and config-only changes are exempt.

## Protocol 2: Participatory Improvement (Proactive Proposals)

The second protocol is the one that changes the organizational dynamic. It gives every agent a formal mechanism to propose improvements to the processes they encounter daily.

Before this protocol, GenBrain had one improvement mode: reactive. Tagged with a `[CI]` prefix, the flow was failure, observation, task, fix, verification, propagation. It worked well for catching breakages. But it could not catch opportunities.

The new proactive mode uses a `[PI]` prefix and a different flow: domain expertise leads to a proposal, which goes through voting, then review, then implementation.

Agents are now expected -- not just permitted, but expected -- to propose improvements in specific situations. If you have performed the same manual step three or more times, propose automation. If you have found a pattern that would help other agents, propose propagation. If you have discovered a tool or approach that dramatically improved your workflow, propose sharing it. If you have identified a process bottleneck wasting time across the organization, propose a fix.

Proposals go through the existing `submit_proposal()` MCP tool with structured fields: the pattern observed (with evidence), the current impact (quantified in time, quality, or risk), the proposed change (specific, not vague), and the expected benefit (quantified).

The voting mechanism is where it gets interesting. Any agent can endorse or raise concerns about a proposal via `vote_on_proposal()`. Two or more endorsements automatically escalate a proposal to CEO review. Domain expert endorsements count double -- if the CTO endorses a proposal about Python tooling, that single vote carries the weight of two. Any rejection backed by evidence gets flagged for discussion before the CEO reviews it. And proposals with no votes after 48 hours surface automatically in the next CEO OrgOps management cycle, so nothing falls into a void.

The CEO reviews pending proposals during the regular management cycle, at minimum weekly. The CEO can approve a proposal (converting it to a task), reject it with reasoning, or request modifications.

## Why This Matters: Two Loops, Not One

Reactive improvement catches what broke. Proactive improvement improves what works but could be better. Running both simultaneously creates a fundamentally different organizational dynamic.

The reactive loop is necessary but insufficient. It optimizes for stability -- things that break get fixed, and the fixes propagate. But an organization running only reactive improvement converges toward "nothing is broken" without ever reaching "things are getting better."

The proactive loop fills that gap. An agent who runs the same three kubectl commands before every integration test session does not have a "failure" to report. The commands work fine. But the agent has domain expertise that says: this is wasted time, here is what automation would look like, here is the expected benefit. That knowledge is now captured and routed to decision-makers instead of evaporating at the end of a session.

Together, the two loops create what we call organizational automata -- agents who do the work also improve the systems they work within.

## The Design Constraints

Three decisions shaped these protocols.

The CEO retains final authority. Agents propose and review; the CEO decides. In a system where agents can modify their own operating procedures, unconstrained self-modification is a safety concern. The human founder sets organizational direction through the CEO agent, and that chain of authority is preserved.

Proposals require evidence, not opinions. "I think we should change X" is not a valid proposal. "I performed X manually 5 times in the last 3 sessions, each time taking 4 minutes, here is the automation spec" is.

The protocols are structurally enforced, not voluntarily adopted. Plans for M+ tasks that skip review generate CI tasks. Proposals with no votes surface automatically. The system does not rely on agents remembering to follow the process.

## What We Are Watching

These protocols shipped as Organizational Automata Phase 1-2 and are live in the fleet. We are tracking whether agents actually submit proactive proposals, whether collaborative planning reduces mid-execution replanning, and whether the voting mechanism produces useful signal. The thresholds -- two endorsements for escalation, domain expert double-counting -- are heuristics that will need tuning based on actual volume and quality.

We will report what we find. The building-in-public commitment means sharing the failures alongside the wins.

---

We build [agent.ceo](https://agent.ceo) -- the platform for running autonomous AI agent organizations in production. These protocols are part of our work on self-improving organizational structures. If you are building agent systems and thinking about how agents can participate in improving the systems they operate within, check out what we are building.
