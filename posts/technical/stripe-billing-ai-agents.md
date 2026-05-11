---
title: "Stripe Billing for AI Agent Services"
slug: "stripe-billing-ai-agents"
date: 2026-05-10
category: technical
cluster: "platform-engineering"
tags: [stripe, billing, metered-billing, saas, pricing, ai-agents, subscriptions]
description: "Implement Stripe metered billing for AI agent platforms with pay-as-you-go pricing, usage tracking, and subscription management."
relatedPosts: [saas-platform-ai-agents, cost-optimization-ai-agents, real-time-agent-monitoring]
---

# Stripe Billing for AI Agent Services

Billing for AI agent services presents unique challenges compared to traditional SaaS. Agents consume variable compute resources over unpredictable timeframes — a coding agent might run for 8 hours straight, while a monitoring agent ticks for 30 seconds every 5 minutes. As more organizations adopt the [Cyborgenic Organization](/blog/cyborgenic-organizations) model -- where AI agents work as autonomous peers alongside humans -- billing must accurately reflect the value agents deliver rather than forcing traditional per-seat pricing. At agent.ceo, we built a flexible billing system using Stripe that supports both subscription-based and pay-as-you-go pricing models. This post covers our implementation end-to-end.

## Pricing Model Design

We offer three billing approaches, each suited to different usage patterns:

| Model | Price | Best For |
|-------|-------|----------|
| Pay-as-you-go | $1/agent-hour | Experimentation, burst workloads |
| Standard subscription | $200/agent/month | Steady-state teams |
| Volume subscription | $160/agent/month | Large fleets (10+ agents) |

The key insight is that agent-hours are the natural billing unit. Unlike API calls (which are too granular) or monthly seats (which penalize occasional users), agent-hours map directly to value delivered — an agent running for an hour has done roughly an hour of productive work.

## Stripe Product and Price Configuration

We configure Stripe products and prices programmatically during platform setup:

```typescript
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

// Create the base product
const product = await stripe.products.create({
  name: 'AI Agent Compute',
  description: 'Autonomous AI agent runtime on agent.ceo',
  metadata: {
    platform: 'agent-ceo',
    version: '2'
  }
});

// Pay-as-you-go metered price
const meteredPrice = await stripe.prices.create({
  product: product.id,
  currency: 'usd',
  recurring: {
    interval: 'month',
    usage_type: 'metered'
  },
  billing_scheme: 'per_unit',
  unit_amount: 100,  // $1.00 per agent-hour
  metadata: { plan: 'payg' }
});

// Standard subscription price
const standardPrice = await stripe.prices.create({
  product: product.id,
  currency: 'usd',
  recurring: {
    interval: 'month',
    usage_type: 'licensed'
  },
  unit_amount: 20000,  // $200.00 per agent per month
  metadata: { plan: 'standard' }
});

// Volume subscription price with tiered pricing
const volumePrice = await stripe.prices.create({
  product: product.id,
  currency: 'usd',
  recurring: {
    interval: 'month',
    usage_type: 'licensed'
  },
  billing_scheme: 'tiered',
  tiers_mode: 'graduated',
  tiers: [
    { up_to: 10, unit_amount: 20000 },   // First 10: $200 each
    { up_to: 50, unit_amount: 16000 },   // 11-50: $160 each
    { up_to: 'inf', unit_amount: 12000 } // 51+: $120 each
  ],
  metadata: { plan: 'volume' }
});
```

## Usage Metering Pipeline

The metering pipeline tracks agent runtime down to the second, then reports to Stripe in hourly increments. This runs as a platform service alongside the [agent monitoring stack](/blog/real-time-agent-monitoring).

```typescript
import { getFirestore, FieldValue } from 'firebase-admin/firestore';

const db = getFirestore();

interface UsageRecord {
  orgId: string;
  agentId: string;
  startTime: number;
  endTime: number;
  computeSeconds: number;
}

class BillingMeterService {
  private stripe: Stripe;

  constructor() {
    this.stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
  }

  /**
   * Called every minute by the metering cron job.
   * Aggregates active agent time and reports to Stripe.
   */
  async reportUsage(): Promise<void> {
    const orgs = await db.collection('organizations')
      .where('plan', '==', 'payg')
      .get();

    for (const org of orgs.docs) {
      const orgData = org.data();
      const activeAgents = await db
        .collection(`organizations/${org.id}/agents`)
        .where('status', '==', 'running')
        .get();

      if (activeAgents.empty) continue;

      // Calculate total agent-seconds since last report
      const now = Date.now();
      let totalSeconds = 0;

      for (const agent of activeAgents.docs) {
        const agentData = agent.data();
        const lastReported = agentData.lastBillingReport?.toMillis() || agentData.startedAt.toMillis();
        totalSeconds += Math.floor((now - lastReported) / 1000);

        // Update last reported timestamp
        await agent.ref.update({
          lastBillingReport: FieldValue.serverTimestamp()
        });
      }

      // Convert to agent-hours (Stripe unit) — round up to nearest minute
      const agentMinutes = Math.ceil(totalSeconds / 60);
      const agentHours = agentMinutes / 60;

      if (agentHours > 0) {
        // Report to Stripe
        await this.stripe.subscriptionItems.createUsageRecord(
          orgData.stripeSubscriptionItemId,
          {
            quantity: Math.ceil(agentHours * 100), // Report in centihours for precision
            timestamp: Math.floor(now / 1000),
            action: 'increment'
          }
        );

        // Store usage record for internal analytics
        await db.collection(`organizations/${org.id}/usage`).add({
          reportedAt: FieldValue.serverTimestamp(),
          agentCount: activeAgents.size,
          totalSeconds,
          agentHours: Math.round(agentHours * 1000) / 1000,
          stripeReported: true
        });
      }
    }
  }

  /**
   * Handle agent state transitions for billing accuracy
   */
  async onAgentStateChange(orgId: string, agentId: string, newState: string): Promise<void> {
    const agentRef = db.doc(`organizations/${orgId}/agents/${agentId}`);
    const agent = await agentRef.get();
    const agentData = agent.data();

    if (newState === 'paused' || newState === 'terminated') {
      // Final usage report for this session
      const lastActive = agentData.lastBillingReport?.toMillis() || agentData.startedAt.toMillis();
      const sessionSeconds = Math.floor((Date.now() - lastActive) / 1000);

      if (sessionSeconds > 0) {
        const org = await db.doc(`organizations/${orgId}`).get();
        await this.stripe.subscriptionItems.createUsageRecord(
          org.data().stripeSubscriptionItemId,
          {
            quantity: Math.ceil((sessionSeconds / 3600) * 100),
            timestamp: Math.floor(Date.now() / 1000),
            action: 'increment'
          }
        );
      }
    }

    await agentRef.update({
      status: newState,
      [`stateHistory.${Date.now()}`]: newState
    });
  }
}
```

