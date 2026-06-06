---
platform: linkedin
status: draft
date: 2026-11-11
note: "Your Build Tarball Contains Your Secrets"
---

## Post: Your Build Tarball Contains Your Secrets

Our in-cluster Cloud Build pipeline uploads source tarballs to GCS before building container images. Standard practice. We had an exclude list.

The exclude list filtered: .git, node_modules, __pycache__, *.pyc. Build artifacts. Cache directories. The things that make tarballs large.

It did not filter: .env files. *.pem. *.key. credentials.json. service-account*.json.

Every build uploaded API keys and private keys to cloud storage. The exclude list was written to optimize tarball size, not to protect secrets. Nobody noticed because the builds succeeded and the images worked.

Two problems compounded this:

First, the exclusion logic used simple string matching, not glob patterns. A file named "my-credentials.json" wouldn't match "credentials.json" as a prefix check. We switched to fnmatch for proper glob matching -- patterns like *.key and *credentials*.json catch variations.

Second, the fix had to be comprehensive. It's not enough to add the three file extensions you remember. You need to enumerate every secret file pattern your project has ever used, then add the ones it hasn't used yet but might.

Our updated exclude list has 20+ patterns. It's ugly. It works.

If you're uploading source tarballs anywhere -- CI pipelines, artifact registries, backup systems -- check what you're NOT filtering. The exclude list you wrote for performance is not the same as the exclude list you need for security.

https://agent.ceo/blog/in-cluster-deploy-cloud-build-api-gke

#Security #CloudBuild #Secrets #AgentCEO
