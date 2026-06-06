---
platform: linkedin
status: draft
date: 2026-10-17
note: "Blog launch — The 30-Second Crash Loop That Wasn't a Crash"
---

## Post: New Blog -- The 30-Second Crash Loop That Wasn't a Crash

New post: we spent weeks watching our agents waste 30 seconds on every restart before we realized the crash loop wasn't a crash at all.

Here's what happened. Our wrapper runs `claude --continue` to resume the agent's previous conversation. On a fresh PVC -- no prior session, no transcript files -- Claude exits 1 with "No conversation found to continue." Our self-healing loop sees exit 1, treats it as a crash, and retries with exponential backoff: 2s, 4s, 8s. Three retries. All fail identically. After 30 seconds, the nuclear fallback kicks in and strips `--continue` to start a fresh session.

Every restart. Every session archive. Thirty seconds of retrying something that could never succeed.

The fix: a precondition check called `has_resumable_session()`. One find command:

`find ~/.claude/projects/ -name "*.jsonl" -type f -size +0c -print -quit`

It looks for non-empty `.jsonl` transcript files under `~/.claude/projects/`. If one exists, use `--continue`. If none exist, start fresh immediately. Zero retries. Zero backoff.

The pattern is universal: precondition checking is cheaper than retry. Before attempting an operation, verify the prerequisite exists. Don't let your self-healing loop waste cycles on failures that are guaranteed to repeat.

Read the full breakdown: https://agent.ceo/blog/crash-loop-fresh-pvc-has-resumable-session

#CrashLoop #PreconditionCheck #BuildingInPublic #AgentCEO
