# Link-earning plan: third-party links from 0, plus the founder's X lane

Row `task-8d17c81d` · assigner and verifier ceo · 2026-09-13 · **Nothing sent, posted or submitted by an agent.**

## Baseline (the founder's Search Console, verified 2026-09-13 ~22:5xZ)

| Reading | Value |
|---|---|
| External links, total | **14** |
| Linking sites | linkedin.com 7 · github.com 6 · npmjs.com 1 |
| Linked pages | `/` 13 · `/developers/docs` 1 |
| Third-party links (a site we do not control, or a page we did not write) | **0** |

All 14 links are on surfaces we own: our LinkedIn, our GitHub repos and our npm package. Search engines and
answer engines rank on what other sites say about us, and today no other site says anything.

**Classes used below.** *Owned*: our own accounts and repos. *Placed*: on a third-party domain, but we
wrote or submitted it (directory profile, awesome-list entry, a Dev.to cross-post). *Earned*: a third
party chose to link (a partner's case-study link, a citation of a definition). M5 reports total and
third-party. Third-party is split into placed and earned, because only earned links prove anyone else cares.

## What is broken before we add a single link (measured 2026-09-13 ~23:0xZ)

1. **The npm package points readers at a private repo.** `@agent.ceo/mcp` sets `homepage` to
   `github.com/GenBrainAI/agent-hub#readme`, with `repository` and `bugs` on the same repo.
   `curl https://github.com/GenBrainAI/agent-hub` → **404** to anyone outside the org (the repo is private).
   It also rules the package out of `awesome-mcp-servers`, which accepts only servers with a public repo.
2. **Our own READMEs link to dead or retired pages.** `agent-ceo-sdk`: logo `agent.ceo/logo.png` 404,
   `/developers/docs/api` 404, `/developers/docs/contributing` 404. `agent-framework-starter`: "1 agent-week
   free" (a retired offer) and `docs.agent.ceo` (302 to the homepage). `nats-agent-patterns`: "Try it free".
   None of the 8 public repos sets a homepage URL. `GenBrainAI/.github` does not exist (404), so the org has
   no profile README, and the org `blog` field is empty.
3. **The one deep page that already earns a link contradicts pricing.** `/developers/docs` (prod and stg) serves
   "Sign up for free — 3 agents and 100 agent-hours/month included. No credit card required." `/pricing` serves
   "Flat per-agent / month — no agent-hour metering". That is gate G2 in `off-page-submissions.md`.
4. **The live glossary defines agent-hour as a billing unit.** `agent.ceo/blog/glossary-ai-agent-orchestration`
   (200) says "Pay-as-you-go pricing is $1 per agent-hour". Served pricing retired that. Lane 4 cannot publish
   a citable definition while our own glossary contradicts it.
5. **None of the five deep pages a link should point at is fully ready.** The Ghost-Agent explainer is
   merge-held (marketing.blog#11, 404 today). The entity page `/about` serves unverified facts until
   website#1079 is merged and deployed (G1). `/pricing`, `/agents` and `/developers/docs` are 200. `/developers/docs`
   carries defect 3.
6. **This repo is public, and it names a design partner.** `docs/marketing/weekly-report-2026-09-13.md:27`
   names one partner. The PR #11 branch names both. One partner's draft agreement says it will not be named
   publicly without written agreement. So lane 3 below uses no partner names, and the drafts live in the
   private agent-hub repo. The existing mentions are for the CEO/founder to rule on. Removing them now would
   not remove them from git history.
7. **Instrument note.** `grep -o '16 predefined roles'` on the raw HTML of `/agents` returns **0** on prod and
   stg. React renders `16` as its own text node. Once tags are stripped, the sentence is served on both
   ("16 predefined roles ready to deploy … or create custom roles"). Any check that pins this truth must
   strip tags first, or it will report a false failure.

## The five lanes at a glance

Link counts are **estimates for the first 30 days after each lane's gates clear. They are unverified.** The row's
hypothesis of 20 third-party links in a month is only reachable if the Product Hunt launch lands inside that
month. Without it, expect about 6–12, almost all placed.

| Lane | Expected links (30 days) | Effort | Owner | Founder actions |
|---|---|---|---|---|
| 1. Assets we control | +10–14 **owned**, deep and descriptive; 0 third-party | cto ~1.5 h · fullstack ~1 h | cto (npm, repos, org profile) · fullstack (website) | Publish the npm version (his npm login) · set the org `blog` URL (org owner) · rule G2 |
| 2. Free submissions | 5–10 **placed**: directories 3–6, awesome-lists 1–2, Dev.to/Hashnode 2, Product Hunt 1 (plus scrapers that copy it) | founder ~4 h over two weeks; marketing drafted it all | founder submits; marketing keeps the copy consistent | Every submission, from his own accounts · clear G1–G5 · pick the PH date |
| 3. Design-partner case studies | 0–2 **earned**, and only after a real outcome plus written consent | marketing 1 h per page per round; the partner's review | founder (the ask); marketing (drafts) | Ask each partner, in his own words, whether a case study is welcome · return their edits |
| 4. Citations | 0–2 **earned** in 30 days; compounding | marketing 1 h; fullstack 30 min (glossary fix) | marketing (definitions), fullstack (page) | Go on #11 · go on the agent-hour page · use the one-line definitions in his replies |
| 5. X.com | 0–2 **earned** indirectly; its real product is awareness (M1, M3) | founder ≤ 20 min/week; marketing drafts weekly | founder posts; marketing drafts | Confirm his handle · set the bio and pinned post · post from the calendar |

## Lane 1 — assets we control (row spec for cto and fullstack)

Goal: every owned link lands on a deep page, with an anchor that says what is there, and no owned surface sends
a reader to a 404 or a retired offer. These are owned links, so M5 total rises and third-party does not.

**Link targets and when each may be used** (check it on the day: `curl -s -o /dev/null -w '%{http_code}' <url>` = 200, control `https://agent.ceo/blog/zz-fake-slug` = 404):

| Anchor text (use verbatim) | URL | Usable |
|---|---|---|
| Agent roles: 16 predefined or custom | https://agent.ceo/agents | now |
| Pricing: from $50/month flat, bring your own model key | https://agent.ceo/pricing | now |
| Developer docs | https://agent.ceo/developers/docs | now (after the G2 line is fixed, preferably) |
| About agent.ceo and GenBrain AI | https://agent.ceo/about | after website#1079 is deployed to prod (G1) |
| The ghost agent problem, defined | https://agent.ceo/blog/what-is-the-ghost-agent-problem | after #11 is live on prod |
| What is an agent-hour? | https://agent.ceo/blog/what-is-an-agent-hour | after lane 4's page is live |

### Row A → cto: npm package and public repos

1. **`@agent.ceo/mcp` (`packages/agent-ceo-mcp/package.json` in agent-hub):** set `homepage` to
   `https://agent.ceo/developers/docs`. Point `repository` and `bugs` at a public location, or remove them
   (today both 404 for the public). Publishing the package source to a public repo is a separate decision.
   It also makes the package eligible for `awesome-mcp-servers`.
2. **Its README:** append the block below. Also check `https://agent.ceo/dashboard/settings`, which is 307
   today, to confirm where a signed-out reader lands. Bump to 1.0.2. The npm publisher is the founder's
   account, so **the founder publishes** unless cto already holds a publish token.
3. **Each of the 8 public repos:** set the About "Website" field to the most specific page (SDKs and the MCP
   SDK use `/developers/docs`, patterns and examples use `/agents`, the homebrew tap uses `/developers/docs`).
4. **README fixes (exact):**
   - `agent-ceo-sdk`: `https://agent.ceo/logo.png` (404) → `https://agent.ceo/icon.svg` (200).
     `/developers/docs/api` and `/developers/docs/contributing` (both 404) → `https://agent.ceo/developers/docs`.
   - `agent-framework-starter`: replace "1 agent-week free" with
     `[Pricing: from $50/month flat, bring your own model key](https://agent.ceo/pricing)`. Replace
     `docs.agent.ceo` with `https://agent.ceo/developers/docs`.
   - `nats-agent-patterns`: replace "Try it free -- [agent.ceo](https://agent.ceo)" with the pricing anchor above.
   - `cyborgenic-patterns`, `cyborgenic-examples`, `agent-mcp-sdk`, `homebrew-super-agent-ceo`, `agent.ceo.docs`: append the block.
5. **The block (identical everywhere, add the gated lines only when they are usable):**

   ```markdown
   ## agent.ceo
   - [Agent roles: 16 predefined or custom](https://agent.ceo/agents)
   - [Pricing: from $50/month flat, bring your own model key](https://agent.ceo/pricing)
   - [Developer docs](https://agent.ceo/developers/docs)
   <!-- add after G1 deploy: - [About agent.ceo and GenBrain AI](https://agent.ceo/about) -->
   <!-- add after #11 is live: - [The ghost agent problem, defined](https://agent.ceo/blog/what-is-the-ghost-agent-problem) -->
   ```
6. **Org profile:** create public `GenBrainAI/.github` with `profile/README.md` containing the short description
   from `off-page-submissions.md` §1 and the block above. **The org `blog` field** (`https://agent.ceo`) is an org
   owner setting → founder (or devops if they hold org admin).

**Verification (runnable by anyone):**
`curl -s https://registry.npmjs.org/@agent.ceo/mcp | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['versions'][d['dist-tags']['latest']]['homepage'])"`
→ `https://agent.ceo/developers/docs` (today: `…agent-hub#readme`, which is the known-negative).
`for r in agent-ceo-sdk agent-framework-starter nats-agent-patterns; do gh api repos/GenBrainAI/$r/readme -H 'Accept: application/vnd.github.raw' | grep -c 'agent.ceo/pricing'; done`
→ each ≥ 1 (today 0). `gh api repos/GenBrainAI/agent-ceo-sdk/readme -H 'Accept: application/vnd.github.raw' | grep -c 'logo.png'` → 0 (today 1).

### Row B → fullstack: agent-ceo-website

1. `app/developers/docs/page.tsx:450` and `app/developers/docs/[...slug]/page.tsx:59`: replace the "3 agents
   and 100 agent-hours/month … no credit card" line with the founder's G2 ruling. Until he rules, link
   `/pricing` with the pricing anchor instead of stating a free offer.
2. `app/developers/docs/page.tsx`: in the closing call-to-action, add the `/agents` and `/pricing` anchors from the
   table. Add the Ghost-Agent anchor only after #11 is live.
3. `content/blog/glossary-ai-agent-orchestration.mdx:28`: replace the Agent-Hour entry with lane 4's definition,
   **on the founder's go for the agent-hour page**. Link the entry to `/blog/what-is-an-agent-hour` once that is live.
4. Not in scope, noted only: `lib/pricing-tiers.ts:50` still describes "100 agent-hours/month". It is not served on
   `/pricing` but feeds `/enterprise` and Stripe config.

**Verification:** `curl -s https://stg.agent.ceo/developers/docs | grep -c '100 agent-hours'` → 0 (today 1, the
known-negative). `curl -s https://stg.agent.ceo/blog/glossary-ai-agent-orchestration | grep -c 'per agent-hour'` → 0
(today 1). Then the same two against prod after `./deploy.sh`.

Neither row is dispatched by marketing. The CEO dispatches them.

## Lane 2 — free submissions (the founder submits)

Full copy per venue: [`link-earning-venue-copy.md`](link-earning-venue-copy.md). G2, Capterra, Product Hunt and
the AI-agent directories are already specified, with gates G1–G5, in [`off-page-submissions.md`](off-page-submissions.md).
They are not repeated here.

| Venue | Fit, checked 2026-09-13 | Gate | Link class |
|---|---|---|---|
| e2b-dev/awesome-ai-agents (≈30.0k★, last push 08-21) | Has a "Closed-source projects and companies" section. PR or Google form | G1 (entity facts) | placed |
| Jenqyang/Awesome-AI-Agents (≈1.2k★, 09-11) | "Platforms/API" section already lists hosted products (Crewship, Taskade Genesis) | none | placed |
| punkpeye/awesome-mcp-servers (≈94.9k★) | **Not eligible**: public-repo servers only; our MCP source is private (lane 1 item 1) | lane 1 public source | — |
| kyrolabs/awesome-agents, kaushikb11/awesome-llm-agents | **Not a fit**: open-source frameworks only | — | skip |
| slavakurilyak/awesome-ai-agents, appcypher/awesome-mcp-servers | Stale (no push since 2025-09) / archived | — | skip |
| Show HN | **Not eligible today.** HN's rules: "blog posts, sign-up pages … can't be Show HNs", and "make it easy for users to try your thing out, ideally without barriers such as signups". Our product needs a signup, and G4 is unverified | a no-signup try path | — |
| Hacker News, regular submission | Eligible for a Ghost-Agent page once it is live | #11 live | placed (the discussion can earn) |
| Dev.to, Hashnode | Cross-post with a canonical URL back to agent.ceo | original live on prod | placed |
| AlternativeTo, SaaSHub | Not checked beyond the list in off-page §6 | G1–G3 | placed |

## Lane 3 — design-partner case studies

This repo is public, so the partners are not named here (see finding 6). Two one-page drafts, one per
current design partner, are in **agent-hub (private)** at
`docs/business/design-partners/case-study-drafts-2026-09-13.md`.

- **Every outcome field is a placeholder.** Neither engagement has produced a published outcome, and marketing
  will not invent one. The drafts give the structure, the facts already on record, and the questions only the
  partner can answer.
- **Consent first.** One partner's publicity form is silent by default, and B3 (case study) requires approval of
  the full text. The other's draft agreement says no public naming without written agreement. A draft is shown
  to a partner only by the founder.
- **The link we are after** is the partner linking back from their own site, blog or changelog. That ask is
  the founder's to make, in the same conversation, and it is optional for them.
- Expected: 0 links in 30 days is the most likely result. One engagement is not provisioned yet (a 90-day term
  once it starts).

## Lane 4 — citations: two quotable definitions with stable URLs

A definition earns citations when it is short, stands alone, and lives at a URL that never changes. **Stable URL
rule:** the slug is permanent. If a page ever moves, it gets a 301, never a new slug.

### The ghost agent problem

> **A ghost agent is an AI agent that keeps running after the person who created it is gone, on credentials
> nobody tracks, doing work nobody owns.**

- URL: `https://agent.ceo/blog/what-is-the-ghost-agent-problem` (marketing.blog#11, merge-held; 404 today).
- Already carries this sentence as the bold opening and as the FAQ answer, which the website emits as FAQPage.
- Its one agent.ceo claim is truth R (served on prod and stg; see finding 7).

### The agent-hour

> **An agent-hour is one AI agent running for one hour. It measures how much agent capacity an organization
> used, the way a person-hour measures human effort. It says nothing about what the agent produced.**

- URL: `https://agent.ceo/blog/what-is-an-agent-hour`. Draft page:
  [`posts/marketing/what-is-an-agent-hour.md`](../../posts/marketing/what-is-an-agent-hour.md) (merge-held with this
  plan's lane 4 go; needs the same hand-port as #11).
- Its one agent.ceo claim is truth P: `/pricing` serves "Flat per-agent / month — no agent-hour metering" (prod 3
  matches). Internally, agent-hours are informational usage telemetry, not the billing basis
  (agent-hub `conductor/src/billing/api.py:467-470`). The page says nothing about a customer-visible agent-hour
  report, because none has been checked.
- **Blocked by finding 4.** The live glossary says the opposite, so fix fullstack row B item 3 in the same deploy.

**How these get cited without outreach:** the founder uses the one-line definition plus its URL when he answers
someone's thread (lane 5 reply drafts). The Dev.to/Hashnode cross-posts carry them. The directory long
descriptions link the Ghost-Agent page once it is live. No Wikipedia or Wiktionary edits: it would be self-promotion
on a term nobody else has used yet, and it would be reverted.

## Lane 5 — X.com (the founder's own account; no agent account)

Calendar, bio, pinned post and the weekly drafting contract: [`x-founder-lane-2026-09-14.md`](x-founder-lane-2026-09-14.md).
Two weeks, three threads (one per content-calendar pillar), 5–7 posts per thread, at most one product truth per
post, and every truth served on stg today. Every link-bearing post waits until its URL returns 200 on agent.ceo.

## Founder actions, in the order they unblock links

| # | Action | Unblocks | Needed by |
|---|---|---|---|
| 1 | Go on marketing.blog#11, then the hand-port and `./deploy.sh` | Ghost-Agent anchors (lanes 1, 2, 4, 5) | Wed 09-16 |
| 2 | Merge and deploy website#1079 (G1) · answer F2/G3 (contact email) | `/about` anchor · every directory | before any submission |
| 3 | Rule G2: is there a free offer, yes or no | `/developers/docs` fix · Product Hunt pricing tag · directories | this week |
| 4 | Confirm his X handle; set bio and pinned post | lane 5 | Mon 09-14 |
| 5 | Publish `@agent.ceo/mcp` 1.0.2 after cto's change; set the org `blog` field | lane 1 | after row A |
| 6 | Open the two awesome-list PRs from his GitHub account (text ready) | 1–2 placed links | after #2 |
| 7 | Cross-post to Dev.to and Hashnode with the canonical URL | 2 placed links | after #1 |
| 8 | Ask each design partner whether a case study is welcome | lane 3 | when an outcome exists |
| 9 | Go on the agent-hour page (with fullstack's glossary fix) | lane 4 | no date |
| 10 | Read Search Console Links every Friday and send the two M5 numbers | M5 | weekly |

## Measurement — M5 external links

Added to [`weekly-report-template.md`](weekly-report-template.md) as M5. The founder, or his local agent, reads
Search Console → Links → *Top linking sites* and *Top linked pages*. Marketing classifies each linking site as
owned, placed or earned against the owned list (linkedin.com company and founder profile, github.com/GenBrainAI,
npmjs.com/package/@agent.ceo/mcp). Search Console updates with a lag of days, so a new link may appear a week
late. Baseline 2026-09-13: **14 total / 0 third-party (0 placed, 0 earned)**.
