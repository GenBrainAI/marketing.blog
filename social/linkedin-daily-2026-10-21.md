---
platform: linkedin
status: draft
date: 2026-10-21
note: "118 Lines of Wrapper Replaced by 1 Line of exec"
---

## Post: 118 Lines of Wrapper Replaced by 1 Line of exec

We had a crash-resilient MCP wrapper script. 118 lines of bash. Dual retry budgets with separate counters for fast crashes vs. slow failures. Exponential backoff. Time-based exit classification to distinguish startup failures from runtime crashes. PID tracking, signal forwarding, cleanup traps.

We replaced all of it with:

`exec python -m mcp_servers.agent_hub_mcp 2>> /tmp/log`

`exec` replaces the shell process with python. No subshell, no wrapper, no background process. stdin and stdout pipes pass through directly to the python process. SIGTERM reaches python without signal forwarding. There's nothing to clean up because there's no wrapper process.

What about crash recovery? The MCP server handles its own reconnection logic internally. Claude Code has built-in MCP reconnection. Our 118-line wrapper was duplicating crash recovery that already existed at two other layers in the stack.

Worse, the wrapper was actively harmful. Backgrounding with `&` broke stdin in non-interactive shells -- the exact bug that caused a platform-wide outage. The retry loop amplified failures instead of recovering from them. The complexity of the script obscured the root cause for days.

Connection establishment dropped from timing out at 30 seconds to completing in 1.3 seconds. By deleting code.

The instinct to add resilience layers is strong. But sometimes the most resilient thing you can do is remove the layer that's creating the fragility.

Full post: https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#SimplifyCode #LessIsMore #MCP #AgentCEO
