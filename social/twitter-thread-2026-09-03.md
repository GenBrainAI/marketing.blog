---
platform: twitter
status: draft
date: 2026-09-03
note: "Wednesday tutorial — 6 steps to self-running content calendar"
---

## Thread: Build a Self-Running Content Calendar in 6 Steps

Your AI agent can run its own content calendar. No scheduling tools. No databases. No human reminders.

6 steps:

---

Step 1: Put the calendar in the agent's instructions. 4 lines in CLAUDE.md. Monday = deep-dive. Wednesday = tutorial. Friday = product update. The agent reads this on every wakeup. It cannot forget to check a file it already reads.

---

Step 2: Source topics from git log. Agent finds feat: commits since the last blog post. Cross-references against existing posts. Uncovered feature = next topic. Topics stay current because the codebase stays current.

---

Step 3: Give a standing mandate. "You NEVER go idle. If no assigned tasks, execute the content calendar." The agent treats content as default work, not optional work.

---

Step 4: Dual-format output. Every blog post ships as .md for the content repo AND .mdx for the website. One research pass, two deliverables. Different frontmatter schemas, handled automatically.

---

Step 5: Generate social content alongside blog posts. LinkedIn post + Twitter thread from the same material. The blog is the source of truth for social — no separate planning needed.

---

Step 6: Quality gates. MDX verification rejects bare angle brackets. Subagent review catches fabricated claims. Cross-reference check prevents duplicate topics.

Full tutorial: agent.ceo/blog/build-autonomous-content-calendar-ai-agent

#AIAgents #ContentAutomation #AgentCEO
