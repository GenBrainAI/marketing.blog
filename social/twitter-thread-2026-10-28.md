---
platform: twitter
status: draft
date: 2026-10-28
note: "Concept — Docker image CLI version staleness"
---

## Thread: Your Docker Image Bakes a CLI Version. Your Pod Runs For Weeks.

Your Docker image snapshots a CLI version at build time.

Your Kubernetes pod runs for weeks.

The CLI vendor ships updates every few days.

See the problem?

---

We run AI agents as long-lived K8s pods. Each agent depends on a CLI tool that gets frequent upstream updates -- features, bug fixes, performance.

The Docker image locks in whatever version was current at build time. After two weeks, our agents are running stale binaries and missing improvements.

---

The obvious fix: rebuild and redeploy the image for every CLI update.

The problem with that fix: ReadWriteOnce PVCs force strategy: Recreate. Every redeploy = downtime. You do not want to take an agent offline just to bump a CLI version.

---

What you actually need: a self-update mechanism that runs between sessions, never disrupts live work, handles failures gracefully (bad update should not brick the agent), and adds no meaningful startup delay.

Tomorrow: exactly how we built one. PVC-stamped, time-gated, best-effort.

---

Read more: https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#Docker #Kubernetes #CLITools #AgentCEO
