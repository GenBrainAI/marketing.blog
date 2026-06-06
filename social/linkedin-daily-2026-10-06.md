---
platform: linkedin
status: draft
date: 2026-10-06
note: "Blog launch: Why :latest Broke Our Customer Agents"
---

## Post: Why :latest Broke Our Customer Agents

New blog post. We wrote up the full investigation into how `:latest` silently broke our customer-org agents -- and the three-layer fix we shipped.

`:latest` is a well-known Kubernetes foot-gun. But in multi-tenant platforms, the failure mode is specific: your core fleet stays current via CI. Tenant deployments drift behind silently. No errors, no alerts. Just stale images missing bug fixes that your own agents got weeks ago.

We caught it when customer-org users reported MCP server timeouts. The MCP handshake takes ~1.2s even with unreachable NATS. Their pods were running an image that predated commit 1494f5107 -- the dual-scope MCP fix our core fleet already had.

The three-layer fix:

1. `resolve_platform_agent_image()` reads the immutable SHA from the reference deployment. It rejects `:latest` -- if you pass a tag instead of a digest, it fails explicitly.

2. The provisioner pins new customer orgs to the current SHA at creation time. No more `:latest` as the default.

3. `sync-customer-org-images.sh` catches up existing customer orgs after every core fleet release. Existing tenants don't get left behind.

We added 7 new test cases covering the resolver and the image precedence chain. If the resolver ever falls back to `:latest`, the tests catch it before CI does.

Full writeup: https://agent.ceo/blog/image-pinning-latest-tag-customer-agent-drift

#Kubernetes #ImagePinning #MultiTenant #AgentCEO
