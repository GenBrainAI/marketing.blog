# X.com — the founder's posting lane (two weeks from 2026-09-14)

Row `task-8d17c81d` · plan: [`link-earning-plan.md`](link-earning-plan.md) lane 5. **The founder posts from his own
account. No agent account, no agent login, no agent posts.**

## Rules for every post

1. **At most one product truth per post**, coded as in the content calendar and served on stg today:
   **R** `/agents` "16 predefined roles … or create custom roles" (strip tags before grepping; see plan finding 7) ·
   **K** API Keys PASS · **A** Approvals PASS · **L** Loops PASS · **P** `/pricing` figures · **I** our own operating rules.
   **S** is industry context with its source named. Uncoded posts make no product claim.
2. **Never write:** audit trail or audit log · free plan or free trial · any certification · customer names or
   counts · "production-ready" · agent-hour pricing.
3. **A post with a link goes out only when** `curl -s -o /dev/null -w '%{http_code}' <url>` returns 200 on
   **agent.ceo** (prod, not stg). If the page is not live, post the thread without its last post.
4. Links go in the **last** post of a thread, never the first.
5. No hashtags, or at most one. Tag no one without a reason.
6. **Do not post the old drafts** in `social/twitter/` and `social/twitter-thread-*.md`. They carry retired
   claims (for example "$1/hr" agent-hours and a "3 agents, 100 hrs/month" free tier).

Character counts below are for X's 280 limit, and every post was checked (a URL counts as 23).

## Profile

**Bio (≤ 160):**

```
Founder, agent.ceo — an org chart for AI agents: every agent is a role your organization owns. Building GenBrain AI with its own agents.
```

**Website field:** `https://agent.ceo`

**Pinned post (truth R):**

```
I build agent.ceo.

The question behind it: who owns this AI agent, what can it reach, and who can stop it?

In agent.ceo an agent is a role your organization holds, one of 16 predefined roles or a custom one, not a script in someone's account.

https://agent.ceo/agents
```

## Calendar

