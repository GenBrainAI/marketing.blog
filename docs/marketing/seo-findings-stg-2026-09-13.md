# Technical SEO findings — stg.agent.ceo, 2026-09-13 ~21:00Z

For **fullstack**. Row `task-f2e200a6`. Every reading below has its exact URL and a command anyone can run
again. The 4 main pages are `/`, `/pricing`, `/agents` and `/blog`. Findings are listed worst first.

## Findings

| # | Area | URL | Reading | Why it matters / suggested fix |
|---|---|---|---|---|
| S1 | OpenGraph | `https://stg.agent.ceo/pricing`, `/agents`, `/blog` | **No `og:image` and no `twitter:image`** on all three. `/pricing` also has **no `og:type`**. `/` has both (`https://agent.ceo/opengraph-image?217119f93277e677` → 200 image/png, 148,637 B). Blog posts have both (`/blog/the-fovea-loop`: `og:image https://agent.ceo/opengraph-image`, `og:type article`). | A LinkedIn or Slack share of /pricing, /agents or /blog shows no card image. That matters now, because the founder is about to share links. Fix: give these routes an `opengraph-image`, or inherit the root image in their `metadata.openGraph`. `https://stg.agent.ceo/pricing/opengraph-image` → 404 today. |
| S2 | Page speed | `https://stg.agent.ceo/blog` | **First request TTFB 2.62 s** (`x-nextjs-cache: STALE`, `s-maxage=3600, stale-while-revalidate`). Warm TTFB 25–36 ms. HTML is **479,735 B raw / 47,940 B gzip** with **239 inline scripts**, against 29–36 on the other pages. Every post is rendered on one page, and `/blog?page=2` → 200. | The first visitor after each hourly revalidation waits about 2.6 s. The page grows with every post, and batches 1–2 add 20 more. Fix: paginate or trim the index payload (one card per post, no per-post inline data). |
| S3 | Sitemap | `https://stg.agent.ceo/sitemap.xml` | 383 `<loc>`. **381 → 200**, and **1 → 404: `/start/enterprise`**. That URL is 200 on prod (`https://agent.ceo/start/enterprise`), so this is a stg/main regression or a removed route that is still in the sitemap. 0 entries are future-dated (lastmod > 2026-09-13), and a fabricated slug is not listed (known-negative 0). | When this ships to prod, the sitemap will list a 404. Fix: either restore the route, or drop it from the sitemap generator in the same change. |
| S4 | Robots meta | `https://stg.agent.ceo/blog/tag/zz-fabricated-tag` | Status 404 (good: the old soft-404 is gone). But the page carries **two robots metas: `noindex` and `index, follow`**. | Conflicting directives. Google takes the most restrictive, but other crawlers may not. Fix: the not-found layout should not also emit the root `index, follow`. |
| S5 | Staging indexability | `https://stg.agent.ceo/` (and all 4 main pages) | `<meta name="robots" content="index, follow">`, **no `X-Robots-Tag`** header. Canonicals and sitemap `<loc>`s point to `https://agent.ceo…` (correct). | Staging relies on canonicals alone to stay out of the index. Suggested: `X-Robots-Tag: noindex` on the stg host only. Low priority. |
| S6 | Page weight | `/`, `/pricing`, `/agents`, `/blog` on stg | 20–21 external JS files each, **~300 KB gzip JS per page** (309,298 · 307,689 · 312,008 · 307,836 B). HTML gzip: 17,405 · 14,573 · 7,881 · 47,940 B. | The same ~300 KB ships to /agents, which is a mostly static catalog. Worth a bundle audit. Core Web Vitals are **not measured** (see below). |

## Checked and fine

| Area | URL | Reading |
|---|---|---|
| robots.txt | `https://stg.agent.ceo/robots.txt` | 200 `text/plain`. `Allow: /`, disallows app routes (`/api/`, `/dashboard`, `/chat` …), and `Sitemap: https://agent.ceo/sitemap.xml`. Prod: 200. |
| Canonical | the 4 main pages | `https://agent.ceo`, `https://agent.ceo/pricing`, `https://agent.ceo/agents`, `https://agent.ceo/blog`. Each is self-referencing to prod. |
| Title / description / H1 | the 4 main pages | Every page has a unique title and a description, with exactly 1 `<h1>`. There are 0 `<img>` without `alt`. |
| Structured data | `/` | Organization, SoftwareApplication, Offer, FAQPage. `/pricing`, `/agents`, `/blog`: Organization, SoftwareApplication, Offer. A post adds Article, BreadcrumbList, FAQPage. |
| Warm TTFB | the 4 main pages | 3 samples each, gzip. `/` 32–71 ms, `/pricing` 32–115 ms, `/agents` 25–116 ms, `/blog` 25–36 ms (after revalidation). `/`, `/pricing` and `/agents` are `x-nextjs-cache: HIT`, `s-maxage=31536000`. |
| Error status | `https://stg.agent.ceo/zz-fabricated` | 404, which is a real 404 and not a soft 200. |
| hreflang | `/` | None. The site is English-only, so this is correct. |

## Not measured, and why
- **LCP / CLS / TBT (Lighthouse).** This pod has no Chrome (`agent-browser` wants `agent-browser install`). The
  PageSpeed Insights API answered `Quota exceeded … Queries per day` for all 4 URLs. Anyone with a browser can run:
  `npx lighthouse https://stg.agent.ceo/blog --only-categories=performance,seo --form-factor=mobile`
- **Prod**, beyond the spot checks above. Prod lags main, so these are staging readings.

## Re-run
```bash
for p in / /pricing /agents /blog; do
  curl -s --compressed -o /tmp/p -w "$p %{http_code} ttfb=%{time_starttransfer} gz=%{size_download}\n" https://stg.agent.ceo$p
  grep -oE '<meta (property|name)="(og:image|og:type|twitter:image)" content="[^"]*"|<link rel="canonical" href="[^"]*"' /tmp/p
done
curl -s https://stg.agent.ceo/sitemap.xml | grep -o '<loc>[^<]*' | sed 's#<loc>https://agent.ceo##' \
  | xargs -P 16 -I{} sh -c 'echo "$(curl -s -o /dev/null -w %{http_code} https://stg.agent.ceo{}) {}"' | grep -v '^200'
curl -s https://stg.agent.ceo/blog/tag/zz-fabricated-tag | grep -o '<meta name="robots" content="[^"]*"'
```
