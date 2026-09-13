# Monthly awareness note — October 2026 (DRAFT ONLY)

Row `task-388aca82` · verifier ceo · **DRAFT. No agent sends this, schedules it, or loads it into any tool.**
The founder decides whether it goes, edits it, and sends it from his own inbox. The CRM is his.

## What it is

One short note a month to the CRM's 73 emailable contacts (46 accounts). Restart plan channel 4:
*"news/feature notes, no ask"*. It carries **no ask**: no call to book, no offer, no price, no
"reply if interested". The only thing a reader can reply to is the opt-out, which email law requires.

Why it is this cautious: touches 1–3 went to 65 of these contacts and got 0–1 genuine replies out of
128 cold follow-ups. A fourth sales touch would spend what goodwill is left. A useful note once a
month does not.

## Send conditions (all must be true on the send date)

| # | Condition | How to check | Owner |
|---|---|---|---|
| 1 | Each link in the note returns `200` on agent.ceo | The loop below; a fabricated slug must return `404` | marketing checks, on request |
| 2 | The founder has decided the 65 stale Touch-4 rows (restart plan decision 2) | His ruling | founder |
| 3 | Bounced, opted-out and "not interested" contacts are removed | CRM suppression list | founder / seed-crm |
| 4 | Contacts already in a live conversation (e.g. a design partner, an inbound request for terms) get a personal email instead, not this note | Founder's judgement | founder |
| 5 | Sent from the founder's own inbox, one recipient per email (no visible list) | — | founder |

```bash
for p in /blog/your-company-is-already-a-graph /blog/what-is-the-ghost-agent-problem \
         /blog/should-an-ai-agent-verify-its-own-work /blog/how-to-offboard-an-ai-agent \
         /blog/zz-fabricated-slug; do
  printf "%s %s\n" "$(curl -s -o /dev/null -w '%{http_code}' https://agent.ceo$p)" "$p"
done
# needs 200 200 200 200 404
```

**Earliest sensible date: Tue 2026-10-06.** By then the week-1 set (09-16) and posts 1–10 (09-21 → 10-02)
are live, if the founder's go on marketing.blog#11 and website#1080 landed on schedule. If they slipped,
move the date by the same number of days. **Today (2026-09-13) all four article links return 404**,
because none of them is published yet.

## Subject line (pick one)

1. `What we wrote about AI agents in September`
2. `agent.ceo — a short note for October`

## The note (173 words, links excluded)

> Hi {{first_name}},
>
> A short monthly note on what we are building at agent.ceo. No action needed.
>
> In September we started writing in public about a problem most companies running AI agents now have:
> agents that keep running after the person who built them has moved on, on keys nobody tracks. It has a
> name, the ghost agent problem:
> https://agent.ceo/blog/what-is-the-ghost-agent-problem
>
> Three pieces from the month:
>
> - **Your company is already a graph.** Your processes are already steps, hand-offs and decisions, and
>   agents fit into that shape. https://agent.ceo/blog/your-company-is-already-a-graph
> - **Should an AI agent verify its own work?** The rule we run our own company by.
>   https://agent.ceo/blog/should-an-ai-agent-verify-its-own-work
> - **How to offboard an AI agent.** Five steps for when its owner leaves.
>   https://agent.ceo/blog/how-to-offboard-an-ai-agent
>
> One thing that works today: in agent.ceo, an agent's proposal waits until a person approves or rejects
> it, and the decision is kept.
>
> Moshe Beeri
> Founder, agent.ceo
>
> *You are receiving this because we have been in touch about agent.ceo. If you would rather not get this
> monthly note, reply "stop" and you will not hear from us again.*

## Claim check

| Sentence | Source |
|---|---|
| "an agent's proposal waits until a person approves or rejects it, and the decision is kept" | Readiness run stg 2026-09-13 03:47Z, **Approvals PASS** (agent-hub `docs/org/plan.md`, row "Readiness runs on stg"). Same sentence as the week-1 LinkedIn draft |
| "the rule we run our own company by" | agent-hub `CLAUDE.md` §3 "Never self-verify" (truth code I) |
| Ghost agent problem description | Industry framing of a named problem, not a product claim (truth code R/S in the calendar) |
| "Moshe Beeri, Founder" | Served on /about after website#1079 deploys |

**Deliberately absent:** any offer, beta price, pricing, meeting request, customer name, usage number,
audit-trail claim, free tier, and any product capability beyond the one Approvals sentence.

## No-ask check (run on the final text before sending)

```bash
sed -n '/^## The note/,/^## Claim check/p' awareness-note-2026-10.md \
  | grep -n -i -E "book|call|demo|schedule|offer|discount|price|\\$[0-9]|interested|let me know|reply if|trial|free|meet"
# expect: no output
```
On the note above this prints nothing (run 2026-09-13). The opt-out's "reply \"stop\"" is deliberately not in
the pattern. If the founder's edit makes this print a line, the note has become an ask.

## What we will read afterwards (no tracking pixels, no link shorteners)

- **M1:** replies other than "stop", and new conversations the founder names within 14 days. Marketing logs
  them on the row.
- **Opt-outs:** the count of "stop" replies. More than 5 of 73 means the note is unwelcome, and the next one
  is skipped and brought back to the founder.
