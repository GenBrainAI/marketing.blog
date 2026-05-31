#!/usr/bin/env bash
# marketing.blog build recipe — run by the generic cicd runner inside this repo
# checkout (already at $TAG). Ports the posts CHANGED in this tag's commit into
# agent-ceo-website/content/blog/*.mdx and pushes main (the website's deploy.yml
# then runs gcloud run deploy). Env: REPO TAG SHA GITHUB_TOKEN.
set -euo pipefail
WEBSITE_REPO="${WEBSITE_REPO:-GenBrainAI/agent-ceo-website}"
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
log(){ echo "[blog-build $(date -u +%H:%M:%S)] $*"; }
: "${GITHUB_TOKEN:?GITHUB_TOKEN required}"
url(){ echo "https://x-access-token:${GITHUB_TOKEN}@github.com/$1.git"; }

CHANGED="$(git diff --name-only HEAD~1 HEAD -- 'posts/**/*.md' 2>/dev/null || true)"
[ -z "$CHANGED" ] && CHANGED="$(git show --pretty='' --name-only HEAD -- 'posts/**/*.md' 2>/dev/null || true)"
if [ -z "$CHANGED" ]; then log "no changed posts in ${TAG:-HEAD} — nothing to publish"; exit 0; fi
log "changed posts: $(echo "$CHANGED" | tr '\n' ' ')"

git clone --quiet --depth 1 "$(url "$WEBSITE_REPO")" "$WORK/web"
for p in $CHANGED; do
  slug="$(basename "$p" .md)"
  python3 "$HERE/blog_md_to_mdx.py" --src "$p" --dst "$WORK/web/content/blog/$slug.mdx"
done
cd "$WORK/web"
git config user.email "cicd@agent.ceo"; git config user.name "CICD Runner"
git add content/blog
if git diff --cached --quiet; then log "website already matches source — nothing to deploy"; exit 0; fi
git commit --quiet -m "blog: publish from ${REPO:-marketing.blog}@${TAG:-tag} [cicd]"
git push --quiet "$(url "$WEBSITE_REPO")" HEAD:main
log "pushed ${WEBSITE_REPO} main → website deploy.yml will build + gcloud run deploy. Verify: https://agent.ceo/blog"
