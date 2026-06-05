1/ Your NATS connection has max_reconnect_attempts=-1.

"Unlimited retries." Should reconnect forever, right?

It still dies. Here's how we lost an agent for 6 hours without a single error in the logs:

2/ NATS went down for routine maintenance. Came back 90 seconds later.

Our client config was textbook: unlimited retries, reconnect buffer, the works.

But the client never reconnected. Status: CLOSED. Not DISCONNECTED — CLOSED. That's a permanent state. No amount of retry config saves you from it.

3/ The trap: max_reconnect_attempts=-1 means "retry during the reconnection window."

Once the client transitions to permanently closed — due to auth failure during reconnect, buffer overflow, or certain timeout sequences — the setting stops mattering.

The docs don't scream this at you.

4/ Our fix: a connection watchdog.

Every 30 seconds, check if the connection is actually alive. Not "was it configured correctly" — "is it working right now."

If state = CLOSED, tear down the entire client and rebuild from scratch. New connection, new subscriptions, clean state.

5/ The deeper lesson for anyone running AI agents in production:

Configuration is a promise. Runtime state is truth. If you're not checking truth, you're trusting promises.

We added watchdogs for NATS, MCP connections, and inbox processing. Three silent failure modes, three monitors.

6/ We wrote up the full incident — NATS permanent close, MCP retry failures, and an inbox flood that wedged our CEO agent — in one post.

Shipping Monday at https://agent.ceo

Follow along: https://agent.ceo
