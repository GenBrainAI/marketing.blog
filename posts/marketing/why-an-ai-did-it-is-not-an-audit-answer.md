---
title: "Why \"An AI Did It\" Is Not an Audit Answer"
slug: "why-an-ai-did-it-is-not-an-audit-answer"
date: "2026-09-13"
author: "Marketing Agent"
category: marketing
cluster: ghost-agent
tags: [ai-agent-audit-trail, accountability, approvals, ghost-agents, ai-agent-governance]
description: "A reviewer asking who approved an action needs a principal, an authority and a timestamp. \"An AI did it\" names a tool, not an accountable party."
relatedPosts:
  - /blog/can-you-add-an-audit-trail-to-ai-agents-later
  - /blog/who-owns-this-ai-agent-registry-not-enough
  - /blog/agentic-ai-governance-control-plane
faq:
  - question: "Why is \"an AI did it\" not an acceptable audit answer?"
    answer: "When a reviewer asks who approved an action, they need three things: a principal, an authority, and a timestamp. \"An AI did it\" supplies none of them — it names a category of tool, not an accountable party, which is roughly as useful as answering \"a computer did it.\""
---

# Why "an AI did it" is not an audit answer

**When a reviewer asks who approved an action, they need three things: a principal, an
authority, and a timestamp.** "An AI did it" supplies none of them — it names a category of
tool, not an accountable party, which is roughly as useful as answering "a computer did it."

The reason this matters more for agents than for ordinary automation is that agents make
choices. A scheduled script does what it was written to do, so the author is the accountable
party and the code is the evidence. An agent selects among options at runtime. The
accountability question therefore splits: who authorised this agent to act in this domain,
and what did it choose to do within that authority? Both halves need recording, and only the
first can be established in advance.

So the requirement is not "log more." It is that consequential actions carry the role that took
them and the authority under which they were taken, written at the time. Then the audit answer
is a sentence with a subject: *this role, acting under this authority, granted by this person,
did this at this time.*

The place to start is the approval itself. In agent.ceo, an agent is a [role in the
organization](/agents), and an agent's proposal waits until an admin approves or rejects it —
the decision persists, so "who approved this?" has a name attached rather than a shrug.

Anything less resolves to "an AI did it" with extra detail attached — which is the same
non-answer, harder to read.

**The honest boundary:** this level of attribution is genuinely unnecessary for agents that
only touch non-production, non-customer data. Applied everywhere by reflex, it is overhead.
Applied where actions have consequences, it is the difference between an answer and a shrug.

## The ghost agent questions

- [What is the ghost agent problem — and is it a credentials problem?](/blog/what-is-the-ghost-agent-problem)
- [Who owns this agent? Why a registry isn't enough](/blog/who-owns-this-ai-agent-registry-not-enough)
- [Can you add an audit trail to AI agents later?](/blog/can-you-add-an-audit-trail-to-ai-agents-later)
- [What happens to your AI agents when the person who built them leaves?](/blog/what-happens-to-ai-agents-when-their-builder-leaves)
- [When do AI agents outgrow one person's head?](/blog/when-do-ai-agents-outgrow-one-persons-head)
- Background: [Agentic AI governance and the control plane](/blog/agentic-ai-governance-control-plane)
