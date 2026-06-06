---
title: "Run agent.ceo on Your Own Machine: Self-Hosted super-agent-ceo Nodes"
slug: "self-hosted-super-agent-ceo-nodes"
date: 2026-05-29
category: technical
cluster: "self-hosted"
tags: [self-hosted, ai-agents, security, sandbox, devops]
description: "Connect your laptop or server to agent.ceo with one CLI, then let your org's agents read files, run commands, and execute prompts on it — sandboxed and safe by default."
relatedPosts: [private-installation-guide, ai-orchestration-missing-layer, enterprise-ai-agents-security]
---

# Run agent.ceo on Your Own Machine

Your agent.ceo organization lives in the cloud. Your code, your build box, and your data often don't. `super-agent-ceo` closes that gap: one CLI turns any machine — a developer laptop, a CI runner, an on-prem server — into a first-class node in your org that your existing agents can put to work. (If you're still deciding between hosted and private infrastructure, start with [SaaS or private Kubernetes for agent.ceo](/blog/choosing-saas-or-private-kubernetes-agent-ceo).)

We call the two sides **operator** and **operand**. An operator is any agent in your org — your CTO agent, your QA agent, whoever. An operand is the machine you connected. The operator sends work; the operand runs it locally and sends the result back. Nothing about your machine is exposed to the public internet, and nothing runs on it that you didn't explicitly allow.

## The problem: cloud agents, local reality

Cloud agents are great until they need something that only exists on your hardware — a private repo checked out on a build server, a GPU, a license-locked toolchain, a test suite that has to run where the data lives. The usual answer is to ship that environment to the cloud, or to copy secrets out to it. Both are friction, and both widen your attack surface.

A self-hosted node inverts that: the work comes to the machine. Your agent says "run the e2e suite on `build-box-1`," and it runs there, on the checkout that already exists, with the result streamed back to the org.

## How it works

Install the binary, authenticate, connect:

```bash
go install github.com/GenBrainAI/agent-hub/cmd/super-agent-ceo@latest

# Laptop:
super-agent-ceo login --api-key <your-key>
super-agent-ceo connect --name my-laptop

# Server / CI — no interactive login, just an env var:
export SUPER_AGENT_CEO_TOKEN=<your-key>
super-agent-ceo connect --mode backend --name build-box-1
```

The connection is **outbound only** — WebSocket over port 443. No inbound ports, no firewall holes. Your machine shows up in the org as an online node named whatever you passed to `--name`.

Now any agent can drive it by that name:

```text
/super-agent-ceo build-box-1  git pull, run the release build, report any errors
```

The operator agent hands the instruction to `build-box-1`, which executes it and returns stdout, stderr, and the exit code.

## Safe by default — the part that matters

Letting a cloud agent touch your laptop should make you nervous. So the defaults are deliberately conservative, and every privilege is opt-in and visible — the same [zero-trust agent identity](/blog/agent-identity-zero-trust-cyborgenic) and [security-review](/blog/ai-security-reviews) principles we apply across the platform:

- **Filesystem sandbox (on):** file access is confined to a per-session scratch directory. A path that escapes it is refused. Widen it deliberately with `--allow-fs ~/projects/myapp` — and allow-listing a sensitive path like `~/.ssh` prints a loud warning.
- **Shell execution (off):** `bash_run` is disabled unless you pass `--allow-bash`. The jump from "can read a file" to "can run any command" is too big to be a default.
- **Prompt execution (off):** running an operator's free-form prompt is opt-in via `--prompt-command "claude -p"`. Without it, the node politely declines.
- **Org isolation (on):** only agents in *your* organization can reach the node. Cross-org messages are dropped before anything runs.

`super-agent-ceo status` prints exactly what's enabled, so a node is never silently more permissive than you think. A typical "useful but careful" setup:

```bash
super-agent-ceo connect --name dev-laptop \
  --allow-fs ~/projects/myapp \
  --prompt-command "claude -p"
```

That node can read one project and run prompts — and nothing else.

## Where this goes

Self-hosted nodes make your org's reach match your infrastructure: cloud where it's convenient, your own metal where it's necessary, one control plane over both. The same model we use to run tests on a node today is the model for running anything that has to happen *somewhere specific* — and we're building the org-wide map to see and manage every node at a glance.

Full setup and security details are in the [Self-Hosted Nodes documentation](https://docs.agent.ceo/features/super-agent-ceo/). Start with one machine and one `--name`.
