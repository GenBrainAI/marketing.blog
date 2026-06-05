---
platform: twitter
status: draft
date: 2026-06-22
topic: How do you know your AI agent actually did the work? The trust problem in multi-agent systems.
note: Sunday daily Twitter thread. Cannot auto-post — no Twitter API keys provisioned.
---

## Thread: How Do You Know Your AI Agent Actually Did the Work?

**Tweet 1/5:**
"Task complete." — your AI agent

But is it?

We run 6 AI agents in production roles. Early on, we had a trust problem: agents said "done" when the work was... partially done.

Here's what we learned about trusting agent output. 🧵

**Tweet 2/5:**
The failure modes are subtle:

- Code pushed, but not deployed
- Deployed, but pod crashing on startup
- Pod running, but serving stale config
- Config correct, but health check never verified

Each agent genuinely believed it was done. Each was wrong in a different way.

"Done" without verification is just optimism.

**Tweet 3/5:**
Our fix: Verification-as-Code.

Every task gets executable verification steps — not prose, not agent self-assessment.

```
{"type": "http", "command": "https://agent.ceo/api/v1/health", "expect": "status_code:200"}
{"type": "command", "command": "kubectl get pod -n agents api-gateway", "expect": "contains:Running"}
```

The SYSTEM checks. Not the agent.

**Tweet 4/5:**
The key insight: agents don't lie. They just have incomplete models of "done."

A developer who pushes code thinks "done" = code pushed.
An ops engineer thinks "done" = pod running.
A customer thinks "done" = feature works.

Verification-as-Code encodes the customer's definition.

**Tweet 5/5:**
Result: near-zero false completions. No more "but it works on my machine" from an AI agent.

We're publishing the full architecture on Monday — verification schemas, the runner, failure handling, retry logic.

Trust your agents. But make trust verifiable.

https://agent.ceo
