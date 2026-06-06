---
platform: twitter
status: draft
date: 2026-09-23
note: "Not Every Agent Action Is Worth Remembering"
---

## Thread: Not Every Agent Action Is Worth Remembering

We built an observation log for our AI agents. First version recorded everything -- every file read, every grep, every ls.

Within hours it was useless. Thousands of entries that said "agent looked at something." Zero signal.

---

So we filter ruthlessly. Our log only records actions that change state:

- Write, Edit
- git push, git commit
- kubectl apply
- test runs (pytest, jest)
- builds, npm install
- inter-agent messages

Read, grep, find, ls? Dropped. They don't change state.

---

For Bash commands, we filter by keywords. Only commands containing "git push", "kubectl", "pytest", "docker", "gh pr" get recorded.

A plain `ls` or `cat` is noise. It tells you nothing about what the agent accomplished.

---

The result: our observation log stays at 10,000 entries max. Every entry represents an actual action with a measurable outcome -- success or failure, with evidence.

That's a dataset a cybernetic learner can use. A firehose of file reads is not.

---

If you're building agent observability, start by deciding what NOT to record. The log that records everything teaches you nothing.

Full system deep dive: https://agent.ceo/blog/cybernetic-learning-loop-agents-write-own-rules

#AIAgents #Observability #BuildingInPublic #AgentCEO
