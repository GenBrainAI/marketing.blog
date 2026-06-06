---
platform: twitter
status: draft
date: 2026-10-06
note: "Blog launch: Why :latest Broke Our Customer Agents"
---

## Thread: Why :latest Broke Our Customer Agents

New post: how `:latest` silently broke our customer-org agents and the three-layer fix we shipped.

`:latest` is a known K8s foot-gun. In multi-tenant platforms the failure mode is specific: your core fleet stays current via CI. Tenant deployments drift behind with no alerts.

---

We caught it when customer-org users reported MCP server timeouts. MCP handshake takes ~1.2s even with unreachable NATS. Their pods were running an image that predated commit 1494f5107 -- the dual-scope MCP fix our core fleet already had.

The image tag said `:latest`. The image content was weeks old.

---

Layer 1: `resolve_platform_agent_image()` reads the immutable SHA from the reference deployment. It rejects `:latest` -- pass a tag instead of a digest, it fails explicitly.

Layer 2: the provisioner pins new customer orgs to the current SHA at creation time. No more `:latest` default.

---

Layer 3: `sync-customer-org-images.sh` catches up existing customer orgs after every core fleet release. Existing tenants don't get left behind.

7 new test cases for the resolver and image precedence chain. If the resolver ever falls back to `:latest`, tests catch it before CI does.

---

Full writeup: https://agent.ceo/blog/image-pinning-latest-tag-customer-agent-drift

#Kubernetes #ImagePinning #MultiTenant #AgentCEO
