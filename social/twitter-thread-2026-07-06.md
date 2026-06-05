1/ Our CEO agent burned an entire context window processing its own status messages.

No errors. No crashes. Just an AI agent having a very productive conversation with itself about how productive it was being.

Here's the story:

2/ The CEO agent checks its inbox, processes tasks, and sends status updates.

One status update got routed back to its own inbox. It processed the update. Processing generated a new status message. That message hit the inbox. Repeat.

40 cycles. Zero useful work. 100% context consumed.

3/ Every message in the chain looked legitimate:

"Task status: checking inbox" -> processes -> "Task status: processed 1 message" -> processes -> "Task status: processed 1 message about processing"

No error to catch. No anomaly to detect. Just a perfectly functioning system doing nothing.

4/ The fix: an inbox-flood gate with three rules.

Rule 1: Skip messages where sender = self. Always.
Rule 2: Process max N messages per cycle, then yield. Prevents any flood from consuming the full window.
Rule 3: Track message chains. If origin traces back to self through any path, drop it.

5/ Why this bug is uniquely dangerous in AI agent systems:

Traditional software loops spike CPU or memory. You get alerts.

AI agent loops spike token usage and context. They look like work. Your monitoring says "agent is active and processing messages." Everything green. Everything wrong.

6/ We're publishing the full write-up tomorrow — this bug plus two more silent failure modes we found and fixed in production.

NATS connections dying silently. MCP proxies failing on transient errors. And this inbox flood.

Details at https://agent.ceo
