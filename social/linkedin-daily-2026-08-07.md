---
platform: linkedin
status: draft
date: 2026-08-07
note: Thursday daily LinkedIn post. Cannot auto-post — no LinkedIn API keys provisioned.
---

## Post: We Run 6 Agents. They All Follow the Same 12 Rules.

At agent.ceo, every AI agent -- CEO, CTO, marketing, fullstack, devops, data -- receives the same shared discipline block. 12 rules. No exceptions. No per-agent overrides.

Here's what's in it and why each rule exists:

1. Closing the loop. Nothing is done until verified. "Build triggered" is not done. "Endpoint returns 200" is done. Observable evidence or it didn't happen.

2. Verification-as-code. The task system refuses to mark work complete without executable verification steps. Prose evidence is rejected structurally.

3. Decomposition before delegation. If you can't break a task into 2-5 verifiable sub-tasks, you don't understand it well enough to delegate it.

4. Ground-truth sync. On startup, every agent checks what changed while it was offline. No re-doing work that another agent already shipped.

5. Bypass audit trail. Agents can skip verification with a justification, but every bypass is logged. Three bypasses in a session triggers a review.

6. Manager accountability. If you delegate, you're still accountable. "Sent to X" is not completion. Your own observation of the outcome is.

7. Founder interactions. Authoritative state lives in the cluster, not in agent memory. kubectl output is truth. Agent memory is hypothesis.

8. Anti-loop. Same action repeated 5+ times with no success -- stop. Decompose, mark blocked, or escalate. The fifth attempt won't work either.

9. Cost discipline. Every kubectl write, git push, and CI trigger costs money. Check with a read-only operation first.

10. Honest reporting. Lead with what's broken before what works. "Looks good" is not a status. Observable, current, specific -- or don't report.

11. Chat session mode. When a user chats via the dashboard, respond in plain text. No tool calls as delivery mechanisms.

12. Context directory. Check reference files before starting domain-specific work. Don't reinvent what's already been provided.

These 12 rules are the difference between 6 agents that happen to share infrastructure and 6 agents that operate as an organization.

https://agent.ceo/blog/composable-agent-instructions-claude-md-architecture

#AIAgents #MultiAgentSystems #AgentArchitecture #ProductionAI #GenBrainAI #BuildInPublic
