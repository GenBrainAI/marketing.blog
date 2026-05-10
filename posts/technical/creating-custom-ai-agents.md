---
title: "Creating Custom AI Agents with Templates"
slug: "creating-custom-ai-agents"
date: 2026-05-10
category: technical
cluster: "getting-started"
tags: [custom-agents, templates, configuration, roles, permissions, tutorial]
description: "Build custom AI agents tailored to your team's needs. Define roles, tools, permissions, and knowledge scope using agent.ceo templates."
relatedPosts: [first-ai-agent-team, deploying-ai-agents-kubernetes, getting-started-agent-ceo]
---

# Creating Custom AI Agents with Templates

While agent.ceo ships with pre-built agent templates for common roles like code review and security analysis, the real power comes from creating custom agents tailored to your team's specific needs. This guide teaches you how to define agent templates with precise roles, tool configurations, permissions, and knowledge scopes.

By the end of this tutorial, you will have created and deployed a custom agent that handles a unique workflow in your organization.

## Why Custom Agents?

Every engineering team has unique processes, conventions, and pain points. Custom agents let you:

- Automate team-specific workflows that no pre-built template covers
- Encode your organization's standards and knowledge into an autonomous worker
- Create specialists that understand your architecture deeply
- Build agents that integrate with internal tools and services

This is what makes agent.ceo a platform for building [cyborgenic organizations](/blog/cyborgenic-organizations) rather than just a tool.

## Prerequisites

- An agent.ceo account with at least one integration connected
- Completed the [Getting Started guide](/blog/getting-started-agent-ceo)
- A clear idea of the task you want to automate

## Step 1: Define the Agent's Role

Start by clearly articulating what your agent will do. A well-defined role includes:

- **Primary responsibility**: The main task the agent performs
- **Trigger conditions**: What events activate the agent
- **Success criteria**: How to measure if the agent is doing its job
- **Boundaries**: What the agent should NOT do

Example: Let's create a "Release Manager" agent that automates your release process.

```yaml
# role-definition.yaml
role:
  name: "Release Manager"
  description: |
    Manages the release process for all services. Handles version bumping,
    changelog generation, release branch creation, and deployment coordination.
    Notifies the team at each stage and gates releases on CI status.
  
  primary_responsibilities:
    - Create release branches on schedule
    - Generate changelogs from merged PRs
    - Bump version numbers following semver
    - Coordinate deployment across services
    - Post release notes to Slack and GitHub
  
  triggers:
    - schedule: "every Tuesday at 10:00 UTC"
    - command: "/release"
    - event: "all-checks-passing on release branch"
  
  success_criteria:
    - releases_deployed_on_schedule: true
    - zero_failed_releases: true
    - changelog_accuracy: "> 95%"
    - team_notification_sent: true
  
  boundaries:
    - never_force_push: true
    - never_skip_ci: true
    - never_deploy_without_approval: true
    - never_modify_production_directly: true
```

## Step 2: Create the Agent Template

Templates define the complete configuration for an agent. Create one using the CLI or dashboard:

```bash
# Create a new template
agentceo template create release-manager
```

This opens the template editor. Define the full configuration:

```yaml
# templates/release-manager.yaml
apiVersion: agent.ceo/v1
kind: AgentTemplate
metadata:
  name: release-manager
  description: "Automated release management agent"
  version: "1.0.0"
  author: "engineering-team"
  tags:
    - releases
    - deployment
    - automation

spec:
  # Agent identity
  identity:
    display_name: "ReleaseBot"
    avatar: "rocket"
    git_name: "release-bot"
    git_email: "release-bot@company.com"
    branch_prefix: "release/"

  # Role description (injected into agent's system prompt)
  role_prompt: |
    You are a Release Manager agent responsible for automating the release
    process. You follow semantic versioning strictly. You never skip CI checks
    or deploy without explicit approval from a designated approver.
    
    Your release process:
    1. Collect all merged PRs since last release
    2. Determine version bump (major/minor/patch) based on conventional commits
    3. Create release branch
    4. Generate changelog
    5. Create version bump commit
    6. Open release PR for approval
    7. After approval, tag and trigger deployment
    8. Post release notes

  # Tool access
  tools:
    github:
      access: read-write
      capabilities:
        - create-branches
        - create-prs
        - create-releases
        - manage-labels
        - read-commits
        - create-tags
    slack:
      access: write
      channels:
        - "#releases"
        - "#engineering"
    jira:
      access: read-write
      capabilities:
        - transition-issues
        - add-comments
        - update-fix-versions

  # Repository scope
  repositories:
    - org/api-service
    - org/web-frontend
    - org/mobile-app
    - org/shared-libs

  # Permissions
  permissions:
    git:
      - push-to-release-branches
      - create-tags
      - create-pull-requests
    ci:
      - trigger-workflows
      - read-status
    deployment:
      - trigger-staging
      - request-production-approval

  # Knowledge scope
  knowledge:
    files:
      - RELEASE.md
      - docs/release-process.md
      - .github/workflows/release.yml
      - CHANGELOG.md
    context:
      - "Release schedule: Every Tuesday at 10:00 UTC"
      - "Version format: semver (MAJOR.MINOR.PATCH)"
      - "Commit format: Conventional Commits"
      - "Approvers: @tech-lead, @engineering-manager"

  # Resource requirements
  resources:
    cpu_request: "250m"
    cpu_limit: "1000m"
    memory_request: "1Gi"
    memory_limit: "4Gi"
    storage: "10Gi"

  # Triggers
  triggers:
    scheduled:
      - cron: "0 10 * * 2"  # Every Tuesday at 10:00 UTC
        action: "initiate-release"
    webhook:
      - event: "slash_command"
        command: "/release"
        action: "initiate-release"
      - event: "pr.approved"
        filter: "branch starts with release/"
        action: "finalize-release"
    manual:
      - command: "release"
        description: "Manually trigger a release cycle"
```

[Screenshot: Template editor showing the release-manager configuration with syntax highlighting]

## Step 3: Define Agent Behaviors

Specify how the agent should behave in different scenarios:

```yaml
# behaviors.yaml (extend the template)
behaviors:
  initiate_release:
    steps:
      - name: "Gather changes"
        action: |
          List all merged PRs since the last release tag.
          Categorize by type: feature, fix, breaking change, chore.
      
      - name: "Determine version"
        action: |
          Based on conventional commits:
          - Any "BREAKING CHANGE" or "!" -> major bump
          - Any "feat:" -> minor bump
          - Only "fix:", "docs:", "chore:" -> patch bump
      
      - name: "Create release branch"
        action: |
          git checkout -b release/v{new_version}
          Update version in package.json / pyproject.toml / version.go
      
      - name: "Generate changelog"
        action: |
          Create CHANGELOG entry with:
          - Version number and date
          - Grouped changes (Features, Fixes, Breaking Changes)
          - Links to PRs and issues
          - Contributors list
      
      - name: "Open release PR"
        action: |
          Create PR from release/v{version} to main
          Add labels: release, v{version}
          Request review from approvers
          Post summary to #releases channel
  
  finalize_release:
    steps:
      - name: "Verify CI"
        action: |
          Confirm all checks pass on the release branch.
          If any fail, notify and wait.
      
      - name: "Merge and tag"
        action: |
          Merge release PR (squash)
          Create git tag v{version}
          Push tag to trigger deployment workflow
      
      - name: "Post release notes"
        action: |
          Create GitHub Release with changelog content
          Post to #releases: "v{version} deployed to production"
          Update Jira fix versions
  
  handle_failure:
    steps:
      - name: "Diagnose"
        action: |
          Analyze failure reason from CI logs.
          Determine if it's a flaky test, real failure, or infrastructure issue.
      
      - name: "Respond"
        action: |
          If flaky: retry once, then escalate
          If real failure: comment on PR with diagnosis, notify author
          If infrastructure: alert DevOps channel
```

## Step 4: Add Knowledge Context

Provide the agent with the knowledge it needs to make good decisions:

```bash
# Create agent knowledge directory in your repo
mkdir -p .agent-ceo/knowledge/release-manager/

# Add release process documentation
cat > .agent-ceo/knowledge/release-manager/process.md << 'EOF'
# Release Process

## Schedule
- Releases happen every Tuesday at 10:00 UTC
- Hotfixes can be released at any time with tech lead approval

## Version Strategy
- We use semantic versioning (semver)
- Breaking changes require major version bump
- New features require minor version bump
- Bug fixes require patch version bump

## Approval Requirements
- Standard releases: 1 approval from tech lead
- Major releases: 2 approvals (tech lead + engineering manager)
- Hotfixes: 1 approval from any senior engineer

## Rollback Policy
- If deployment fails health checks, auto-rollback is triggered
- Manual rollback requires notification in #incidents
EOF

# Add service-specific release notes
cat > .agent-ceo/knowledge/release-manager/services.md << 'EOF'
# Service Release Notes

## api-service
- Deployed to GKE via Helm
- Requires database migration check before deploy
- Health check endpoint: /health

## web-frontend
- Deployed to Vercel
- Requires build step (npm run build)
- Preview deployments for each PR

## mobile-app
- Requires app store review (not auto-deployed)
- Release creates a build artifact only
- Notify mobile team for submission
EOF
```

