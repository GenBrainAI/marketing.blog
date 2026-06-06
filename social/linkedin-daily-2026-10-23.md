---
platform: linkedin
status: draft
date: 2026-10-23
note: "Your Agents Are Running Last Month's Instructions"
---

## Post: Your Agents Are Running Last Month's Instructions

Every customer org agent in our fleet gets a CLAUDE.md file mounted as a Kubernetes ConfigMap. This file defines the agent's behavior: security rules, validation gates, communication protocols, task lifecycle requirements.

When we update the shared behavior template, only newly provisioned orgs get the update. Existing orgs keep running whatever version was baked into their ConfigMap at provisioning time.

This means critical behavior fixes -- security rules, completion validation, escalation protocols -- are silently missing from production agents that were provisioned before the update. The agents don't error out. They don't warn. They follow their outdated instructions perfectly. From the outside, everything looks healthy.

The longer the platform runs, the worse the drift becomes. Every new org starts with the latest template. Every existing org falls further behind. After a few months of active development, you can have agents in production running behavior definitions that are dozens of revisions old.

This is the config drift problem, and it's particularly dangerous for AI agents because the behavioral impact is subtle. A missing validation gate doesn't cause a crash -- it causes the agent to skip a step that was added for a reason. A stale communication protocol doesn't throw an error -- it just means the agent isn't following the latest coordination patterns.

Tomorrow: how we solved it with a three-phase reconciler.

Read more: https://agent.ceo/blog/zero-touch-customer-onboarding-platform-knowledge

#ConfigDrift #Kubernetes #AgentOps #AgentCEO
