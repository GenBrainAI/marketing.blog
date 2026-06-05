1/ Your AI agent's tools just vanished mid-session.

No error. No log. Tools that worked 30 seconds ago now return "not found."

We wrote the debugging guide we wish we'd had. 5 steps to diagnose MCP disconnections in production:

2/ Step 1: Check tool registration.

Is the tool actually registered with the MCP server? Don't assume — verify. We found tools that were defined in config but never made it through the registration handshake.

Start here. Everything else assumes the tool exists upstream.

3/ Step 2: Check scope conflicts.

MCP configs can live in two places: user scope and local/project scope. When both define tool lists, the merge behavior is not what you expect.

We had a local whitelist silently overriding user-scope tool definitions. 103 tools filtered out. Zero warnings.

4/ Step 3: Check the whitelist.

A tool whitelist that defines the allowed universe (instead of restricting a dangerous subset) will silently drop every tool you forget to add.

This is how 17 KB/wiki tools got stripped from every agent at startup. The whitelist was "secure." It was also wrong.

5/ Step 4-5: Check crash recovery and silent errors.

MCP server restarts don't always re-register tools. And many MCP implementations swallow connection errors instead of surfacing them.

Both failure modes look the same: tools that were there, then weren't.

6/ Full 5-step diagnostic checklist with commands, config examples, and the 65-test regression suite:

https://agent.ceo/blog/debug-mcp-disconnections-ai-agents

We run 6 AI agents 24/7 at GenBrain AI. This is how we keep them operational. Follow the build at https://agent.ceo
