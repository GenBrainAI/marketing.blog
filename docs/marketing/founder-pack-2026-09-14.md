# Founder pack — week of Mon 2026-09-14

Row `task-f2e200a6` · verifier ceo · **nothing here is sent or posted by an agent.** You improve,
you give the go, you post. Calendar: [`content-calendar-2026-09-14.md`](content-calendar-2026-09-14.md).

## 1. Waiting for your go (one line each)

| PR | What your merge does | Your go |
|---|---|---|
| [marketing.blog #11](https://github.com/GenBrainAI/marketing.blog/pull/11) | Six Ghost-Agent pages + article 1 + channel plan. On go, marketing hand-ports them into a website PR for **Wed 09-16**. Open choice: article 1 optional sentence A (present tense). | go / edit / hold · A yes / no |
| [website #1079](https://github.com/GenBrainAI/agent-ceo-website/pull/1079) | llms.txt + llms-full.txt on live pricing, and a truthful /about. Prod changes only when you run `./deploy.sh`. Open: F2 publish `moshe@agent.ceo`? · F3 say "production is a working cluster"? | go · F2 · F3 |
| [website #1080](https://github.com/GenBrainAI/agent-ceo-website/pull/1080) | Posts 1-10. Each goes live on its own date, **09-21 → 10-02**, after one merge + one deploy. Merge **after #11 is ported**; 3 posts link to two #11 pages. | go by Fri 09-18 |
| [website #1082](https://github.com/GenBrainAI/agent-ceo-website/pull/1082) | Posts 11-20, **10-05 → 10-20**, same mechanics. Not needed until 10-02. | go by 10-02 |

## 2. Your first LinkedIn post (from article 1)

Edit freely. It is your voice, not ours. 196 words. One product truth. One question.

> Open any process manual in your company. A purchase order arrives. Someone checks the budget, a
> second person approves, legal sees the big ones, finance pays.
>
> That is a graph: steps, hand-offs, and a decision at every junction.
>
> For a hundred years those junctions were people. Then some became rules in software. Now a
> junction can be an agent, and you choose which kind. A person. An AI that owns the junction. An
> agent from another company, reached over an open protocol. Or a person who decides, junction by
> junction, whether they are adding judgement or just applying a rule.
>
> That last one is the question I keep asking inside our own company. Most approval steps turn out
> to be a rule wearing a person.
>
> One junction already works the way I want all of them to: in agent.ceo, an agent's proposal
> waits until a person approves or rejects it, and the decision is kept.
>
> Drawing the whole graph, versioning it and handing it to another team is what we are building
> toward. The longer version: https://agent.ceo/blog/your-company-is-already-a-graph
>
> Which approval step in your company is a real judgement call, and which is a rule wearing a person?

**The one product truth:** a proposal waits for an admin, who approves or rejects it, and the
decision persists. Readiness run on stg 2026-09-13 03:47Z, **Approvals PASS** (agent-hub
`docs/org/plan.md`, row "Readiness runs on stg"). No agent can present a prod session, so prod is
your statement. Nothing else in the post is a product claim.

**Before you post:** the link must be live. Today it is 404 on both hosts (checked 2026-09-13
~21:10Z). It serves after #11 is ported and deployed. Check with:
`curl -s -o /dev/null -w "%{http_code}\n" https://agent.ceo/blog/your-company-is-already-a-graph`
(needs `200`).

## 3. Week 1 — what you do, and when (≈ 25 min in total)

| Day | You | Marketing (no sends) |
|---|---|---|
| **Mon 09-14** | Go on #11 (+ A yes/no). Edit the LinkedIn post above. *10 min* | On go: hand-port #11's six pages + article 1 into a merge-held website PR, claim-checked |
| **Tue 09-15** | Merge that PR and run `./deploy.sh`. *5 min* | Check each of the 7 URLs on stg, and on prod after your deploy, against a fabricated slug (404) |
| **Wed 09-16** | Post the LinkedIn draft once the link reads 200. *2 min* | Note on the row: 7 URLs + status codes |
| **Thu 09-17** | Send a personal note from your own inbox to anyone who engaged. No ask. *5 min* | Draft those notes on request, as a row note only |
| **Fri 09-18** | Send marketing 2 numbers: comments+reshares from outside your network, and new followers/requests (M2). Go on #1080 (+ #1079 whenever). *3 min* | Weekly 5-line note: M1 inbound, M2 your numbers, M3 = answer-engine presence on the 6 questions (baseline 0/6) |

**If the go on #11 slips:** everything shifts by the same number of days. #1080's first date is
09-21, so if #11 is not live by then, move #1080's dates in-branch before merging. That avoids two
links landing on /blog.

## Also for fullstack (not for you)
Technical SEO readings on stg: [`seo-findings-stg-2026-09-13.md`](seo-findings-stg-2026-09-13.md).