## Customer Portal and Invoice Customization

We integrate Stripe's customer portal to let organizations manage their billing, while customizing invoices with agent-level detail:

```typescript
// Create customer portal session
async function createPortalSession(orgId: string): Promise<string> {
  const org = await db.doc(`organizations/${orgId}`).get();

  const session = await stripe.billingPortal.sessions.create({
    customer: org.data().billingCustomerId,
    return_url: `https://app.agent.ceo/org/${orgId}/settings/billing`
  });

  return session.url;
}

// Webhook handler for invoice customization
async function handleInvoiceCreated(invoice: Stripe.Invoice): Promise<void> {
  const orgId = invoice.metadata?.orgId;
  if (!orgId) return;

  // Fetch agent-level usage breakdown
  const usageRecords = await db
    .collection(`organizations/${orgId}/usage`)
    .where('reportedAt', '>=', new Date(invoice.period_start * 1000))
    .where('reportedAt', '<=', new Date(invoice.period_end * 1000))
    .get();

  // Add detailed line items per agent
  const agentUsage = aggregateByAgent(usageRecords);

  for (const [agentName, hours] of Object.entries(agentUsage)) {
    await stripe.invoiceItems.create({
      customer: invoice.customer as string,
      invoice: invoice.id,
      description: `Agent: ${agentName} — ${hours.toFixed(1)} hours`,
      amount: 0,  // Informational only, actual charge is on metered line
      currency: 'usd'
    });
  }
}
```

## Webhook Processing

Stripe webhooks drive billing state changes across the platform. We process these through a dedicated service with idempotency guarantees:

```typescript
// Stripe webhook handler
app.post('/webhooks/stripe', async (req, res) => {
  const sig = req.headers['stripe-signature'];
  const event = stripe.webhooks.constructEvent(
    req.body, sig, process.env.STRIPE_WEBHOOK_SECRET
  );

  // Idempotency check
  const processed = await db.doc(`stripe_events/${event.id}`).get();
  if (processed.exists) {
    return res.json({ received: true, duplicate: true });
  }

  switch (event.type) {
    case 'customer.subscription.deleted':
      // Terminate all agents for this org
      await terminateOrgAgents(event.data.object.metadata.orgId);
      break;

    case 'invoice.payment_failed':
      // Pause non-critical agents, notify org admins
      await pauseNonCriticalAgents(event.data.object.metadata.orgId);
      await notifyPaymentFailure(event.data.object);
      break;

    case 'customer.subscription.updated':
      // Handle plan changes — adjust agent limits
      await syncOrgLimits(event.data.object);
      break;
  }

  // Mark event as processed
  await db.doc(`stripe_events/${event.id}`).set({
    type: event.type,
    processedAt: FieldValue.serverTimestamp()
  });

  res.json({ received: true });
});
```

## Usage Dashboard Integration

We expose real-time usage data through the platform dashboard so customers can track costs before their invoice arrives. This data feeds from the same metering pipeline that reports to Stripe, ensuring consistency. Our [cost optimization guide](/blog/cost-optimization-ai-agents) explains how customers can use these dashboards to reduce their monthly spend.

## Handling Edge Cases

Several billing edge cases required careful handling:

**Spot instance preemption**: When a GKE spot node is reclaimed, the agent pod is evicted. We must report final usage before the pod terminates. A preStop hook triggers the billing flush, and a reconciliation job catches any missed reports.

**Clock skew**: Agent pods and the billing service may have slightly different clocks. We use server-side Firestore timestamps as the source of truth, not pod-local time.

**Free tier abuse**: The free trial (1 agent-week) is tracked at the organization level. We prevent users from creating multiple organizations to chain free trials by linking to their verified email domain.

For teams building their own [multi-tenant agent platforms](/blog/multi-tenant-agent-orchestration), getting billing right from the start avoids painful migrations later. The key principle is: meter at the lowest granularity possible, then aggregate for billing. You can always reduce precision in reporting, but you cannot retroactively add precision to metering.

Understanding your [agent architecture patterns](/blog/multi-agent-architecture-patterns) also informs billing design — hierarchical agent teams where a manager agent delegates to workers need careful attribution of costs to the correct organizational unit.

> agent.ceo offers both SaaS and enterprise private installation options for organizations of any size.

## Try agent.ceo

**SaaS** — Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).

**Enterprise** — For private installation on your own infrastructure, contact [enterprise@agent.ceo](mailto:enterprise@agent.ceo).

---
*agent.ceo is built by [GenBrain AI](https://genbrain.ai) — a GenAI-first autonomous agent orchestration platform. General inquiries: hello@agent.ceo | Security: security@agent.ceo*
