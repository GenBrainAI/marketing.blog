---
platform: twitter
status: draft
date: 2026-08-22
note: Friday case study — content pipeline workflow thread
---

## Thread: How an AI agent writes 10 blog posts with zero human editors

Our marketing agent wrote 10 blog posts in 2 weeks. No human touched a single draft. Here is every step:

---

1/ WAKE UP + CHECK INBOX. Agent starts on cron. Pulls latest from git. Checks TMS inbox for assigned tasks. If no tasks, falls through to the content standing mandate.

---

2/ READ GIT LOG. Runs git log on the engineering repo. Finds new feat: commits since the last blog post. New feature merged = new blog post to write. Source material is the actual code diff.

---

3/ WRITE BLOG POST. Spawns a fresh subagent with the content brief. Subagent writes 800-1300 words with full frontmatter, internal links, CTA. Main agent reviews for quality.

---

4/ DUAL FORMAT. Same content, two files. .md with slug, cluster, relatedPosts. .mdx with quoted date, author field, no H1. Different frontmatter schemas, different parsing rules.

---

5/ VERIFY + COMMIT + PR. Regex checks the .mdx for bare angle brackets that break JSX. Commits .md to marketing branch. Creates PR with .mdx on website repo. Writes daily social content.

Result: 10 posts, 30+ social files, 6 PRs, 0 human editors.

agent.ceo/blog/ai-marketing-agent-content-pipeline-case-study #ContentAutomation #AIAgents #BuildInPublic
