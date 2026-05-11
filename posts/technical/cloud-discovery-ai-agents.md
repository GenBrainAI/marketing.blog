---
title: "Cloud Discovery: AI Agents Mapping Your Infrastructure"
slug: "cloud-discovery-ai-agents"
date: 2026-05-10
category: technical
cluster: "ai-devops"
tags: [cloud-discovery, aws, gcp, azure, infrastructure, cost-optimization, ai-agents]
description: "AI agents scan your AWS, GCP, and Azure accounts to map resources, find orphaned infrastructure, and eliminate cloud waste automatically."
relatedPosts: [ai-powered-devops, kubernetes-ai-agents, self-healing-infrastructure]
---

# Cloud Discovery: AI Agents Mapping Your Infrastructure

Every engineering organization has shadow infrastructure — resources created for a demo six months ago, load balancers pointing to decommissioned services, storage buckets from a departed engineer's experiment. These orphaned resources silently drain your cloud budget. In a [Cyborgenic Organization](/blog/cyborgenic-organizations), infrastructure awareness is not a quarterly audit — it is a continuous function owned by AI agents that scan your cloud accounts, build a living map of your infrastructure, and identify resources that no longer serve a purpose.

## The Shadow Infrastructure Problem

A typical mid-size SaaS company accumulates cloud waste at a rate of 15-30% of their total spend. Common culprits:

- **Orphaned load balancers**: No healthy backend targets
- **Idle compute instances**: Running but serving zero traffic
- **Unused elastic IPs**: Allocated but unattached (AWS charges for these)
- **Stale snapshots**: Months-old EBS/disk snapshots nobody needs
- **Oversized instances**: Running on 4xlarge when small would suffice
- **Abandoned storage**: S3 buckets or GCS buckets with no recent access
- **Unused databases**: RDS instances or Cloud SQL with zero connections

Manual audits catch some of these, but they happen quarterly at best. By the time you audit, another batch of waste has accumulated.

## How Agent Cloud Discovery Works

The agent.ceo cloud discovery agent connects to your cloud provider APIs using read-only credentials and builds a complete resource graph:

```python
class CloudDiscoveryAgent:
    """Scan cloud accounts and build infrastructure map."""
    
    def __init__(self, providers):
        self.providers = providers  # [AWSProvider, GCPProvider, AzureProvider]
        self.resource_graph = ResourceGraph()
    
    async def full_scan(self):
        """Perform complete infrastructure discovery."""
        for provider in self.providers:
            resources = await provider.discover_all()
            
            for resource in resources:
                self.resource_graph.add_node(resource)
                
                # Discover relationships
                relations = await provider.get_relationships(resource)
                for relation in relations:
                    self.resource_graph.add_edge(
                        resource.id, 
                        relation.target_id,
                        relation.type
                    )
        
        # Identify orphans (nodes with no incoming edges from active services)
        orphans = self.resource_graph.find_orphans()
        
        # Identify oversized resources
        oversized = await self.check_utilization(self.resource_graph.all_compute())
        
        return DiscoveryReport(
            total_resources=len(self.resource_graph.nodes),
            orphaned_resources=orphans,
            oversized_resources=oversized,
            estimated_waste=self.calculate_waste(orphans + oversized)
        )
```

## Multi-Cloud Resource Discovery

The agent understands resources across all major cloud providers:

```python
class AWSProvider:
    """AWS resource discovery."""
    
    async def discover_all(self):
        resources = []
        
        # EC2 instances
        ec2 = self.session.client('ec2')
        instances = ec2.describe_instances()
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                resources.append(Resource(
                    id=instance['InstanceId'],
                    type='ec2:instance',
                    provider='aws',
                    region=self.region,
                    metadata={
                        'state': instance['State']['Name'],
                        'type': instance['InstanceType'],
                        'launch_time': instance['LaunchTime'],
                        'tags': {t['Key']: t['Value'] for t in instance.get('Tags', [])}
                    }
                ))
        
        # Load Balancers
        elbv2 = self.session.client('elbv2')
        lbs = elbv2.describe_load_balancers()
        for lb in lbs['LoadBalancers']:
            target_groups = elbv2.describe_target_groups(
                LoadBalancerArn=lb['LoadBalancerArn']
            )
            healthy_targets = 0
            for tg in target_groups['TargetGroups']:
                health = elbv2.describe_target_health(
                    TargetGroupArn=tg['TargetGroupArn']
                )
                healthy_targets += sum(
                    1 for t in health['TargetHealthDescriptions']
                    if t['TargetHealth']['State'] == 'healthy'
                )
            
            resources.append(Resource(
                id=lb['LoadBalancerArn'],
                type='elbv2:loadbalancer',
                provider='aws',
                region=self.region,
                metadata={
                    'dns': lb['DNSName'],
                    'healthy_targets': healthy_targets,
                    'scheme': lb['Scheme']
                }
            ))
        
        # RDS instances
        rds = self.session.client('rds')
        dbs = rds.describe_db_instances()
        for db in dbs['DBInstances']:
            resources.append(Resource(
                id=db['DBInstanceIdentifier'],
                type='rds:instance',
                provider='aws',
                region=self.region,
                metadata={
                    'engine': db['Engine'],
                    'instance_class': db['DBInstanceClass'],
                    'connections': await self.get_db_connections(db),
                    'storage_gb': db['AllocatedStorage']
                }
            ))
        
        # S3 buckets, EBS volumes, Elastic IPs, etc.
        resources.extend(await self.discover_storage())
        resources.extend(await self.discover_networking())
        
        return resources


class GCPProvider:
    """GCP resource discovery."""
    
    async def discover_all(self):
        resources = []
        
        # Compute instances
        compute = googleapiclient.discovery.build('compute', 'v1')
        instances = compute.instances().aggregatedList(
            project=self.project
        ).execute()
        
        for zone, data in instances.get('items', {}).items():
            for instance in data.get('instances', []):
                resources.append(Resource(
                    id=instance['selfLink'],
                    type='compute:instance',
                    provider='gcp',
                    region=zone,
                    metadata={
                        'status': instance['status'],
                        'machine_type': instance['machineType'].split('/')[-1],
                        'created': instance['creationTimestamp']
                    }
                ))
        
        # GKE clusters
        container = googleapiclient.discovery.build('container', 'v1')
        clusters = container.projects().locations().clusters().list(
            parent=f'projects/{self.project}/locations/-'
        ).execute()
        
        for cluster in clusters.get('clusters', []):
            resources.append(Resource(
                id=cluster['selfLink'],
                type='container:cluster',
                provider='gcp',
                region=cluster['location'],
                metadata={
                    'node_count': cluster['currentNodeCount'],
                    'version': cluster['currentMasterVersion'],
                    'status': cluster['status']
                }
            ))
        
        return resources
```

## Orphan Detection Logic

The most valuable analysis is identifying orphaned resources — infrastructure that costs money but provides no value:

```python
class OrphanDetector:
    """Identify resources that are no longer serving a purpose."""
    
    ORPHAN_RULES = {
        'elbv2:loadbalancer': lambda r: r.metadata['healthy_targets'] == 0,
        'ec2:instance': lambda r: (
            r.metadata['state'] == 'running' and
            r.metadata.get('cpu_avg_7d', 100) < 2.0  # <2% CPU for a week
        ),
        'ebs:volume': lambda r: r.metadata.get('attached') == False,
        'ec2:eip': lambda r: r.metadata.get('association_id') is None,
        'rds:instance': lambda r: r.metadata.get('connections', 1) == 0,
        's3:bucket': lambda r: (
            r.metadata.get('last_access_days', 0) > 90 and
            r.metadata.get('object_count', 1) > 0
        ),
        'ebs:snapshot': lambda r: (
            r.metadata.get('age_days', 0) > 180 and
            not r.metadata.get('has_ami_reference', False)
        ),
    }
    
    def detect_orphans(self, resources):
        orphans = []
        for resource in resources:
            rule = self.ORPHAN_RULES.get(resource.type)
            if rule and rule(resource):
                orphans.append(OrphanFinding(
                    resource=resource,
                    monthly_cost=self.estimate_cost(resource),
                    confidence=self.calculate_confidence(resource),
                    recommendation=self.get_recommendation(resource)
                ))
        return orphans
```

## The Discovery Report

After scanning, the agent produces a detailed infrastructure report:

