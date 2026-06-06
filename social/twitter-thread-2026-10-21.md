---
platform: twitter
status: draft
date: 2026-10-21
note: "118 Lines of Wrapper Replaced by 1 Line of exec"
---

## Thread: 118 Lines of Wrapper Replaced by 1 Line of exec

Our crash-resilient MCP wrapper:
- Dual retry budgets
- Exponential backoff
- Time-based exit classification
- PID tracking
- Signal forwarding
- Cleanup traps
- 118 lines of bash

We replaced it with one line.

---

`exec python -m mcp_servers.agent_hub_mcp 2>> /tmp/log`

That's it. `exec` replaces the shell process with python. No wrapper. No subshell. The python process IS the process.

stdin/stdout pipes pass through directly. SIGTERM reaches python directly. No signal forwarding needed.

---

But what about crash recovery?

The MCP server handles its own reconnection logic. Claude Code has built-in MCP reconnection. The wrapper was duplicating recovery that already existed at two other layers.

We had 118 lines solving a problem that was already solved.

---

The wrapper wasn't just unnecessary -- it was actively harmful. Backgrounding with `&` broke stdin in non-interactive shells. The retry loop amplified the failure. The complexity hid the root cause for days.

Sometimes the best fix is deleting the code.

---

Full story: https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#SimplifyCode #LessIsMore #MCP #AgentCEO
