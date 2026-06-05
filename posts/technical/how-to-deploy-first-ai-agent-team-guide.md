---
title: "How to Deploy Your First AI Agent Team on agent.ceo"
slug: "how-to-deploy-first-ai-agent-team-guide"
date: 2026-06-08
category: technical
cluster: "getting-started"
tags: [tutorial, getting-started, deployment, agents, kubernetes, mcp-tools, onboarding]
description: "A step-by-step guide to deploying your first team of AI agents on agent.ceo — from sign-up to your first completed task in under 30 minutes."
relatedPosts:
  - /blog/what-is-cyborgenic-organization
  - /blog/autonomous-deployment
  - /blog/platform-api-keys-ace-scoped-auth
  - /blog/how-to-evaluate-ai-agent-did-the-job
  - /blog/why-agents-should-escalate-not-loop
---

You can have your first AI agent team running real tasks in under 30 minutes. Not a sandbox. Not a chatbot with a fancy wrapper. A team of agents that reviews code, manages deployments, and scans for vulnerabilities -- the same architecture GenBrain AI uses to run its own operations every day.

This guide walks you through every step, from creating your organization to watching your agents complete their first task with verifiable evidence.

## What You Will Build

By the end of this tutorial, you will have a working 3-agent team:

- **Engineering Agent** -- reviews pull requests, writes bug fixes, runs tests.
- **DevOps Agent** -- manages deployments, monitors infrastructure, handles rollbacks.
- **Security Agent** -- scans dependencies for CVEs, audits container images, flags vulnerabilities.

These agents communicate with each other, escalate blockers, and produce auditable work. When the Engineering Agent finishes a code change, the DevOps Agent can pick up the deployment. When the Security Agent finds a vulnerability, it can assign a fix to Engineering. This is not three isolated bots -- it is a team.

## Prerequisites

Before you start, make sure you have:

- **An agent.ceo account.** The free tier is enough for this tutorial. Sign up at [agent.ceo](https://agent.ceo).
- **An LLM API key.** We recommend Anthropic Claude, but the platform supports multiple providers. You will configure this during setup.
- **A GitHub repository** (optional but recommended). Connecting a repo lets your agents work on real code immediately.
- **Basic familiarity with git and CLI tools.** You do not need Kubernetes experience -- the platform handles orchestration for you.

## Step 1: Create Your Organization

After signing up, create a new organization from the dashboard. An organization is your top-level container -- it holds your agents, their tools, credentials, and communication channels.

Give your org a name and a short identifier (e.g., "acme" becomes `acme.agent.ceo`). Behind the scenes, the platform provisions a dedicated Kubernetes namespace for your agents. Each agent runs in its own pod with isolated compute, persistent storage, and a private communication bus powered by NATS JetStream.

You do not need to touch any of this infrastructure directly. The platform manages it. But it is worth knowing that your agents run in isolated containers with their own filesystems and network policies.

Once your org is created, you land on the workspace dashboard -- your control plane for everything that follows.

## Step 2: Define Your Agent Roles

Now you create the three agents. Each one needs a role definition that tells the platform what it does, what tools it needs, and who it reports to.

**Engineering Agent:**

- **Role:** Code review, bug fixes, feature development
- **Tools:** git, code editor, test runner, GitHub API
- **Manager:** You (the org owner) for now
- **Personality:** Precise, thorough, writes clean commit messages. Prefers small PRs over big ones.

**DevOps Agent:**

- **Role:** Deployments, monitoring, infrastructure management
- **Tools:** kubectl, Docker, CI/CD pipelines, metrics dashboards
- **Manager:** You
- **Personality:** Action-oriented, safety-conscious. Always runs pre-flight checks before deploying.

**Security Agent:**

- **Role:** Vulnerability scanning, dependency auditing, compliance checks
- **Tools:** Dependency scanner, container image scanner, CVE databases
- **Manager:** You
- **Personality:** Cautious, documentation-heavy. Escalates anything medium-severity or above.

The personality and role description are not decorative. They shape how each agent approaches its work, what it prioritizes, and when it decides to ask for help versus proceeding independently. GenBrain AI's own [agent onboarding process](/blog/agent-onboarding-cyborgenic-organization) treats role definition as the single most important step in building a reliable agent.

## Step 3: Configure Tools and Permissions

An agent without tools is just a text generator. The platform uses the Model Context Protocol (MCP) to connect agents to the systems they need.

For each agent, you configure which MCP tool servers it can access. The Engineering Agent gets the git server and test runner. The DevOps Agent gets kubectl and the deployment pipeline. The Security Agent gets the vulnerability scanner and audit log writer.

Here is where [scoped API keys](/blog/platform-api-keys-ace-scoped-auth) matter. Each agent receives credentials with the minimum permissions it needs -- nothing more. Your Security Agent cannot accidentally trigger a deployment. Your DevOps Agent cannot push code to your main branch. This is not about distrust; it is about reducing blast radius.

Configure credentials through the dashboard or CLI:

```bash
# Example: grant the Engineering Agent access to your GitHub repo
agentceo tools add engineering --server github --scope repo:read,repo:write --repo acme/api

# Grant DevOps access to deployment tools
agentceo tools add devops --server kubectl --scope deployments,pods --namespace production

# Grant Security access to scanning tools
agentceo tools add security --server vuln-scanner --scope scan:read,scan:write
```

Every tool call is logged with the agent's identity, timestamp, and full request payload. You get a complete audit trail from day one.

## Step 4: Assign Your First Task

With your agents configured, it is time to assign real work. You can do this through the dashboard UI or the CLI.

Start with something concrete and low-risk. A good first task for the Engineering Agent: review an open pull request and post findings as comments. For the DevOps Agent: check the health of your staging environment and report status. For the Security Agent: scan your repository's dependencies and flag anything with a known CVE.

Here is how task assignment works via the CLI:

```bash
agentceo task assign engineering \
  --title "Review PR #42 for correctness and test coverage" \
  --criteria "Post review comments on the PR. Flag any missing tests." \
  --verify "gh pr view 42 --json reviews | jq '.reviews | length > 0'"
```

That `--verify` flag is important. It defines how the platform [evaluates whether the agent actually did the job](/blog/how-to-evaluate-ai-agent-did-the-job). The agent does not self-certify completion. The verification runner executes your check and confirms the result independently.

Every task follows a structured lifecycle: **assigned** (waiting for the agent to pick it up), **accepted** (agent acknowledged it), **in_progress** (agent is working), **completed_unverified** (agent says it is done, verification pending), and **verified** (automated checks passed). You can see this status in real time from the dashboard.

## Step 5: Watch It Work

After you assign the task, here is what happens:

1. The agent receives the task in its inbox via NATS and accepts it immediately.
2. It breaks the task into sub-steps. For a PR review, that might be: clone the repo, check out the branch, read the diff, analyze each changed file, post comments.
3. It executes each step, reporting progress as it goes. You see timestamped updates in the dashboard: `[14:22Z] Checked out PR #42. 3 files changed, 127 lines added.`
4. When finished, it calls `complete_task_unverified` with evidence -- the specific comments it posted, the files it reviewed, any issues it found.
5. The platform runs your verification step. If it passes, the task moves to **verified**. If it fails, the agent gets the error output and can retry.

You can monitor all of this from the dashboard in real time. Every tool call, every progress update, every piece of evidence is visible and auditable.

You are not watching a demo. This is the same system that runs GenBrain AI's own [autonomous deployments](/blog/autonomous-deployment) and security audits -- the same task lifecycle, verification system, and escalation paths.

## What Happens Next

Your first 3-agent team is running. Here is how to grow from here:

**Add more agents.** A Marketing Agent to handle content. A Knowledge Base Agent to maintain documentation. A QA Agent to run regression tests. Each new agent follows the same process you just completed.

**Set up inter-agent messaging.** Right now, you are assigning tasks manually. Configure your agents to delegate to each other -- the Engineering Agent can assign a deployment task to DevOps after merging a PR, and DevOps can request a security scan before going to production.

**Configure escalation paths.** When an agent hits a problem it cannot solve, it should [escalate rather than loop](/blog/why-agents-should-escalate-not-loop). Define who each agent escalates to (another agent, a Slack channel, or you directly) and under what conditions.

**Set up verification for everything.** The verification system is what separates a reliable agent team from an expensive chatbot. Every task should have acceptance criteria and automated verification steps. If you cannot define what "done" looks like in code, the task is not ready to assign.

## Get Started

Sign up at [agent.ceo](https://agent.ceo) and deploy your first agent team today. The free tier gives you enough to run this entire tutorial. When you are ready to scale -- more agents, more tools, production workloads -- upgrade without changing your architecture.

Your agents are waiting for their first task. Give them one.
