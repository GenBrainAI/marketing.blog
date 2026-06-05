Your AI agent just lost access to 17 tools and nobody noticed.

We ship 199 MCP tools across 6 production agents at GenBrain AI. Last week we discovered our agents could only see 96 of them. The other 103 — including all 17 knowledge base and wiki tools — were being silently stripped at startup.

No errors. No warnings. Agents just... never knew those tools existed.

The cause: a whitelist configuration that was supposed to restrict dangerous tools was also filtering out every KB tool we'd built. The whitelist checked tool names against an allow-list, and our knowledge base tools weren't on it. So they vanished. Every agent, every session, every restart.

The worst part? Agents can't miss what they never see. They worked around the gap by falling back to raw file reads and grep. Slower, less accurate, but functional enough that nobody flagged it.

We found the root cause, fixed it, and wrote 65 tests to make sure it never happens again.

Tomorrow: we're publishing our full 5-step diagnostic checklist for debugging MCP disconnections mid-session. If you're running AI agents with MCP tooling, you'll want this one.

Follow the build: https://agent.ceo
