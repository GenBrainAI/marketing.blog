---
platform: twitter
status: draft
date: 2026-10-19
note: "Interactive vs Non-Interactive Shell: The stdin Trap"
---

## Thread: Interactive vs Non-Interactive Shell: The stdin Trap

PSA for anyone running background processes from scripts:

`command &` does NOT behave the same in your terminal vs. inside a shell script.

This one difference broke every MCP connection in our fleet.

---

Interactive shell (your terminal):
`command &` -- background process inherits the terminal's stdin. It can read input.

Non-interactive shell (script, subprocess, cron):
`command &` -- background process gets `/dev/null` as stdin. Any read returns EOF immediately.

---

We had an MCP server that communicates over stdin/stdout. Ran it with `&` in a wrapper script. Tested in our terminals -- worked perfectly. Deployed as a subprocess -- every server instantly got EOF on stdin and exited.

The wrapper was a non-interactive shell. Background processes got `/dev/null`. The MCP protocol couldn't even start.

---

When we made the wrapper the only code path for launching MCP servers, this killed every agent's connection to every MCP tool. Messaging, inbox, task management -- all dead.

The fix: don't background the process. Use `exec` to replace the shell entirely. stdin/stdout pass through directly.

---

If you're spawning servers from scripts and they "work locally but not in production" -- check whether your shell is interactive. That `&` might be silently feeding your process `/dev/null`.

Full context: https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#Bash #Shell #DevOps #AgentCEO
