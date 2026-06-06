---
platform: twitter
status: draft
date: 2026-08-21
note: Thursday engagement — pre-deploy checklist thread
---

## Thread: Pre-deploy checklist for autonomous agents

Most teams have deploy checklists. Almost nobody has an agent pre-deploy checklist. Here is the one we run at agent.ceo before every launch:

---

1/ DRY-RUN LOGS CLEAN. Run the agent in dry-run mode. Read every tool call it attempted. If it tried to hit an endpoint that does not exist, it will do the same in production. Fix it now.

---

2/ PAUSE FILE TEST. Create the PAUSE file. Confirm the agent stops within one loop cycle. Remove it. Confirm the agent resumes. If this does not work, you have no kill switch.

---

3/ STATUS REPORTER CHECK. Query the status reporter. Every daemon should show running. If the status reporter itself is down, you are flying blind.

---

4/ HUMAN GATE + BLOCK LIMIT. Confirm the approval timeout is set (we use 2 minutes). Confirm the stop-block limit is set (we use 3). Without these, a stuck agent waits forever or retries forever.

Full breakdown: agent.ceo/blog/safely-test-ai-agents-production-controls #AIAgents #ProductionSafety #AgentOps
