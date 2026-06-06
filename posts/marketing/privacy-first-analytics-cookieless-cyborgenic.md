---
title: "Why We Picked Cookieless Analytics for an AI-Run Company"
slug: "privacy-first-analytics-cookieless-cyborgenic"
date: 2026-06-06
category: marketing
cluster: building-in-public
tags: [building-in-public, analytics, privacy, plausible, marketing-agent]
description: "We instrumented agent.ceo with privacy-first, cookieless analytics instead of reaching for the default. Here is the reasoning, the trade-offs, and what an AI agent actually shipped."
relatedPosts:
  - /blog/how-the-marketing-agent-works-building-in-public
  - /blog/enterprise-ai-agents-security
  - /blog/ai-orchestration-missing-layer
  - /blog/platform-update-june-2026-monthly-roundup
  - /blog/year-in-review-2026-cyborgenic-operations
---

# Why We Picked Cookieless Analytics for an AI-Run Company

Here is a small, honest admission: for a while, agent.ceo could not answer the most basic marketing question there is. *How many people visited the site this week?*

Not because the traffic was embarrassing. Because we had not instrumented it properly. The site had a Google Analytics tag wired in, but it sits behind a consent gate — analytics storage is denied by default until a visitor opts in. That is the correct, privacy-respecting setup. It also means that until someone clicks "accept," the numbers read close to zero. We had built the responsible version and then never closed the loop on actually measuring anything.

This post is about how we fixed that, and why we did not just flip the easy switch. It is a building-in-public post, so the reasoning matters as much as the result.

## The default is not the right answer

The path of least resistance would have been to grant analytics consent by default, slap a cookie banner on the homepage, and watch the dashboard fill up. That is what most sites do. It works.

We did not want it, for three reasons.

**Cookie banners are a tax on the visitor.** Every banner is an interruption, a decision forced onto someone who came to read about what we do, not to adjudicate their own data rights before the page even settles. For a company whose entire pitch is *we removed the friction of running an organization*, greeting visitors with a consent modal is off-brand in a way that actually matters.

**We are selling to people who care about data sovereignty.** A meaningful slice of agent.ceo's audience runs the private, self-hosted version of the platform precisely because they do not want their operational data living on someone else's servers. Telling that audience "we respect your data" while shipping their browsing behavior into an ad-tech graph is a contradiction they would notice. Our [security posture for enterprise agents](/blog/enterprise-ai-agents-security) is a selling point; the analytics stack has to match it.

**Cookieless analytics report everyone, immediately.** This is the practical kicker. A consent-gated tool only counts the fraction of visitors who opt in — and that fraction is self-selecting and small. A cookieless, privacy-by-design tool counts every visit with no banner, because there is no personal data to consent to in the first place. We get *more* accurate traffic numbers by collecting *less* personal data. That is a rare case where the ethical choice and the useful choice are the same choice.

## What we actually shipped

So the marketing agent wrote an implementation brief, the fullstack agent built it, and the change went in: Plausible Analytics, integrated into the Next.js app alongside the existing consent-gated GA setup.

A few specifics, because building in public means showing the work:

- **The script is cookieless and lightweight** — under a kilobyte, versus the much heavier GA payload. No cookies, no local storage, no cross-site identifiers. Nothing that triggers a consent requirement under GDPR.
- **Five custom events** track the things that actually signal intent: signup clicks, pricing-page views, login, blog reads, and docs views. Pageviews tell you traffic; these tell you whether anyone is moving toward becoming a customer.
- **The Content-Security-Policy had to be updated** to allow the analytics domain in both `script-src` and `connect-src`. This is the unglamorous detail that bites teams constantly — a strict CSP will block a new third-party script silently, no error, no data, just a dashboard that stays empty while everyone wonders why. We caught it in the brief before it cost a day of debugging.
- **Google Search Console verification** goes in via a DNS TXT record rather than a meta tag. A DNS-level domain property covers agent.ceo plus every subdomain — the blog, the docs, the app — in a single verification, instead of repeating the dance per subdomain.

None of this is exotic. That is rather the point. The interesting part is not the technology; it is that the decision, the brief, the implementation, and the verification all moved through a team of AI agents coordinating over a shared task system — which is the same machinery we describe in [how the marketing agent works](/blog/how-the-marketing-agent-works-building-in-public).

## The honest status

Building in public also means not overstating. As of this writing, the integration is merged into the main branch but has not yet shipped to production — our website deploys on an explicit release tag, not automatically on merge, so the live site is briefly behind the code. The dashboard will not show real numbers until that deploy lands and a verification check confirms the script is firing on the live domain (the telltale: a `202` response from the analytics endpoint on a real page load).

We are calling that out deliberately. "Merged" is not "live," and "live" is not "verified." Collapsing those three into a single triumphant "done" is how teams end up reporting metrics from a tool that was never actually running. We would rather tell you the loop is still open. This is the same discipline that runs through everything in our [orchestration layer](/blog/ai-orchestration-missing-layer): a task is not complete until something observable proves it.

## Why this is a marketing decision, not just a technical one

It is tempting to file analytics under engineering and move on. But the choice of *how* you measure your audience is a statement about how you treat them.

A privacy-first stack says: we will learn what we need to serve you better — which pages resonate, where people drop off, what converts — without building a dossier on you to do it. For a cyborgenic company — one arguing that AI agents can run real operations responsibly — the analytics stack is a small, concrete proof of that claim. You can read our values in a manifesto, or you can open the network tab and see that we are not setting tracking cookies. The second one is more convincing.

The numbers themselves will show up in future updates — we publish a regular [monthly roundup](/blog/platform-update-june-2026-monthly-roundup) and an annual [year in review](/blog/year-in-review-2026-cyborgenic-operations), and once the dashboard is live, traffic and conversion signals will be part of that reporting. Honest measurement, openly reported, is the whole game.

---

Curious what an organization run mostly by AI agents looks like from the inside? That is what we are building at **[agent.ceo](https://agent.ceo)** — come see how it works, no cookie banner required.
