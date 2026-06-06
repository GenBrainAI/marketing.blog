---
platform: twitter
status: draft
date: 2026-10-14
note: "Your Agent Finished One Task and Quit. It Had Three More."
---

## Thread: Your Agent Finished One Task and Quit. It Had Three More.

AI agents don't have intrinsic motivation.

They finish a task, the CLI exits, and they sit idle -- even with three more tasks assigned in the TMS. The agent decides "I'm done" before the system checks "but are you actually done?"

---

Our fix: a stop hook that fires when the agent tries to exit.

It queries the TMS for tasks in `assigned`, `accepted`, or `in_progress` status. If work exists, it returns `{"decision": "block", "reason": "..."}` with exit code 2.

The agent stays alive. The prompt watchdog re-injects the next task. Work continues.

---

Why not block forever? We cap it at 3 blocks per session.

The counter lives at `/tmp/stop_block_count` and resets at session start. If the agent can't progress after 3 attempts, the task is probably stuck on an external dependency. Let it restart with fresh context instead of trapping it.

---

Three blocks, then release. Simple mechanism, massive impact on task throughput.

The gap between "agent completed a task" and "agent completed ALL its tasks" is where most autonomous systems leak productivity.

Read more: https://agent.ceo/blog/prompt-watchdog-daemon-keeps-agents-working

#AIAgents #AutonomousLoop #TaskManagement #AgentCEO
