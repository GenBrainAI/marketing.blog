---
platform: linkedin
status: draft
date: 2026-10-18
note: "The Retry That Created the Problem It Solved"
---

## Post: The Retry That Created the Problem It Solved

We wrote a crash-resilient MCP wrapper script. 118 lines of bash: dual retry budgets, exponential backoff, PID tracking, signal forwarding, cleanup traps. Solid engineering. It caused a platform-wide outage.

The wrapper backgrounded the MCP server with `&`. In a non-interactive shell, bash gives backgrounded processes `/dev/null` as stdin. The MCP protocol runs over stdin. So the server read EOF, exited 0, and the wrapper dutifully restarted it. New server, same `/dev/null` stdin, same EOF, same exit.

The retry loop -- built specifically to fight startup races -- kept spawning servers that all got `/dev/null` stdin. Every retry reproduced the exact failure it was designed to prevent. The infrastructure meant to ensure reliability was the sole cause of the outage.

The cruel part: it worked perfectly in our terminals. Interactive shells give backgrounded processes real stdin. Non-interactive shells give `/dev/null`. We tested interactively, deployed non-interactively, and the behavioral difference was completely invisible until production.

Sometimes your safety net is the thing strangling you. The fix wasn't adding more retries or smarter health checks. It was understanding that `command &` means different things depending on where the shell is running.

Full breakdown: https://agent.ceo/blog/crash-resilient-mcp-wrapper-startup-race

#MCP #SelfInflictedBug #AIAgents #AgentCEO
