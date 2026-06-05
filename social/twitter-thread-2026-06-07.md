---
platform: twitter
status: draft
date: 2026-06-07
note: Saturday Twitter thread. Cannot auto-post — no Twitter API keys provisioned.
---

## Thread: The `:latest` Tag Lie

1/ Your Kubernetes agents are running old code and nobody told you.

We just spent a week debugging MCP timeouts in a customer org. The root cause? Their agents were on a stale container image from weeks ago.

The tag said `latest`. The image was not latest.

2/ Here's what happens: you provision a customer org with `agent:latest`. Day 1, that resolves to the current SHA. Day 30, same tag — but Kubernetes hasn't re-pulled. The pod is still running the original image.

You ship a fix. Internal agents get it immediately. Customer agents? Still on the old image.

3/ The symptom was MCP tool timeouts. We had shipped a dual-scope MCP fix weeks earlier. Our fleet had it. The customer fleet didn't.

We chased networking issues, load patterns, DNS. The answer was deployment hygiene.

4/ The fix: pin customer org agent images to the exact platform SHA. Not :latest, not :stable — the digest.

When we ship a new image, we roll orgs forward deliberately. No more silent drift.

5/ If you deploy containers in production, audit your image tags today.

`:latest` in a Deployment manifest is a ticking clock. It works on day one and lies to you on day thirty.

Full post: https://agent.ceo/blog/hardened-customer-org-provisioning-platform-update
