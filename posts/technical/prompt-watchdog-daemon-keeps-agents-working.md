---
title: "The Prompt Watchdog: How a Daemon Keeps AI Agents Working"
slug: "prompt-watchdog-daemon-keeps-agents-working"
date: 2026-09-22
category: technical
cluster: "architecture-deep-dives"
tags: [prompt-watchdog, idle-detection, autonomous-agents, daemon, tmux, deep-dive]
description: "Deep-dive into the prompt watchdog -- a background daemon that monitors AI agent sessions, detects idle states, and injects prompts to keep agents productive."
relatedPosts:
  - /blog/human-gate-timeout-agent-fleet-idle-incident
  - /blog/anatomy-agent-wakeup-cycle-first-60-seconds
  - /blog/ralph-loop-one-task-per-session-anti-drift
  - /blog/how-to-build-self-pacing-autonomous-loops
  - /blog/autonomous-loop-stop-hook-gate-ai-agents
---

# The Prompt Watchdog: How a Daemon Keeps AI Agents Working

Here is the dirty secret of autonomous AI agents: they stop.

Not crash. Not error out. They just... finish a task, print a summary, and sit at an interactive prompt forever. The cursor blinks. The pod burns compute. The agent waits for input that never comes — and in a cyborgenic organization with no human at the keyboard, it waits forever.

At GenBrain AI, we run a fleet of Claude Code agents inside tmux sessions on Kubernetes. Each agent has a [stop hook](/blog/autonomous-loop-stop-hook-gate-ai-agents) that fires when the agent tries to exit -- but the stop hook only fires on exit attempts. An agent that finishes its work and parks at the `❯` prompt never triggers it. Without intervention, that agent sits idle indefinitely.

The prompt watchdog is a Python daemon that bridges this gap. It runs inside the same pod as the agent, monitors the tmux session every 15 seconds, detects idle states, and injects prompts to keep the agent working. The difference between a one-task agent and a continuous one.

## How It Detects Idle

The watchdog captures the tmux pane content via `tmux capture-pane` on a 15-second interval (`CHECK_INTERVAL_SECONDS = 15`) and answers three questions: Is the agent at a prompt? Is it actively working? Is it stuck in a blocking dialog?

**Prompt detection** (`is_at_prompt`) looks for patterns that indicate the agent is waiting for input:

- `^❯\s*$` -- an empty prompt, nothing typed
- `^❯\s+` -- a prompt with partial input (stale text)
- Strings like "bypass permissions on" or "shift+Tab to cycle" -- TUI elements that appear only at an interactive prompt

**Activity detection** (`is_actively_working`) scans the last 10 lines for signs of life: "Ideating", "Thinking", "Running...", "Compacting", "Auto-compact: N%", token download/upload counters, or "thought for". If any of these appear, the agent is mid-task and the watchdog backs off.

**Prompt-line extraction** (`extract_prompt_line`) is a subtlety that matters. Claude Code's TUI displays dynamic status lines -- auto-compact percentages, token counters, thinking timers -- that change constantly. If the watchdog used the full screen content for idle comparison, these status updates would reset the idle timer every time they ticked. Instead, it extracts only the actual prompt line, skipping status lines entirely. This way, an agent sitting at `❯` with a spinning token counter still registers as idle.

## Exponential Backoff: Not Too Eager, Not Too Passive

The first time the watchdog detects an idle agent, it waits 5 minutes (`IDLE_BASE_SECONDS = 300`) before intervening. Why not immediately? Because agents sometimes pause briefly between steps -- reading a file, waiting for a tool response, or thinking through an approach. A 5-minute window filters out these false positives.

If the agent goes idle again after being nudged, the threshold increases by 3x (`IDLE_BACKOFF_MULTIPLIER = 3`):

- First idle: 300 seconds (5 minutes)
- Second idle: 900 seconds (15 minutes)
- Third idle: 2,700 seconds (45 minutes)
- Fourth and beyond: capped at 7,200 seconds (2 hours) via `IDLE_CAP_SECONDS`

The formula: `min(IDLE_BASE_SECONDS * (IDLE_BACKOFF_MULTIPLIER ** attempt), IDLE_CAP_SECONDS)`.

After `MAX_AUTO_CONTINUES = 3` attempts, the watchdog stops injecting prompts and sends a notification to the human. If three nudges did not get the agent productive, something is genuinely wrong -- maybe a blocker, maybe a broken tool, maybe an edge case the agent cannot handle. Escalation, not infinite retries.

## Prompt Injection: The tmux Paste-Buffer Trick

Sending text to a tmux session sounds trivial. It is not. The naive approach -- `tmux send-keys "check your inbox"` -- sends characters one at a time. For short strings, this works. For multi-line prompts, it is unreliable: characters arrive out of order, special characters get interpreted as tmux key bindings, and long messages get truncated.

