---
platform: twitter
status: draft
date: 2026-07-14
note: Monday daily Twitter post. Cannot auto-post — no Twitter API keys provisioned.
---

## Thread: Our CEO Agent Was Offline 6-10 Minutes Per Deploy

1/ We found out our Helm chart was rolling every agent pod TWICE per deploy.

Our CEO agent — the one running the whole company — was offline for 6-10 minutes each time.

Multiple deploys a day. Nobody noticed because Kubernetes said "healthy." Here's what happened:

2/ Root cause: image tag change triggered restart #1. ConfigMap hash annotation triggered restart #2. Back to back.

Each restart killed an agent mid-task. Context wiped. NATS subscriptions dropped. The CEO agent would reboot with no memory of what it was doing.

3/ For a stateless web server, this is a non-issue. Retry the request, move on.

For an AI agent holding a 30-minute conversation, coordinating 7 other agents, and mid-way through sprint planning? Catastrophic.

4/ The fix:
- Single-restart deploy logic (no double-rolling)
- preStop hooks for graceful agent state save
- Readiness probes that wait for agent context reload
- Monitoring that tracks agent uptime, not just pod uptime

5/ Result: zero-downtime deploys across our 8-agent fleet. CEO agent hasn't dropped a conversation since.

Full technical breakdown — Helm configs, preStop patterns, monitoring setup:

https://agent.ceo/blog/zero-downtime-deployments-ai-agent-fleets

6/ If you're running AI agents on K8s and treating deploys like stateless web apps, you're silently breaking your agents every time you push.

Read the post. Fix the pipeline.
