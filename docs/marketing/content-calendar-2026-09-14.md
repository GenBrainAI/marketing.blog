# SEO / AEO content calendar — 6 weeks from 2026-09-14

Row: `task-8ed603a6` (assigner ceo, verifier ceo). Publication mechanics:
[`publication-mechanics.md`](publication-mechanics.md).

**Goal (founder, 2026-09-13):** a high volume of truthful, question-shaped pages, so search engines
and LLMs notice agent.ceo. Marketing drafts. The founder improves, gives the go per batch, and posts
to LinkedIn himself. No sends. No CRM.

**Rule for every entry:** a post may claim about agent.ceo only the product truth in its row. That
truth is a journey that passed on stg, or text the served site already carries. Anything else is
said as industry context or not said.

## Claim sources, and what they allow

| Code | Source (re-runnable by anyone) | What it allows |
|---|---|---|
| **R** | `stg.agent.ceo/agents` → "16 predefined roles … or create custom roles" | Agents are org roles |
| **K** | Readiness run stg 2026-09-13 03:47Z **API Keys PASS** (agent-hub `docs/org/plan.md`; journey in `docs/readiness/2026-09-11-surface-readiness.md` §API Keys) | Key minted with one scope, used alone on `GET /api/v1/customers/ORG/agents` → 200, listed without value, refused after revoke |
| **A** | Same run **Approvals PASS** | A proposal waits; admin rejects; decision persists |
| **L** | Same run **Loops PASS** | Solo-loop pattern, 60 s cadence, 3-turn cap, 3-min wall limit; output kept; stop signal; no new output after a full cadence |
| **M** | Same run **Meetings PASS** (text journey only) | Create, message, end, transcript and summary kept; non-member 403 |
| **G** | Same run **Registry PASS** | Org's registered agents listed. NB: no per-agent detail route |
| **P** | `stg.agent.ceo/pricing` and `agent.ceo/pricing` both serve $50 · $100 · $200 · $400 · From $2,000 | Pricing figures |
| **D** | Founder 2026-09-13 19:5xZ | No beta price; production is a working cluster; design-partner agreement; contact the founder |
| **I** | agent-hub `CLAUDE.md` shared discipline (our own operating rules) | Dogfooding statements about how we run, not product capability |
| **S** | OutSystems 94%/12% and IBM IBV 18%, URLs 200 with figures present 2026-09-13 | Industry context |

Route existence on **prod** (so how-to posts work for readers): `api.agent.ceo` answers 401 on
`/api/v1/orgs/x/meetings`, `/loops`, `/loop/patterns/capability`, `/api/v1/approvals` and
`/api/v1/customers/x/agents`, and 404 on a fabricated route (measured 2026-09-13 ~19:4xZ).

## The three pillars

1. **Ghost Agent Problem**: problem-first questions an IT or ops leader asks (the L2 GEO layer).
2. **Graph engineering**: roles as nodes, handoffs as edges, bounded loops as building blocks,
   human junctions. Dogfooded: how agent.ceo runs itself.
3. **How-to per surface**: only surfaces whose customer journey is green on stg. The rest are
   listed below with why they wait.

## Calendar

Status: **R** = publication-ready in a merge-held PR · **P** = planned (not drafted).

### Week 1 — launch set (Wed 2026-09-16)

Six pages published **together**, because they cross-link. This is the one week above five. They are
PR marketing.blog#11, and they need a hand-port into the website on go (mechanics §3).

| Date | Slug | Pillar | Target query | Answer-engine question | Truth | St |
|---|---|---|---|---|---|---|
| 09-16 | what-is-the-ghost-agent-problem | 1 | ghost agent problem | What is the ghost agent problem? | R, S | R |
| 09-16 | who-owns-this-ai-agent-registry-not-enough | 1 | who owns an ai agent | Who owns an AI agent, and why isn't a registry enough? | R, G, S | R |
| 09-16 | can-you-add-an-audit-trail-to-ai-agents-later | 1 | ai agent audit trail | Can you add an audit trail to AI agents later? | A | R |
| 09-16 | what-happens-to-ai-agents-when-their-builder-leaves | 1 | ai agents employee leaves | What happens to AI agents when the person who built them leaves? | R | R |
| 09-16 | why-an-ai-did-it-is-not-an-audit-answer | 1 | ai accountability audit | Why is "an AI did it" not an audit answer? | R, A | R |
| 09-16 | when-do-ai-agents-outgrow-one-persons-head | 1 | how many ai agents need governance | When do AI agents outgrow one person's head? | L | R |

