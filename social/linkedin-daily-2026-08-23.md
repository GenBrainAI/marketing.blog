---
platform: linkedin
status: draft
date: 2026-08-23
note: Saturday technical — dual-format challenge
---

## Post: The .md vs .mdx Problem Nobody Warns You About

When our marketing agent started writing blog posts, it hit a bug that no tutorial mentions: the same content needs to exist in two formats, and the second one breaks in ways that are invisible until build time.

Markdown (.md) is forgiving. Write angle brackets, use HTML fragments, leave a stray character -- it renders fine. MDX (.mdx) is not. It parses your content as JSX. A bare angle bracket without a closing pair crashes the build. A comparison like "latency was under 50ms" with a literal less-than sign breaks the entire site.

The frontmatter differs too. The .md version uses slug, cluster, and relatedPosts fields. The .mdx version uses quoted dates, an author field, and omits those three fields entirely. The .md has an H1 heading. The .mdx does not -- the site template generates one from the title.

The agent's solution: after generating every post, run regex verification against the .mdx output. Strip code blocks first, then check for unescaped angle brackets. If any check fails, rewrite the offending line before committing.

Result: 10 consecutive posts, zero build failures.

If you are building any automated content system that targets MDX, add format verification before your commit step.

https://agent.ceo/blog/ai-marketing-agent-content-pipeline-case-study

#MDX #ContentAutomation #AIAgents #DevOps #AgentCEO
