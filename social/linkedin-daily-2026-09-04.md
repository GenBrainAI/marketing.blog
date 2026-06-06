---
platform: linkedin
status: draft
date: 2026-09-04
note: "Thursday engagement — sourcing topics from git"
---

## Post: Source Topics from Git, Not a Backlog

Content backlogs are where autonomous agents go to produce irrelevant work.

The problem: a human writes a list of topics in week 1. By week 3, half the topics are stale because the product shipped new features that nobody added to the list. The agent dutifully writes about last month's priorities.

The fix is simple. The agent runs git log. It finds commits tagged with "feat:" since the last blog post. It cross-references against existing posts. Any feature without a post becomes the next topic.

When features run out — and they do run out — the agent pivots to meta-analysis. How did the system change over the last sprint? What patterns emerged across multiple features? These posts write themselves because the raw material is in the commit history.

This approach has a structural advantage: topics cannot go stale because they are generated from the current state of the codebase. The backlog is the git log. It updates itself every time someone pushes code.

No planning meetings. No editorial calendars. Just the repo.

https://agent.ceo/blog/build-autonomous-content-calendar-ai-agent

#AIAgents #ContentStrategy #BuildingInPublic #AgentCEO
