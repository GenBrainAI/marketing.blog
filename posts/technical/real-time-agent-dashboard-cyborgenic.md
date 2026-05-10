---
title: "Building a Real-Time Agent Dashboard: Monitoring Your Cyborgenic Organization"
slug: "real-time-agent-dashboard-cyborgenic"
date: 2026-07-30
category: technical
cluster: "getting-started"
tags: [cyborgenic, dashboard, monitoring, observability, real-time, tutorial]
description: "A practical guide to building a real-time dashboard for monitoring agent task throughput, SLA compliance, cost tracking, and fleet health in a Cyborgenic Organization."
relatedPosts:
  - /blog/monitoring-ai-agent-fleet
  - /blog/real-time-agent-monitoring
  - /blog/agent-sla-enforcement-cyborgenic
  - /blog/agent-performance-benchmarking-cyborgenic
  - /blog/cost-optimization-ai-agents
---

# Building a Real-Time Agent Dashboard: Monitoring Your Cyborgenic Organization

You would never run a production server without monitoring. So why would you run a Cyborgenic Organization without a dashboard?

GenBrain AI is the company behind [agent.ceo](https://agent.ceo), and we operate six AI agents around the clock — CTO, Security, DevOps, Marketing, Fullstack, and CEO. They complete roughly 89 tasks per day. Without real-time visibility into what each agent is doing, how much it is spending, and whether it is meeting SLAs, we would be flying blind.

This is the practical guide to building a real-time agent dashboard. Not a conceptual overview. Actual architecture, actual code patterns, actual metrics. By the end, you will have a dashboard that shows fleet status, task throughput, SLA compliance, cost tracking, and an alert feed — the five panels every Cyborgenic Organization needs.

## Why You Need a Dashboard (Not Just Logs)

Logs tell you what happened. A dashboard tells you what is happening right now and what is about to go wrong.

When we first launched our Cyborgenic Organization, we relied on logs and periodic inbox checks. That worked for about two weeks. Then the Marketing agent got stuck in a retry loop on a social media API — burning $14 in tokens over three hours before anyone noticed. The DevOps agent missed an SLA by 40 minutes because its task queue backed up behind a long-running deployment. The CTO agent silently failed on a task and moved on to the next one without escalating.

Each of these incidents was visible in the logs. None of them were visible in real time. A dashboard would have caught all three within minutes.

The five panels we built, and the five panels you need:

1. **Fleet Status** — which agents are running, idle, errored, or crashed
2. **Task Throughput** — tasks completed per hour, success rate, failure reasons
3. **SLA Compliance** — real-time tracking per agent, breach countdown timers
4. **Cost Tracking** — token usage and API costs per agent, per hour, with budget alerts
5. **Alert Feed** — live stream of SLA breaches, errors, escalations, and anomalies

## Architecture: Events, Streams, and State

The dashboard architecture has three layers: **event ingestion**, **state aggregation**, and **rendering**.

### Event Ingestion via NATS

Every agent in a Cyborgenic Organization built on [agent.ceo](https://agent.ceo) publishes structured events to NATS subjects. These events are the raw data for your dashboard.

The key subjects to subscribe to:

```
agent.{name}.status      — heartbeat, state changes (running/idle/error)
agent.{name}.task.start   — task accepted, includes task ID and description
agent.{name}.task.complete — task finished, includes outcome and duration
agent.{name}.task.fail     — task failed, includes error and retry count
agent.{name}.cost          — token usage per API call
agent.{name}.sla.warning   — SLA deadline approaching (80% elapsed)
agent.{name}.sla.breach    — SLA deadline missed
```

Subscribe to `agent.>` to get everything. In production, you want selective subscriptions per panel to avoid processing noise.

```typescript
import { connect, StringCodec } from "nats";

const nc = await connect({ servers: "nats://localhost:4222" });
const sc = StringCodec();

// Subscribe to all agent events
const sub = nc.subscribe("agent.>");

for await (const msg of sub) {
  const event = JSON.parse(sc.decode(msg.data));
  const [_, agentName, eventType, subType] = msg.subject.split(".");
  
  switch (eventType) {
    case "status":
      updateFleetPanel(agentName, event);
      break;
    case "task":
      updateThroughputPanel(agentName, subType, event);
      break;
    case "cost":
      updateCostPanel(agentName, event);
      break;
    case "sla":
      updateSLAPanel(agentName, subType, event);
      addToAlertFeed(agentName, event);
      break;
  }
}
```

### State Aggregation

Raw events are too granular for a dashboard. You need aggregated state: tasks per hour (not individual task events), cumulative cost (not per-call cost), rolling SLA compliance percentage (not individual checks).

We use a lightweight in-memory aggregator that maintains sliding windows:

```typescript
interface AgentMetrics {
  name: string;
  status: "running" | "idle" | "error" | "offline";
  lastHeartbeat: Date;
  
  // Throughput (1-hour sliding window)
  tasksCompleted: number;
  tasksFailed: number;
  successRate: number;
  
  // SLA (24-hour rolling)
  slaCompliance: number;
  activeDeadlines: SLADeadline[];
  
  // Cost (current day)
  tokenUsage: { input: number; output: number };
  apiCost: number;
  costTrend: number[];  // last 24 hourly buckets
}

class MetricsAggregator {
  private agents: Map<string, AgentMetrics> = new Map();
  
  onTaskComplete(agent: string, event: TaskCompleteEvent) {
    const metrics = this.getOrCreate(agent);
    metrics.tasksCompleted++;
    metrics.successRate = metrics.tasksCompleted / 
      (metrics.tasksCompleted + metrics.tasksFailed);
    this.pruneWindow(metrics, "throughput", 3600_000); // 1hr
    this.broadcast("throughput", metrics);
  }
  
  onCostEvent(agent: string, event: CostEvent) {
    const metrics = this.getOrCreate(agent);
    metrics.tokenUsage.input += event.inputTokens;
    metrics.tokenUsage.output += event.outputTokens;
    metrics.apiCost += event.cost;
    
    // Check for cost anomaly
    const hourlyAvg = metrics.apiCost / this.hoursElapsedToday();
    if (event.cost > hourlyAvg * 3) {
      this.emitAlert(agent, "cost_spike", {
        expected: hourlyAvg,
        actual: event.cost,
        message: `${agent} cost spike: $${event.cost.toFixed(2)} 
                  (3x hourly average)`
      });
    }
    
    this.broadcast("cost", metrics);
  }
}
```

### Rendering via WebSocket

The aggregator pushes state updates to connected dashboard clients over WebSocket. Each panel subscribes to its data channel. Updates are debounced — you do not need 60fps for a metrics dashboard. We push at most once per second per panel.

```typescript
// Server side
wss.on("connection", (ws) => {
  // Send current state snapshot on connect
  ws.send(JSON.stringify({
    type: "snapshot",
    fleet: Array.from(aggregator.agents.values()),
    alerts: aggregator.recentAlerts(50)
  }));
  
  // Stream updates
  aggregator.on("update", (panel, data) => {
    ws.send(JSON.stringify({ type: "update", panel, data }));
  });
});
```

On the client side, each panel component listens for its update type and re-renders. We use a straightforward React setup, but any framework works — the WebSocket protocol is framework-agnostic.

## The Five Panels in Detail

### Panel 1: Fleet Status

The simplest and most important panel. A row of cards, one per agent. Each card shows:

- **Agent name and role** (CTO, Security, DevOps, etc.)
- **Status indicator** — green (running), yellow (idle), red (error), gray (offline)
- **Current task** — what the agent is working on right now
- **Uptime** — how long since last restart or crash

Status is determined by heartbeats. Every agent publishes a heartbeat to `agent.{name}.status` every 30 seconds. If you miss three consecutive heartbeats (90 seconds), the agent shows as offline. This has caught two agent crashes that would have gone unnoticed for hours.

In our fleet right now: 6 agents, all green, average uptime 6.3 days since last restart.

### Panel 2: Task Throughput

A time-series chart showing tasks completed per hour across the fleet, with a breakdown by agent. Overlay the failure rate as a separate line.

Key metrics displayed:

| Metric | Current Value |
|--------|--------------|
| Tasks/day (fleet) | 89 |
| Tasks/hour (peak) | 7.2 |
| Success rate | 94% |
| Avg task duration | 8.4 min |
| Retry rate | 6.1% |

The throughput panel also shows a task type breakdown. Engineering tasks take longer but have higher success rates. Marketing content tasks are fast but occasionally need rework. Security scans are the most consistent.

### Panel 3: SLA Compliance

This is the panel you watch when you care about reliability. It shows:

- **Fleet-wide SLA compliance** — currently 97.3% across all agents
- **Per-agent compliance** — color-coded bars. Green above 95%, yellow 90-95%, red below 90%
- **Active deadline timers** — countdown clocks for tasks approaching their SLA deadline
- **Recent breaches** — last 10 SLA violations with root cause tags

The deadline timers are the most actionable element. When a task hits 80% of its SLA window, the timer turns yellow. At 90%, it turns red. We have caught and resolved four potential breaches by noticing yellow timers and investigating why an agent was taking longer than expected.

For implementation details on how SLAs are defined and enforced, see our earlier post on [agent SLA enforcement](/blog/agent-sla-enforcement-cyborgenic).

### Panel 4: Cost Tracking

Money. The panel every founder checks first.

- **Today's total spend** — currently tracking around $33/day
- **Per-agent cost breakdown** — pie chart showing which agents consume the most
- **Hourly cost trend** — line chart for the last 24 hours
- **Budget utilization** — progress bar against the monthly $1,000 budget
- **Cost per task** — average and per-agent breakdown

The cost panel includes **anomaly detection**. If an agent's hourly cost exceeds 3x its rolling average, it triggers a cost spike alert. This catches retry loops — when an agent fails a task and retries repeatedly, each retry burns tokens. Our $14 Marketing agent incident would have triggered an alert within 15 minutes instead of running for three hours.

```typescript
// Anomaly detection logic
function checkCostAnomaly(agent: AgentMetrics, newCost: number) {
  const rollingAvg = agent.costTrend
    .slice(-6)  // last 6 hours
    .reduce((a, b) => a + b, 0) / 6;
  
  if (newCost > rollingAvg * 3 && rollingAvg > 0.50) {
    return {
      alert: true,
      severity: newCost > rollingAvg * 5 ? "critical" : "warning",
      message: `Cost spike: $${newCost.toFixed(2)}/hr vs ` +
               `$${rollingAvg.toFixed(2)}/hr average`
    };
  }
  return { alert: false };
}
```

### Panel 5: Alert Feed

A reverse-chronological feed of everything that needs attention:

- SLA breaches and warnings
- Cost anomalies
- Agent crashes or offline events
- Task failures after max retries
- Escalations to founder

Each alert has a severity (info, warning, critical), a timestamp, the source agent, and a one-line description. Critical alerts also trigger push notifications.

In a typical day, we see 3-5 warnings (mostly SLA timers approaching deadlines) and zero criticals. A day with more than 2 criticals means something systemic is wrong — usually an external API outage or a deployment that introduced a bug.

## What Our Dashboard Shows Today

Right now, the GenBrain AI dashboard shows:

| Panel | Value |
|-------|-------|
| Fleet status | 6/6 agents green |
| Tasks today | 89 completed, 6 failed |
| SLA compliance (7d) | 97.3% |
| Cost today | $33.12 |
| Active alerts | 1 warning (DevOps SLA at 82%) |

This is all from a fleet running at $1,000/month. For context on how that cost breaks down and compares to human teams, see our [cost optimization guide](/blog/cost-optimization-ai-agents).

## Advanced Features Worth Building

Once you have the five core panels running, these additions pay for themselves:

**Agent comparison view.** Side-by-side metrics for two agents. Useful when you are tuning prompts or testing model upgrades — run the same task type on two configurations and compare throughput, cost, and quality in real time.

**Task trace drill-down.** Click any task in the throughput panel to see its full trace: every tool call, every API request, every context switch. This is how you debug slow tasks. We found that 60% of our slowest tasks were caused by a single tool call that timed out and retried three times.

**Historical trend overlays.** Compare this week's metrics to last week's. Spot regressions early. Our [performance benchmarking system](/blog/agent-performance-benchmarking-cyborgenic) feeds into this, giving you week-over-week quality trends alongside throughput and cost.

**Predictive budget alerts.** Based on current burn rate, when will you hit your monthly budget? If the answer is "day 22," you need to throttle. We project daily and show a budget runway indicator — green if we will finish the month under budget, yellow if within 10%, red if over.

## Getting Started

If you are running a Cyborgenic Organization on [agent.ceo](https://agent.ceo), the event infrastructure is already there. NATS subjects are publishing. You need:

1. **A NATS subscriber** that aggregates events into panel state
2. **A WebSocket server** that pushes state updates to the browser
3. **A frontend** with five panels — start with the fleet status panel, add one panel at a time
4. **Anomaly detection** on the cost panel — this is the one that saves you real money

Build the fleet status panel first. It takes an afternoon and immediately tells you if an agent is down. Then add cost tracking. Then throughput. Then SLA. Then alerts.

You do not need a fancy UI framework. A plain HTML page with WebSocket listeners and some CSS works fine for a team of one founder and six agents. Polish comes later. Visibility comes now.

The Cyborgenic Organization runs 24/7. Your monitoring should too.

---

*Build your Cyborgenic Organization with built-in observability. [agent.ceo](https://agent.ceo) provides the event infrastructure, agent fleet management, and SLA enforcement — you bring the dashboard.*

*Need enterprise-grade monitoring with custom dashboards, audit trails, and compliance reporting? Contact [enterprise@agent.ceo](mailto:enterprise@agent.ceo) for a dedicated deployment tailored to your fleet.*
