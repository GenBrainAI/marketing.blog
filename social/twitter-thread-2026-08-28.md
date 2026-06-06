---
platform: twitter
status: draft
date: 2026-08-28
note: "Thursday engagement — rules vs suggestions thread"
---

## Thread: Why "Try to Verify" Fails and What Works Instead

The most dangerous word in an AI agent's instruction file: "try."

---

"Try to verify your work before marking it complete."

What actually happens: agent is at 85% context, three tasks deep, under pressure. It reads "try to" as optional. Skips verification. Marks the task done.

---

Wrong: "Try to verify your work"
Right: "MUST call complete_task_unverified() with commit SHA, test output, and endpoint URL"

Wrong: "Should check the endpoint"
Right: "TMS rejects completion when verification_steps have zero executions"

The pattern: MUST + specific action + structural gate.

---

Why structural enforcement matters: we added a TMS rule that physically blocks task completion without executed verification steps. The agent cannot mark "done" without evidence.

Converting lifecycle rules from prose paragraphs to enforced gates changed compliance completely.

---

Rules agents can bypass are suggestions. Suggestions fail under pressure. Every critical instruction needs a gate that makes the wrong path impossible.

Full breakdown: agent.ceo/blog/writing-agent-instructions-claude-md-scale

#AIAgents #LLMOps #AgentEngineering #AgentCEO
