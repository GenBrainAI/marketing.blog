---
platform: linkedin
status: draft
date: 2026-09-23
note: "Not Every Agent Action Is Worth Remembering"
---

## Post: Not Every Agent Action Is Worth Remembering

When we built the observation log for our AI agents, our first instinct was to record everything. Every file read, every grep, every ls. Total recall.

It was useless. Within hours the log was flooded with pure read operations -- noise that told us the agent looked at something, not that it did anything. You can't learn from "agent read a file." You learn from "agent pushed code and the build broke."

So we filter. Our observation log only records actions that change state: Write, Edit, git push, git commit, kubectl apply, test runs, builds, npm install, inter-agent messages. For Bash commands specifically, we filter by keywords -- only commands containing "git push", "kubectl", "pytest", "docker", "gh pr", and similar get recorded. A plain ls or cat is noise and gets dropped.

The result: our observation log stays at 10,000 entries max. Every single entry represents an actual action with a measurable outcome -- success or failure, with evidence. That's the dataset a cybernetic learner can actually use. No signal buried under ten thousand file reads.

If you're building agent observability, start by deciding what NOT to record. The log that records everything teaches you nothing.

Deep dive on the full system: https://agent.ceo/blog/cybernetic-learning-loop-agents-write-own-rules

#AIAgents #Observability #BuildingInPublic #AgentCEO
