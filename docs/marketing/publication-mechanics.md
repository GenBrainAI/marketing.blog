# Publication mechanics — from draft to a served post, with no CEO step

Written once for `task-8ed603a6`, 2026-09-13. Calendar: [`content-calendar-2026-09-14.md`](content-calendar-2026-09-14.md).

## 0. The route, and the decision it needs

| Route | State 2026-09-13 | Use it? |
|---|---|---|
| **A. `marketing.blog` → cicd converter → website** | **Dormant.** The last runner commit in agent-ceo-website is `2e2efd5c` (2026-05-31). A tag fired on 2026-08-15 was never consumed. The transform `.cicd/blog_md_to_mdx.py` still runs locally, but it **drops `faq`**: it emits only title/date/author/category/tags/excerpt. | No |
| **B. Write the post directly as `agent-ceo-website/content/blog/<slug>.mdx`** | Works. `app/blog/[slug]/page.tsx` renders it, `BlogSeo` emits Article, `FaqJsonLd` emits FAQPage from `faq:`, and the site layout emits Organization. | **Yes** |

**Founder decision F1:** confirm route B. Then the website repo is the source of truth for published
posts, and `marketing.blog` holds drafts and planning only. Until he confirms, route B is what this
batch uses. Nothing is published until he says go.

## 1. Write the post

File: `content/blog/<slug>.mdx`. The slug is the URL: `https://agent.ceo/blog/<slug>`.

```yaml
---
title: "The question, as a searcher types it?"
date: "YYYY-MM-DD"          # the PUBLISH day, quoted
author: "Marketing Agent"    # the founder may re-byline on go
category: "Marketing"        # or Engineering / Product
tags: [kebab-case, ...]      # do NOT add `tutorial` or `getting-started` (see §6)
excerpt: "≤160 chars, the direct answer"
faq:
  - question: "..."
    answer: "..."           # plain text, no HTML
---
```

Body rules:
- **The first bold sentence is the answer.** That is the sentence answer engines lift.
- **Every `faq` question and answer also appears visibly in the body** under `## FAQ`. Google requires
  FAQPage questions to be visible (see the comment in `components/blog/faq-jsonld.tsx`).
- MDX is not Markdown. **Never put a bare `<` or `{` `}` in prose.** They are allowed inside code fences.
- At least 2 visuals (tables and/or a ```mermaid block) and 1 code block, per `CONTENT-STANDARDS.md`.
- Internal links go only to URLs that return **200 on both** `agent.ceo` and `stg.agent.ceo` today,
  or to a post in the same PR.

## 2. Check every claim (the gate, before the PR)

Every sentence about agent.ceo must map to a truth code in the calendar (R K A L M G P D I S). Put the
table in the PR body: `slug | claim | truth code | re-run command`. If a claim has no code, cut it.

Re-run commands anyone can execute:

```bash
# served text (known-positive + known-negative in one go)
P=$(curl -s https://stg.agent.ceo/pricing); echo "$P" | grep -c '\$200'; echo "$P" | grep -c 'zzqq-none'   # >0, then 0
# route exists on prod (401) vs a fabricated route (404)
for p in /api/v1/orgs/x/loops /api/v1/orgs/x/zz-not-a-route; do curl -s -o /dev/null -w "$p %{http_code}\n" https://api.agent.ceo$p; done
# every internal link in the batch, both hosts
grep -ohE '\]\(/[^)]+\)' content/blog/<slug>.mdx | tr -d '()]' | sort -u | while read u; do
  for h in stg.agent.ceo agent.ceo; do printf "%s %s " $h $u; curl -s -o /dev/null -w "%{http_code}\n" https://$h$u; done; done
```

## 3. Porting a `marketing.blog` draft (only for PR #11's six pages)

```bash
python3 .cicd/blog_md_to_mdx.py --src posts/marketing/<slug>.md --dst ../agent-ceo-website/content/blog/<slug>.mdx
# then paste the source's `faq:` block back into the .mdx frontmatter. The transform drops it.
```

## 4. Open the PR

- Branch: **`marketing-<name>`**. Never `marketing/<name>`. A branch literally named `marketing`
  exists, so a slash is rejected.
- Title prefix: `[MERGE-HELD]`. Body: the claim table, the internal-link table, the publish dates, and
  "nothing is published by this PR until deploy".
- Push: `git -c credential.helper='!f(){ echo "username=x-access-token"; echo "password=$GITHUB_TOKEN"; };f' push -u origin <branch>`
- One PR per week or per batch. **The founder's merge is the go.**

## 5. How a batch reaches readers — dates do the scheduling

- `isFutureDated()` in `lib/blog.ts` hides a post dated after today (UTC). A future-dated slug
  **redirects to `/blog`**, and the route revalidates hourly (`revalidate = 3600`).
- So **one merge plus one deploy publishes a whole batch on its dates.** Posts appear on their own
  day with no further step. Merge two weeks at once and the site drips them out.
- **Staging** follows main. Measured lag: up to ~3 h. **Prod** ships only when the founder runs
  `./deploy.sh` (project `agent-hub-ceo`). A merge publishes nothing to prod. Any agent can check
  staging first; only the founder publishes prod.
- **If the go comes after a post's date:** move `date` to the real publish day in the same PR.
  Otherwise it goes live back-dated.

## 6. Structured data the site already emits (do not re-add)

| Type | Emitter | Trigger |
|---|---|---|
| Article | `components/blog` `BlogSeo` | every post |
| FAQPage | `FaqJsonLd` | `faq:` frontmatter present |
| Organization, SoftwareApplication | `app/layout` | every page |
| BreadcrumbList | `BlogSeo` | every post |
| HowTo | `HowToJsonLd` | tags include `tutorial` or `getting-started`. **Avoid these tags.** The steps it would generate are not claim-checked |

## 7. Verify after deploy (the surface, not the merge)

On the post's date, for each slug:

```bash
for h in stg.agent.ceo agent.ceo; do
  curl -s -o /tmp/p -w "$h %{http_code} " https://$h/blog/<slug>
  grep -oE '"@type":"(Article|FAQPage)"' /tmp/p | sort -u | tr '\n' ' '; echo
done
curl -s -o /dev/null -w "control %{http_code}\n" https://agent.ceo/blog/zz-fabricated-slug   # must be 404
```

Pass = `200` with both `"@type":"Article"` and `"@type":"FAQPage"`, and the control returns 404. A
`307` means the post is still future-dated, or the deploy has not run.

## 8. Weekly loop (marketing, no CEO step)

1. Monday: draft the next week's calendar rows into one `[MERGE-HELD]` PR (§1–§4).
2. Draft the LinkedIn version of the week's anchor post for the founder
   (`docs/marketing/founder-channel-plan.md`).
3. After the founder merges and deploys: run §7 on each publish day and note the results on the week's
   TMS row.
4. When a readiness run turns a waiting surface green, add its how-to row to the calendar.
5. When a pillar page lands, add one line to `public/llms.txt` and `public/llms-full.txt` in the next
   PR.
