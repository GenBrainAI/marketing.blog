---
platform: twitter
status: draft
date: 2026-10-23
note: "Your Agents Are Running Last Month's Instructions"
---

## Thread: Your Agents Are Running Last Month's Instructions

Every customer org agent in our fleet gets a CLAUDE.md mounted as a Kubernetes ConfigMap. It defines their behavior -- security rules, validation gates, communication protocols.

There's a problem: updates don't propagate.

---

When we update the shared behavior template, only NEW orgs get the new version. It's baked into the ConfigMap at provisioning time.

Existing orgs? They keep running whatever version they were provisioned with. Could be last week's. Could be last month's.

---

Critical security fix in the behavior template? New validation gate for task completion? Updated communication protocol?

Silently missing from every agent provisioned before the update. The longer the platform runs, the worse the drift gets. More orgs = more stale configs.

---

This is config drift, and it's invisible. The agents don't error. They don't warn. They just follow their outdated instructions perfectly.

Tomorrow: how we built a reconciler to fix it automatically.

---

Read more: https://agent.ceo/blog/zero-touch-customer-onboarding-platform-knowledge

#ConfigDrift #Kubernetes #AgentOps #AgentCEO
