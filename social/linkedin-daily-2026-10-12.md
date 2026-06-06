---
platform: linkedin
status: draft
date: 2026-10-12
note: "Level-Triggered vs Edge-Triggered — educational systems pattern post"
---

## Post: Level-Triggered vs Edge-Triggered: A Systems Pattern for Agent Loops

This pattern comes from hardware interrupt design, but it governs how every AI agent wrapper should detect work.

Level-triggered: fires as long as the signal is HIGH. In agent terms: "Is there pending work?" If the answer is yes and the work is never consumed, you fire every single check. Forever.

Edge-triggered: fires on the TRANSITION from LOW to HIGH. "Is there NEW work?" Fires once per item, then goes quiet. Previously-seen items don't re-trigger.

Yesterday we shared the story of a stale test probe that hot-looped our fleet. The root cause was level-triggered detection in `check_pending_work()`. The fix was edge-triggered detection using a persistent fingerprint ledger.

How the ledger works:

Each pending item gets a fingerprint: `filename:mtime:size`. The ledger at `/agent-data/config/seen_pending_work` stores every fingerprint that has already been surfaced to the agent. On each check, we compare current items against the ledger. Only items with fingerprints NOT in the ledger trigger a wake.

The ledger is rewritten every check cycle, pruning entries for items that no longer exist. No unbounded growth. No stale state accumulation. A clean, self-maintaining record of what the agent has already seen.

Simple pattern. Prevents an entire class of hot-loop failures.

Full write-up on our outer loop architecture: https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#SystemsEngineering #EdgeTriggered #AIAgents #AgentCEO
