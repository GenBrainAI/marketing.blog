---
title: "Getting Started with agent.ceo in 5 Minutes"
slug: "getting-started-agent-ceo"
date: 2026-05-10
category: technical
cluster: "getting-started"
tags: [getting-started, quickstart, onboarding, tutorial, agent-ceo]
description: "Get your first AI agent running on agent.ceo in under 5 minutes. Sign up, connect your tools, run discovery, and deploy your first autonomous agent."
relatedPosts: [first-ai-agent-team, connecting-ai-agents-github, configuring-cloud-discovery]
---

# Getting Started with agent.ceo in 5 Minutes

You have heard about autonomous AI agents transforming engineering organizations. Now it is time to experience it firsthand. This guide walks you through going from zero to a running AI agent in under five minutes, using agent.ceo's streamlined onboarding flow.

By the end of this tutorial, you will have:

- Created your agent.ceo account
- Connected your development tools
- Run an automated discovery scan of your infrastructure
- Deployed your first autonomous AI agent

Let's get started.

## Prerequisites

Before you begin, make sure you have:

- A GitHub account with at least one active repository
- Access to your team's Slack workspace (optional but recommended)
- A Jira or Linear project board (optional)
- 5 minutes of uninterrupted time

## Step 1: Sign Up for agent.ceo

Navigate to [agent.ceo](https://agent.ceo) and click **Get Started Free**. The free tier includes one full agent-week trial with a complete discovery scan included.

```
https://agent.ceo/signup
```

Enter your work email and create your organization. If your company already has an agent.ceo organization, ask your admin to invite you instead.

[Screenshot: Sign-up page showing email input, organization name field, and "Create Organization" button]

## Step 2: Connect Your Tools

Once your account is created, you will land on the **Integrations** dashboard. agent.ceo uses OAuth for all tool connections, meaning your credentials are never stored directly.

### Connect GitHub

Click **Connect GitHub** and authorize agent.ceo to access your repositories. You can choose specific repositories or grant organization-wide access.

```bash
# The OAuth flow will request these permissions:
# - repo (read/write for PR reviews and fixes)
# - read:org (to map your team structure)
# - workflow (to trigger and monitor CI runs)
```

[Screenshot: GitHub OAuth authorization screen showing requested permissions]

### Connect Slack (Optional)

Click **Connect Slack** and select your workspace. Agents use Slack to send status updates, ask clarifying questions, and notify you of completed work.

### Connect Jira/Linear (Optional)

Click **Connect Project Board** and authenticate with your project management tool. This allows agents to read tickets, update statuses, and create sub-tasks.

[Screenshot: Integrations dashboard showing connected GitHub with green checkmark, Slack pending]

## Step 3: Run the Discovery Scan

With your tools connected, click **Run Discovery Scan**. This automated process takes 30-60 seconds and maps your entire engineering environment:

```bash
# Discovery scan analyzes:
# - Repository structure and languages used
# - CI/CD pipeline configurations
# - Team members and their roles
# - Active branches and PR patterns
# - Infrastructure configuration files
```

[Screenshot: Discovery scan progress bar at 60% showing "Analyzing repository structure..."]

The scan produces an **Organization Map** that shows:

- **Repositories**: All connected repos with language breakdown
- **Team Structure**: Contributors and their areas of ownership
- **Infrastructure**: Detected services, deployment targets, and configurations
- **Opportunities**: Suggested areas where agents can provide immediate value

Review the organization map to verify accuracy. You can edit any incorrectly detected information.

## Step 4: Review Your Organization Map

After the scan completes, you will see a visual representation of your engineering organization. This is what agents use to understand context and make decisions.

```yaml
# Example organization map output:
organization:
  name: "Acme Corp Engineering"
  repositories: 12
  languages:
    - TypeScript (45%)
    - Python (30%)
    - Go (25%)
  services:
    - api-gateway (Go, deployed to GKE)
    - web-frontend (TypeScript, Vercel)
    - ml-pipeline (Python, AWS Lambda)
  team_members: 8
  open_prs: 14
  ci_pipelines: 3
```

This map becomes the foundation for [agent lifecycle management](/blog/agent-lifecycle-management) and helps the platform recommend which agents to deploy first.

## Step 5: Deploy Your First Agent

Now for the exciting part. Click **Deploy First Agent** and choose from the recommended agent types based on your discovery scan results.

For most teams, we recommend starting with a **Code Review Agent**:

```yaml
# Default Code Review Agent configuration
agent:
  role: "code-reviewer"
  name: "ReviewBot"
  repositories:
    - all-connected
  triggers:
    - pull_request.opened
    - pull_request.synchronize
  capabilities:
    - code-review
    - style-check
    - security-scan
  notifications:
    slack_channel: "#engineering"
```

Click **Deploy** and your agent spins up in its own Kubernetes pod within seconds. You can learn more about the underlying infrastructure in our guide on [Kubernetes AI agents](/blog/kubernetes-ai-agents).

[Screenshot: Agent deployment confirmation showing "ReviewBot" with green "Running" status]

## Step 6: Verify Your Agent is Working

Once deployed, verify your agent is operational:

1. Open the **Dashboard** and confirm the agent shows a green "Active" status
2. Check the agent's activity log for the initial startup sequence
3. Create a test pull request on one of your connected repositories
4. Watch the agent automatically review and comment on your PR

```bash
# Create a quick test PR
git checkout -b test/agent-verification
echo "# Test" > test-file.md
git add test-file.md
git commit -m "test: verify agent.ceo integration"
git push origin test/agent-verification
# Open PR via GitHub UI or CLI
gh pr create --title "Test: Agent Verification" --body "Testing agent.ceo integration"
```

Within 30 seconds, you should see your agent comment on the PR with a code review.

## What Happens Next

Your agent is now autonomously reviewing every pull request opened against your connected repositories. Here is what to explore next:

- **[Your First AI Agent Team](/blog/first-ai-agent-team)**: Scale from one agent to a coordinated team
- **[Setting Up AI Security Reviews](/blog/setting-up-ai-security-reviews)**: Add automated security auditing
- **[Monitoring Your AI Agent Fleet](/blog/monitoring-ai-agent-fleet)**: Track performance and costs

## Understanding the Architecture

Each agent runs in an isolated Kubernetes pod with its own instance of Claude Code CLI. This means agents have full development environments and can clone repos, run tests, and submit changes just like a human developer. Read more about this in our [architecture deep-dive](/blog/architecture-agent-ceo).

The platform handles all orchestration, including scaling agents up and down based on workload, managing tool access permissions, and coordinating between agents when you deploy a full team.

## Free Tier Details

Your free trial includes:

- **1 agent-week**: One agent running continuously for 7 days, or multiple agents sharing the time
- **Full discovery scan**: Complete mapping of your engineering organization
- **All integrations**: Connect unlimited tools during the trial
- **Dashboard access**: Full monitoring and control capabilities

No credit card required. After the trial, choose a plan that fits your team size and workload.

## Troubleshooting Common Issues

**Agent shows "Pending" status for more than 60 seconds:**
Check that your GitHub OAuth token has the required permissions. Reconnect the integration if needed.

**Discovery scan finds no repositories:**
Ensure you granted repository access during the GitHub OAuth flow. You can update permissions in Settings > Integrations.

**Agent does not comment on PRs:**
Verify the agent is configured to watch the correct repository and that PR triggers are enabled.

## Try agent.ceo

Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).
