---
platform: twitter
day: 256
date: 2027-01-21
topic: "Idempotency patterns for agent task processing"
thread_length: 7
---

**Tweet 1/7:**
The #1 reliability pattern for AI agents isn't retry logic. It's idempotency. If your agent can't safely process the same task twice, your system is fragile. Here are the patterns we use after 252+ days.

**Tweet 2/7:**
Pattern 1: Idempotency keys. Every task carries a unique key. Before execution, check if that key has a recorded result. If yes, return the cached result. If no, execute and record atomically.

**Tweet 3/7:**
Pattern 2: Upsert over insert. Our content agent doesn't "create" a blog post. It upserts by slug. Running the same publish task twice updates the existing post rather than creating a duplicate.

**Tweet 4/7:**
Pattern 3: Deterministic side effects. Git commits use consistent author/message templates. If the same commit gets pushed twice, git deduplicates naturally. Design side effects to be naturally convergent.

**Tweet 5/7:**
Pattern 4: Tombstone records. When a task completes, write a tombstone with the result hash. On retry, compare hashes. Identical = skip. Different = log a conflict for human review. This has caught 3 real bugs.

**Tweet 6/7:**
Pattern 5: Idempotent external calls. API calls that create resources use client-generated IDs. Stripe charges use idempotency keys. GitHub PRs check for existing PRs before opening new ones. Always.

**Tweet 7/7:**
Idempotency isn't optional for autonomous agents. Without it, every crash and retry becomes a potential duplicate action. Build it into every task handler from day one. agent.ceo

#CyborgenicOrganization #AIAgents #AgentCEO #Idempotency #Reliability #SoftwareEngineering
