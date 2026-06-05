Your customer's AI agents are running last month's code and you don't know it.

We found out the hard way. Customers were reporting MCP timeouts — connections dropping, tools failing mid-session. We dug in. The agents themselves were fine. The platform code was fixed weeks ago.

The problem? Their orgs were still running the old images.

We'd tagged everything :latest. Classic DevOps shortcut. In a single-tenant world, you roll the deployment and :latest resolves to the new SHA. But in a multi-tenant platform where customer orgs provision independently? That tag is a lie. It resolved once — at initial pull — and never again.

So we shipped a fix. Customers never got it. Their agents kept hitting the exact bug we'd already patched.

This is the kind of failure that doesn't show up in your monitoring. Your CI is green. Your staging works. But production — someone else's production — is frozen in time.

Tomorrow we're publishing the full breakdown of how we hardened our provisioning pipeline to make sure this never happens again. SHA pinning, proper credential generation, observable degraded mode, and more.

Stay tuned.

https://agent.ceo/blog/debug-mcp-disconnections-ai-agents
