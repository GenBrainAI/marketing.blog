---
title: "Configuring Cloud Discovery for AWS/GCP/Azure"
slug: "configuring-cloud-discovery"
date: 2026-05-10
category: technical
cluster: "getting-started"
tags: [cloud-discovery, aws, gcp, azure, infrastructure, tutorial]
description: "Connect AWS, GCP, or Azure credentials to agent.ceo for automated cloud resource discovery. Map your entire infrastructure in minutes."
relatedPosts: [getting-started-agent-ceo, deploying-ai-agents-kubernetes, monitoring-ai-agent-fleet]
---

# Configuring Cloud Discovery for AWS/GCP/Azure

Understanding your cloud infrastructure is the first step toward managing it effectively. agent.ceo's cloud discovery feature connects to your AWS, GCP, or Azure accounts with read-only credentials and automatically maps every resource, service, and relationship in your environment.

This guide walks you through connecting each cloud provider, running discovery scans, and using the resulting infrastructure map to deploy specialized [cloud discovery AI agents](/blog/cloud-discovery-ai-agents).

## What Cloud Discovery Maps

The discovery scan identifies and catalogs:

- **Compute**: EC2 instances, GCE VMs, Azure VMs, containers, serverless functions
- **Networking**: VPCs, subnets, load balancers, DNS records, firewalls
- **Storage**: S3 buckets, Cloud Storage, Blob Storage, databases
- **Security**: IAM roles, security groups, access policies, encryption status
- **Costs**: Resource pricing, underutilized instances, optimization opportunities
- **Relationships**: Service dependencies, data flows, network connectivity

## Prerequisites

- An agent.ceo account (see [Getting Started](/blog/getting-started-agent-ceo))
- Read-only access credentials for your cloud provider(s)
- Permission to create IAM roles or service accounts

## Step 1: Create Read-Only Credentials

Cloud discovery uses strictly read-only access. This is non-negotiable for security. The agent cannot modify, create, or delete any resources in your cloud accounts.

### AWS: Create an IAM Role

```bash
# Create a policy document for read-only access
cat > agent-ceo-discovery-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "s3:List*",
        "s3:GetBucketLocation",
        "s3:GetBucketTagging",
        "rds:Describe*",
        "elasticloadbalancing:Describe*",
        "autoscaling:Describe*",
        "lambda:List*",
        "lambda:GetFunction",
        "ecs:Describe*",
        "ecs:List*",
        "eks:Describe*",
        "eks:List*",
        "iam:List*",
        "iam:GetRole",
        "iam:GetPolicy",
        "cloudformation:Describe*",
        "cloudformation:List*",
        "route53:List*",
        "cloudwatch:GetMetricData",
        "cloudwatch:ListMetrics",
        "ce:GetCostAndUsage",
        "tag:GetResources"
      ],
      "Resource": "*"
    }
  ]
}
EOF

# Create the IAM policy
aws iam create-policy \
  --policy-name AgentCeoDiscoveryPolicy \
  --policy-document file://agent-ceo-discovery-policy.json

# Create a role for agent.ceo with external ID
aws iam create-role \
  --role-name AgentCeoDiscoveryRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "YOUR_EXTERNAL_ID_FROM_DASHBOARD"
        }
      }
    }]
  }'

# Attach the policy to the role
aws iam attach-role-policy \
  --role-name AgentCeoDiscoveryRole \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT:policy/AgentCeoDiscoveryPolicy
```

[Screenshot: AWS IAM console showing AgentCeoDiscoveryRole with read-only policy attached]

### GCP: Create a Service Account

```bash
# Create a service account
gcloud iam service-accounts create agent-ceo-discovery \
  --display-name="agent.ceo Cloud Discovery" \
  --description="Read-only access for agent.ceo infrastructure discovery"

# Grant Viewer role at project level
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:agent-ceo-discovery@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/viewer"

# Grant additional read-only roles for specific services
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:agent-ceo-discovery@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/compute.viewer"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:agent-ceo-discovery@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/container.viewer"

# Create and download a key file
gcloud iam service-accounts keys create agent-ceo-key.json \
  --iam-account=agent-ceo-discovery@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### Azure: Create a Service Principal

```bash
# Create a service principal with Reader role
az ad sp create-for-rbac \
  --name "agent-ceo-discovery" \
  --role "Reader" \
  --scopes "/subscriptions/YOUR_SUBSCRIPTION_ID" \
  --output json

# Output will include:
# {
#   "appId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
#   "displayName": "agent-ceo-discovery",
#   "password": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
#   "tenant": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
# }

# For additional resource visibility, add Security Reader
az role assignment create \
  --assignee APP_ID \
  --role "Security Reader" \
  --scope "/subscriptions/YOUR_SUBSCRIPTION_ID"
```

## Step 2: Connect Credentials to agent.ceo

Navigate to **Settings > Cloud Providers** in your dashboard.

### Connect AWS

```bash
# Via CLI
agentceo cloud connect aws \
  --role-arn "arn:aws:iam::YOUR_ACCOUNT:role/AgentCeoDiscoveryRole" \
  --external-id "YOUR_EXTERNAL_ID" \
  --regions "us-east-1,us-west-2,eu-west-1"
```

### Connect GCP

```bash
# Via CLI
agentceo cloud connect gcp \
  --service-account-key agent-ceo-key.json \
  --projects "project-id-1,project-id-2"
```

### Connect Azure

```bash
# Via CLI
agentceo cloud connect azure \
  --tenant-id "YOUR_TENANT_ID" \
  --client-id "YOUR_APP_ID" \
  --client-secret "YOUR_PASSWORD" \
  --subscriptions "YOUR_SUBSCRIPTION_ID"
