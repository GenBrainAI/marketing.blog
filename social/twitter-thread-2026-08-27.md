---
platform: twitter
status: draft
date: 2026-08-27
note: "Wednesday tutorial — CLAUDE.md scaling thread"
---

## Thread: 6 Rules for Agent Instructions That Scale

We run 6 AI agents in production roles. Their instruction files started as quick docs. They are now critical infrastructure.

6 rules we learned the hard way:

---

1/ Shared rules in ONE file. Role config in separate overlays.

We used to copy-paste a "core rules" block into every agent's config. Updated one, forgot the others. An agent ran stale verification rules for days before we noticed.

Fix: single source of truth, assembled at deploy time by a build script.

---

2/ Rules, not suggestions.

"Try to verify your work" becomes "skip verification" under pressure. Every instruction must be MUST + specific action + structural enforcement.

An agent will find every loophole you leave open.

---

3/ List anti-patterns explicitly.

You think "verify before marking complete" is clear. Your agent thinks "I verified by reading my own output." List the exact failure modes: no prose evidence, no self-reported success, no skipping hooks.

---

4/ Tables for scanning, not prose for reading.

Agents under token pressure skim. A 200-word paragraph about verification rules gets lost. A 6-row table with "Wrong | Right" columns survives and gets followed.

---

5/ Standing mandates need structural enforcement.

"Never push to main" is a suggestion until a pre-push hook rejects it. Pair every critical rule with a gate: hooks, TMS refusal, CI checks.

---

6/ ConfigMap delivery. Update the shared file, rebuild, reconciler patches within 10 minutes. Every agent gets the new version. No manual copy-paste. No drift.

Full tutorial: agent.ceo/blog/writing-agent-instructions-claude-md-scale

#AIAgents #LLMOps #AgentEngineering #AgentCEO
