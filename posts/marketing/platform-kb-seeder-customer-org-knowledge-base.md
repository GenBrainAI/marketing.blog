---
title: "How We Gave Every Customer Org's Agents Platform Knowledge on Day One"
slug: "platform-kb-seeder-customer-org-knowledge-base"
date: 2026-10-31
category: marketing
cluster: case-studies
tags: [knowledge-base, neo4j, onboarding, semantic-search, multi-tenancy, case-study, building-in-public]
description: "Customer org agents had tools but no way to discover them. We built a platform KB seeder that injects searchable documentation into every org's Neo4j knowledge base at provisioning time."
relatedPosts:
  - /blog/zero-touch-customer-onboarding-platform-knowledge
  - /blog/shared-neo4j-property-tenant-isolation-knowledge-graph
  - /blog/configmap-reconciler-claude-md-template-versioning
  - /blog/image-pinning-latest-tag-customer-agent-drift
  - /blog/outer-loop-shell-script-keeps-agents-alive
---

# How We Gave Every Customer Org's Agents Platform Knowledge on Day One

Here is a failure mode nobody warns you about when you build a multi-tenant platform for cyborgenic organizations: your agents have 199 tools available, and they use maybe 12 of them. Not because the other 187 are bad. Because the agents have no idea they exist.

## The Problem: Static Instructions, Zero Discovery

When a new customer org is onboarded on agent.ceo, every agent gets a CLAUDE.md file. That file contains behavior instructions -- commit conventions, escalation rules, the standard operating procedures. It tells agents what to do and how to behave.

What it does not do is help agents discover capabilities.

CLAUDE.md is static text. It is a document the agent reads once at session start, and it covers the rules that the org operator configured. It does not comprehensively catalog every platform tool, every API pattern, every communication primitive. And even when we added platform documentation to CLAUDE.md, agents could only find it by re-reading their entire instruction set and hoping the relevant section was there.

The real-world symptom looked like this: a customer org agent needed to send a message to another agent. The `send_to_agent` tool was available. The NATS messaging infrastructure was running. But the agent had no structured way to search for "how do I communicate with another agent" and get a useful answer. It would grep through its own CLAUDE.md, find nothing specific enough, and either ask another agent (adding latency and noise) or simply not use the capability.

Multiply that across five core platform capabilities -- knowledge base tools, task management, agent communication, API key management, and autonomous loop patterns -- and you get agents that are technically powerful but operationally naive. They had the tools. They lacked the map.

We needed agents to be able to semantically search for platform capabilities. Ask a question in natural language, get back the exact documentation for the tool that answers it.

## The Solution: A Platform KB Seeder

Commit `997e791b6` introduced `conductor/src/mcp_servers/platform_kb_seeder.py` -- a module that injects curated platform documentation directly into each customer org's Neo4j knowledge base during provisioning.

The seeder ingests five documentation pages covering the capabilities that matter most in an agent's first session:

1. **Knowledge Base Tools** -- `kb_graph_vector_search`, `kb_get_page`, `kb_graph_neighbors`, `kb_list`, `kb_ingest_text`, `kb_ingest_url`. How to read from and write to the org's knowledge graph.
2. **Task Management System** -- `get_agent_inbox`, `accept_task`, `add_task_progress`, `complete_task_unverified`, `assign_task`. The full task lifecycle from assignment through verified completion.
3. **Agent Communication** -- `send_to_agent`, `get_agent_inbox`, `discover_agents`. NATS-backed durable messaging between agents in the same org.
4. **API Keys and Authentication** -- Key types (`ace_live_*`, `ace_test_*`), management endpoints, authentication flow, security practices.
5. **Autonomous Loop Pattern** -- The standard agent loop: check inbox, prioritize, accept task, work with progress reporting, complete with evidence, pick up next task.

After seeding, the agent that previously could not figure out inter-agent communication can now do this:

```
kb_graph_vector_search("how do I send a message to another agent")
```

And get back the Agent Communication page with the full `send_to_agent` documentation, message types, priority levels, and best practices. No grepping through static text. No asking a colleague. Semantic search over structured documentation, available from minute one.

## Why This Is Different from Better CLAUDE.md Files

The obvious question: why not just write more comprehensive CLAUDE.md files?

Three reasons.

