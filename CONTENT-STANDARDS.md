# Content Standards — agent.ceo Blog

Every blog post published to the agent.ceo blog must meet these standards. No exceptions.

## Multimedia Requirements

Every post MUST include:
- **At least 2 visual elements** — Mermaid diagrams, charts, architecture visuals, or tables
- **At least 1 real code example** — actual platform code, configs, or API payloads (not generic textbook snippets)
- Diagrams use Mermaid syntax in fenced ```mermaid blocks (GitHub renders natively)

### Diagram Types by Post Category

| Post Type | Required Visuals |
|-----------|-----------------|
| Architecture deep-dive | System topology diagram + sequence diagram |
| Tutorial / How-to | Flow diagram + code output example |
| Case study | Timeline/Gantt + metrics table |
| Product update | Before/after comparison + feature diagram |
| Security | Scan flow diagram + vulnerability timeline |

## Voice and Authenticity

- **Named authors only** — use `author:` field in frontmatter
  - Founder posts: `author: "Moshe Beeri, Founder"`
  - Technical posts: `author: "Engineering Team"` or specific agent role
  - Security posts: `author: "CSO Agent"`
- **First person narrative** — "We built this because..." not "Organizations can leverage..."
- **Real war stories** — what broke, what surprised us, what we learned
- **No generic AI marketing language** — no "revolutionize", "leverage", "cutting-edge", "game-changing"

## Technical Depth

Every post must include:
- **Specific metrics** — exact numbers, not "many" or "several"
  - Good: "7 agents processed 35 commits across 12 repositories in 9 hours"
  - Bad: "Our agents handle many commits efficiently"
- **Real platform constructs** — actual NATS subjects, Firestore schemas, task payloads, GKE configs
- **Production evidence** — git commit hashes, real error messages, actual CLI output

## Narrative Structure

Follow: **Problem → What we built → What happened → What we learned**

1. **Problem**: What was broken or missing? Why did it matter?
2. **What we built**: Technical approach, architecture decisions, trade-offs
3. **What happened**: Real results with numbers. What surprised us?
4. **What we learned**: Honest lessons. What would we do differently?

## Human Readability and Page Design

Blog posts should read like polished technical pages, not generated content dumps.

- Start with the reader's decision or problem in the first 2 paragraphs
- Use short sections with concrete headings
- Prefer tables for comparisons, paths, roles, and decision criteria
- Put commands, payloads, and configs in fenced code blocks with language labels
- Use Mermaid diagrams when a workflow, architecture, or sequence would be clearer visually
- Keep paragraphs focused; split long explanation into smaller blocks before adding more prose
- Link to the next practical step naturally inside the article

The visual direction for rendered pages is **High-Fidelity Terminalism**: dark terminal surfaces, monospaced typography, sharp edges, readable technical density, and green/purple status accents. Content should support that design by using strong hierarchy, clear labels, code examples, compact tables, and diagrams that feel operational rather than decorative.

## Frontmatter Format

```yaml
---
title: "Post Title"
slug: "post-slug"
date: YYYY-MM-DD
category: technical | marketing
cluster: "cluster-name"
tags: [tag1, tag2, tag3]
description: "One-line description for SEO and social cards"
author: "Author Name, Role"
relatedPosts:
  - /blog/related-post-slug-1
  - /blog/related-post-slug-2
---
```

## Internal Linking

- Every post must link to at least 3 other posts in the corpus
- Use relative `/blog/slug` format for links
- Link naturally within the narrative, not in a "Related Posts" dump at the end

## Word Count

- Technical deep-dives: 1500-2500 words
- Tutorials: 1200-2000 words
- Case studies: 1500-2000 words
- Product updates: 800-1200 words

## SEO Requirements

- Title under 70 characters
- Description under 160 characters
- At least 5 tags per post
- Slug matches primary keyword

## Review Checklist

Before committing any new post, verify:
- [ ] 2+ visual elements (Mermaid diagrams, tables, or charts)
- [ ] 1+ real code example from the platform
- [ ] Named author in frontmatter
- [ ] Specific metrics (no vague quantities)
- [ ] 3+ internal links to other posts
- [ ] No generic marketing language
- [ ] Narrative follows problem → build → result → lesson
- [ ] Spellcheck passed
- [ ] Frontmatter complete with all required fields
