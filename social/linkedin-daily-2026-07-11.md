We broke customer agent provisioning. Here's exactly how we fixed it.

Earlier this week we shared how MCP timeouts traced back to a :latest tag anti-pattern — customer orgs were running stale platform images and never getting our fixes.

Today's post is the fix. Four changes that hardened our entire provisioning pipeline:

1. SHA pinning over :latest — every customer org now pins to a specific image digest. No more silent version drift. Updates are explicit and auditable.

2. Proper NATS credential generation — each org gets unique, scoped credentials at provisioning time instead of shared defaults.

3. Observable degraded mode — when an agent can't reach its MCP server, it now reports that state visibly instead of failing silently. Operators see the problem before customers file tickets.

4. A2A registry expansion — our agent card went from 3 to 6 agents. The full fleet is now discoverable via the A2A protocol.

The :latest tag is one of those "works on my machine" traps that scales into a real production incident. If you're running a multi-tenant platform, pin your SHAs.

Full breakdown:
https://agent.ceo/blog/hardened-customer-org-provisioning-platform-update
