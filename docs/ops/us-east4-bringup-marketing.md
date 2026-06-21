# us-east4 Bring-Up — Marketing / Blog Publishing Re-Wire

**Owner:** Marketing · **Date:** 2026-06-21 · **Authorized by:** founder (via CEO, us-east4 bring-up prep)
**Purpose:** make blog publishing work on **day one** in the greenfield us-east4 project, and lock in the working convention that nearly cost us content during the migration.

> ⚠️ **Replace `<US_EAST4_PROJECT_ID>` throughout with the real new project id** (confirm with CTO/DevOps — greenfield us-east4 project). Everything else is concrete.

---

## 1. How blog publishing actually works (current, europe-west4)

The publish chain — grounded in `.github/workflows/cicd-trigger.yml` + `.cicd/build.sh`:

1. Push a **`cicd_*` git tag** to `marketing.blog` (push to a branch does NOT publish — tag only).
2. GitHub Action `cicd-trigger.yml` runs → authenticates to GCP with GitHub secret **`CICD_PUBLISHER_KEY`** (a service-account key JSON).
3. Action publishes a BuildRequest JSON to **Pub/Sub topic `cicd-build-requests`** in **project `agent-hub-ceo`** (← currently hardcoded).
4. A generic **cicd runner** subscribed to that topic checks out the repo at the tag and runs **`.cicd/build.sh`**.
5. `build.sh`: finds posts changed in the tag's commit → converts `posts/**/*.md` → `.mdx` via `.cicd/blog_md_to_mdx.py` → clones **`GenBrainAI/agent-ceo-website`** (env `WEBSITE_REPO`, auth via `GITHUB_TOKEN`) → writes `content/blog/<slug>.mdx` → commits + pushes website `main` → the website's `deploy.yml` runs `gcloud run deploy`. Verify: `https://agent.ceo/blog`.

**Slug rule:** `<slug>` = post filename without the `.md` (and we name posts `YYYY-MM-DD-<slug>.md`; the published slug is the clean part).

## 2. What must be RECREATED in the new project (`<US_EAST4_PROJECT_ID>`)

| # | Resource | Action |
|---|---|---|
| 1 | Pub/Sub topic `cicd-build-requests` | Create in `<US_EAST4_PROJECT_ID>` |
| 2 | Publisher service account + key | New SA with `roles/pubsub.publisher` on the topic; export key JSON → set as GitHub secret `CICD_PUBLISHER_KEY` (org or `marketing.blog` repo) |
| 3 | cicd runner + subscription | Runner (DevOps/CTO-owned) must run in/against the new project, **subscribed** to the new topic, and hold a `GITHUB_TOKEN` that can push to `GenBrainAI/agent-ceo-website` |
| 4 | Workflow project param | Stop hardcoding the project — see §3 |
| 5 | Website deploy (`agent-ceo-website` `deploy.yml`) | Owned by Fullstack/DevOps; its `gcloud run deploy` target must point at the new region/project (out of marketing scope — flagged for that handover section) |

GitHub repos (`marketing.blog`, `agent-ceo-website`) are unaffected by the region move — they live on GitHub and survive.

## 3. Parameterize the workflow (one-time fix so future moves are config-only)

Replace the hardcoded project (and make the topic a variable too) in `.github/workflows/cicd-trigger.yml`. Merge-ready version provided at **`.cicd/cicd-trigger.us-east4.yml`** in this branch. The only line that changes:

```diff
-          gcloud pubsub topics publish cicd-build-requests --project agent-hub-ceo --message="$REQ"
+          gcloud pubsub topics publish "${CICD_TOPIC:-cicd-build-requests}" --project "$CICD_PROJECT" --message="$REQ"
```
with, in the job step env:
```yaml
        env:
          CICD_PROJECT: ${{ vars.CICD_PROJECT }}     # set repo/org variable = <US_EAST4_PROJECT_ID>
          CICD_TOPIC: ${{ vars.CICD_TOPIC }}         # optional; defaults to cicd-build-requests
```
Set GitHub **Actions variable** `CICD_PROJECT=<US_EAST4_PROJECT_ID>` on the repo (or org). After cutover, future region moves are just a variable change — no code edit.

## 4. Exact re-wire steps (gcloud)

```bash
PROJECT=<US_EAST4_PROJECT_ID>
# 1. Topic
gcloud pubsub topics create cicd-build-requests --project "$PROJECT"
# 2. Publisher SA + key
gcloud iam service-accounts create cicd-publisher \
  --project "$PROJECT" --display-name "CICD Pub/Sub publisher"
gcloud pubsub topics add-iam-policy-binding cicd-build-requests --project "$PROJECT" \
  --member "serviceAccount:cicd-publisher@${PROJECT}.iam.gserviceaccount.com" \
  --role roles/pubsub.publisher
gcloud iam service-accounts keys create /tmp/cicd-publisher-key.json \
  --project "$PROJECT" --iam-account "cicd-publisher@${PROJECT}.iam.gserviceaccount.com"
# → set the JSON as GitHub secret CICD_PUBLISHER_KEY (gh secret set CICD_PUBLISHER_KEY < /tmp/cicd-publisher-key.json), then shred the local file
# 3. Subscription for the runner (push or pull, per runner design — DevOps/CTO)
gcloud pubsub subscriptions create cicd-build-requests-sub \
  --project "$PROJECT" --topic cicd-build-requests
# 4. Set the workflow project variable
gh variable set CICD_PROJECT --repo GenBrainAI/marketing.blog --body "$PROJECT"
```

## 5. Smoke test (after cutover, before relying on it)
1. Create a trivial throwaway post under `posts/technical/` on a branch, merge to `marketing`.
2. Tag it: `git tag cicd_smoke-$(date +%s) && git push origin <tag>`.
3. Confirm: Action runs green → BuildRequest in Pub/Sub → runner builds → `agent-ceo-website` `main` gets the `.mdx` → website redeploys → post 200 at `https://agent.ceo/blog/<slug>`.
4. Remove the throwaway post + tag.

## 6. Working convention (root-cause fix — MANDATORY going forward)
**Marketing works directly in the cloned GitHub repos, NOT the pod-local `/agent-data/workspace`.**
- The old workspace had **no git remote** → drafts there were local-only and were nearly lost at europe-west4 teardown (rescued to `marketing.blog` `drafts/2026-06-21-handover-preserved/` @ `79f2829`).
- Blog drafts → `marketing.blog/posts/...` (or `drafts/` if not ready to publish). Social drafts → `marketing.blog/social/`. Commit + push every session. The commit/push is the durable artifact; nothing pod-local is assumed to survive.

## 7. Held credits announcement — GA gate (unchanged)
The Prepaid Credits + Platform Keys launch announcement stays **HELD / GA-gated**. It publishes **only on founder GA sign-off, AFTER the new region is live + verified** and self-signup is confirmed open. Drafts preserved at `marketing.blog` `drafts/2026-06-21-handover-preserved/` (@ `79f2829`). Do not tag/publish it during bring-up.
