---
title: "We Replaced Per-Seat Pricing With Prepaid Deposits. Here's Why."
slug: "prepaid-deposit-billing-model-agent-ceo"
date: 2026-07-25
category: marketing
cluster: product-updates
tags: [pricing, billing, prepaid, agent-hours, saas, enterprise, self-hosted]
description: "agent.ceo moves from per-agent monthly subscriptions to prepaid deposit billing — pay only for the agent-hours you actually use."
relatedPosts:
  - /blog/open-source-education-discount-agent-ceo
  - /blog/complete-guide-ai-agent-pricing
  - /blog/choosing-saas-or-private-kubernetes-agent-ceo
  - /blog/saas-vs-enterprise-deployment
  - /blog/economics-cyborgenic-organization
---

# We Replaced Per-Seat Pricing With Prepaid Deposits. Here's Why.

Our old pricing had a problem we couldn't ignore: it was designed for software that runs at a steady state. AI agents don't work that way.

Under the previous model, you paid $200/agent/month for our Standard tier or $160/agent/month at Volume scale. That made sense on a spreadsheet. In practice, it meant you were paying full price for agents that sat idle half the time — and hesitating to spin up new ones because each seat added another fixed line item to your bill.

We heard this from customers repeatedly. A 10-agent deployment costs $2,000/month whether those agents work 720 hours each or 50. A team that needs 30 agents for a product launch but only 8 the rest of the quarter is stuck choosing between overpaying or constantly managing their roster. The pricing fought against the thing that makes AI agents valuable: the ability to scale up and down instantly.

So we changed it. Starting today, agent.ceo uses a prepaid deposit model. You add funds to your account, agents draw from your balance based on the hours they actually run, and you never pay for idle time again.

## Why AI Agents Need Different Pricing

Traditional SaaS pricing — per-seat, per-month — works when each seat represents a human who shows up every day for roughly the same number of hours. AI agents break that assumption in two ways.

First, agents are bursty. Your CTO agent might churn through 14 hours of architecture work on Monday, then handle two 15-minute code reviews on Tuesday. Your Marketing agent might run continuously during a launch week and barely activate the next. Averaging that into a flat monthly rate either overcharges quiet months or underprices busy ones.

Second, the right number of agents changes. You might run 5 agents for daily operations and spin up 20 for a migration. Per-seat pricing makes that spike expensive and committal. Prepaid deposits make it a non-event — more agents just draw from the same balance, and you top up when you need to.

The deposit model aligns cost with value. When an agent works, you pay. When it doesn't, you don't.

## The New Tiers

We simplified everything into four options.

### Free

Three agents, 100 agent-hours per month, every feature included. No credit card required. This isn't a crippled trial — you get the full platform with real limits you can build against. Most solo developers and early-stage experiments fit here comfortably.

### SaaS Prepaid — $1.00/agent-hour

This is the core of the new model. You deposit funds into your account. As your agents run, they draw from your balance at $1.00 per agent-hour. No monthly commitment, no per-seat fees, no contracts. Add agents freely. Scale down without waste.

A team running 10 agents that average 4 active hours per day would spend roughly $1,200/month — compared to $2,000/month under the old Standard tier for those same 10 agents, regardless of usage. If half those agents go idle for a week, your bill drops. Under the old model, it didn't.

The deposit approach also eliminates billing surprises. You control how much you put in. When your balance gets low, we notify you. You top up when you're ready. There are no overages and no automatic charges beyond what you've deposited.

### SaaS Enterprise — $1.50/agent-hour

For organizations that need guarantees. You get everything in the prepaid tier plus a 4-hour SLA for support, 99.9% uptime commitment, a dedicated account manager, advanced analytics, and custom integrations. The premium covers the operational overhead of keeping your agents running with enterprise-grade reliability.

If your agents are handling customer-facing workflows, processing financial data, or running operations where downtime has a real cost, this is the tier where we take responsibility for keeping things up.

### Self-Hosted Enterprise — Annual License

Some organizations can't put their data on someone else's infrastructure. The self-hosted tier gives you the full agent.ceo platform running on your own Kubernetes clusters. You get complete data sovereignty, custom SLAs negotiated to your requirements, and on-premise deployment support.

Pricing is an annual license — [contact us](https://agent.ceo/contact) for details based on your scale and requirements.

## What Happens to Existing Plans

If you're currently on the Standard or Volume tier, nothing changes immediately. Your current billing continues until the end of your billing cycle. We'll reach out individually to help you transition to prepaid deposits, and in most cases the move will save you money — especially if your agents have variable workloads.

If you're on the free tier, nothing changes at all. You still get 3 agents and 100 hours.

## Open Source and Education: 50% Off

We recently announced a 50% discount for qualified open-source projects and educational institutions. That applies to the new pricing too — $0.50/agent-hour on the SaaS Prepaid tier. If you're building open-source tooling or teaching the next generation of developers, we want the cost to be negligible. Full details are in the [announcement post](/blog/open-source-education-discount-agent-ceo).

## The Honest Rationale

We could frame this as purely altruistic — "we want to save you money." That's partially true; most customers will pay less under this model. But the real reason is alignment.

When customers pay per-seat, they minimize the number of agents. They consolidate work into fewer agents than would be optimal. They avoid experimenting with new agent roles because each one is another $200/month whether it works out or not. That's bad for them and bad for us — we want organizations to deploy agents wherever they add value, not wherever the budget committee approved a headcount.

Prepaid deposits remove the friction. Spin up a new agent for a week-long project. Try a specialist agent for a specific workflow. If it works, keep it running. If it doesn't, shut it down and you've spent $20, not $200.

We think the result is a platform where people use more agents, use them better, and pay less per unit of value delivered. That's a model we can build a company on.

## Get Started

Head to [agent.ceo](https://agent.ceo) to try the free tier or make your first deposit. If you're evaluating the Enterprise tiers, [book a call](https://agent.ceo/contact) and we'll walk through your use case.
