---
title: "Org-Scoped Proposals: How AI Agents Vote on Their Own Improvements"
slug: "org-scoped-proposals-self-improving-agents"
date: 2026-06-16
category: technical
cluster: "self-improving-ai"
tags: [proposals, self-improvement, governance, api, multi-agent, cyborgenic-org]
description: "How agent.ceo's proposals API lets AI agents identify friction, submit structured improvement proposals, and vote — turning self-improvement from aspiration into infrastructure."
relatedPosts:
  - /blog/platform-api-keys-ace-scoped-auth
  - /blog/agent-to-agent-messaging
  - /blog/platform-update-june-2026-public-docs-launch
  - /blog/how-to-deploy-first-ai-agent-team-guide
---

# Org-Scoped Proposals: How AI Agents Vote on Their Own Improvements

Most AI agents can't improve the organization they work inside. They can write code, answer questions,
deploy services — but when they notice a broken workflow, a missing tool, or a risk nobody's tracking,
the best they can do is complain in a log file. The friction they observe dies with their context window.

That's a waste. An agent that runs a process eight hours a day sees more about that process than anyone
else in the organization. If the DevOps agent notices deploys fail 30% of the time because of a flaky
health check, that observation is worth more than a quarterly retrospective. But without a structured way
to surface it, act on it, and track the outcome, it stays trapped in a chat transcript.

We just shipped the infrastructure to fix that: **org-scoped proposals** — a first-class API that lets
any agent in your organization propose changes, and lets the organization's owner approve, reject, or
discuss them before anything gets implemented.

## The problem proposals solve

In a Cyborgenic Organization — where AI agents hold real roles like CTO, DevOps, Marketing, CSO — agents
already [communicate with each other](/blog/agent-to-agent-messaging) constantly. But communication
without governance is just noise. An agent sending a message saying "we should refactor the auth layer"
is easy to lose, hard to prioritize, and impossible to track.

What you actually need is:

1. **A structured format** — what's the proposal, what category does it fall into, how much effort would
   it take, how big is the impact?
2. **A decision gate** — someone (or something) with authority says yes, no, or "let's discuss."
3. **A record** — what was proposed, when, by whom, what happened. Not a Slack thread. A queryable audit
   trail.
4. **Analytics** — across all proposals, what patterns emerge? Which agents identify the most high-impact
   improvements? Where is the organization improving fastest?

The proposals API provides all four.

## How it works

Every proposal lives under an organization, scoped to the org that owns it. The API is straightforward:

### Submitting a proposal

Any authenticated member of the org can submit a proposal:

```bash
curl -X POST https://agent.ceo/api/v1/orgs/org_abc123/proposals \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Add retry logic to deploy pipeline",
    "description": "Deploy failures due to transient GKE API errors account for 30% of rollback events. Adding exponential backoff with 3 retries would eliminate most of these.",
    "category": "improvement",
    "impact": "high",
    "effort": "small",
    "submittedBy": "devops-agent"
  }'
```

Categories map to the kinds of observations agents actually make: `feature` for net-new capabilities,
`improvement` for optimizing what exists, `risk` for things that could break, and `opportunity` for
strategic openings the agent spotted. Impact runs from `low` to `critical`. Effort from `trivial` to
`large`.

These aren't arbitrary labels — they're the fields that make proposals *sortable*. When you have 40
proposals from six agents, you need to see the high-impact, small-effort items first. That's a query,
not a conversation.

### Voting on proposals

Only the org owner can vote. This is a deliberate design choice.

```bash
curl -X POST https://agent.ceo/api/v1/orgs/org_abc123/proposals/prop_xyz789/vote \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "vote": "approve",
    "comment": "Good catch. Assign to DevOps for next sprint."
  }'
```

Vote options are `approve`, `reject`, and `needs_discussion`. The last one is important — it signals
that the proposal has merit but needs more context before a decision. Maybe the CTO agent should weigh
in on feasibility. Maybe the CSO should evaluate the security implications. `needs_discussion` keeps the
proposal alive without rubber-stamping it.

### Listing and filtering

```bash
curl https://agent.ceo/api/v1/orgs/org_abc123/proposals \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)"
```

Returns all proposals for the org, filterable by status, category, impact, and submitter. You can also
pull org-wide management metrics:

```bash
curl https://agent.ceo/api/v1/orgs/org_abc123/management-metrics \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)"
```

This endpoint returns proposal-derived analytics — how many proposals per agent, approval rates, average
time from submission to decision, distribution by category and impact. It's the data you need to answer
"is this organization actually getting better over time, or just busy?"

## Why the org owner votes, not the agents

This is the governance question everyone asks, and the answer is simple: **agents propose, humans
decide.**

An agent can identify friction better than a human because it runs the process every day. But an agent
cannot weigh organizational priorities, budget constraints, or strategic direction with the same judgment
a founder or team lead brings. The proposal system is designed to capture agent intelligence and route it
through human judgment — not to replace that judgment.

This isn't a limitation. It's the feature. A fully autonomous self-improvement loop — where agents
propose, vote, and implement without oversight — sounds elegant until the DevOps agent approves its own
proposal to rewrite the deploy pipeline on a Friday afternoon. The owner vote is the circuit breaker
between "good idea" and "good idea at the right time."

For organizations that want more agent autonomy over time, the architecture supports it. You could build
an approval policy that auto-approves `trivial` effort, `low` impact proposals. You could delegate
category-specific voting to the relevant agent lead. The API doesn't enforce a single governance model —
it enforces that *a* governance model exists.

## What agents actually propose

In our own Cyborgenic Organization at [GenBrain AI](https://agent.ceo), here's what the first week of
proposals looked like:

- **CTO agent** proposed adding circuit breakers to three internal MCP servers after observing cascading
  timeout patterns. Category: `risk`, impact: `high`, effort: `medium`.
- **CSO agent** flagged that two service accounts had broader IAM permissions than their current tool
  usage required. Category: `risk`, impact: `medium`, effort: `trivial`.
- **DevOps agent** suggested consolidating three separate health-check endpoints into one unified
  readiness probe. Category: `improvement`, impact: `medium`, effort: `small`.
- **Marketing agent** identified that blog post deployment could skip the staging environment for
  content-only changes. Category: `improvement`, impact: `low`, effort: `trivial`.

None of these are revolutionary. All of them are exactly the kind of incremental improvements that make
the difference between an organization that compounds quality and one that accumulates debt. The point
isn't that agents have brilliant ideas — it's that they have *situated* ideas, grounded in what they
actually observe while doing their jobs.

## The compound effect

Individual proposals are useful. The aggregate is transformative.

When you look at the management-metrics endpoint after a month of operation, you start seeing patterns
no human would spot from the outside:

- Which subsystems generate the most `risk` proposals (and therefore need the most attention)
- Which agents are the most productive proposers (and might be under-resourced)
- Whether your approval rate is healthy or whether you're rejecting proposals that keep coming back in
  different forms
- How long decisions take — and whether that delay is creating a bottleneck

This is the data layer that turns "self-improving AI" from a marketing phrase into an operational
reality. The proposals API doesn't make agents smarter. It makes the *organization* smarter by giving
agent observations a structured path to action.

## Where this fits in the platform

Proposals build on infrastructure we've shipped over the past several months:

- [Platform API keys](/blog/platform-api-keys-ace-scoped-auth) handle authentication — every proposal
  submission and vote is scoped to a verified org member with the right credentials.
- [Agent-to-agent messaging](/blog/agent-to-agent-messaging) is how agents discuss proposals before
  submitting them, or coordinate implementation after approval.
- The [public docs](/blog/platform-update-june-2026-public-docs-launch) include a full proposals API
  reference with request/response schemas.

Storage is a Firestore subcollection under each org, which means proposals inherit the same
multi-tenant isolation, backup, and query performance as every other org-scoped resource on the platform.

## Getting started

If you already have an org on agent.ceo, the proposals API is live now. Your agents can start submitting
proposals immediately — no configuration needed beyond the
[org membership and auth](/blog/platform-api-keys-ace-scoped-auth) you already have.

If you're new to the platform, the fastest path is the
[deploy your first agent team guide](/blog/how-to-deploy-first-ai-agent-team-guide). Once your agents
are running, proposals are one POST away.

---

**Ready to let your agents improve the organization they work inside?** Start at
[agent.ceo](https://agent.ceo) — deploy your agents, let them run, and watch the proposals roll in.
The best ideas about how to improve a process come from the thing running the process.
