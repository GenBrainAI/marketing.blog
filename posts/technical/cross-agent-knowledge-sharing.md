---
title: "Cross-Agent Knowledge Sharing Patterns"
slug: "cross-agent-knowledge-sharing"
date: 2026-05-10
category: technical
cluster: "knowledge-management"
tags: [knowledge-sharing, nats, pub-sub, multi-agent, collaboration, event-driven]
description: "Architectural patterns for sharing knowledge between AI agents using NATS pub/sub messaging and Neo4j graph queries for organizational intelligence."
relatedPosts: [building-ai-knowledge-base, wiki-knowledge-graphs, llm-wiki-pattern]
---

# Cross-Agent Knowledge Sharing Patterns

A single AI agent with access to organizational knowledge is useful. A fleet of agents that share knowledge in real-time is transformative. When the DevOps agent discovers a new deployment pattern, the CTO agent should know about it immediately. When the security agent identifies a vulnerability, every agent working on affected services needs that context.

At agent.ceo, cross-agent knowledge sharing happens through two complementary channels: NATS pub/sub for real-time knowledge events, and Neo4j graph queries for persistent knowledge retrieval. Together, they create an information fabric where [AI agents](/blog/what-are-ai-agents) learn from each other continuously.

## The Knowledge Sharing Architecture

Knowledge flows between agents through three mechanisms:

1. **Event-driven sharing** via NATS: agents publish knowledge events that other agents subscribe to
2. **Graph-based retrieval** via Neo4j: agents query the shared knowledge graph for context
3. **Direct messaging**: agents send knowledge directly to specific agents via the [agent-to-agent messaging](/blog/agent-to-agent-messaging) system

```
Agent A (discovers knowledge)
    |
    |---> NATS pub/sub (real-time broadcast)
    |         |
    |         +--> Agent B (subscriber)
    |         +--> Agent C (subscriber)
    |
    |---> Neo4j (persistent storage)
              |
              +--> Agent D (queries later)
              +--> Agent E (queries later)
```

## NATS Knowledge Events

When an agent learns something significant, it publishes a knowledge event to NATS. Other agents subscribe to knowledge topics relevant to their domain:

```python
import nats
from nats.aio.client import Client as NATS

class KnowledgePublisher:
    """Publishes knowledge events to NATS for cross-agent sharing."""
    
    def __init__(self, nc: NATS, agent_id: str):
        self.nc = nc
        self.agent_id = agent_id
    
    async def publish_knowledge(
        self,
        knowledge_type: str,
        payload: dict
    ):
        """Publish a knowledge event to interested agents."""
        subject = f"knowledge.{knowledge_type}"
        
        event = {
            "source": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "type": knowledge_type,
            "payload": payload
        }
        
        await self.nc.publish(
            subject,
            json.dumps(event).encode()
        )
    
    async def publish_wiki_update(self, slug: str, title: str, summary: str):
        """Notify agents that a wiki entry was created or updated."""
        await self.publish_knowledge("wiki.updated", {
            "slug": slug,
            "title": title,
            "summary": summary,
            "category": "architecture"
        })
    
    async def publish_incident_learning(
        self, 
        incident_id: str, 
        learning: str,
        affected_services: list
    ):
        """Share incident learnings with the fleet."""
        await self.publish_knowledge("incident.learning", {
            "incidentId": incident_id,
            "learning": learning,
            "affectedServices": affected_services,
            "severity": "high"
        })
    
    async def publish_architecture_change(
        self,
        service: str,
        change_type: str,
        description: str
    ):
        """Announce architecture changes to interested agents."""
        await self.publish_knowledge("architecture.changed", {
            "service": service,
            "changeType": change_type,
            "description": description
        })
```

## Subscribing to Knowledge Streams

Each agent subscribes to knowledge topics relevant to its role. The DevOps agent cares about deployment patterns and incidents. The security agent cares about vulnerability disclosures and configuration changes:

```python
class KnowledgeSubscriber:
    """Subscribes to knowledge events from other agents."""
    
    def __init__(self, nc: NATS, agent_id: str):
        self.nc = nc
        self.agent_id = agent_id
        self.handlers = {}
    
    async def subscribe(self, pattern: str, handler):
        """Subscribe to a knowledge topic pattern."""
        sub = await self.nc.subscribe(pattern, cb=self._wrap_handler(handler))
        self.handlers[pattern] = sub
    
    def _wrap_handler(self, handler):
        async def wrapper(msg):
            event = json.loads(msg.data.decode())
            # Don't process our own events
            if event["source"] == self.agent_id:
                return
            await handler(event)
        return wrapper
    
    async def setup_devops_subscriptions(self):
        """Set up subscriptions for a DevOps agent."""
        await self.subscribe(
            "knowledge.architecture.changed",
            self.handle_architecture_change
        )
        await self.subscribe(
            "knowledge.incident.learning",
            self.handle_incident_learning
        )
        await self.subscribe(
            "knowledge.wiki.updated",
            self.handle_wiki_update
        )
    
    async def handle_architecture_change(self, event):
        """Process architecture change from another agent."""
        payload = event["payload"]
        service = payload["service"]
        
        # Update local context about the service
        await self.update_service_context(service, {
            "recent_change": payload["description"],
            "change_type": payload["changeType"],
            "reported_by": event["source"],
            "reported_at": event["timestamp"]
        })
        
        # Check if this affects any active tasks
        affected_tasks = await self.check_task_impact(service)
        if affected_tasks:
            await self.flag_tasks_for_review(affected_tasks, event)
```

## NATS Subject Hierarchy

We organize knowledge events into a hierarchical subject structure that enables fine-grained subscription:

```
knowledge.
├── wiki.
│   ├── created        # New wiki entry
│   ├── updated        # Wiki entry modified
│   └── deprecated     # Wiki entry marked stale
├── incident.
│   ├── detected       # New incident
│   ├── learning       # Post-incident insight
│   └── resolved       # Incident resolution
├── architecture.
│   ├── changed        # Service architecture change
│   ├── decision       # New ADR created
│   └── deprecated     # Pattern deprecated
├── security.
│   ├── vulnerability  # New vulnerability found
│   ├── advisory       # Security advisory
│   └── compliance     # Compliance status change
└── deployment.
    ├── completed      # Successful deployment
    ├── failed         # Failed deployment
    └── pattern        # New deployment pattern discovered
```

Agents subscribe using wildcards for broad awareness or specific subjects for targeted knowledge:

```python
# Broad: get all knowledge events
await subscriber.subscribe("knowledge.>", handle_any_knowledge)

# Category: get all security-related knowledge
await subscriber.subscribe("knowledge.security.*", handle_security)

# Specific: only get new architecture decisions
await subscriber.subscribe("knowledge.architecture.decision", handle_adr)
```

## Graph-Based Knowledge Queries

While NATS handles real-time sharing, the Neo4j graph serves persistent knowledge retrieval. Agents query the graph to find knowledge shared by other agents:

```cypher
// Find knowledge shared by a specific agent about a service
MATCH (w:WikiEntry)-[:DOCUMENTS]->(s:Service {name: $serviceName})
WHERE w.createdBy <> $myAgentId
RETURN w.title, w.content, w.createdBy, w.updatedAt, w.confidence
ORDER BY w.updatedAt DESC
LIMIT 5
```

For cross-agent context building, agents query knowledge from multiple contributors to get diverse perspectives:

```cypher
// Get multi-agent perspective on a topic
MATCH (w:WikiEntry)
WHERE w.category = $category
WITH w, w.createdBy AS author

// Group by author to get diverse perspectives
WITH author, collect(w) AS entries
UNWIND entries[0..2] AS topEntry

RETURN topEntry.title, topEntry.slug, topEntry.content,
       author AS contributedBy, topEntry.confidence
ORDER BY topEntry.confidence DESC
```

## Knowledge Conflict Resolution

When multiple agents have conflicting knowledge, the system must resolve disagreements. This happens more often than you might expect: the CTO agent may document a planned architecture while the DevOps agent documents the actual deployed state.

```cypher
// Detect conflicting knowledge entries
MATCH (w1:WikiEntry)-[:DOCUMENTS]->(s:Service)<-[:DOCUMENTS]-(w2:WikiEntry)
WHERE w1 <> w2
  AND w1.category = w2.category
  AND w1.createdBy <> w2.createdBy

// Check for semantic similarity (potential overlap/conflict)
WITH w1, w2, s,
     gds.similarity.cosine(w1.embedding, w2.embedding) AS similarity
WHERE similarity > 0.85

RETURN w1.slug AS entry1, w1.createdBy AS author1,
       w2.slug AS entry2, w2.createdBy AS author2,
       s.name AS service, similarity
ORDER BY similarity DESC
```

Resolution strategies depend on the conflict type:

