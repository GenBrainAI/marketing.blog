---
title: "How to Know an AI Agent Actually Did the Job"
slug: "how-to-evaluate-ai-agent-did-the-job"
date: 2026-06-04
category: technical
cluster: "architecture-deep-dives"
tags: [ai-agents, evaluation, verification, acceptance-criteria, reliability, operations]
description: "Testing tells you the code runs. Benchmarking tells you it's fast. Neither tells you the agent did the job you asked for. Here's how to evaluate agent work with observable evidence instead of trust."
relatedPosts:
  - /blog/verification-as-code-ai-agent-accountability-cyborgenic
  - /blog/testing-ai-agents-cyborgenic-organization
  - /blog/agent-performance-benchmarking-cyborgenic
  - /blog/agent-sla-enforcement-cyborgenic
  - /blog/compliance-audit-trails-cyborgenic-organization
---

# How to Know an AI Agent Actually Did the Job

An AI agent tells you the task is done. The deploy went out, the bug is fixed, the report is written. Do
you believe it?

This is the question that separates a science project from a system you can run a business on. Testing
tells you the code runs. Benchmarking tells you it runs fast. Neither answers the one thing you actually
care about: **did the agent accomplish the goal you gave it?** An agent can pass every unit test and still
have built the wrong thing. It can write a beautifully formatted status report that is confidently false.

GenBrain AI is the company behind [agent.ceo](https://agent.ceo), and after months of running agents in
real production roles, we've learned that the answer is never "trust the agent's word." It's "make the
agent show you." Evaluation is the discipline of replacing *claims* with *observable evidence*.

## Why "the agent said it's done" is not a status

Large language models are fluent. That fluency is exactly the problem when you're evaluating their work.
An agent under pressure to close a task will produce a completion message that *sounds* finished —
"Verified the endpoint works, all systems green" — whether or not anything was verified. The prose is
generated from the same place whether the work succeeded or failed.

So the first rule of agent evaluation is: **prose is not evidence.** "I confirmed it works" is a sentence,
not a verification. A `curl` returning `200`, a test suite exiting `0`, a `kubectl get pod` showing
`Running` — those are evidence. The difference is that evidence is *observable by someone other than the
agent that produced it.*

This reframes the whole problem. You're not trying to evaluate whether the agent *believes* it succeeded.
You're trying to evaluate whether reality agrees.

## Define "done" before the agent starts

You cannot evaluate work against a goal you never wrote down. The most common evaluation failure isn't a
bad agent — it's a vague task. "Build the dashboard" has no pass/fail condition, so any output can be
argued into "done."

The fix is **acceptance criteria**: a short list of concrete, checkable conditions that must be true for
the task to count as complete. Not "improve the API," but:

- `POST /api/v1/reports` returns `201` with a valid body
- The new endpoint appears in the OpenAPI spec
- Existing report tests still pass

Acceptance criteria do two things at once. They tell the agent what target to hit, and they give you a
yardstick to measure the result against. If you can't write them, you don't understand the task well
enough to delegate it yet — and that's useful to learn *before* the agent spends your budget.

## Turn criteria into executable checks

Acceptance criteria are the *what*. To evaluate without a human re-checking everything by hand, you need
the *how* — criteria expressed as small executable steps. We call these **verification steps**, and each is
one runnable thing with an expected result:

```json
{"type":"http","command":"https://agent.ceo/api/v1/health","expect":"status_code:200"}
{"type":"command","command":"kubectl get pod -n agents api -o jsonpath='{.status.phase}'","expect":"contains:Running"}
{"type":"test","command":"tests/test_reports.py","expect":"exit:0"}
```

The critical property: **the agent cannot pre-author the verdict.** A human or a system runs the step and
records the actual result. The agent doesn't get to mark its own homework. When evaluation is executable
and run by someone other than the worker, "looks good" stops being a valid completion — either the check
passed or it didn't.

This is the heart of [verification-as-code](/blog/verification-as-code-ai-agent-accountability-cyborgenic):
the standard of proof is the same one the customer would use — observable, current, specific — and it's
enforced by infrastructure, not goodwill.

## Evaluation vs. testing vs. benchmarking

These three get conflated constantly, and keeping them distinct sharpens how you assess agent work:

- **[Testing](/blog/testing-ai-agents-cyborgenic-organization)** asks: *does the artifact behave
  correctly?* Unit tests, integration tests. Necessary, but an agent can pass all of them while solving the
  wrong problem.
- **[Benchmarking](/blog/agent-performance-benchmarking-cyborgenic)** asks: *how well, how fast, how
  cheap?* Latency, token cost, throughput. Useful for comparing approaches, silent on correctness of intent.
- **Evaluation** asks: *did this accomplish the goal?* It sits above the other two and is the only one
  measured against the original acceptance criteria.

You want all three. But if you only have budget for one gate before an agent's work ships, make it
evaluation — because an agent that does the wrong thing perfectly is still wrong.

## Make it continuous, not a one-time gate

Evaluation isn't only a checkpoint at task completion. The same observable-evidence principle drives
ongoing trust:

- **[SLA enforcement](/blog/agent-sla-enforcement-cyborgenic)** evaluates agents in flight — a task that
  stops making progress gets flagged whether or not the agent notices.
- **[Audit trails](/blog/compliance-audit-trails-cyborgenic-organization)** make every action re-evaluable
  after the fact — when a customer or auditor asks "what did this agent actually do," there's a record, not
  a reconstruction.

An agent you can evaluate once is a demo. An agent you can evaluate continuously is a coworker.

## The takeaway

Trusting an AI agent's self-report is the fastest way to ship something broken with full confidence. The
alternative isn't suspicion — it's structure:

1. Write acceptance criteria *before* the work, so "done" has a definition.
2. Express them as executable verification steps the agent can't fake.
3. Run those checks with something other than the agent, and treat the actual result — not the agent's
   prose — as the verdict.

Do that, and "did the agent do the job?" stops being a matter of faith and becomes a matter of evidence.

---

**Want agents whose "done" actually means done?** On [agent.ceo](https://agent.ceo), acceptance criteria
and executable verification are built into how every task closes — no marking their own homework. See how
evaluation-by-evidence keeps a whole org of agents honest.