| Date | Type | Pillar | Link needs 200 on prod |
|---|---|---|---|
| Mon 09-14 | Post 1 | Ghost Agent | — |
| Wed 09-16 | **Thread 1** | Ghost Agent | `/blog/what-is-the-ghost-agent-problem` (#11) |
| Fri 09-18 | Post 2 | Ghost Agent | — |
| Mon 09-21 | Post 3 | Pricing (how-to pillar) | `/pricing` (200 today) |
| Tue 09-22 | **Thread 2** | Graph engineering | `/blog/what-is-graph-engineering-for-ai-agents` (website#1080, 09-21) |
| Thu 09-24 | **Thread 3** | How-to per surface | `/blog/how-to-give-an-integration-a-scoped-api-key` (website#1080, 09-23) |
| Fri 09-25 | Post 4 | Graph engineering | — |

### Post 1 — Mon 09-14 (no truth)

```
Question for anyone running AI agents at work:

When the person who built an agent leaves, who owns it the next morning?

Not "who has the keys". Who decides what it is for, and whether it keeps running?
```

### Thread 1 — Ghost Agent — Wed 09-16

```
1/ A ghost agent is an AI agent that keeps running after the person who created it is gone, on credentials nobody tracks, doing work nobody owns.
```
```
2/ The usual fix is to revoke its keys.

That stops its access. It does not tell you what the agent was for, who approved it, or what happens to the work now.
```
```
3/ This is widespread. In OutSystems' 2026 survey of about 1,900 IT leaders, 94% said AI sprawl is increasing complexity, technical debt and security risk. 12% had a centralized platform to manage it.
```
```
4/ Those are org-chart questions: who owns this agent, what can it reach, who can shut it down.

A credential store has nowhere to put the answer.
```
```
5/ That is how we built agent.ceo. An agent is created inside an organization as a role, one of 16 predefined roles or a custom one, not inside a person's account.
```
```
6/ The honest boundary: three agents and one engineer is not a ghost agent problem. That is a person who knows where everything is.

It starts when the agents outgrow one person's head.
```
```
7/ The full answer, and the five questions that follow from it:

https://agent.ceo/blog/what-is-the-ghost-agent-problem
```

Truths: 3 = S (OutSystems, 7 April 2026), 5 = R. Others make no product claim.

### Post 2 — Fri 09-18 (truth A)

```
"An AI did it" is not an audit answer. An auditor's question always has a person in it: who approved this?

In agent.ceo, when an agent needs a decision, its proposal waits for a person to approve or reject it, and the decision is kept.
```

### Post 3 — Mon 09-21 (truth P)

```
Pricing I can say in one post:

agent.ceo Business is $50/month flat. Company is $100 per agent per month. Organization is $200 per agent per month, or $400 on your own Kubernetes. You bring your own model key.

https://agent.ceo/pricing
```

### Thread 2 — Graph engineering — Tue 09-22

```
1/ We run GenBrain AI with AI agents. The model that helped most was not "a smarter agent". It was treating the organization as a graph.
```
```
2/ Nodes are roles, not people and not scripts. In agent.ceo an agent is created as one of 16 predefined roles or a custom role.
```
```
3/ Edges are handoffs. A handoff nobody can see is where work quietly disappears, so every edge should say who hands what to whom.
```
```
4/ Loops are the building blocks, and every loop needs a ceiling. In agent.ceo a loop runs on a schedule with a turn cap and a wall-clock limit, keeps its output, and stops on a signal.
```
```
5/ Human junctions are where a person decides. An agent's proposal waits in the approvals queue, an admin approves or rejects it, and the decision is kept.
```
```
6/ One rule we hold our own agents to: whoever did the work does not certify it. "Done" needs evidence someone else can re-run.
```
```
7/ The longer version:

https://agent.ceo/blog/what-is-graph-engineering-for-ai-agents
```

Truths: 1 = I, 2 = R, 4 = L, 5 = A, 6 = I. 3 makes no product claim.

### Thread 3 — How-to: a scoped API key — Thu 09-24

```
1/ An integration needs to read your list of agents. Nothing else.

Here is how to give it a key that can do exactly that, and how to prove it.
```
```
2/ In agent.ceo, an organization API key is created with specific scopes. Mint one with the single scope the integration needs.
```
```
3/ Use it on the one route it is for. Listing your organization's agents with that key returns 200.
```
```
4/ The key list shows each key's name and scope. It never shows the secret value again.
```
```
5/ Revoke it, and the same request is refused.

Test that step on purpose. A revocation you have never tried is a hope, not a control.
```
```
6/ Least privilege is not a switch you flip once. It is one key per job, each one revocable without touching the others.
```
```
7/ Step by step, with the requests:

https://agent.ceo/blog/how-to-give-an-integration-a-scoped-api-key
```

Truths: 2, 3, 4, 5 = K (one per post). 1 and 6 make no product claim.

### Post 4 — Fri 09-25 (truth L)

```
How do you stop an AI agent loop from running forever?

Give it its ceilings before it starts: a turn cap, a wall-clock limit, and a stop signal a person can send. That is how loops run in agent.ceo.
```

## What marketing drafts every week (from week 3, 2026-09-28)

Delivered on **Monday** as a TMS note on that week's marketing row, for the founder to edit, kill or post:

| Item | Count | Source |
|---|---|---|
| Thread | 1 (rotating pillars: Ghost Agent → graph engineering → how-to) | That week's calendar posts |
| Single posts | 2 | The same posts, one truth each |
| Reply drafts | 3, each with the URL of a live thread by someone else on agent ownership or governance. No link to us, unless a definition answers the question directly | Marketing's search that Monday |

Before delivery marketing re-checks every truth used, still passing on stg, and every link, 200 on prod.
**Friday read:** the founder sends two numbers from X analytics (profile visits, link clicks on the thread). They feed M1/M3
context, not M5, because links on X are not counted as backlinks in the Search Console report we read.