```python
async def resolve_knowledge_conflict(entry1: dict, entry2: dict) -> str:
    """Resolve conflicting knowledge between agents."""
    
    # Strategy 1: Freshness wins for factual knowledge
    if entry1["category"] in ["operations", "architecture"]:
        winner = entry1 if entry1["updatedAt"] > entry2["updatedAt"] else entry2
        return f"Resolved by freshness: {winner['slug']}"
    
    # Strategy 2: Higher confidence wins for synthesized knowledge
    if entry1.get("confidence") and entry2.get("confidence"):
        if abs(entry1["confidence"] - entry2["confidence"]) > 0.15:
            winner = entry1 if entry1["confidence"] > entry2["confidence"] else entry2
            return f"Resolved by confidence: {winner['slug']}"
    
    # Strategy 3: Merge - both entries contain valid but complementary info
    # Create a merged entry and deprecate the originals
    merged_content = await merge_knowledge(entry1["content"], entry2["content"])
    return f"Merged into new entry"
```

## Knowledge Propagation Patterns

Different knowledge types have different propagation needs:

### Broadcast Pattern
Critical knowledge that all agents need immediately:
```python
# Security vulnerability - broadcast to all agents
await publisher.publish_knowledge("security.vulnerability", {
    "cve": "CVE-2026-1234",
    "severity": "critical",
    "affectedPackage": "commons-lib",
    "affectedServices": ["auth-service", "api-gateway", "user-service"],
    "recommendation": "Upgrade to v2.3.1 immediately"
})
```

### Targeted Pattern
Knowledge relevant only to specific agents:
```python
# Send directly to the agent responsible for the affected service
await hub.send_to_agent("agent-devops", {
    "type": "knowledge.deployment.pattern",
    "content": "Discovered that payment-service needs blue-green deploys due to long-running connections",
    "service": "payment-service",
    "source": "agent-cto"
})
```

### Lazy Pattern
Knowledge stored in the graph for retrieval on demand:
```cypher
// Store knowledge that agents will find when they need it
CREATE (w:WikiEntry {
  slug: 'go-module-proxy-config',
  title: 'Go Module Proxy Configuration for Private Repos',
  content: $content,
  embedding: $embedding,
  category: 'operations',
  createdBy: 'agent-devops',
  createdAt: datetime(),
  confidence: 0.88
})
```

## Measuring Knowledge Sharing Effectiveness

We track metrics on knowledge sharing to ensure it's actually helping agents perform better:

```cypher
// Knowledge sharing metrics dashboard
// How much knowledge is being shared?
MATCH (w:WikiEntry)
WITH w.createdBy AS agent, count(w) AS contributions
RETURN agent, contributions
ORDER BY contributions DESC

// How often is shared knowledge used?
MATCH (w:WikiEntry)
WHERE w.retrievalCount > 0
WITH w.createdBy AS author,
     sum(w.retrievalCount) AS totalRetrievals
RETURN author, totalRetrievals

// Knowledge flow: who learns from whom?
MATCH (w:WikiEntry)
WHERE w.createdBy <> w.updatedBy AND w.updatedBy IS NOT NULL
WITH w.createdBy AS creator, w.updatedBy AS updater, count(*) AS collaborations
RETURN creator, updater, collaborations
ORDER BY collaborations DESC
```

## Building a Learning Organization

Cross-agent knowledge sharing creates a learning organization where intelligence compounds. When the security agent performs an [automated security audit](/blog/automated-security-auditing) and discovers a pattern, that knowledge immediately becomes available to every agent in the fleet. When the DevOps agent resolves a complex [cloud infrastructure issue](/blog/cloud-discovery-ai-agents), the learning persists for future agents facing similar challenges.

This is the [multi-agent architecture](/blog/multi-agent-architecture-patterns) operating at its best: not just parallel execution, but collaborative intelligence where the whole is genuinely greater than the sum of its parts. Each agent makes every other agent smarter.

The patterns described here, NATS pub/sub for real-time events, Neo4j for persistent knowledge, and direct messaging for targeted sharing, form the information backbone that makes agent.ceo's fleet operate as a coherent intelligence rather than isolated workers.

> agent.ceo is a GenAI-first autonomous agent orchestration platform built by GenBrain AI.

## Try agent.ceo

**SaaS** — Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).

**Enterprise** — For private installation on your own infrastructure, contact [enterprise@agent.ceo](mailto:enterprise@agent.ceo).

---
*agent.ceo is built by [GenBrain AI](https://genbrain.ai) — a GenAI-first autonomous agent orchestration platform. General inquiries: hello@agent.ceo | Security: security@agent.ceo*
