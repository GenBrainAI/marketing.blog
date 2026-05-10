---
platform: twitter
scheduled_date: 2026-09-25
thread_length: 7
day: 138
---

**Tweet 1/7:**
We tried 4 NATS JetStream configurations before finding one that doesn't lose messages under load. 138 days of real production traffic. Here's what we learned.

**Tweet 2/7:**
Attempt 1: Default stream, single replica, file storage. Worked great until the server restarted during a burst. 23 task assignments vanished. Agents sat idle for 2 hours before anyone noticed.

**Tweet 3/7:**
Attempt 2: Added replicas (R3) for durability. Messages survived restarts. But consumer ack policy was AckNone. Agents crashed mid-processing and messages were marked delivered. Same result: lost work.

**Tweet 4/7:**
Attempt 3: Switched to AckExplicit. Agents ack only after completing the task and committing to git. Unacked messages redeliver after 30 seconds. No more lost work. But we hit duplicate processing during slow tasks.

**Tweet 5/7:**
Attempt 4 -- the one that stuck: AckExplicit + MaxDeliver(3) + deduplication window of 5 minutes + idempotent task handlers. Messages survive crashes. Duplicates get caught. Failed tasks retry 3 times then dead-letter.

**Tweet 6/7:**
The lesson: NATS JetStream is powerful but the defaults assume you'll configure durability yourself. "At least once" delivery means nothing if your consumers don't ack correctly. The ack policy IS your reliability policy.

**Tweet 7/7:**
4 attempts, 3 outage incidents, 1 configuration that's run GenBrain AI flawlessly for 11 weeks straight. Zero lost messages. Full NATS stream config and rationale at agent.ceo

Read more: https://agent.ceo/blog/nats-stream-configuration-lessons
