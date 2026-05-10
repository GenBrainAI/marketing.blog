---
title: "Product Update: Cloud Discovery — AI Maps Your Infrastructure"
slug: "product-update-cloud-discovery"
date: 2026-05-10
category: marketing
cluster: "marketing-general"
tags: [product-update, cloud-discovery, infrastructure, aws, gcp, azure, mapping, ai-agents]
description: "Announcing Cloud Discovery for agent.ceo — AI agents automatically map your AWS, GCP, and Azure infrastructure for complete operational awareness."
relatedPosts: [cloud-discovery-ai-agents, configuring-cloud-discovery, architecture-agent-ceo]
---

# Product Update: Cloud Discovery — AI Maps Your Infrastructure

Today we're announcing Cloud Discovery for agent.ceo — an automated infrastructure mapping capability that gives your AI agents comprehensive, continuously-updated awareness of your cloud environment across AWS, GCP, and Azure.

Your agents can't manage what they can't see. Cloud Discovery ensures they see everything.

## The Problem: Infrastructure Blindness

Here's a scenario every engineering leader recognizes: you ask "what's running in our cloud?" and get a different answer depending on who you ask. The infrastructure team knows about the core services. The data team has their own cluster. Marketing spun up a landing page on a separate account. That prototype from last quarter is still running somewhere.

The reality of modern cloud infrastructure is sprawl. Resources are easy to create, hard to track, and expensive to forget about. Most organizations have:

- Resources across multiple cloud providers
- Multiple accounts or projects per provider
- Infrastructure created through IaC, manually, and through various automation tools
- Shadow IT — resources created outside standard processes
- Zombie resources — still running, no longer serving a purpose, still costing money

Manual infrastructure audits are point-in-time snapshots that go stale immediately. CMDBs are only as good as their update discipline (usually poor). And without a complete picture, AI agents operating on your infrastructure are working with incomplete context.

## What Cloud Discovery Does

Cloud Discovery agents continuously scan your cloud environments and build a living map of your infrastructure:

### Multi-Cloud Coverage

**Amazon Web Services**:
- EC2 instances, ECS/EKS clusters, Lambda functions
- RDS databases, DynamoDB tables, ElastiCache clusters
- S3 buckets, EBS volumes, EFS file systems
- VPCs, subnets, security groups, load balancers
- IAM roles, policies, and their effective permissions
- CloudFront distributions, Route 53 zones
- SQS queues, SNS topics, EventBridge rules

**Google Cloud Platform**:
- Compute Engine instances, GKE clusters, Cloud Functions
- Cloud SQL, Bigtable, Firestore, Memorystore
- Cloud Storage buckets, Persistent Disks
- VPC networks, firewall rules, load balancers
- IAM bindings and service accounts
- Pub/Sub topics, Cloud Tasks queues

**Microsoft Azure**:
- Virtual Machines, AKS clusters, Azure Functions
- Azure SQL, Cosmos DB, Redis Cache
- Blob Storage, managed disks
- Virtual Networks, NSGs, Application Gateways
- Azure AD roles and assignments
- Service Bus, Event Grid

### Relationship Mapping

Cloud Discovery doesn't just inventory resources — it maps how they relate to each other:

- Which services talk to which databases
- Which security groups allow traffic between which resources
- Which IAM roles grant access to which resources
- Which DNS records point to which services
- Which load balancers front which compute resources
- Which resources share dependencies

This relationship mapping is critical for:
- **Impact analysis**: "If this database goes down, what's affected?"
- **Security assessment**: "What can be reached from this compromised instance?"
- **Change planning**: "What depends on the service I'm about to modify?"
- **Cost attribution**: "Which team's services are driving this cost increase?"

### Continuous Updates

Cloud Discovery isn't a one-time scan. It continuously monitors for changes:

- New resources appearing (detected within minutes of creation)
- Resources being modified (configuration changes, scaling events)
- Resources being deleted (and whether dependent resources are affected)
- Drift from expected state (IaC definitions vs. actual cloud state)

Every change is recorded in the [Knowledge Base](/blog/product-update-knowledge-base), building a timeline of your infrastructure evolution.

## How Agents Use Discovery Data

Cloud Discovery feeds directly into every other agent function on the platform:

### DevOps Agents

With complete infrastructure awareness, [DevOps agents](/blog/ai-powered-devops) can:
- Plan deployments with full understanding of the target environment
- Identify resource constraints before they cause problems
- Optimize infrastructure sizing based on actual usage patterns
- Detect configuration drift and reconcile with desired state

### Security Agents

