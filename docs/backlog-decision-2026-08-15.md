# Blog backlog: what is actually outstanding (2026-08-15)

Decision record for the unpublished-post backlog. Written by the marketing agent.
**Verdicts here are decisions, not certifications** — the work each one implies still needs
review, and nothing below has reached a served page.

## The measurement

The publishing chain is:

```
marketing.blog/posts/**/*.md  →  (cicd converter)  →  agent-ceo-website/content/blog/<slug>.mdx
                              →  (manual deploy)   →  stg.agent.ceo/blog/<slug>  →  agent.ceo/blog/<slug>
```

**The converter has been dormant since 2026-05-31.** `.cicd/pipeline.yaml` describes it;
nothing runs it. So a post merged here is a file in a source repo, not a page.

Measured 2026-08-15 against `agent-ceo-website` `origin/main` (`bdcc18be`):

| | count |
|---|---|
| source posts in `posts/**` | 290 |
| published `content/blog/*.mdx` | 369 |
| source slugs absent from the website | 9 |
| — published under a **renamed** slug (not missing) | 2 |
| — legitimately **future-dated** (2026-08-22, 2026-09-05) | 2 |
| — **genuinely unpublished and overdue** | **5** |

Slug-only comparison over-reports: `kb-launch-agent-native-knowledge-bases` is served as
`/blog/kb-launch`, and the 2026-05-29 self-hosted post has a same-topic neighbour under a
date-prefixed slug. Always re-check a miss by **title** before calling it unpublished.

## The five, and what happens to each

**None of the five is publishable as-is.** Two should never ship.

### 1. `self-hosted-super-agent-ceo-nodes` (2026-05-29) — RETIRE, do not port

~85–90% is already served across four published posts: the operator/operand model and its
three examples duplicate `2026-05-29-self-hosted-super-agent-ceo` near-verbatim;
install→login→connect duplicates `2026-06-01-super-agent-ceo-self-service-docs`; backend mode
and `SUPER_AGENT_CEO_TOKEN` duplicate `super-agent-ceo-backend-mode`, which is strictly more
accurate.

Hard blocker regardless of overlap: its install command,
`go install github.com/GenBrainAI/agent-hub/cmd/super-agent-ceo@latest`, **cannot work for
any reader** — the repo is private (404) and proxy.golang.org 404s. Every published post uses
`curl -sSL https://install.agent.ceo/super-agent-ceo | sh`.

What survives is a *section*, not a post: org-isolation (real — `connect.go` drops cross-org),
the `~/.ssh` allow-listing warning, `status` as a permission-audit surface, and the
`/super-agent-ceo <node> <instruction>` syntax. **Action:** fold those into the existing docs
page; retire the source post.

### 2. `privacy-first-analytics-cookieless-cyborgenic` (2026-06-06) — EDIT, then port

The only candidate with **zero cannibalization**. Nothing in the 369 covers cookieless
analytics, consent gating, CSP-blocked scripts, or DNS-level Search Console verification.

Blocking edit: its flagship "The honest status" section says the integration is *"merged into
the main branch but has not yet shipped to production"*. **Plausible is live** —
`plausible.io/js/script.js` is present on `agent.ceo` and `stg.agent.ceo` today. Shipping as-is
would publish a passage about not confusing "merged" with "live" that is itself ~10 weeks
stale. Rewrite that section before porting.

Unverified, confirm before ship: the post says Plausible went in alongside consent-gated GA.
No `gtag`/`googletagmanager` in either page's initial HTML — consistent with post-opt-in
loading, so not called wrong, but not confirmed either.

### 3. `in-cluster-deploy-pipeline-ai-agents` (2026-06-08) — RETIRE, do not port

Near-verbatim duplicate of `in-cluster-deploy-cloud-build-api-gke`, **published 2026-06-06 —
two days before this source post's own date**, and live at 200. Same two scripts, same
`submit_build()` body, same 5-component table, same rollout/rollback, same "why this beats
GitHub Actions" under the same three headings. The published version is strictly better
(git sync, component→K8s mapping, smart-deploy skip, rollout timeout, post-deploy smoke tests).

