---
platform: linkedin
status: draft
date: 2026-10-14
note: "Your Agent Finished One Task and Quit. It Had Three More."
---

## Post: Your Agent Finished One Task and Quit. It Had Three More.

AI agents don't have intrinsic motivation. They finish a task, the session ends, and they sit idle -- even when three more tasks are waiting in the TMS.

We hit this constantly. An agent completes a code review, calls it done, and the CLI exits. Meanwhile, assigned tasks pile up. The agent doesn't know it should keep going, because nothing told it to check.

The gap: the agent decides "I'm done" before the system checks "but are you actually done?"

Our fix: a stop hook that fires every time an agent tries to exit. It queries the TMS for tasks in `assigned`, `accepted`, or `in_progress` status. If work exists, the hook returns `{"decision": "block", "reason": "..."}` with exit code 2. The agent stays alive, and the prompt watchdog re-injects the next task.

Why not block forever? We cap it at 3 blocks per session. The counter lives at `/tmp/stop_block_count` and resets when the session starts. If an agent can't make progress after 3 blocks, the task is likely stuck on an external dependency. Let it restart with fresh context rather than trapping it in a loop it can't escape.

Three blocks. Then the leash releases. Simple, but it changed our task completion rate overnight.

Read more about the prompt watchdog: https://agent.ceo/blog/prompt-watchdog-daemon-keeps-agents-working

#AIAgents #AutonomousLoop #TaskManagement #AgentCEO
