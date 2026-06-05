1/ We shipped 199 MCP tools to our AI agents. They could only see 96 of them.

The other 103 tools — including all 17 KB/wiki tools — were being silently stripped at every startup.

No errors. No logs. Here's how it happened:

2/ Our MCP config has two scopes: user-level and local (project-level). Both can define tool whitelists.

The problem: local scope had a whitelist that only included "approved" tools. Any tool not explicitly listed got dropped before the agent ever saw it.

Our KB tools weren't on the list. Gone.

3/ The agents never complained. Why would they? You can't request a tool you don't know exists.

They compensated by falling back to raw file reads and grep commands. Functional, but like navigating a library by opening random books instead of checking the catalog.

4/ How we caught it: an agent tried to call wiki_search and got "tool not found." Manual investigation showed the tool was registered upstream but missing from the agent's available tools list.

We diffed registered vs. available. 103 tools missing. All filtered by the same whitelist.

5/ The fix: unified scope resolution + whitelist that adds restrictions instead of defining the universe.

65 tests covering scope conflicts, whitelist behavior, and crash recovery.

Tomorrow we publish the full 5-step diagnostic checklist for debugging MCP tool failures mid-session.

6/ Running AI agents with MCP tooling? This class of bug — silent config conflicts — is waiting for you.

Full story and diagnostic guide dropping tomorrow at https://agent.ceo

Follow the build.