### Week 2 — batch 1, first half (this PR)

| Date | Slug | Pillar | Target query | Answer-engine question | Truth | St |
|---|---|---|---|---|---|---|
| 09-21 | what-is-graph-engineering-for-ai-agents | 2 | graph engineering ai agents | What is graph engineering for AI agents? | R, L, A | R |
| 09-22 | how-to-offboard-an-ai-agent | 1 | offboard ai agent | How do you offboard an AI agent when its owner leaves? | R, K, L | R |
| 09-23 | how-to-give-an-integration-a-scoped-api-key | 3 | least privilege api key ai agent | How do I give an integration an API key that can only do one thing? | K | R |
| 09-24 | where-should-a-human-approve-in-an-ai-agent-workflow | 2 | human in the loop approval ai agents | Where should a human approve in an AI agent workflow? | A, R, I | R |
| 09-25 | what-should-an-ai-agent-inventory-record | 1 | ai agent inventory | What should an AI agent inventory record? | R, G, K, S | R |

### Week 3 — batch 1, second half (this PR)

| Date | Slug | Pillar | Target query | Answer-engine question | Truth | St |
|---|---|---|---|---|---|---|
| 09-28 | how-to-stop-an-ai-agent-loop-running-forever | 2 | stop ai agent loop | How do you stop an AI agent loop from running forever? | L, I | R |
| 09-29 | ai-agent-role-or-service-account | 1 | ai agent service account vs role | Should an AI agent have a role or a service account? | R, K | R |
| 09-30 | how-to-run-a-text-meeting-with-agent-ceo-api | 3 | ai agent meeting transcript api | How do I run a meeting in agent.ceo and keep its record? | M | R |
| 10-01 | should-an-ai-agent-verify-its-own-work | 2 | ai agent self verification | Should an AI agent verify its own work? | I | R |
| 10-02 | how-to-create-watch-and-stop-an-agent-loop | 3 | create ai agent loop api | How do I create, watch and stop a loop in agent.ceo? | L | R |

### Week 4 — batch 2 (website#1082)

| Date | Slug | Pillar | Target query | Answer-engine question | Truth | St |
|---|---|---|---|---|---|---|
| 10-05 | how-much-does-an-ai-agent-team-cost | 3 | ai agent platform pricing | How much does it cost to run a team of AI agents? | P, D | R |
| 10-06 | who-is-accountable-when-an-ai-agent-makes-a-mistake | 1 | ai agent accountability | Who is accountable when an AI agent makes a mistake? | R, A (no audit-trail claim) | R |
| 10-07 | human-junction-patterns-for-agent-graphs | 2 | human approval patterns multi agent | What are the patterns for putting a human decision in an agent graph? | A | R |
| 10-08 | how-to-publish-an-app-from-an-agent | 3 | ai agent publish web app | How does an agent publish an app page in agent.ceo? | Apps PASS (read the journey before drafting) | R |

### Week 5 — batch 2 (website#1082)

| Date | Slug | Pillar | Target query | Answer-engine question | Truth | St |
|---|---|---|---|---|---|---|
| 10-12 | ai-agent-kill-switch | 1 | ai agent kill switch | Who can shut an AI agent down, and how fast? | L, K | R |
| 10-13 | solo-loop-the-smallest-agent-building-block | 2 | agent loop patterns | What is the simplest loop pattern for an AI agent? | L | R |
| 10-14 | how-agent-ceo-runs-its-own-company-on-agent-loops | 2 | company run by ai agents | What does it look like when a company runs on AI agents? | I, L | R |
| 10-15 | how-to-list-every-agent-in-your-organization | 3 | list ai agents in organization | How do I list every agent my organization runs? | G | R |

### Week 6 — batch 2 (10-19, 10-20, #1082) and batch 3 (10-21, 10-22, website#1085)

| Date | Slug | Pillar | Target query | Answer-engine question | Truth | St |
|---|---|---|---|---|---|---|
| 10-19 | agent-ceo-design-partners | 3 | agent.ceo design partner | How do I work with agent.ceo as a design partner? | D, P | R |
| 10-20 | shadow-ai-agents-vs-ghost-agents | 1 | shadow ai agents | What is the difference between shadow AI agents and ghost agents? | R | R |
| 10-21 | how-to-test-that-an-agent-check-can-fail | 2 | known negative test ai agent | How do you know an AI agent's check can actually fail? | I | R |
| 10-22 | how-to-read-what-an-agent-loop-produced | 3 | ai agent loop output | How do I see what an agent loop produced? | L (`/output`, `/artifacts`) | R |