```

[Screenshot: Cloud Providers settings page showing AWS connected with green status, GCP pending, Azure not connected]

## Step 3: Run the Discovery Scan

Once credentials are connected, initiate the discovery scan:

```bash
# Run discovery on all connected providers
agentceo cloud discover --all

# Or run for a specific provider
agentceo cloud discover --provider aws

# Run with verbose output
agentceo cloud discover --all --verbose
```

The scan typically takes 2-5 minutes depending on the size of your infrastructure. Progress is reported in real-time:

```
[1/6] Scanning compute resources... 45 instances found
[2/6] Scanning networking... 12 VPCs, 34 subnets mapped
[3/6] Scanning storage... 28 buckets, 6 databases found
[4/6] Scanning security... 89 IAM roles, 156 security groups analyzed
[5/6] Mapping relationships... 234 connections identified
[6/6] Generating cost analysis... $12,450/month estimated
Discovery complete! View results at https://app.agent.ceo/cloud-map
```

[Screenshot: Discovery scan progress showing all 6 phases completing with resource counts]

## Step 4: Review the Infrastructure Map

After the scan completes, explore your infrastructure map:

```bash
# View summary
agentceo cloud summary

# Example output:
# Cloud Infrastructure Summary
# ============================
# Provider    Resources    Services    Monthly Cost
# AWS         156          12          $8,200
# GCP         89           7           $4,250
# Azure       34           4           $1,800
# ────────────────────────────────────────────────
# Total       279          23          $14,250
```

The visual map in the dashboard shows:

- **Service topology**: How services connect and depend on each other
- **Resource groups**: Logical groupings by team, project, or environment
- **Security posture**: Color-coded risk indicators on each resource
- **Cost attribution**: Spending breakdown by service, team, and environment

[Screenshot: Interactive cloud infrastructure map showing services connected by lines with cost annotations and security risk colors]

## Step 5: Configure Continuous Monitoring

Set up ongoing discovery to keep your infrastructure map current:

```yaml
# continuous-discovery.yaml
continuous_discovery:
  schedule:
    full_scan: "daily at 03:00 UTC"
    incremental_scan: "every 4 hours"
    cost_analysis: "weekly on Monday at 06:00 UTC"
  
  change_detection:
    notify_on:
      - new_resources_created
      - resources_deleted
      - security_group_modified
      - iam_role_changed
      - public_access_enabled
    channels:
      - slack: "#infrastructure-changes"
      - dashboard: true
  
  drift_detection:
    compare_to: "infrastructure-as-code"
    terraform_state:
      - s3://company-terraform/production/terraform.tfstate
      - s3://company-terraform/staging/terraform.tfstate
    alert_on_drift: true
```

```bash
# Enable continuous monitoring
agentceo cloud monitor \
  --schedule "every 4 hours" \
  --notify-changes true \
  --drift-detection true
```

## Step 6: Deploy Cloud-Aware Agents

With your infrastructure mapped, deploy agents that understand your cloud environment:

```yaml
# Cloud-aware agent configuration
agent:
  name: "CloudOps-Agent"
  role: "cloud-operations"
  
  cloud_context:
    providers:
      - aws
      - gcp
    focus_areas:
      - cost-optimization
      - security-compliance
      - resource-rightsizing
      - unused-resource-detection
  
  automated_actions:
    - detect-unused-resources:
        threshold: "30 days inactive"
        action: "recommend-termination"
    - monitor-cost-spikes:
        threshold: "20% above average"
        action: "alert-and-analyze"
    - check-security-compliance:
        framework: "CIS Benchmarks"
        action: "report-violations"
```

```bash
# Deploy cloud operations agent
agentceo agent deploy \
  --template cloud-operations \
  --name "CloudOps-Agent" \
  --cloud-providers aws,gcp
```

## Step 7: Generate Infrastructure Reports

Use discovery data to generate actionable reports:

```bash
# Cost optimization report
agentceo cloud report cost-optimization
# Output: Identifies $2,400/month in savings from unused resources

# Security posture report
agentceo cloud report security-posture
# Output: 3 critical, 7 high, 15 medium security findings

# Compliance report
agentceo cloud report compliance --framework cis-aws
# Output: 89% compliant, 12 controls failing
```

These reports integrate with the broader [SaaS platform monitoring](/blog/saas-platform-ai-agents) capabilities of agent.ceo.

## Multi-Cloud Considerations

If you run workloads across multiple providers:

- **Unified view**: All resources appear on a single map regardless of provider
- **Cross-cloud dependencies**: Discovery identifies connections between providers (e.g., GCP service calling AWS API)
- **Normalized metrics**: Costs and resources are presented in a consistent format
- **Provider-specific recommendations**: Optimization suggestions account for each provider's pricing model

## Security of Discovery Credentials

Your cloud credentials are handled with strict security measures:

- Credentials are encrypted at rest using AES-256
- Access is limited to the discovery service only
- Credentials are never exposed in agent workspaces
- All API calls are logged and auditable
- Read-only access is enforced at the IAM level
- External IDs and conditions prevent confused deputy attacks

For additional security considerations, review our [2FA/MFA configuration guide](/blog/2fa-mfa-ai-platforms).

> agent.ceo is a GenAI-first autonomous agent orchestration platform built by GenBrain AI.

## Try agent.ceo

**SaaS** — Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).

**Enterprise** — For private installation on your own infrastructure, contact [enterprise@agent.ceo](mailto:enterprise@agent.ceo).

---
*agent.ceo is built by [GenBrain AI](https://genbrain.ai) — a GenAI-first autonomous agent orchestration platform. General inquiries: hello@agent.ceo | Security: security@agent.ceo*
