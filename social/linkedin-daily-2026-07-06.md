Our CEO agent sent itself a status update. Then processed that update. Then sent itself another update about processing the first one.

40 messages later, it had burned its entire context window on a conversation with itself.

This is the inbox-flood anti-pattern, and it's the hardest bug to spot in multi-agent systems. Every individual message looks legitimate. The routing is correct. The processing logic works. There's no error anywhere. The agent is just... busy. Doing nothing useful.

The root cause: no sender-exclusion rule. When an agent generates a message that routes back to its own inbox, it processes it like any external task. That processing generates more messages. The loop is invisible because each cycle produces real-looking output.

Our fix is a flood gate — three rules:

1. Never process messages from yourself
2. Cap processing at N messages per cycle before yielding
3. Track message origin chains to detect indirect loops

The scariest production bugs aren't the ones that throw errors. They're the ones where everything works exactly as designed, and the design has a hole you never considered.

What feedback loops are hiding in your agent architecture?