```
Cloud Discovery Report - 2026-05-10
====================================

Accounts scanned: 3 (AWS prod, AWS staging, GCP prod)
Total resources:  1,847
Scan duration:    4 minutes 23 seconds

ORPHANED RESOURCES (23 found):
------------------------------
| Resource                    | Type          | Monthly Cost | Confidence |
|-----------------------------|---------------|-------------|------------|
| alb-legacy-api-20240301     | LoadBalancer  | $43.00      | 98%        |
| i-0a3f7c9d2e (staging-old) | EC2 Instance  | $156.00     | 95%        |
| vol-0x8f3a2d1 (unattached) | EBS Volume    | $12.00      | 100%       |
| demo-bucket-hackathon       | S3 Bucket     | $8.00       | 87%        |
| rds-analytics-test          | RDS Instance  | $234.00     | 92%        |
| ... (18 more)               |               |             |            |

OVERSIZED RESOURCES (12 found):
-------------------------------
| Resource              | Current    | Recommended | Monthly Savings |
|-----------------------|------------|-------------|-----------------|
| api-server-prod       | m5.4xlarge | m5.xlarge   | $312.00         |
| worker-batch-process  | c5.2xlarge | c5.large    | $156.00         |
| ... (10 more)         |            |             |                 |

TOTAL ESTIMATED MONTHLY WASTE: $2,847
ANNUAL WASTE IF UNCHECKED:     $34,164
```

## Automated Cleanup Workflows

The agent doesn't just report — it can clean up with appropriate approval flows:

```yaml
# Cleanup policy configuration
apiVersion: agentceo.io/v1
kind: CleanupPolicy
metadata:
  name: cloud-waste-policy
spec:
  autoCleanup:
    # Automatically clean these without approval
    - type: ebs:volume
      condition: "unattached AND age > 30 days"
      action: snapshot-and-delete
    - type: ec2:eip
      condition: "unassociated AND age > 7 days"
      action: release
    - type: ebs:snapshot
      condition: "age > 365 days AND no_ami_reference"
      action: delete
  
  requireApproval:
    # These need human approval via Slack
    - type: ec2:instance
      condition: "low_utilization"
      action: stop-or-rightsize
      approver: "#platform-team"
    - type: rds:instance
      condition: "zero_connections AND age > 14 days"
      action: snapshot-and-terminate
      approver: "#platform-team"
  
  schedule:
    scanInterval: "6h"
    cleanupWindow: "Saturday 02:00-06:00 UTC"
```

## Continuous Infrastructure Mapping

Unlike one-time audits, the agent maintains a living infrastructure map that updates every scan cycle. This enables trend analysis:

```python
async def track_infrastructure_trends(self):
    """Track how infrastructure grows and changes over time."""
    current_scan = await self.full_scan()
    previous_scan = await self.get_previous_scan()
    
    new_resources = current_scan.resources - previous_scan.resources
    removed_resources = previous_scan.resources - current_scan.resources
    
    # Alert on unexpected growth
    if len(new_resources) > self.threshold.daily_growth:
        await self.alert(
            f"Unusual infrastructure growth: {len(new_resources)} new resources "
            f"in last scan cycle (threshold: {self.threshold.daily_growth})"
        )
    
    # Track cost trajectory
    current_cost = sum(r.monthly_cost for r in current_scan.resources)
    previous_cost = sum(r.monthly_cost for r in previous_scan.resources)
    
    if current_cost > previous_cost * 1.1:  # 10% increase
        await self.publish_cost_alert(current_cost, previous_cost)
```

## Integration with Other Agents

Cloud discovery feeds data into the broader agent ecosystem. The [DevOps agent](/blog/ai-powered-devops) uses the infrastructure map for deployment decisions. The [security agent](/blog/ai-security-reviews) checks discovered resources against security policies. The [self-healing agent](/blog/self-healing-infrastructure) monitors the health of mapped resources. All of this coordinates via the [event-driven architecture](/blog/event-driven-nats-ai).

For multi-cloud credential setup and access configuration, see [credential management for multi-cloud](/blog/credential-management-multi-cloud) and the [cloud discovery configuration guide](/blog/configuring-cloud-discovery).

## Getting Started

Deploy the cloud discovery agent with read-only IAM credentials for each cloud account. The first scan produces a complete infrastructure map within minutes. Set up cleanup policies gradually — start with obvious waste (unattached volumes, released IPs) and expand as confidence builds.


**Continue reading:** Explore [the architecture behind agent.ceo](/blog/architecture-agent-ceo), learn about [scaling AI agents to 100 concurrent workers](/blog/scaling-ai-agents), or get started with our [5-minute quickstart guide](/blog/getting-started-agent-ceo).

> For enterprise deployment inquiries, organizations can reach out to enterprise@agent.ceo.

## Try agent.ceo

**SaaS** — Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).

**Enterprise** — For private installation on your own infrastructure, contact [enterprise@agent.ceo](mailto:enterprise@agent.ceo).

---
*agent.ceo is built by [GenBrain AI](https://genbrain.ai) — a GenAI-first autonomous agent orchestration platform. General inquiries: hello@agent.ceo | Security: security@agent.ceo*