The watchdog uses a paste-buffer approach instead:

1. `tmux send-keys C-u` -- clears any stale text on the input line
2. Writes the prompt message to a temporary file
3. `tmux load-buffer &lt;tempfile&gt;` -- loads the message into tmux's paste buffer
4. `tmux paste-buffer` -- pastes the entire message atomically into the session
5. `tmux send-keys Enter` -- submits the prompt

This delivers the full message reliably, regardless of length or special characters. The `C-u` at the start is important: if the agent had partial input on the line (a half-typed command, a stale error message), clearing it first prevents the injected prompt from appending to garbage.

## The Human Gate

Autonomous prompt injection is powerful. It is also dangerous if a human is actively working in the session.

Every agent session is accessible via ttyd (a web terminal). When a human is interacting with the agent directly, the watchdog must not inject prompts -- that would interrupt the conversation and overwrite what the human is typing.

The watchdog checks for human activity via `is_human_engaged()`. It reads the tmux `client_activity` timestamp, which updates whenever a human types in the web terminal. If that timestamp is within `CONVERSATION_TIMEOUT = 120` seconds, prompt injection is suppressed. It also falls back to a legacy `/tmp/last_human_interaction` file.

The 120-second timeout was originally 900 seconds (15 minutes). We reduced it after the [fleet idle incident](/blog/human-gate-timeout-agent-fleet-idle-incident), where agents sat idle for extended periods because the human gate was too conservative -- a brief human check-in would suppress injection for 15 minutes, during which the agent had nothing to do.

## Priority Wakeups: Bypassing the Gate

The human gate creates a problem: what if a task gets assigned to an idle agent while a human recently checked its terminal? The agent has work to do, but the gate blocks injection for two more minutes.

Priority wakeups solve this. When NATS delivers a task to an agent's inbox, the delivery mechanism creates a `/tmp/wakeup_pending` file. The watchdog checks for this file on every cycle. When it finds one, it injects the wakeup prompt immediately, bypassing the human gate entirely. Assigned work should never wait.

The wakeup message includes the sender's name for context. This fix was added directly in response to the fleet idle incident, where agents had tasks in their inbox but the human gate was blocking injection.

## Blocking Dialog Auto-Dismiss

There is one more failure mode the watchdog handles: TUI dialogs that block the entire session until a human presses a key.

Claude Code occasionally surfaces dialogs like "Turn on usage credits", "Turn on extra usage", or satisfaction surveys ("how is claude doing this session"). In an interactive session, these are minor -- you press Enter and move on. In an autonomous agent session with no human watching, they are catastrophic. The agent cannot proceed, the prompt watchdog's idle detection sees a blocked session (not an idle prompt), and the agent sits frozen until someone notices.

The watchdog detects these known dialog patterns in the tmux pane content and auto-presses Enter or the appropriate key to dismiss them. A usage credits popup that would block an unattended agent indefinitely gets dismissed in 15 seconds.

## Loop Control Modes

Not every agent should be nudged the same way. The watchdog reads a loop control configuration that sets one of three modes:

- **`paused`**: Skip all injection. The agent is intentionally stopped -- maybe for maintenance, maybe to save costs during off-hours.
- **`task-only`**: Re-inject the specific directive if the agent goes idle. This is single-task mode: the agent works on one assigned task, and if it drifts or finishes prematurely, it gets the original directive again.
- **`active`**: Normal operation with exponential backoff idle detection. The agent is part of the active fleet and should continuously pull work from its inbox.

## Why Not Just Use Cron?

The watchdog needs state -- idle duration, backoff attempt count, last prompt line for comparison. A stateless cron job would re-detect idle from scratch every cycle. The human gate needs real-time timestamp checks. The blocking dialog logic needs to read the tmux pane and send context-appropriate keystrokes. This is session supervision, not job scheduling.

## The Bigger Picture

The prompt watchdog is one piece of a larger [autonomous loop architecture](/blog/how-to-build-self-pacing-autonomous-loops). The [stop hook](/blog/autonomous-loop-stop-hook-gate-ai-agents) prevents premature exits. The [wakeup cycle](/blog/anatomy-agent-wakeup-cycle-first-60-seconds) bootstraps agent state on startup. The [Ralph loop pattern](/blog/ralph-loop-one-task-per-session-anti-drift) enforces one-task-per-session discipline to prevent drift.

Together, these components create agents that start reliably, work continuously, stay on task, and recover from idle states without human intervention. The prompt watchdog is the component that turns "works once" into "works always."

---

**GenBrain AI builds autonomous agent organizations at [agent.ceo](https://agent.ceo).** Our fleet of AI agents runs 24/7, managed by the same infrastructure described in this post. If you are building autonomous agents and want to stop babysitting idle sessions, [check out the platform](https://agent.ceo).
