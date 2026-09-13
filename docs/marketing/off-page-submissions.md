# Off-page submissions — G2, Capterra, Product Hunt, AI-agent directories

Row `task-388aca82` · verifier ceo · **Nothing here is submitted by an agent.** Restart plan channel 3
("off-page entity presence"). Baseline today: **0 directory or review profiles** (restart plan §3 search).
Every submission waits for the founder's go, and most need his work email and a login anyway.

## 0. Before ANY submission: five gates

Directories and review sites check the claims on your website. Today the website contradicts itself, so
a submission now would be checked against the wrong facts.

| # | Gate | Measured 2026-09-13 | Owner | Clears when |
|---|---|---|---|---|
| G1 | **/about serves unverified facts** | prod and stg /about both serve "San Francisco, CA", "Free tier gets you started immediately", "5.0K commits". website#1079 replaces them with Beeri B.V., Netherlands, GenBrain AI and Moshe Beeri | founder (merge + `./deploy.sh`) | `curl -s https://agent.ceo/about \| grep -c "Beeri B.V."` ≥ 1 and `grep -c "San Francisco"` = 0 |
| G2 | **Free hours contradict pricing** | prod and stg /agents serve "Start free with 100 hours. No credit card required." /pricing offers no free level. Directories ask "free / paid / free trial". | founder rules, then fullstack edits /agents | One answer on both pages |
| G3 | **Contact email** | website#1079 F2 (publish `moshe@agent.ceo`?) is open. /pricing already serves `sales@genbrain.ai` on the OEM link. G2 needs a work email **on the product's domain** (agent.ceo), per the third-party guide below | founder | F2 answered |
| G4 | **The door works** | `/sign-up` 200, `/start/enterprise` 200, `/business` and `/organizations/new` 307 (redirect, not followed). Whether a new visitor can finish signup was last checked 2026-07-29 (restart plan B2), not since | qa walk → fullstack | A fresh signup reaches an organization, with notes on the row |
| G5 | **Assets** | The only brand asset in the website repo is `public/icon.svg`. There are no screenshots, logo PNG or video. The pod has no browser to capture them (PageSpeed notes 2026-09) | founder, or design on request | Files listed in §5 exist |

**Order:** G1–G3 are one merge, one deploy and two founder sentences. G4 and G5 are the long poles. Product
Hunt should come **last**. It is a one-day event, and it should land when the blog has the week-1 set and
posts 1–10 live.

## 1. The copy (shared by every site)

Every sentence below is a truth-coded claim from the content calendar. Counts are exact characters.

| Field | Copy | Chars | Truth |
|---|---|---|---|
| Product name | `Agent.ceo` | 9 | served |
| Company | GenBrain AI (legal entity Beeri B.V., Netherlands) | — | website#1079 (G1) |
| Website | `https://agent.ceo` | — | served |
| Tagline A | `Every AI agent is a role your organization owns` | 47 | R |
| Tagline B | `The org chart for your AI agents` | 32 | R |
| Pricing URL | `https://agent.ceo/pricing` | — | P |
| Pricing model | Paid. Flat per agent per month, bring your own model key | — | P (G2 may change "Paid") |

**Short description (≤ 260, for Product Hunt and most directories):**

> Agent.ceo gives AI agents an org chart. Each agent is a role your organization holds. Keys carry
> specific scopes, loops run with hard limits and stop on a signal, and an agent's proposal waits for a
> person to approve or reject it. Bring your own model key.

*(256 characters. Truth: R, K, L, A, P.)*

**Long description (G2, Capterra, directories with a long field):**

> Agent.ceo is an organizational layer for AI agents. It answers "who owns this agent?" by creating
> every agent inside an organization as a role, not inside a person's account. Choose from 16 predefined
> roles or define a custom role with your own system prompt.
>
> What it does today:
> - Organization API keys are created with specific scopes, listed by name and scope without their
>   secret values, and refused after revocation.
> - An agent's proposal waits in the organization's approvals queue. An admin approves or rejects it,
>   and the decision is kept.
> - Loops run from an enabled pattern with a schedule, a turn cap and a wall-clock limit. Their output is
>   kept, and they stop on an explicit stop signal.
> - Text meetings keep their transcript and summary. People outside the organization are refused.
> - A registry lists the organization's registered agents.
>
> Pricing is flat per agent per month, not per agent-hour, and you bring your own model key. Business is
> $50/month flat. Company is $100/agent/month. Organization is $200/agent/month, or $400/agent/month on
> your own Kubernetes cluster. Enterprise starts at $2,000/month plus Organization per-agent pricing.
>
> Built for IT, operations and engineering leaders who already run AI agents and cannot say who owns each
> one, what it can reach, or how to stop it.

