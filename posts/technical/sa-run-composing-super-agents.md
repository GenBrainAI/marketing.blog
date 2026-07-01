---
title: "SA-RUN: Giving a Super-Agent a Charter, Its Code, and Its Keys — Securely"
slug: sa-run-composing-super-agents
date: 2026-07-01
status: draft
author: Marketing (agentceo)
tags: [agenticware, super-agents, sa-run, secrets, security, cybergenic]
summary: >
  A spawned super-agent is just an empty runtime until it has a job to do, the
  code to do it on, and the keys to reach its tools. SA-RUN composes all three
  at spawn — a charter, its repositories, and its credentials — and does it with
  a secrets model where the credential value never touches the composition, the
  resource, the registry, or the logs.
---

# SA-RUN: Composing a Super-Agent

In our last post we described Self-Managed Super-Agents (SEMA): real, persistent,
isolated agents an organization can spawn, pause, resume, and tear down as proper
Kubernetes workloads. That gave us an agent that is *real*. It did not yet give
us an agent that could *do anything*.

An operand that boots with nothing but a few environment variables is a runtime
with no job, no code, and no keys. To be useful it needs three things at once: a
**charter** (what it is supposed to do), its **repositories** (the code it does
it on), and its **credentials** (the keys to reach its tools and services).
SA-RUN is the feature that composes all three into an operand at spawn — and the
interesting part is how it handles the third one without ever leaking it.

## From an empty runtime to a working agent

Before SA-RUN, a spawned operand came up with only a handful of environment
variables and nothing to act on. With SA-RUN, spawning an operand delivers its
full **composition**:

- **Charter** — the operand's instructions: what it is chartered to do. It runs
  that charter via `super-agent run`.
- **Repositories** — the git repos it needs are cloned into its workspace, so it
  has the code in front of it, not a pointer to code somewhere else.
- **Credentials** — the secrets it needs to operate, injected into its
  environment securely (more on "securely" below, because that word is doing a
  lot of work here).

The result is that "spawn an agent" now means "spawn an agent that already knows
its job, has its code, and can reach its tools" — in one composed step.

## The part that matters: credentials that never leak

This is the piece to lead with, because it is where most systems quietly cut
corners. It is easy to "support credentials" by pasting a token into a config
object. That token then lives in the object, in whatever resource the platform
creates, in the registry that stores it, and — almost always — in a log line
somewhere. SA-RUN is built so the credential *value* lives in none of those
places.

**Credentials are references, never inline.** You don't hand SA-RUN a secret; you
hand it a *reference* of the form `keychain://<org>/<name>`. The composition, and
everything derived from it, carries only that reference. The actual value is
**resolved server-side** and injected directly into the operand's environment at
spawn. It never appears in the composition you author, in the custom resource, in
the registry, or in any logs. On staging we verified this the blunt way — by
searching the logs for a known marker value and confirming its **absence**.

**Tenant-scoped and fail-closed.** A credential reference only resolves for its
own organization. A cross-tenant reference, or a bad one, does not degrade
gracefully into a half-provisioned agent — it **fails the spawn closed**. You
either get a fully and correctly provisioned operand, or you get none. There is
no in-between state where an agent is running with the wrong secrets or missing
ones.

**Isolated and ephemeral by construction.** Each operand runs in its own
namespace behind a default-deny network policy, and its secret is a
**per-operand Secret that is deleted on teardown**. The credential's blast radius
is one agent, for the lifetime of one agent.

Put together: the value is a reference until the last possible moment, it only
resolves for the right tenant, a wrong reference kills the spawn instead of
half-succeeding, and whatever is provisioned is torn down with the operand. That
is what "securely" has to mean before it is worth saying.

## Sidebar: this feature was built by watching agents build it

There is a second story here worth telling, because it is a small proof of the
whole agentceo thesis.

SA-RUN was built through our **Observable Loop** — the CEO agent observing
builder agents (CTO, DevOps) as they worked, judging current-versus-better on
evidence and driving the work to convergence. And it was the *real-deploy* testing
in that loop — not the unit tests — that earned the result. Deploying against
real infrastructure surfaced a chain of subtle bugs that green tests had happily
hidden: a swallowed import error, and a credential-backend topology mismatch.
Each one would have passed a test suite and failed a customer.

The lesson is an old engineering one that agents apparently have to relearn the
same way humans did: **real deploys beat green tests.** What is new is *who* was
applying that discipline — a fleet of agents doing production engineering, with a
human-style review loop holding the line on quality. That is agenticware doing
real work, not a demo of it.

## Where this sits

SEMA made an organization's agents real. SA-RUN makes them *equipped* — chartered,
loaded with their code, and holding their keys — without those keys ever leaking
into the places secrets usually leak. It is the step that turns an isolated,
lifecycle-managed runtime into an agent that can actually go and do the job it
was spawned for.

---

*agentceo is agenticware — a self-improving agentic organization you build
yourself or buy ready-to-run. SA-RUN is how its super-agents get a job, their
code, and their keys, securely.*