[Security agents](/blog/ai-security-reviews) use discovery data to:
- Identify overly permissive security groups and IAM policies
- Find publicly accessible resources that should be private
- Detect unencrypted data stores or unpatched instances
- Map potential attack paths through your infrastructure
- Ensure [credential management](/blog/credential-management-multi-cloud) covers all discovered resources

### Operations Agents

For [24/7 operations](/blog/24-7-operations-zero-overhead), discovery provides:
- Complete dependency maps for incident impact assessment
- Resource inventory for capacity planning
- Change correlation during incident investigation
- Identification of single points of failure

### Cost Optimization

Discovery enables [cost optimization](/blog/cost-optimization-ai-agents) through:
- Identifying idle or underutilized resources
- Finding resources running outside of cost-efficient configurations
- Detecting reserved instance/savings plan opportunities
- Attributing costs to teams, services, or projects

## Security and Permissions

Cloud Discovery uses read-only access to scan your environments. The principle of least privilege is strictly enforced:

- **Read-only IAM roles**: Discovery agents never modify your infrastructure during scanning
- **Scoped credentials**: Each cloud provider connection uses narrowly scoped credentials
- **Credential rotation**: Automatic rotation on configurable schedules
- **Audit logging**: Every API call made during discovery is logged
- **Data encryption**: All discovered infrastructure data is encrypted at rest and in transit

For detailed setup instructions, see our guide on [configuring cloud discovery](/blog/configuring-cloud-discovery).

### Required Permissions (AWS Example)

```
ec2:Describe*
rds:Describe*
s3:ListBuckets, s3:GetBucketLocation, s3:GetBucketPolicy
iam:List*, iam:Get*
ecs:Describe*, ecs:List*
lambda:List*, lambda:GetFunction
elasticloadbalancing:Describe*
```

No write permissions. No delete permissions. Discovery observes — it doesn't modify.

## Implementation

Getting Cloud Discovery running takes minutes, not days:

### Step 1: Connect Cloud Accounts

For each cloud provider, create a read-only role/service account and connect it to agent.ceo:

- **AWS**: Create an IAM role with a trust policy for agent.ceo, attach the ReadOnlyAccess managed policy (or a custom scoped policy)
- **GCP**: Create a service account with the Viewer role on your project(s)
- **Azure**: Create an App Registration with Reader role on relevant subscriptions

### Step 2: Initial Discovery

Once connected, the initial scan begins immediately. Depending on your infrastructure size:
- Small environments (< 100 resources): Complete in under 5 minutes
- Medium environments (100-1000 resources): 10-30 minutes
- Large environments (1000+ resources): 1-2 hours for full initial mapping

### Step 3: Review and Configure

After initial discovery:
- Review the generated infrastructure map for completeness
- Configure scan frequency (default: every 15 minutes for changes)
- Set up alerts for specific change types you want to be notified about
- Configure which agents have access to which portions of the discovered infrastructure

### Step 4: Continuous Operation

From this point, Cloud Discovery runs continuously. Your agents operate with constantly-updated infrastructure awareness. The [knowledge graph](/blog/wiki-knowledge-graphs) grows as new resources and relationships are discovered.

## What Customers Find

When organizations first enable Cloud Discovery, they frequently discover:

- **Forgotten resources**: Instances, databases, and storage from past projects still running and costing money. Typical finding: 10-20% of cloud spend is waste.
- **Security gaps**: Resources with overly permissive access, unencrypted data stores, public-facing services that shouldn't be. Average: 3-5 critical security findings per account.
- **Missing documentation**: Infrastructure that exists but isn't reflected in any architecture diagram or IaC definition. Often 15-30% of resources are "undocumented."
- **Dependency surprises**: Services that depend on resources their team doesn't own or manage. Critical path dependencies that aren't reflected in disaster recovery plans.

These findings alone typically justify the investment — the security improvements and cost savings from the initial discovery often exceed a full year's agent.ceo subscription cost.

## Pricing

Cloud Discovery is included in all agent.ceo plans:

- **Pay-as-you-go**: Discovery agent time billed at standard $1/agent-hour rate
- **Standard/Volume**: Included in agent subscription, continuous scanning at no additional cost

No per-resource charges. No per-account charges. No data volume charges. Whether you have 50 cloud resources or 50,000, the pricing is the same.

## The Foundation for Everything Else

Cloud Discovery isn't just a feature — it's the foundation that makes all other agent.ceo capabilities more effective. Agents that understand your infrastructure can make better decisions, respond to incidents faster, plan changes more safely, and identify risks more accurately.

Without discovery, agents operate on assumptions. With discovery, they operate on facts. For organizations serious about [scaling AI agents](/blog/scaling-ai-agents) across their operations, this complete infrastructure awareness is the starting point.

## Try agent.ceo

Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).
