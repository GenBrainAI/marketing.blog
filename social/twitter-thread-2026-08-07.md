---
platform: twitter
status: draft
date: 2026-08-07
note: Thursday Twitter thread. Cannot auto-post — no Twitter API keys provisioned.
---

## Thread: The 12 Rules Every agent.ceo Agent Follows

1/ We run 6 AI agents in production. CEO, CTO, marketing, fullstack, devops, data. Every single one follows the same 12 rules -- no exceptions.

Here they are, with why each one matters:

---

2/ Rule 1: Nothing is done until verified. "Build triggered" is not done. "Endpoint returns 200" is done.

Rule 2: Verification-as-code. The task system structurally refuses to close a task without executable evidence. Prose like "I confirmed it works" is rejected.

---

3/ Rule 3: Decomposition before delegation. Can't break it into 2-5 verifiable sub-tasks? You don't understand it enough to hand it off.

Rule 4: Ground-truth sync. Every agent checks what changed while it was offline before doing anything. No duplicating work another agent already shipped.

---

4/ Rule 5: Bypass audit trail. Agents can skip verification -- but it's logged. 3 bypasses in one session triggers review.

Rule 6: Manager accountability. Delegating doesn't clear your responsibility. "Sent to X" is not completion. Your own observation is.

---

5/ Rule 7: Cluster state is truth, agent memory is hypothesis. kubectl output wins over "I remember creating that."

Rule 8: Anti-loop. Same action fails 5 times? Stop. Decompose, mark blocked, escalate. Attempt 6 won't magically work.

---

6/ Rule 9: Cost discipline. Every write operation costs money. Read first.

Rule 10: Honest reporting. Lead with what's broken. "Looks good" is not a status.

Rule 11: Chat mode protocol. Rule 12: Check reference files before reinventing.

Full shared discipline block: https://agent.ceo/blog/composable-agent-instructions-claude-md-architecture

#AIAgents #MultiAgentSystems #BuildInPublic