This knowledge is ingested and available to the agent during runtime, similar to how [knowledge base building](/blog/building-ai-knowledge-base) works for broader context.

## Step 5: Test the Template

Before deploying to production, test your template:

```bash
# Validate template syntax
agentceo template validate templates/release-manager.yaml

# Dry-run the template (simulates without executing)
agentceo template test release-manager \
  --trigger "initiate-release" \
  --dry-run

# Output:
# [DRY RUN] Would gather 12 merged PRs since v2.3.1
# [DRY RUN] Version bump: 2.3.1 -> 2.4.0 (minor - new features detected)
# [DRY RUN] Would create branch: release/v2.4.0
# [DRY RUN] Would generate changelog with 8 features, 3 fixes, 1 chore
# [DRY RUN] Would open PR: "Release v2.4.0"
# [DRY RUN] Would post to #releases
# Validation: PASS - all steps executable
```

[Screenshot: Template test output showing dry-run results with all steps passing validation]

## Step 6: Deploy the Custom Agent

Deploy your custom agent from the template:

```bash
# Deploy agent from template
agentceo agent deploy \
  --template release-manager \
  --name "ReleaseBot" \
  --team "Core Engineering"

# Verify deployment
agentceo agent status ReleaseBot
# Status: Running
# Next trigger: Tuesday 10:00 UTC (in 3 days)
# Knowledge loaded: 2 documents
# Tools connected: GitHub, Slack, Jira
```

## Step 7: Iterate and Improve

After deployment, monitor your agent's performance and iterate on the template:

```bash
# View agent activity logs
agentceo agent logs ReleaseBot --since 7d

# Check decision accuracy
agentceo agent metrics ReleaseBot --metric decision-accuracy

# Update the template
agentceo template update release-manager --file templates/release-manager-v2.yaml

# Redeploy with updated template
agentceo agent redeploy ReleaseBot --template release-manager
```

Track metrics like:
- How often the agent completes releases without human intervention
- Version bump accuracy (did it choose the right semver bump?)
- Time saved compared to manual release process
- Error rate and types of failures

## Template Sharing and Reuse

Share templates across your organization:

```bash
# Publish template to organization catalog
agentceo template publish release-manager \
  --visibility organization \
  --description "Automated release management for all services"

# List available templates
agentceo template list --scope organization

# Use a shared template
agentceo agent deploy \
  --template org/release-manager \
  --name "ReleaseBot-Mobile" \
  --override-repos org/mobile-app
```

## Advanced Template Features

### Conditional Logic

```yaml
# Template with conditional behaviors
behaviors:
  on_pr_merged:
    conditions:
      - if: "pr.labels contains 'breaking-change'"
        then: "schedule-major-release"
      - if: "pr.labels contains 'hotfix'"
        then: "initiate-hotfix-release"
      - else: "add-to-next-release"
```

### Multi-Agent Coordination

```yaml
# Template that coordinates with other agents
coordination:
  notify_agents:
    - agent: "DevOps-Agent"
      event: "release-tagged"
      message: "Deploy v{version} to staging"
    - agent: "QA-Agent"
      event: "staging-deployed"
      message: "Run regression suite on staging"
```

### Template Inheritance

```yaml
# Extend a base template
apiVersion: agent.ceo/v1
kind: AgentTemplate
metadata:
  name: release-manager-enterprise
  extends: release-manager  # Inherits all base configuration
spec:
  # Override specific settings
  permissions:
    deployment:
      - trigger-staging
      - trigger-production  # Additional permission for enterprise
  behaviors:
    # Add compliance checks
    pre_release:
      - run-compliance-audit
      - verify-license-headers
      - check-export-controls
```

For more on how templates integrate with the broader platform, see our guide on [MCP tool integration](/blog/mcp-tool-integration).

## Try agent.ceo

Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).
