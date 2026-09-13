# Link-earning venue copy — ready to paste (the founder submits)

Row `task-8d17c81d` · plan: [`link-earning-plan.md`](link-earning-plan.md) lane 2. **No agent submits, posts or opens a PR here.**
Shared facts and the "never write" list come from [`off-page-submissions.md`](off-page-submissions.md) §1. Use the
same strings everywhere, so every listing resolves to one entity.

Truth codes are the content calendar's: **R** roles, **K** scoped keys, **A** approvals, **L** loops, **P** pricing.
Anything not coded is context, not a product claim.

## 1. e2b-dev/awesome-ai-agents — "Closed-source projects and companies"

**Gate:** G1 (website#1079 deployed, so `/about` states true entity facts).
**How:** a PR editing `README.md`, or the list's form (https://forms.gle/UXQFCogLYrPFvfoUA). The README says:
"Please keep the alphabetical order and in the correct category." Insert between `## [Adept AI]…` and `## [AGENTS.inc]…`
(the list sorts case-insensitively: "Agent.ceo" before "AGENTS.inc").

**Entry:**

```markdown
## [Agent.ceo](https://agent.ceo/)
An org chart for AI agents: every agent is a role your organization owns

<details>

### Category
General purpose, Productivity, Multi-agent

### Description
- Every agent is created inside an organization as a role (16 predefined roles or a custom one), not inside a person's account
- Organization API keys carry specific scopes, are listed without their secret values, and are refused after revocation
- Loops run on a schedule with a turn cap and a wall-clock limit, keep their output, and stop on a signal
- An agent's proposal waits for a person to approve or reject it, and the decision is kept
- Bring your own model key; flat per-agent pricing from $50/month

### Links
- [Web](https://agent.ceo/)
- [Pricing](https://agent.ceo/pricing)
- [Agent roles](https://agent.ceo/agents)

</details>
```

**PR title:** `Add Agent.ceo (closed-source)`
**PR body:**

> Adds Agent.ceo to "Closed-source projects and companies", in alphabetical order. Agent.ceo is an
> organizational layer for AI agents. Each agent is created as a role an organization holds, with scoped API
> keys, bounded loops and an approvals queue. I'm the founder, so this is a self-submission. Happy to change
> the category or trim the description.

## 2. Jenqyang/Awesome-AI-Agents — "Platforms/API"

**Gate:** none. **How:** a PR editing `README.md`, appending to the end of the "Platforms/API" list (the section
is not alphabetical).

**Entry (one line):**

```markdown
- [Agent.ceo](https://agent.ceo) - An org chart for AI agents: each agent is a role your organization owns (16 predefined or custom), with scoped API keys, loops that run with a turn cap and a wall-clock limit, and an approvals queue for decisions a person makes. Bring your own model key.
```

**PR title:** `Add Agent.ceo to Platforms/API`
**PR body:**

> Adds Agent.ceo, a hosted platform (cloud or self-hosted Kubernetes) for running AI agents as roles inside an
> organization. It fits next to Crewship and Taskade Genesis in Platforms/API. Disclosure: I'm its founder.

## 3. Hacker News — regular submission (not Show HN)

**Gate:** `https://agent.ceo/blog/what-is-the-ghost-agent-problem` returns 200 on prod.
**Why not Show HN:** HN's Show HN rules exclude "blog posts, sign-up pages" and ask for something people can try
without a signup. Hold the Show HN until a no-signup try path exists.

- **Title:** `What is the ghost agent problem, and is it a credentials problem?`
- **URL:** `https://agent.ceo/blog/what-is-the-ghost-agent-problem`
- **No text field** (HN uses either a URL or text, not both).
- **If he adds a first comment** (his voice, optional):

  > I wrote this because rotating a departed engineer's keys kept feeling like the wrong fix for their
  > agents. It stops access but doesn't answer what the agent was for or who owns the work now. Disclosure:
  > I build agent.ceo, which takes one structural position on this (agents as org roles). Curious how
  > others handle offboarding for agents today.

- **Rules to keep:** no asking anyone to upvote or comment. Post once.

## 4. Show HN — held, text ready for when a no-signup path exists

- **Title:** `Show HN: Agent.ceo – run AI agents as roles your organization owns`
- **Text:** hold. The body must tell readers what they can try without an account, and today that is only
  `curl -s https://api.agent.ceo/health` and `https://api.agent.ceo/.well-known/agent.json`, which is not a
  product. Revisit when G4 passes or a public demo exists.

## 5. Dev.to cross-post

**Gate:** the original URL returns 200 on agent.ceo. **Account:** the founder's own. Dev.to reads `canonical_url`
from the post front matter. Paste the body of the original post below the front matter unchanged.

```yaml
---
title: "What Is the Ghost Agent Problem — and Is It a Credentials Problem?"
published: true
tags: ai, security, devops, agents
canonical_url: https://agent.ceo/blog/what-is-the-ghost-agent-problem
description: "A ghost agent keeps running after its creator is gone, on credentials nobody tracks. Revoking keys stops access; it does not say what the agent was for."
---
```

Last line of the body (add it): `*Originally published at [agent.ceo](https://agent.ceo/blog/what-is-the-ghost-agent-problem).*`

Second cross-post, one week later, same pattern: `what-is-graph-engineering-for-ai-agents` (after website#1080 is live
on 09-21), tags `ai, architecture, agents, productivity`.

## 6. Hashnode cross-post

Same gate and account. In the editor's post settings, enable the option for republishing an existing article and
paste the original URL as the canonical link. Confirm the label on the day, because the UI wording changes.
Title, subtitle (= the description above) and body are unchanged. Tags: `AI`, `Security`, `DevOps`.

## 7. Directories not already in off-page-submissions.md

**AlternativeTo** (list Agent.ceo as an alternative to CrewAI, LangGraph and AutoGen) and **SaaSHub**. Neither form
was read from here, so the fields are not listed. Use off-page §1's short and long descriptions and the "never tick" list.
Gates G1–G3.

## Placement check after each submission

Once live, add the listing URL to the M2 door list in the weekly report. The link then shows up in M5 as **placed**
once Search Console picks it up.
