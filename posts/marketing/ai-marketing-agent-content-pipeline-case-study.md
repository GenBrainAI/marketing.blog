---
title: "How an AI Marketing Agent Shipped 10 Blog Posts in Two Weeks"
slug: "ai-marketing-agent-content-pipeline-case-study"
date: 2026-08-22
category: marketing
cluster: building-in-public
tags: [content-pipeline, marketing-agent, building-in-public, case-study, automation]
description: "Real numbers from our AI marketing agent: 10 blog posts, 30+ social files, dual-format publishing, zero human editing. Here's the workflow."
relatedPosts:
  - /blog/how-the-marketing-agent-works-building-in-public
  - /blog/automated-content-pipeline-cyborgenic
  - /blog/content-engine-scale-case-study-cyborgenic
  - /blog/platform-update-august-2026-monthly-roundup
  - /blog/incident-learning-loop-ai-agent-platform
---

# How an AI Marketing Agent Shipped 10 Blog Posts in Two Weeks

Between August 1 and August 20, our marketing agent wrote 10 blog posts, generated 30+ social media files, created 6 pull requests on the website repo, and published every piece in dual format -- all without a single human keystroke in the drafting process. No editorial meetings. No content briefs. No brainstorming sessions. Just an autonomous agent reading git commits and turning engineering work into publishable content.

Here are the real numbers, the real workflow, and the honest limitations.

## The Output

In 20 days, the marketing agent produced:

- **10 blog posts**, each between 800 and 1,300 words, with full frontmatter, internal cross-links, and a call to action
- **Dual-format publishing**: every post exists as a `.md` file in the marketing.blog repo and a `.mdx` file formatted for the Next.js website repo
- **30+ social media drafts** across LinkedIn and Twitter, written daily to promote the posts
- **6 pull requests** opened on the agent-ceo-website repo, each containing verified `.mdx` content ready for merge
- **Zero human edits** between raw commit data and the final draft

The topics were not chosen from a content calendar someone wrote. They came directly from `git log`. The agent scanned recent commits, cross-referenced them against already-published content, identified gaps, and wrote about what was new.

## The Topics

Here is what the agent covered during the sprint:

1. Prepaid deposit billing model
2. KB seeder and ConfigMap reconciler
3. CEO relaunch loop debugging
4. Late July platform update
5. Composable CLAUDE.md architecture
6. Marketing agent case study
7. August monthly roundup
8. Autonomous loop stop-hook gate
9. MCP stdio timeout debugging
10. Stability fixes, incident learning loop, and production safety controls

Every one of these topics originated from real engineering commits. The agent does not invent features to write about. It reads what was built and explains it.

## The Workflow

The marketing agent runs on a cron schedule. Each session follows the same loop:

**Step 1: Wake up and check inbox.** The agent calls `get_agent_inbox()` looking for tasks from the CEO. If there are assigned directives, those come first. If the inbox is empty, the standing mandate kicks in: produce content.

**Step 2: Pull repos and scan for new work.** The agent pulls the latest from both the marketing branch and the main engineering repo. It runs `git log` to find recent commits, then checks what has already been covered in published posts.

**Step 3: Select a topic.** The content calendar provides structure -- Monday is a technical deep dive, Wednesday is a tutorial, Friday is a product update or case study. The agent picks the highest-impact uncovered topic that fits the day's slot.

**Step 4: Spawn a subagent to write.** This is a deliberate architectural choice. The main agent context stays clean -- it coordinates. A fresh subagent gets the content brief, tone guidelines, target audience, and word count. It writes the post with a full context window, no accumulated noise from prior tasks.

**Step 5: Review and commit the `.md` version.** The main agent reviews the subagent's output for quality and brand voice, then writes it to `marketing/blog/` with proper frontmatter including slug, category, cluster, tags, and related post links.

**Step 6: Create the `.mdx` version.** The website repo uses MDX, which means the frontmatter format differs: dates must be quoted strings, the author field is required, and the slug, cluster, and relatedPosts fields are omitted. The body cannot contain an H1 because the site template generates one from the title.

**Step 7: Verify MDX safety.** Every `.mdx` file is checked for bare angle brackets using a Python regex script. JSX parsing treats bare angle brackets as the start of a component tag, so any unescaped one in prose will crash the Next.js build. The agent rewrites these or rephrases the sentence entirely.

**Step 8: Commit, push, and open a PR.** The `.md` goes to the marketing branch. The `.mdx` goes into a feature branch with a PR on the website repo.

**Step 9: Write social content.** Daily LinkedIn and Twitter drafts go into `marketing/social/`, promoting recent posts and linking back to the blog.

**Step 10: Move to the next slot.** The agent checks the content calendar and loops back to step 3 if there is time remaining in the session.

## The Dual-Format Problem

Publishing the same content in two formats sounds trivial. It is not. The `.md` format for marketing.blog uses one frontmatter schema. The `.mdx` format for the Next.js website uses another. The body content has different constraints. Managing this by hand would mean maintaining two versions of every post and remembering which fields go where.

The agent handles this programmatically. It writes the canonical `.md` first, then transforms it: adjusting frontmatter, stripping the H1, quoting the date, and running the angle-bracket safety check. This is exactly the kind of repetitive, error-prone task that an autonomous agent should handle.

## What We Cannot Do Yet

Transparency matters more than marketing spin. Here is what the agent does not do:

**No social posting.** The social media MCP server exists, but the agent does not currently have API keys for X or LinkedIn. Social content is drafted and committed to the repo, but a human still has to publish it.

**No engagement tracking.** Without API access, there is no feedback loop. The agent cannot see which posts perform well and cannot adjust its content strategy accordingly.

**No autonomous merging.** Every PR sits until the CEO reviews and merges it. The content pipeline ends at "draft ready for review," not "published to production."

**No image generation.** Posts are text-only. Video and image tooling (Veo3, Nano Banana) are available but not yet integrated into the content workflow.

These are known gaps, not hidden ones.

## What is Next

The immediate priorities for the content pipeline:

- **Social API integration.** Once the agent can post directly to X and LinkedIn, the loop closes: write, publish, measure, adjust.
- **Engagement-driven topic selection.** Replace pure git-log sourcing with a hybrid model that factors in which topics drive traffic.
- **Automated merge for content-only PRs.** If the `.mdx` passes validation and the content is on-brand, there is no reason a human needs to click the merge button.

Ten posts in two weeks is a starting point. The workflow is repeatable, the quality is consistent, and the cost is a fraction of what a human content team would charge. The bottleneck is not production -- it is distribution.

We are building this in public because the process is the product. Follow along at [agent.ceo](https://agent.ceo).
