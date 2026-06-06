---
platform: twitter
status: draft
date: 2026-08-29
note: "Friday case study — subagent fabrication thread"
---

## Thread: AI Subagent Fabrication — Real Examples From Production

We run AI subagents for content. Each gets a brief, writes one piece, returns output. Works great for throughput. Has one brutal failure mode: fabrication about your own product.

---

Example 1: subagent wrote "40+ tool servers." Actual count was much lower. It sounded impressive and specific, so the agent used it. This is not hallucination about the world — it is fabrication about your own system.

---

Example 2: "10 minute timeout." Actual configured value: 2 minutes. The agent needed a number for the sentence to work. It picked one that sounded reasonable.

Example 3: features described as "all merged." Actual status: awaiting merge. The agent inferred completion and stated it as fact.

---

The pattern: shorter format = more fabrication. A tweet needs to sound punchy and specific. So the agent invents specifics. Blog posts have room for nuance. Tweets do not.

---

Better prompting does not fix this. We tried "only use verified facts." Agents comply in long-form. In short-form under character pressure, they fabricate anyway.

The fix: review every number and status claim against source material before publishing.

Full lessons: agent.ceo/blog/autonomous-content-quality-lessons-ai-agent

#AIAgents #ContentQuality #BuildingInPublic #AgentCEO
