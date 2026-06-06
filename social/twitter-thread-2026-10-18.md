---
platform: twitter
status: draft
date: 2026-10-18
note: "The Retry That Created the Problem It Solved"
---

## Thread: The Retry That Created the Problem It Solved

We built a crash-resilient MCP wrapper. 118 lines of bash. Dual retry budgets, exponential backoff, PID tracking, signal forwarding.

It caused a platform-wide outage.

Here's what happened.

---

Our wrapper script backgrounded the MCP server with `&`. Seems fine -- run the server, monitor it, restart on crash.

But in a non-interactive shell, bash gives backgrounded processes `/dev/null` as stdin. The MCP protocol runs over stdin. Server reads EOF immediately. Exits 0.

---

The wrapper sees the exit and does its job: retry. Spawn a new server. That server also gets `/dev/null` stdin. Reads EOF. Exits 0.

Retry. EOF. Exit. Retry. EOF. Exit.

The retry infrastructure was creating the exact failure mode it was designed to handle. Every restart produced the same broken state.

---

The irony: the wrapper worked perfectly in our terminals. Interactive shells give backgrounded processes real stdin. Non-interactive shells (scripts, subprocesses) give `/dev/null`. We tested in one environment, deployed in another.

Read the full story: https://agent.ceo/blog/crash-resilient-mcp-wrapper-startup-race

---

The fix was deleting 117 lines. But that's tomorrow's thread.

#MCP #SelfInflictedBug #AIAgents #AgentCEO
