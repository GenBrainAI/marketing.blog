---
platform: linkedin
status: draft
date: 2026-08-28
note: "Thursday engagement — rules not suggestions"
---

## Post: Write Rules, Not Suggestions

The single most common failure in AI agent instruction files: writing suggestions instead of rules.

"Try to verify your work before marking it complete."

What happens: the agent is 90% through context, under token pressure, three tasks deep. It reads "try to" and skips verification. The task gets marked done. The bug ships.

This is not a prompting failure. It is a specification failure. "Try to" is not a rule. It is a hope.

The fix has three parts:

First, use MUST, not "try to" or "should." MUST is unambiguous.

Second, specify the exact action. Not "verify your work" but "call complete_task_unverified() with commit SHA, test output, and endpoint URL."

Third, add structural enforcement. A hook that rejects task completion when verification_steps have not been executed. The agent cannot bypass what the system refuses to accept.

We rewrote our shared instruction file with this pattern. Before: converting our task lifecycle from a paragraph description to a table reduced missed accept_task calls from roughly 40% to near zero. The same principle applies to every critical rule — structural enforcement beats prose every time.

Full post: https://agent.ceo/blog/writing-agent-instructions-claude-md-scale

#AIAgents #LLMOps #AgentEngineering #BuildingInPublic #AgentCEO