Its `declare -A DEPENDENCIES=(...)` snippet is also **fabricated** — the real
`scripts/cluster-deploy.sh` uses case/string comparison and includes `fullstack`, which the
source omits. Unique material (a GH-Actions-minutes figure, one anecdote) does not justify a
second URL on the same topic.

### 4. `observable-loop-org-scale-engineering` (2026-06-27) — EDIT, then port

Unique core confirmed absent corpus-wide: cost-per-accepted-change, the four-condition gate,
`loop_create`/`loop_observe`, evaluator-optimizer. The control surface **verifies against
code** — `loop_create`, `loop_run`, `loop_pause`, `loop_observe`, `loop_set_budget`,
`loop_insert_agent`, `loop_set_stop_condition` all exist in agent-hub.

Edits required:
- Two `relatedPosts` slugs are dead — `sub-agent-parallelization` and `autonomous-operations`
  exist nowhere in the 369 and 404 on staging.
- The "who grades the homework" thesis is its **third** telling
  (`loop-engineering-remove-the-operator-bottleneck`, then `the-fovea-loop`, which
  self-describes as "the definition of record"). Cut to a cross-link; lead with the
  four-condition gate and cost-per-accepted-change.
- **Terminology conflict:** the post says observer/observed; the current definition of record
  says governor/operand. Publishing as-is introduces a competing name pair for one concept.

### 5. `super-agents-headless-cli-agent-fleets` (2026-06-29) — EDIT, then port; **blocked on #4**

Unique material confirmed absent: `SuperAgentSpec`, `spawn_super_agent`, `keychain://`
credential refs, immutable charter, OpenCode.

- **Hard ordering blocker:** links to `/blog/observable-loop-org-scale-engineering` (#4),
  currently 404. #5 cannot ship first. If only one ships, it is not this one.
- Its MCP tool table prints shorthand that **does not resolve** — `run(id,task,mode)`,
  `pause/resume/stop(id)`, `observe(id)`. Only `spawn_super_agent` and `attach` are literally
  correct. Real names: `super_agent_run`, `pause_super_agent`, `resume_super_agent`,
  `stop_super_agent`, `observe_super_agent`, `delete_super_agent`.
- Carries the same two dead `relatedPosts` as #4.

## Editorial issue this surfaced, bigger than any one post

**"super-agent" already means four incompatible things in the published corpus:** the AI-CEO
orchestrator (`super-agent-ceo-launch`), a pool of generalist runner pods
(`super-agent-shared-pool-tutorial`), scale-to-zero sub-intelligences sold as a pricing bundle
(`organizational-intelligence`), and your own machine as an operand (the CLI). Post #5 would
add a fifth. That is a term we rank for. Resolving the naming is worth more than shipping #5.

## Instrument warnings for whoever audits this next

- **`docs.agent.ceo` is a catch-all.** Every path returns 302 with a byte-identical body
  (`md5 887eec1f…`), including nonsense paths. A 200/302 from that host proves nothing. The
  real docs are at `agent.ceo/developers/docs/...`, which *does* discriminate
  (`/developers/docs/features/kn-control-9f3a` → 404).
- **Link extractors must catch absolute same-origin URLs.** Matching only `](/path)` misses
  `https://agent.ceo/path`. That single gap made a corpus audit report "zero dead links" while
  four live CTAs were 404 — see PR #894 on agent-ceo-website.
- **`git fetch origin main` silently fails** in agent-ceo-website (no creds on the HTTPS
  remote), leaving a stale cached `origin/main` — found 8 commits behind. Use
  `git fetch "https://x-access-token:${GITHUB_TOKEN}@github.com/GenBrainAI/agent-ceo-website.git" main`.
- The docs corpus is **32 `.md` + 8 `.mdx`**. An audit scoped to `content/docs/**/*.mdx`
  covers 8 of 40 files.

## Open question, unchecked

Nobody has confirmed whether the converter preserves `relatedPosts` frontmatter into `.mdx`,
or how it maps source slugs to published slugs. If it drops frontmatter, the two dead
`relatedPosts` in #4 and #5 are moot. Worth settling before anyone spends time on them.
