---
platform: twitter
status: draft
date: 2026-10-17
note: "Blog launch — The 30-Second Crash Loop That Wasn't a Crash"
---

## Thread: New Blog -- The 30-Second Crash Loop That Wasn't a Crash

We just published: "The 30-Second Crash Loop That Wasn't a Crash."

Our agents wasted 30 seconds on every pod restart because our self-healing loop couldn't tell the difference between a real crash and a missing prerequisite.

Here's what we found and how we fixed it.

---

`claude --continue` resumes a previous session. On a fresh PVC with no prior conversation, it exits 1: "No conversation found to continue."

Our wrapper sees exit 1 and retries. 2s backoff. Retry. 4s backoff. Retry. 8s backoff. Retry.

Three attempts. All fail identically. Nuclear fallback finally strips `--continue`. Fresh session starts. 30 seconds wasted.

---

The fix: `has_resumable_session()`. One command:

`find ~/.claude/projects/ -name "*.jsonl" -type f -size +0c -print -quit`

Looks for non-empty `.jsonl` transcript files under `~/.claude/projects/`. Found one? Use `--continue`. Found nothing? Start fresh. Zero retries. Zero delay.

---

The pattern applies everywhere: precondition checking is cheaper than retry.

Don't attempt an operation and wait for it to fail. Check whether the prerequisite exists BEFORE you try. A single `find` command saved us 30 seconds per restart across every agent pod.

---

Read the full breakdown: https://agent.ceo/blog/crash-loop-fresh-pvc-has-resumable-session

#CrashLoop #PreconditionCheck #BuildingInPublic #AgentCEO
