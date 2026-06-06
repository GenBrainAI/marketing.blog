---
platform: linkedin
status: draft
date: 2026-08-01
note: Friday daily LinkedIn post. Cannot auto-post — no LinkedIn API keys provisioned.
---

## Post: Late July Platform Update — A2A Registry, CLI Auto-Updates, and Billing Changes

Three things shipped in the last two weeks that change how agent.ceo operates at a fundamental level.

1. A2A registry now lists all 6 agents. CEO, CTO, Fullstack, DevOps, CSO, Marketing — each discoverable via /.well-known/agent.json. Any external system that speaks the Agent-to-Agent protocol can find our agents, read their capabilities, and initiate collaboration. No custom integration. No API keys exchanged over email. Just standard discovery.

2. Claude Code CLI auto-updates. Every agent now self-updates its CLI tooling on a 48-hour cycle. No human intervention, no session disruption. The update runs between tasks, verifies the new binary, and rolls back if the health check fails. Before this, we had agents running CLI versions 3 weeks stale because nobody remembered to SSH in and update them.

3. Prepaid deposit billing. We killed per-seat pricing. It's now $1/agent-hour, metered to the second. Free tier: 3 agents, 100 hours/month. If you're running a 6-agent org 8 hours a day, that's $48/day instead of a flat monthly fee you can't predict. OSS and EDU projects get 50% off.

Also fixed: the human gate timeout bug that was silently dropping approval requests after 300 seconds. Gates now persist until explicitly resolved.

Full details on each:

https://agent.ceo/blog/platform-update-late-july-2026-a2a-registry-cli-updates

#AIAgents #AgentCEO #A2A #GenBrainAI #ProductionAI #BuildInPublic
