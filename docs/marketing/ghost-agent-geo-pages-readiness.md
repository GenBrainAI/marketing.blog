# Ghost-Agent GEO pages — readiness record (task-ae3b31f9, 2026-09-13)

**State: PUBLICATION-READY, MERGE-HELD for the founder's go. Nothing published.**
Source: `workspace/marketing/DRAFT-ghost-agent-articles.md` (2026-07-30). Files: `posts/marketing/<slug>.md`.

## One claim check per page — against the served stg product today

Rule: a page may say about agent.ceo only what stg serves today. The evidence below is re-runnable
by anyone. It is not read from a pod file.

| Page (slug) | The one agent.ceo claim on the page | Evidence on stg | Removed from the July draft |
|---|---|---|---|
| what-is-the-ghost-agent-problem | An agent is created inside an organization as a role (16 predefined or custom), not in a person's account | `curl -s https://stg.agent.ceo/agents` → 200, text "16 predefined roles ready to deploy … or create custom roles" (~19:30Z) | "acts under declared authority that is **recorded at the time of the action**" (audit log not served, see below); the 88%/21%/33% figures, which have **no publisher or URL anywhere in our files**. Replaced with OutSystems 94%/12% (URL 200, both figures present on the page today). |
| who-owns-this-ai-agent-registry-not-enough | You add an agent by choosing a role; the org's registry lists its registered agents | `/agents` as above + readiness run 2026-09-13 03:47Z **Registry PASS** (agent-hub `docs/org/plan.md`, row "Readiness runs on stg") | "an agent **cannot exist** without a role … the inventory is simply true" (runtime enforcement not measured). Added IBM 18% (URL 200, figure present). |
| can-you-add-an-audit-trail-to-ai-agents-later | An agent's proposal waits for an admin to approve/reject; the decision persists | Same run: **Approvals PASS** (admin rejects a pending proposal and sees the persisted decision) | The "industry coverage says retrofitted trails are weaker" line (no citable source on file). No claim that agent.ceo keeps a per-action audit trail. |
| what-happens-to-ai-agents-when-their-builder-leaves | An agent is a role (CTO, QA Engineer, custom) created inside the organization | `/agents` as above | "Transfer the role and the agents transfer with it — **memory, boundaries, and authority intact**" (no served handover journey; org `transfer-ownership` exists in code, not measured on stg) |
| why-an-ai-did-it-is-not-an-audit-answer | Agent = org role; a proposal waits for an admin's approve/reject; the decision persists | `/agents` + **Approvals PASS** | "**every** action carries the role that took it … written at the time" as a product claim |
| when-do-ai-agents-outgrow-one-persons-head | A loop is created, run, watched and stopped as one bounded sequence | Same run: **Loops PASS** (create/run/view/stop, founder's node bound as participant) | nothing (no product claim in the July draft) |

## Product defects found while checking (for the CEO to route. Marketing does not fix them.)

1. **Org audit log not served on stg.** `GET https://api.stg.agent.ceo/api/v1/organizations/<ORG>/audit-log`
   → `404 {"detail":"Not Found"}`, byte-identical to a fabricated route on the same org. The router
   (`packages/gateway/src/gateway/org_audit_log.py`) is not included in `app_routes.py`; the code
   itself is an **in-memory ring buffer of 1000 events**. Yet stg `/security` says "Audit logging of
   all agent actions" and stg `/llms.txt` says "append-only, tamper-resistant". The public claims go
   further than the product → cto (product) / fullstack (copy).
2. **stg `/.well-known/agent.json` returns 8 agents with empty `id` and `name`** (prod
   `api.agent.ceo` returns named roles). This is the first thing an A2A client or LLM reads. → cto.
3. Could not read topology or capabilities with the org key: 401 for my org and for a fabricated org,
   identical. That is **not evidence either way**, and no page relies on it.

## Meta, links, and publish mechanics

- Title = the question (H1 verbatim); `description` ≤ 160 chars, which the converter maps to `excerpt`; the
  `faq` frontmatter is a single Q&A whose answer is the page's visible bold opening. The website's
  `FaqJsonLd` emits FAQPage from it.
- Internal links, all measured 200 on **both** agent.ceo and stg.agent.ceo today: `/agents`,
  `/blog/agent-sprawl-governance-gap`, `/blog/agentic-ai-governance-control-plane`,
  `/blog/ai-agent-identity-access-management-non-human-workforce`. Control: `/blog/zz-fake-slug` 404.
  Avoided: `/blog/ai-agent-audit-trails-cyborgenic` and `/blog/agent-identity-zero-trust-cyborgenic`
  (307 → /blog, i.e. unpublished).
- **The six cross-link each other. Publish all six together, or they point at 404s.**
- **The converter would strip `faq`.** `.cicd/blog_md_to_mdx.py` emits only title/date/author/
  category/tags/excerpt. It is also dormant (B4). So publishing means a **hand-port** into
  `agent-ceo-website/content/blog/<slug>.mdx`, keeping `faq:`. After that, the website needs its manual deploy.
- **Overlap:** the live post `agent-sprawl-governance-gap` already carries the FAQ question "Why can't
  audit trails be added afterwards?". Page 3 is the question-shaped canonical, and it links there.
  Two FAQPage nodes will answer near-identical questions. The founder can accept this or drop that FAQ item.
- **CONTENT-STANDARDS exception needed:** the standards require ≥ 2 visuals and ≥ 1 code example per
  post. These pages are deliberately short Q&A pages for LLM citation and carry neither. They need a
  founder/CEO ruling. The alternative is to add one diagram each, which lengthens them.
- `date: "2026-09-13"` is a placeholder. Set it to the publish day on go. The website hides future-dated posts.