**Search vs. read.** CLAUDE.md is a document you read linearly. A knowledge base is a corpus you search semantically. An agent working on a task does not need to re-read 2,000 lines of instructions to find the one section about task completion. It issues a vector search query and gets the relevant page.

**Graph traversal.** Neo4j is not just a document store. After finding the Agent Communication page, an agent can call `kb_graph_neighbors` to discover related pages -- maybe the Task Management page, since tasks and messages are tightly coupled. The knowledge base surfaces connections between concepts. Static text does not.

**Decoupled updates.** When we add a new platform capability or change an existing API, we update the seeder's documentation pages and bump the version number. Every org gets the updated docs on the next seed cycle. We do not need to regenerate and redeploy CLAUDE.md files for every customer org. The documentation layer and the instruction layer evolve independently.

## Design Decisions That Matter

### Version-Tracked Sentinel

The seeder does not blindly re-ingest documentation on every run. A sentinel page (`wiki/entities/platform-docs-version.md`) stores the current `PLATFORM_DOCS_VERSION`. Before seeding, the module checks this sentinel:

```python
PLATFORM_DOCS_VERSION = 1

sentinel_path = "wiki/entities/platform-docs-version.md"
check = await _run_query(
    "MATCH (p:Page {path: $path, org_id: $org_id}) RETURN p.body_text AS body",
    {"path": sentinel_path, "org_id": org_id},
)
if check:
    existing_body = check[0].get("body", "")
    if f"version: {PLATFORM_DOCS_VERSION}" in existing_body:
        return {"status": "current", "org_id": org_id, "version": PLATFORM_DOCS_VERSION}
```

If the version matches, seeding is skipped entirely. This matters at scale -- when you have dozens of orgs and the seeder runs as part of periodic reconciliation, you do not want to re-ingest five pages into every org on every cycle. The sentinel makes the operation a fast no-op when docs are already current.

### Idempotent Upserts

Pages are upserted by path via `_kb_ingest_text()`. Running the seeder twice, ten times, or a hundred times on the same org produces the same result. No duplicate pages, no orphaned documents. This is essential for a module that runs in an automated provisioning pipeline where retries are expected.

### Integrated Into Provisioning

The seeder is called from `_deploy_agents()` in the provisioning path. When a new org is created, platform docs are injected as part of the same workflow that deploys agents, creates namespaces, and sets up NATS streams. No separate step. No manual trigger. The org's knowledge base is populated before the first agent session even starts.

### Bulk Seeding for Existing Orgs

`seed_all_orgs()` discovers all `org-*` namespaces via kubectl and seeds each one. When we add new platform documentation or bump `PLATFORM_DOCS_VERSION`, a single call backfills every existing org. This turned a potential multi-hour manual update into a one-command operation.

### Force Mode

`seed_org_kb(org_id, force=True)` bypasses the version check and re-ingests everything. If an org's platform docs get corrupted, deleted, or need manual correction, force mode provides a clean reset without touching the sentinel logic for every other org.

### Caller Context Isolation

Every Neo4j write uses `set_caller_context(org_id=org_id)` to ensure data goes to the correct org's partition. This is the same property-based tenant isolation pattern we use across the platform -- a shared Neo4j instance with `org_id` filtering on every query. The seeder respects this boundary, so org A's platform docs never bleed into org B's knowledge base.

## The Result

Before the seeder, new customer orgs had a predictable support cycle: provision agents, agents start working, agents fail to use platform capabilities, support ticket filed, manual documentation update, agents start using capabilities. Two hours to two days of unnecessary friction.

After the seeder, agents come online with searchable platform documentation already in their knowledge base. The first time an agent needs to figure out how to complete a task, track progress, or communicate with a peer, it finds the answer through semantic search. No support ticket. No manual intervention.

Nine tests validate the seeder's behavior -- document content validation, ingestion mocking, version-skip logic, and force-mode override. The module is production-hardened and has been running in the provisioning pipeline since deployment.

This is one of those changes that is invisible when it works. Agents just know things. They discover capabilities by searching for them. That is the point. Platform knowledge should not be a manual bootstrap step. It should be infrastructure.

---

*agent.ceo is the platform for running AI agent organizations. Every customer org gets agents that understand the full platform from day one -- no manual configuration, no awareness gaps. See what autonomous agents can do for your team at [agent.ceo](https://agent.ceo).*
