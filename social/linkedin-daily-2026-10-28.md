---
platform: linkedin
status: draft
date: 2026-10-28
note: "Concept — Docker image CLI version staleness"
---

## Post: Your Docker Image Bakes a CLI Version. Your Pod Runs For Weeks.

There is a subtle problem with long-lived Kubernetes pods that most teams do not think about until it causes issues.

Your Docker image bakes in whatever CLI tool version was latest at build time. That is fine for containers that restart frequently. But what about pods that run for days or weeks between image rebuilds?

We run AI agents as long-lived pods. Each agent relies on a CLI tool that the upstream vendor updates frequently -- new features, bug fixes, performance improvements. Our Docker image snapshots whichever version was current at build time, and then the agent runs on that version for weeks.

The gap between the baked-in version and the latest release grows wider every day. Our agents slowly fall behind on capabilities that could make them more effective.

The obvious fix -- rebuild and redeploy the Docker image just for a CLI update -- creates its own problems. With ReadWriteOnce PVCs and strategy: Recreate, every redeploy means downtime. You do not want to take an agent offline just to pick up a minor CLI update.

What you need is a self-update mechanism. Something that runs between sessions, does not disrupt live processes, handles failures gracefully (a bad update should not brick the agent), and does not add meaningful startup delay.

Tomorrow, we will show you exactly how we built one.

Read more: https://agent.ceo/blog/outer-loop-shell-script-keeps-agents-alive

#Docker #Kubernetes #CLITools #AgentCEO
