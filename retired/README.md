# retired/

Posts that were written but will **not** be published, with the reason recorded on each one.

## Why this directory sits outside `posts/`

Both automated consumers glob `posts/**/*.md` **recursively**:

- `.cicd/build.sh` — the converter that ports posts into `agent-ceo-website/content/blog`
- `scripts/generate-sitemap.py` — `glob.glob('posts/**/*.md', recursive=True)`

So a `posts/retired/` subdirectory would still be picked up, and the next converter run would
publish these anyway. Retirement has to be *structural* or it is decoration. Files here are
outside both globs and cannot be published by accident.

Nothing is deleted. The drafts stay in git history and in this directory, so a future decision
to revive one is a `git mv` away — it just cannot happen silently.

## What is here

| File | Retired | Why |
|---|---|---|
| `self-hosted-super-agent-ceo-nodes.md` | 2026-08-16 | Superseded — ~85–90% already served by four published posts, and its install command cannot work for any reader. |
| `in-cluster-deploy-pipeline-ai-agents.md` | 2026-08-16 | Near-verbatim duplicate of a post published **two days before this one's own date**, and it contains a fabricated code sample. |

Full reasoning for both, with the measurements behind it, is in
`docs/backlog-decision-2026-08-15.md`.

## Adding to this directory

Move the file here with `git mv`, add a `RETIRED` block at the top of the file stating the
date, the decision-maker, and the evidence, and add a row above. Do not delete posts — a
deleted post looks identical to one that was never written.
