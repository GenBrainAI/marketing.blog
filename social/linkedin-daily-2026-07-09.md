Your agent was working. Then its tools vanished.

Mid-session, no warning — tools that were available 30 seconds ago return "not found." The agent can't call its knowledge base, can't search wiki, can't access half its capabilities. But it keeps running, silently degraded.

This is the most common failure mode we see in production MCP agent systems: tool disconnections that don't throw errors.

We just published our 5-step diagnostic checklist for debugging MCP disconnections:

1. Check tool registration — is the tool actually registered upstream?
2. Check scope conflicts — are user-level and local configs contradicting each other?
3. Check the whitelist — is a restrictive allow-list filtering tools before the agent sees them?
4. Check crash recovery — did the MCP server restart without re-registering tools?
5. Check for silent errors — are failures being swallowed instead of surfaced?

This is how we found that 17 KB tools were being stripped from every agent at startup. No logs. No alerts. Just agents operating at half capacity.

The post includes the exact diagnostic commands, config patterns to watch for, and the 65-test suite we wrote to prevent regression.

Read the full tutorial: https://agent.ceo/blog/debug-mcp-disconnections-ai-agents
