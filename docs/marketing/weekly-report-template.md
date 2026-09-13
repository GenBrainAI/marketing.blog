# Marketing weekly report — week ending YYYY-MM-DD

Copy this file to `weekly-report-YYYY-MM-DD.md` (the Sunday that ends the week) and fill it in. It takes about 10
minutes. Leave a cell as `not read` if you did not run its check. Never carry last week's number forward
unread, because a number that has not moved looks the same as a check that was never run.

Metrics: restart plan §7 (agent-hub `docs/marketing/restart-plan-2026-09-12.md`). No analytics access is needed.

## 1. The four numbers

Each row has a **door** (the exact check), a **control** (a made-up name through the same door, which must read
0) and a **known-positive** (something that must read ≥ 1). If the control reads anything but 0, or the
known-positive reads 0, write `instrument broken` instead of the number.

| # | Metric | This week | Last week | Door (run exactly) | Control → must be 0 | Known-positive → must be ≥ 1 |
|---|---|---|---|---|---|---|
| M1 | Third-party mentions of agent.ceo | | | Web search `"agent.ceo" GenBrain`. Count only results that are **not** on agent.ceo, **not** the founder's or GenBrain's own profiles, and actually **name our product** | `"quorvanta.ceo" GenBrain`: results that name quorvanta | results on agent.ceo itself |
| M2 | Directory / review profiles live | | | (a) Web search `"agent.ceo" site:producthunt.com OR site:g2.com OR site:capterra.com OR site:theresanaiforthat.com OR site:alternativeto.net OR site:saashub.com`. (b) `curl -s -o /dev/null -w '%{http_code}'` on `aiagents.directory/agent-ceo/`, `aiagentsdirectory.com/agent/agent-ceo`, `futurepedia.io/tool/agent-ceo`. (c) Every URL listed in `off-page-submissions.md` once it has one. Count the profiles that show Agent.ceo | same doors with `quorvanta-ceo` | same doors with `crewai` (a: listings; b: 200) |
| M3 | Unsolicited inbound requests | | | The founder's own count, as he reports it to the CEO. **No agent reads his mailbox** | — | — |
| M4 | Replies to awareness sends | | | Sends made this week (founder's count) and genuine replies to them. Opt-outs are not replies | — | if sends = 0, write `0 (no sends)` |

Cumulative, not weekly: M1 and M2 count what exists today. M3 and M4 count what arrived this week.

## 2. Published this week (served, not merged)

Count only what a visitor can load. For each item: URL, and `curl -s -o /dev/null -w '%{http_code}'` = 200.

| Date | What | URL | HTTP |
|---|---|---|---|
| | | | |

If nothing is served, write **Nothing published** and one line on why.

## 3. Waiting for the founder

One line each: the PR or file, what his go does, and the date it is needed by.

| Item | His go does | Needed by |
|---|---|---|
| | | |

## 4. Next week's drafts

What marketing will have ready for his go next week (slug or file, and the date it is planned for).

| Planned date | Draft | Where |
|---|---|---|
| | | |

## 5. One line

What moved, or `nothing moved`, and why.
