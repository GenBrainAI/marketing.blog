---
platform: twitter
status: draft
date: 2026-07-24
note: Thursday daily Twitter post. Cannot auto-post — no Twitter API keys provisioned.
---

## Thread: Cost Discipline for AI Agent Operations

1/ Every kubectl write, every git push, every CI trigger costs money.

Before retrying a failed deploy: investigate the root cause.

This sounds obvious. It's the most common failure mode we see in agent operations. A thread:

2/ The pattern: agent hits a deploy error. Ambiguous message. Agent retries. Same error. Retries again. Same error.

Five attempts later, someone notices 40 minutes of burned compute on a misconfigured secret that was never going to resolve through repetition.

3/ Three rules we enforce structurally:

1. Read before write. `kubectl get` before `kubectl apply`. `git diff` before `git push`. 90% of the time, the read tells you the write would fail.

2. Same action x5 with no success = stop. Decompose, mark blocked, escalate.

3. CI/CD is manual/tag-only. Branch pushes don't trigger builds. No accidental pipelines from a README fix.

4/ Result: 8 AI agents, full Kubernetes infrastructure, under $1,000/month.

Not because we're cheap. Because we're deliberate. Every write operation earns its cost.

Cost discipline isn't about spending less. It's about spending on things that work.

5/ The fifth retry attempt is not going to work either.

Build systems that investigate before they retry. The debugging is cheaper than the repetition.
