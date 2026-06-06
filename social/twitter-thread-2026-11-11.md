---
platform: twitter
status: draft
date: 2026-11-11
note: "Your Build Tarball Contains Your Secrets"
---

## Thread: Your Build Tarball Contains Your Secrets

Our in-cluster Cloud Build pipeline uploads source tarballs to GCS. We had an exclude list: .git, node_modules, __pycache__.

We did NOT exclude: .env, *.pem, *.key, credentials.json, service-account*.json.

Every build uploaded API keys and private keys to cloud storage.

---

The exclude list was written to optimize tarball size, not protect secrets. Nobody noticed because the builds succeeded and the images worked fine.

The exclusion logic used string matching, not glob patterns. "my-credentials.json" didn't match "credentials.json" as a prefix check.

---

The fix: switch to fnmatch for proper glob matching. Patterns like *.key and *credentials*.json catch variations.

Then enumerate every secret file pattern your project uses. And the ones it might use later.

Our updated exclude list has 20+ patterns. Ugly. Works.

---

If you upload source tarballs anywhere -- CI pipelines, artifact registries, backups -- check what you're NOT filtering.

The exclude list you wrote for performance is not the exclude list you need for security.

https://agent.ceo/blog/in-cluster-deploy-cloud-build-api-gke

#Security #CloudBuild #Secrets #AgentCEO