**Feature list (for checkbox or tag fields; tick only these):** role-based agents · custom agent roles ·
scoped API keys · key revocation · approval workflow · scheduled agent loops · loop stop control · meeting
transcripts · agent registry · bring your own key · self-hosted option · cloud deployment.

**Never tick or write:** audit trail / audit log · free plan / free trial (until G2) · SOC 2 / ISO / GDPR
certification · SSO (not checked) · customer logos, customer counts or usage numbers · "Active Directory /
LDAP". LDAP is an Enterprise line on /pricing, but no journey has checked it, so it is not a checkbox
claim · integrations by name · mobile apps.

**Two sentences that must not be used:** "production is a working cluster" (website#1079 F3, open) and any
beta or design-partner price (founder: none).

## 2. G2

**Where:** https://sell.g2.com/create-a-profile (free profile, then claim it).
**Fields and rules:** G2's own page confirms only the process, not the fields. It covers the request
form, conditional approval, vetting in about 3–5 business days, and then a claim where the vendor provides
name, logo and basic product information. The field list below comes from a **third-party guide**
(wheretosubmit.org, read 2026-09-13), so treat it as likely, not certain.

| Field | Value | Status |
|---|---|---|
| Product name | Agent.ceo | ready |
| Company name | GenBrain AI | ready after G1 |
| Website | https://agent.ceo | ready |
| Category | Search G2 for "AI agent" categories on the day and pick the one listing agent platforms. G2's research team assigns the final category | founder picks |
| Work email (on agent.ceo domain) | founder's | **G3** |
| Phone (international SMS) | founder's | founder |
| "I would like to serve as admin for this profile" | tick | — |
| Tagline (< 60) | Tagline A | ready |
| Description | Long description | ready |
| Logo (transparent PNG) | — | **G5** |
| Screenshots (3–5, ≥ 1280×720) | — | **G5** |
| Demo video (60–90 s, optional) | — | skip for now |

**Rules the guide states:** B2B only. Personal email domains are refused. The site needs a privacy policy
(`/privacy` 200), a pricing page (200) and an About page (G1). Paying for reviews is penalised. The guide's
"15 paying customers" is advice for **review** programmes, not for creating a profile. We make no customer
claim either way.

## 3. Capterra (Gartner Digital Markets: also lists on GetApp and Software Advice)

**Where:** Capterra's vendor pages (https://www.capterra.com/vendors/) route to the Gartner Digital Markets
"get listed" request. `digitalmarkets.gartner.com/get-listed` now redirects to a G2 Digital Markets
**login** page (checked 2026-09-13). The form was not readable from here, so the founder opens it signed
in.
**Free:** profile, reviews and badges are free. Only PPC and lead programmes are paid, and anything paid is
a founder financial gate.

| Field (name, logo, description, screenshots: Capterra vendor FAQ. CTA: listing guidelines. Category and pricing rows: our assumption) | Value | Status |
|---|---|---|
| Vendor name and logo | GenBrain AI · logo | G1 · **G5** |
| Product name | Agent.ceo | ready |
| Product description | Long description | ready |
| Screenshots | 3–5 | **G5** |
| Category | Chosen by Capterra's catalog team from the website | — |
| Pricing | Starting price $50/month (Business, flat); per-agent model above | ready (P) |
| Public call to action | "Must be publicly available, with a call to action … a trial, demo, or request for more information." Candidates: `/pricing` → Create a company, or `/start/enterprise` (200) | **G4** |

**Eligibility:** currently marketed or sold, fits a category, publicly available. Pricing is public, so this
holds once G4 confirms the door opens.

## 4. Product Hunt

**Where:** producthunt.com → Submit (founder's own Product Hunt account; he is the maker).
Fields as listed in Product Hunt's help article "How to post a product", read 2026-09-13:

| Field | Value | Status |
|---|---|---|
| URL | https://agent.ceo | ready |
| Product name (name only, no description or emoji) | Agent.ceo | ready |
| Tagline | Tagline B, `The org chart for your AI agents` (32). The form enforces its own limit | ready |
| Topics (a few that fit best) | Artificial Intelligence · Developer Tools · SaaS. Pick on the day from the list | founder picks |
| Thumbnail (240×240; GIF < 3 MB allowed) | from `public/icon.svg` → PNG | **G5** |
| Gallery (1270×760; 2+ images before it shows) | agent catalog, pricing levels, a loop's output view, an approval decided | **G5** |
| YouTube video (optional, full URL, not private) | skip | — |
| Interactive demo (optional) | skip | — |
| Description (≤ 260) | Short description (256) | ready |
| Pricing tag: free / paid / paid with trial or free plan | **Paid**, unless G2 rules a free offer exists | G2 |
| Status: beta/unreleased indicator | leave off. The founder ruled there is no beta price, and pricing is public | ready |
| Promo code (optional) | none. A discount is a financial commitment | — |
| Makers | founder's username | founder |
| Product's X account (optional) | skip unless one exists | — |
| First comment (required) | draft below | ready |
| Launch scheduling (goes live 12:01 AM PST) | a Tuesday–Thursday once G1–G5 clear and posts 1–10 are live (after 10-02) | founder |

**First comment draft (founder's voice, edit freely, 159 words):**

> Hi Product Hunt, I'm Moshe, founder of agent.ceo.
>
> We built this because of a question we could not answer inside our own company, which runs on AI
> agents: who owns this agent, what can it reach, and how do we stop it?
>
> In agent.ceo an agent is a role your organization holds, not a script in someone's account. Pick one of
> 16 predefined roles or write your own. Keys carry specific scopes and are refused once revoked. Loops
> run with a turn cap and a wall-clock limit, and stop on a signal. When an agent needs a decision, its
> proposal waits for a person, and the decision is kept.
>
> You bring your own model key. Pricing is flat per agent per month, not per hour.
>
> We run our own company on it. The rules our agents follow are on the blog, starting with "never
> self-verify".
>
> I'd love to hear how you handle agent ownership today, and what breaks first.

*(Ends with a question, not an offer. Claims: R, K, L, A, P, I.)*

## 5. Assets to produce (G5)

| Asset | Spec | Used by | Source |
|---|---|---|---|
| Logo, transparent PNG | 512×512 and 240×240 | G2, Capterra, PH thumbnail, directories | `public/icon.svg` |
| Screenshot 1: agent catalog | 1280×760 (covers G2 ≥ 1280×720 and PH 1270×760 after crop) | all | public page `/agents` (after G2 fixes its free-hours line) |
| Screenshot 2: pricing levels | same | all | public page `/pricing` |
| Screenshot 3: a loop's output | same | all | signed-in org, a stopped loop with output |
| Screenshot 4: an approval decided | same | all | signed-in org, a rejected harmless proposal |
| Screenshot 5: scoped key list (no values) | same | G2, Capterra | signed-in org |

Screenshots 3–5 need a signed-in organization with no customer data visible. They also need a person
with a browser, and the pod has none.

## 6. AI-agent and AI-tool directories

| Directory | Submit page | Cost | Fields | Checked |
|---|---|---|---|---|
| AiAgents.Directory | https://aiagents.directory/submit/ | **Free** (paid "feature" upgrade via Stripe: skip, financial gate) | Your email · Agent name · Agent website · Agent description. Then a team review | form read 2026-09-13 |
| AI Agents Directory | https://aiagentsdirectory.com/submit-agent | not shown to a reader | form fields not rendered to a reader. Contact hello@aiagentsdirectory.com | page read, form not |
| There's An AI For That | https://theresanaiforthat.com/submit/ | **unknown**. The page answered 403 to this pod. If it is paid, that is a founder financial gate | unknown | **not readable** |
| SaaSHub, AlternativeTo, Futurepedia | — | — | — | **not checked**. Candidates only |

**Copy for the four-field directories:** name `Agent.ceo` · website `https://agent.ceo` · description =
the short description above · email = G3.

## 7. Afterwards: what we read

- **Profiles live:** count of URLs that return 200 and show Agent.ceo (baseline 0), checked weekly against
  a fabricated product slug on the same site that must return 404.
- **M3 (answer-engine presence):** whether any of these profiles appears in answers to the six Ghost-Agent
  questions, on the Friday read.
- **Review requests:** none. Asking customers for reviews is a separate founder decision, and G2 penalises
  paid reviews.

## Sources (read 2026-09-13)

- Product Hunt help, "How to post a product": https://help.producthunt.com/en/articles/479557-how-to-post-a-product
- G2 create a profile: https://sell.g2.com/create-a-profile
- Third-party G2 field guide: https://wheretosubmit.org/guides/g2-submission-guide
- Capterra for vendors: https://www.capterra.com/vendors/ · vendor FAQ: https://www.capterra.com/faq/faqs-vendors/
- AiAgents.Directory submit: https://aiagents.directory/submit/
- Website facts: https://agent.ceo/pricing, https://agent.ceo/agents, https://agent.ceo/about (and website#1079 for the corrected /about)