### Week 7 — batch 3 (website#1085, task-388aca82)

| Date | Slug | Pillar | Target query | Answer-engine question | Truth | St |
|---|---|---|---|---|---|---|
| 10-26 | what-to-do-when-an-ai-agent-api-key-leaks | 1 | ai agent api key leaked | What should you do when an AI agent's API key leaks? | K | R |
| 10-27 | predefined-or-custom-ai-agent-roles | 2 | custom ai agent roles | Should an AI agent use a predefined role or a custom role? | R | R |
| 10-28 | how-to-approve-or-reject-an-agent-proposal | 3 | approve ai agent action api | How do I approve or reject an agent's proposal in agent.ceo? | A | R |
| 10-29 | how-to-keep-a-record-of-decisions-made-with-ai-agents | 1 | ai agent decision log | How do you keep a record of decisions made with AI agents? | A, M (states the absence of an audit trail) | R |

### Week 8 — batch 3 (website#1085)

| Date | Slug | Pillar | Target query | Answer-engine question | Truth | St |
|---|---|---|---|---|---|---|
| 11-02 | ai-agent-governance-checklist | 1 | ai agent governance checklist | What should an AI agent governance checklist include? | R, G, K, A, L, S | R |
| 11-03 | when-is-an-ai-agent-task-actually-done | 2 | ai agent definition of done | When is an AI agent's task actually done? | I | R |
| 11-04 | what-does-byok-mean-for-an-ai-agent-platform | 3 | byok ai agent platform | What does BYOK mean for an AI agent platform? | P | R |
| 11-05 | what-is-bounded-autonomy-for-ai-agents | 2 | bounded autonomy ai agents | What is bounded autonomy for AI agents? | L, A, I | R |

**Totals (updated 2026-09-13, task-388aca82):** 36 entries, all publication-ready in merge-held PRs. That is
6 in marketing.blog#11, 10 in website#1080, 10 in website#1082 and 10 in website#1085. Weeks 2–8 carry 4–5
posts each. The next open week is 9 (11-09).

## The 13 surfaces — which get a how-to, and why the rest wait

Readiness run stg 2026-09-13 03:47Z, and whether stg serves a docs page under `/developers/docs/features/<name>`:

| Surface | Journey | stg docs page | How-to slot |
|---|---|---|---|
| Apps | PASS | none | W4 10-08 |
| Chat | FAIL (creator-delete 403) | none | **wait**: fullstack #3838 |
| Task Board | SKIPPED | none | **wait**: journey not run |
| Channels | SKIPPED | none | **wait**: journey not run |
| Approvals | PASS | proposals page (a different API; not used) | W2 09-24, W4 10-07 |
| Meetings | PASS (text only) | none | W3 09-30 |
| Super Agent | SKIPPED | served | **wait**: operand layer stopped by founder 2026-08-15 |
| Extensions | FAIL (platform-org fixture) | MCP page served | **wait**: devops customer-org fixture |
| Registry | PASS | served | W5 10-15 |
| API Keys | PASS | served | W2 09-23 |
| Loops | PASS | autonomous-loop page served | W3 10-02, W6 10-22 |
| Seeds | SKIPPED | none | **wait**: journey not run |
| Twin | PASS (operator path) | none | **wait**: operator-internal, not a customer surface yet |

**How a waiting surface moves:** when a readiness run turns it green on stg, add a how-to row in the
next open week, with the run's timestamp as its truth.

## What must never appear in a post (measured 2026-09-13)

- **A per-action or tamper-resistant audit trail.** stg `GET …/organizations/<ORG>/audit-log` is 404,
  the same as a fabricated route (task-ae3b31f9 finding).
- **A free tier.** `/pricing` offers none. The stg first-agent docs page still says "free tier (3
  agents, 168 agent-hours/month)". That is a docs defect, routed via the row note.
- **The 88% / 21% / 33% figures.** No publisher anywhere in our files.
- **Automatic handover of agents when a person leaves.** No served handover journey.
- **Audio/video meetings, or agents replying inside meetings.** Not covered by the Meetings journey.
- **A beta price.** The founder ruled there is none.
