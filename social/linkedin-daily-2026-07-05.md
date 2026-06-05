Your AI agent's NATS connection is configured with "unlimited retries." It will still die.

We found this the hard way. Our NATS client had max_reconnect_attempts set to -1 — the documented value for "never stop trying." The server went down for maintenance, came back up, and the client just... sat there. Connected to nothing. No errors. No reconnection. Silent death.

The problem: "unlimited retries" means "unlimited attempts during the initial reconnection window." Once the client transitions to a permanently closed state, retries stop. The setting doesn't cover that case. Nothing in the logs tells you it happened.

We now run a watchdog that checks actual connection state every 30 seconds. Not "is the config correct" — "is data flowing right now." When it detects a permanent close, it tears down the client and rebuilds from scratch.

The infrastructure your agents depend on will fail in ways the documentation doesn't cover. The question isn't whether your connections are configured correctly. It's whether anything is watching them after configuration.

What's monitoring your agent connections right now — config values, or actual state?
