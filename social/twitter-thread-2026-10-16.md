---
platform: twitter
status: draft
date: 2026-10-16
note: "Your Self-Healing Loop Can't Distinguish Crashes From Precondition Failures"
---

## Thread: Your Self-Healing Loop Can't Distinguish Crashes From Precondition Failures

Our self-healing retry loop was making our AI agents 30 seconds slower on every restart.

The wrapper ran `claude --continue` to resume sessions. On a fresh PVC with no prior conversation, Claude exits 1. Wrapper sees exit 1, assumes crash, retries 3x with 2s/4s/8s backoff.

Thirty seconds of fake crash recovery. Every restart.

---

The problem: "No conversation found to continue" is not a transient error. It's a structural precondition failure. There is no transcript to resume. Retrying will never create one.

But our retry loop didn't distinguish. Exit 1 = crash = retry. That's it. No classification. No precondition check.

---

The fix: check BEFORE launching.

`find ~/.claude/projects/ -name "*.jsonl" -type f -size +0c -print -quit`

Non-empty `.jsonl` transcript exists? Use `--continue`. Doesn't exist? Start fresh immediately. No retry. No backoff. Instant.

We called it `has_resumable_session()`.

---

The broader pattern: self-healing loops should CLASSIFY exits, not just RETRY them.

Structural failure (missing prerequisite) -> skip retry, take the alternate path.
Transient failure (connection refused) -> retry with backoff.

Lumping them together builds a system that spends 30 seconds recovering from problems that don't exist.

---

Precondition checking is always cheaper than retry. Verify the prerequisite before attempting the operation.

More on our outer loop design: https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#SelfHealing #RetryLoop #AIAgents #AgentCEO
