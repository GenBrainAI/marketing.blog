# Your company is already a graph

<!--
STATUS: FOUNDER-EDITABLE DRAFT — NOT PUBLISHED. Marketing publishes only after the founder's go.
Source: agent-hub docs/marketing/graph-story-draft-2026-09-11.md (edited draft). Row: task-ae3b31f9.
Edit anything between the two rules below. Everything under "Not for publication" is for you and the CEO.
-->

Article 1 of 3 in the graph engineering series.

---

*The junctions were always decisions. For a hundred years they were people. Now each one can be an
agent — and you get to choose which kind.*

**Summary.** Every organization already runs on a graph: steps, hand-offs, and at every junction a
decision. Nobody draws it any more, but it is written down in the process manuals and the ISO
binders, and in the way a purchase order moves from a request to an approval to a payment. The
decisions are the interesting part. For a hundred years those junctions were people; then some
became rules in software; now each one can be an agent — a human, a super agent, an A2A agent, or a
human in the loop who chooses, junction by junction, whether to act as a function or as a judge.
Everything else in the graph is a function, a loop, or data flowing on an edge.

---

Open a process manual — any one. A purchase order arrives. Someone checks it against a budget. If
it clears it goes to a second approver; if it does not it goes back. Legal sees the ones over a
threshold. Finance pays. Draw that and you have a graph: nodes joined by edges, data moving along
the edges, and a decision at every junction. The ISO-style process standards large organizations
already live by are graphs written as prose — the same structure a diagram would show, at greater
length and lower fidelity. Nobody draws the diagram, because a diagram does not run. It is stale
the week after the offsite, and the real process lives on in habit and email.

The decisions are what the graph is for. At each junction someone asks: is this within budget, is
this customer real, does this contract need legal, is this release safe to ship. Everything between
the junctions is mechanical — fetch the record, format the document, send the mail. For a hundred
years the junctions were people, because only a person could weigh the case the rulebook did not
quite cover. Then some became rules in software, and the ones that fit a rule stopped being
decisions at all. What is new is the third option: a junction can be an agent.

An agent at a junction can be one of four things.

- A **human**, deciding as they always have.
- A **super agent** — an AI that owns the whole junction and its context, with its own tools, its
  own memory and its own permissions.
- An **A2A agent** — an AI reached over an open protocol, possibly belonging to another
  organization. Your supplier's credit check, called as a node in your graph.
- A **human in the loop** — where the person chooses, junction by junction, whether they are a
  function (apply the rule) or a judge (decide).

The fourth is the one people underestimate. "Human in the loop" is usually sold as a safety brake:
the AI proposes, a person signs. The more useful reading is a question the person answers about
themselves — *am I adding judgement here, or am I a rule that happens to be wearing a person?* Most
approval steps in most companies are the second. Naming which is which is the first honest thing a
graph does to an organization.

Nothing else changes when a junction becomes an agent. The steps stay steps. The data keeps flowing
on the edges. Loops stay loops — a step that repeats until a condition holds. You are not replacing
the process; you are changing what sits at its junctions, one junction at a time, and you can put a
human back at any of them.

<!-- FOUNDER CHOICE A (optional, present tense, every clause is served on stg today — see truths below):
Some of this already runs. In agent.ceo today an agent is a role your organization holds, a
proposal can wait at a junction until a person approves or rejects it, and a loop runs until it is
told to stop.
-->

That is what we are building agent.ceo toward: draw your graph, put an agent of the right kind at
each junction, store it as a versioned artifact, run it, watch it run, and hand it to another team
— or another company — whole, with every decision in it reachable on its own, so a process can
start from any step and not only from the top. We are building it inside our own company, on our
own processes, and our agents are doing the building. A graph you have not run is a diagram, and we
have enough of those.

The next article is the method: how an organization critiques its own plans, with agents, before it
builds. The third is the measurement — what changed when we ran our own company on it.

---

## Not for publication — the three product truths this article may claim

Each is something the **served staging product does today**, with the evidence a non-author can
re-read. The article body as written claims none of them in the present tense; optional
sentence A above claims all three and nothing more.

| # | Truth (the most the article may say) | Evidence on stg, re-runnable |
|---|---|---|
| T1 | **A human decision can sit at a junction and is recorded.** An agent's proposal waits in an approvals queue; an admin approves or rejects it and the decision persists. | Readiness run on stg, 2026-09-13 03:47Z: **Approvals PASS** (journey: admin sees a pending proposal, rejects it, sees the persisted decision). agent-hub `docs/org/plan.md`, row "Readiness runs on stg". |
| T2 | **An agent is a role the organization holds, not a person's account.** | `curl -s https://stg.agent.ceo/agents` → 200, "16 predefined roles ready to deploy … or create custom roles" (measured 2026-09-13 ~19:30Z). Same run: **Registry PASS** (org's registered agents listed, a known agent's role read). |
| T3 | **A loop runs until it is stopped, and a super-agent node can be a participant.** | Same run: **Loops PASS** — bounded create/run/view/stop, "with the founder's node bound as participant". |

**What the article must NOT claim in the present tense** (design only, or not green on stg):
drawing a graph, storing it as a versioned artifact, handing a graph to another company, starting a
process from any step (graph engineering design, Phases B/C not started); an A2A agent from another
organization at a junction (stg's public `/.well-known/agent.json` currently returns 8 agents with
**empty `id` and `name`** — a defect, routed via the row note); anything about the task board
(SKIPPED) or chat (FAIL) on the same run.

**Tense.** Kept as "what we are building agent.ceo toward", per the 09-11 editorial note. Your call;
optional sentence A is the honest way to add present tense without overclaiming.

**Channel.** Blog canonical first, your LinkedIn the same day (see `founder-channel-plan.md`). Not
the newsletter. The blog leg is a hand-port to agent-ceo-website: the marketing.blog converter is
dormant (B4, re-verified 2026-09-13).

**Length.** Body unchanged from the 09-11 edit: 591 words, excluding title, deck, summary and the
optional sentence.
