---
platform: linkedin
status: draft
date: 2026-10-16
note: "Your Self-Healing Loop Can't Distinguish Crashes From Precondition Failures"
---

## Post: Your Self-Healing Loop Can't Distinguish Crashes From Precondition Failures

Self-healing retry loops are supposed to make systems resilient. Ours made our agents slower.

Our wrapper script ran `claude --continue` to resume the previous session on restart. When there was no previous session -- a fresh PVC, a cleared workspace -- Claude exited 1: "No conversation found to continue." The wrapper saw exit 1, assumed a transient crash, and retried. Three times. With exponential backoff: 2s, 4s, 8s. Thirty seconds of fake crash recovery before the nuclear fallback finally stripped the `--continue` flag and started fresh.

This happened on every pod restart. Every session archive. Every time we recycled a PVC.

The problem: our retry loop treated every non-zero exit the same way. But "no conversation to continue" is not a transient error. It is a structural precondition failure. No amount of retrying will create a transcript that does not exist.

The fix was embarrassingly simple. Before launching, check whether a resumable session exists:

`find ~/.claude/projects/ -name "*.jsonl" -type f -size +0c -print -quit`

If a non-empty `.jsonl` transcript file exists, use `--continue`. If not, start fresh immediately. No retry. No backoff. No wasted seconds.

The broader lesson: self-healing loops should CLASSIFY exits, not just RETRY them. "No conversation to continue" is structural -- it will fail every single attempt. "Connection refused" is transient -- retrying makes sense. Lumping them together is how you build a system that spends 30 seconds recovering from problems that don't exist.

Read more: https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#SelfHealing #RetryLoop #AIAgents #AgentCEO
