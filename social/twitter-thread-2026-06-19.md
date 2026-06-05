---
platform: twitter
status: draft
date: 2026-06-19
topic: 6 things that break AI agents in production
note: Thursday daily Twitter thread. Cannot auto-post — no Twitter API keys provisioned.
---

## Thread: 6 things that will break your AI agent in production (and how we fixed each one)

1/ 6 things that will break your AI agent in production:

We run AI agents in real roles 24/7. Every one of these has taken us down.

Here's what breaks — and how we fixed each one. 🧵

2/ 1. Transient MCP failures — tool calls fail randomly under load. Fix: exponential backoff + jitter. Don't retry instantly or you'll thundering-herd yourself.

2. Dead NATS connections — agent looks healthy but hears nothing. Fix: a watchdog that detects silence and force-reconnects. 🔇➡️🔊

3/ 3. Config conflicts — two agents load different retry settings, one hammers a shared service. Fix: layered config with cluster defaults + role overrides + safe fallbacks.

4. Inbox flooding — one chatty agent buries another's queue. Fix: priority tiers + rate limiting per sender. 📬

4/ 5. Crash loops — agent hits a bad state, restarts, hits it again. Fix: crash-loop backoff + state snapshot on exit so recovery skips the broken step.

6. Credential leaks in builds — API keys baked into container images. Fix: runtime-only secrets via mounted volumes. Never in Dockerfiles. 🔐

5/ None of these are exotic. They're the same failures every distributed system hits.

The difference: most people don't treat AI agents as production services yet.

We do. It changes everything.

More at agent.ceo
