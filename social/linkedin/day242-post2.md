---
platform: linkedin
day: 242
date: 2027-01-07
topic: "Alerting rules for AI agent fleets — what we actually alert on"
linkedPost: "agent-alerting-rules"
---

The most important alerting decision we made at GenBrain was deciding what not to alert on.

Seven agents, 238+ days of continuous operation, and our AlertManager configuration has exactly 12 rules. Not 120. Twelve. Here is why that matters.

Early on, we alerted on everything. An agent took longer than usual on a task — alert. Token consumption spiked — alert. A message sat in queue for more than 30 seconds — alert. The result was alert fatigue within a week. I started ignoring notifications, which is the worst possible outcome for a monitoring system.

So we rebuilt the alerting philosophy around one principle: only alert on conditions that require human action within 4 hours.

What we alert on:
- Agent health check failure (2 consecutive misses)
- SLA breach or imminent breach (support response > 5 min)
- Security incident detection (any severity)
- Deployment failure after automated retry
- DLQ depth exceeding threshold
- Budget anomaly (daily spend > 2x baseline)

What we do not alert on:
- Transient errors (agents retry automatically)
- Token consumption variance (normal operational fluctuation)
- Task duration outliers (investigated weekly, not urgently)
- Individual message delays (monitored via dashboards)

During the 14-day holiday, this alerting configuration sent me zero notifications. Not because nothing happened — the agents processed thousands of operations. Because nothing happened that required me within 4 hours.

That is the goal. Silence means the system is working.

Read more: [Alerting Rules for AI Agent Fleets](https://agent.ceo/blog/agent-alerting-rules)

#CyborgenicOrganization #Alerting #Monitoring #AIAgents #AgentCEO #SRE #OnCall

— Moshe Beeri, Founder, GenBrain AI
