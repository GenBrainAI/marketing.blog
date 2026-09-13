# Marketing weekly report — week ending 2026-09-13

Row `task-e0bcb4f4` · verifier ceo · template: [`weekly-report-template.md`](weekly-report-template.md). This is the
**baseline** week: nothing has been published or sent yet, so every later week is compared with these numbers.
Measured 2026-09-13 ~22:05–22:20Z by marketing. **Nothing sent.**

## 1. The four numbers

| # | Metric | This week | Last week | Door used | Control → read | Known-positive → read |
|---|---|---|---|---|---|---|
| M1 | Third-party mentions of agent.ceo | **0** | — (first read) | Web search `"agent.ceo" GenBrain`: 8 results. 6 are agent.ceo pages, 1 is the founder's own LinkedIn (owned, not third-party), 1 is Genpact (unrelated). A second door, `"agent.ceo" -site:agent.ceo AI agents organization`, returned 7 results and none named our product. A bare `"agent.ceo"` search returned namesakes (theagent-ceo.com, theceoagent.ai, a GitHub "ceo" repo), none about us | `"quorvanta.ceo" GenBrain`: 9 results, **0** name quorvanta ✅ | agent.ceo's own pages: **6** ✅ (the engine indexes our domain) |
| M2 | Directory / review profiles live | **0** | — | (a) site-restricted web search across Product Hunt, G2, Capterra, There's An AI For That, AlternativeTo and SaaSHub: **0** Agent.ceo listings. (b) `aiagents.directory/agent-ceo/` 404 · `aiagentsdirectory.com/agent/agent-ceo` 404 · `futurepedia.io/tool/agent-ceo` 404 | `quorvanta-ceo` on (b): 404 · 404 · 404 ✅ | `crewai`: (a) listings on Product Hunt, G2 and There's An AI For That; (b) 200 · 200 · 200 ✅ |
| M3 | Unsolicited inbound requests | **2** (September) | — | The founder's own count as relayed by the CEO on this row: two design-partner inbounds in September. His mailbox was **not** read | — | — |
| M4 | Replies to awareness sends | **0 (no sends)** | — | No awareness send has happened. The October note is a draft (`awareness-note-2026-10.md`) | — | — |

**What the instruments cannot see:**

- Product Hunt, G2, Capterra, There's An AI For That, SaaSHub and AlternativeTo answer **403** to a direct `curl` from
  the pod, for our slug and for the control alike. For those sites M2 rests on door (a), the web search, and its
  crewai known-positive shows that door works. A profile created in the last few days may not be indexed yet.
- The guessed slugs in (b) show absence under **that slug** only. The known-positive proves the URL pattern, not that
  a listing could not sit under another slug. Door (a) covers that case for the large sites.
- M1 is one search engine on one day. It sees no forums, Slack communities or private newsletters.

**Two baselines that disagree with the restart plan, recorded rather than smoothed over:**

- M3: restart plan §7 says baseline **1** (MySched). The founder's count relayed on this row is **2** September
  design-partner inbounds. This report uses 2 because the founder's own count is the defined door. The CEO can say
  whether MySched is one of the two.
- M4: §7 gives "0 from 128 cold follow-ups". `awareness-note-2026-10.md` says touches 1–3 got "0–1 genuine replies".
  Neither was an awareness send, so the awareness-send baseline is 0 either way.

## 2. Published this week (served, not merged)

**Nothing published.** Every public-facing change is merge-held for the founder's go:
marketing.blog#11, website#1079, #1080, #1082 and #1085 are all `OPEN`, checked 2026-09-13 ~22:15Z with `gh pr view`.
The article-1 URL `agent.ceo/blog/your-company-is-already-a-graph` was 404 at ~21:10Z (founder pack §2).

Merged this week, internal only (not served to visitors): marketing.blog#12 (content calendar and publication
mechanics), #13 (founder pack and stg SEO findings), #14 (awareness note draft, off-page list, week-2 LinkedIn draft).

## 3. Waiting for the founder

| Item | His go does | Needed by |
|---|---|---|
| [marketing.blog#11](https://github.com/GenBrainAI/marketing.blog/pull/11) | Six Ghost-Agent pages + article 1, hand-ported to the website | Wed 09-16 launch |
| [website#1079](https://github.com/GenBrainAI/agent-ceo-website/pull/1079) + `./deploy.sh` | llms.txt and a truthful /about. Clears directory gate G1. Open: F2 (email), F3 | before any directory submission |
| [website#1080](https://github.com/GenBrainAI/agent-ceo-website/pull/1080) | Posts 1–10, 09-21 → 10-02 | Fri 09-18 |
| [website#1082](https://github.com/GenBrainAI/agent-ceo-website/pull/1082) | Posts 11–20, 10-05 → 10-20 | 10-02 |
| [website#1085](https://github.com/GenBrainAI/agent-ceo-website/pull/1085) | Posts 21–30, 10-21 → 11-05 | 10-20 |
| LinkedIn post 1 (`founder-pack-2026-09-14.md` §2) | His first post, from article 1. Its link must serve 200 first | after #11 is live |
| `off-page-submissions.md` rulings G2 (free hours) and G3 (contact email) | Unblocks G2, Capterra, Product Hunt and directory submissions. **The first thing that can move M2** | no date |
| `awareness-note-2026-10.md` | Send / edit / skip, from his inbox. **The only thing that can move M4** | on or after Tue 10-06 |

## 4. Next week's drafts (week of 2026-09-14)

All already written and merge-held. No new drafting is planned for next week until the founder's go on the above.

| Planned date | Draft | Where |
|---|---|---|
| Wed 09-16 | Six launch-set pages (ghost agent problem, who owns an AI agent, audit trail later, builder leaves, "an AI did it", outgrow one person's head) | marketing.blog#11 |
| Week of 09-14 | LinkedIn post 1 (article 1) | `founder-pack-2026-09-14.md` §2 |
| 09-21 → 09-25 | Posts: graph engineering, offboard an agent, scoped API key, where a human should approve, agent inventory | website#1080 |

## 5. One line

Nothing moved, because nothing has shipped: M1 0 · M2 0 · M3 2 · M4 0 (no sends). The first number that can move
is M2, after G1–G3 clear and the founder submits a directory profile.
