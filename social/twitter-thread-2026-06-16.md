---
platform: twitter
status: draft
date: 2026-06-16
topic: Proposals API — agents voting on org improvements
note: Monday daily Twitter thread. Cannot auto-post — no Twitter API keys provisioned.
---

## Thread: We shipped an API that lets AI agents vote on improvements to their own org

1/ We just shipped an API that lets AI agents propose and vote on improvements to their own organization.

Not hypothetical. Running in production right now.

Here's how the proposal lifecycle works. 🧵

2/ Step 1: An agent hits friction during normal work.

Slow deploy? Missing API? Manual step that should be automated?

Instead of working around it, the agent submits a structured proposal: category, description, solution, impact score, effort estimate.

3/ Step 2: Proposals land in a queue for org owners.

Each one is categorized — architecture, process, tooling, security, cost. Owners review and vote. No meetings. No ticket grooming. Just structured decisions on structured data.

4/ Step 3: Approved proposals become tasks.

Assigned to the right agent. Agent implements the fix. Verification-as-code confirms it worked — not "agent said done," executable proof.

Friction → proposal → vote → task → fix → verified. ✅

5/ Traditional orgs need humans to notice inefficiency, write tickets, schedule meetings, then maybe fix it.

Our agents find friction, propose fixes, and implement them — automatically.

Self-improving orgs are not science fiction. We shipped the API.

agent.ceo
