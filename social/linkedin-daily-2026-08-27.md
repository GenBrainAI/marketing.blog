---
platform: linkedin
status: draft
date: 2026-08-27
note: "Wednesday tutorial — CLAUDE.md scaling rules"
---

## Post: 6 Rules for Agent Instructions That Survive Scaling

We run 6 AI agents in production. Each has a different role — marketing, engineering, DevOps, CEO. Each needs different instructions.

The naive approach: copy-paste a shared rules block into every agent's config file. Then update one rule and forget to propagate it to the others. We did this. It broke things.

The fix is boring infrastructure work:

1. Shared rules live in ONE file. Role-specific config lives in separate overlays.
2. A build script assembles the final instruction file at deploy time. No human copy-paste.
3. Rules are rules, not suggestions. "MUST" + specific action + structural enforcement.
4. Anti-patterns are listed explicitly — agents under pressure invent creative workarounds you never imagined.
5. Reference material uses tables, not prose. Agents scan under context pressure; they do not read essays.
6. Delivery via ConfigMap with a reconciler that checks every 10 minutes. Update once, every agent gets the new version.

The biggest lesson: if you cannot grep your org for where a rule is defined and find exactly one result, you have a duplication problem that will bite you at scale.

Full tutorial: https://agent.ceo/blog/writing-agent-instructions-claude-md-scale

#AIAgents #LLMOps #AgentEngineering #BuildingInPublic #AgentCEO
