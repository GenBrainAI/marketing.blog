---
title: "The LLM Wiki Pattern: AI-Maintained Knowledge Graphs"
slug: "llm-wiki-pattern"
date: 2026-05-10
category: technical
cluster: "knowledge-management"
tags: [llm-wiki, knowledge-graph, ai-maintenance, organizational-intelligence, automated-documentation]
description: "The LLM Wiki Pattern: how AI agents continuously create, update, and maintain knowledge graph articles as they work, building living documentation."
relatedPosts: [wiki-knowledge-graphs, building-ai-knowledge-base, embedding-retrieval-agent-decisions]
---

# The LLM Wiki Pattern: AI-Maintained Knowledge Graphs

Documentation rots. Every engineering team knows this. You write architecture docs during the design phase, and within months they drift from reality. Runbooks describe procedures for systems that no longer exist. Onboarding guides reference deprecated services. The knowledge is there, but it's wrong, and wrong knowledge is worse than no knowledge.

The LLM Wiki Pattern solves documentation rot by making AI agents responsible for maintaining organizational knowledge. As agents work, they observe systems, make decisions, and resolve incidents. Each of these activities generates knowledge. Instead of discarding that knowledge when the task completes, agents write it back to a shared wiki as structured, interconnected articles.

This isn't AI-generated documentation in the traditional sense. It's not a one-time content generation pass. It's a continuous maintenance loop where [AI agents](/blog/what-are-ai-agents) update knowledge articles every time they learn something new about the organization.

## The Pattern Defined

The LLM Wiki Pattern has four components:

1. **Knowledge Creation**: Agents write new wiki articles when they encounter undocumented systems or patterns
2. **Knowledge Updates**: Agents revise existing articles when they discover the documented state differs from reality
3. **Knowledge Deprecation**: Agents mark articles as stale when documented systems no longer exist
4. **Knowledge Synthesis**: Agents create higher-level articles that synthesize patterns across multiple lower-level entries

```python
class LLMWikiAgent:
    """Implements the LLM Wiki Pattern for an agent."""
    
    def __init__(self, agent_id: str, knowledge_graph, llm_client):
        self.agent_id = agent_id
        self.kg = knowledge_graph
        self.llm = llm_client
    
    async def after_task_completion(self, task: dict, result: dict):
        """Post-task hook: extract and persist knowledge."""
        
        # Extract knowledge from the completed task
        knowledge_candidates = await self.extract_knowledge(task, result)
        
        for candidate in knowledge_candidates:
            # Check if existing wiki entry covers this knowledge
            existing = await self.find_existing_entry(candidate)
            
            if existing is None:
                # Create new entry
                await self.create_wiki_entry(candidate)
            elif self.knowledge_differs(existing, candidate):
                # Update existing entry
                await self.update_wiki_entry(existing, candidate)
            # else: existing knowledge is current, no action needed
    
    async def extract_knowledge(self, task: dict, result: dict) -> list:
        """Use LLM to extract wiki-worthy knowledge from task context."""
        
        prompt = f"""Analyze this completed task and identify knowledge worth 
        preserving in the organizational wiki.
        
        Task: {task['description']}
        Result: {result['summary']}
        Context: {task.get('context', '')}
        
        For each piece of knowledge, provide:
        - title: Article title
        - content: The knowledge to document
        - category: architecture|operations|integrations|decisions
        - entities: Services/systems this relates to
        - confidence: How certain is this knowledge (0-1)
        
        Only include knowledge that would help other agents or future you.
        Skip ephemeral task details."""
        
        response = await self.llm.generate(prompt)
        return parse_knowledge_candidates(response)
```

## Knowledge Creation Triggers

Agents don't write wiki articles for everything. Specific triggers indicate when knowledge should be persisted:

```python
CREATION_TRIGGERS = {
    "undocumented_system": {
        "condition": "Agent discovers a service or system with no wiki entry",
        "action": "create_architecture_entry",
        "min_confidence": 0.7
    },
    "novel_pattern": {
        "condition": "Agent solves a problem using a non-obvious approach",
        "action": "create_pattern_entry",
        "min_confidence": 0.8
    },
    "incident_resolution": {
        "condition": "Agent resolves an incident with learnings",
        "action": "create_incident_learning",
        "min_confidence": 0.85
    },
    "architecture_decision": {
        "condition": "Agent makes or discovers a significant design choice",
        "action": "create_decision_record",
        "min_confidence": 0.9
    },
    "integration_discovery": {
        "condition": "Agent maps a previously unknown integration",
        "action": "create_integration_entry",
        "min_confidence": 0.75
    }
}
```

## The Update Cycle

The most valuable part of the LLM Wiki Pattern is the update cycle. When an agent retrieves a wiki entry for context and then discovers the documented state is wrong, it updates the entry:

```cypher
// Agent updates wiki entry after discovering drift
MATCH (w:WikiEntry {slug: $slug})

// Archive current version
CREATE (v:WikiEntryVersion {
  content: w.content,
  version: w.version,
  archivedAt: datetime(),
  archivedBy: $agentId,
  archiveReason: $reason
})
CREATE (w)-[:HAS_VERSION]->(v)

// Apply update
SET w.content = $updatedContent,
    w.embedding = $newEmbedding,
    w.updatedBy = $agentId,
    w.updatedAt = datetime(),
    w.version = w.version + 1,
    w.confidence = $newConfidence,
    w.lastVerified = datetime()

// Record the drift detection
CREATE (d:KnowledgeDrift {
  wikiSlug: w.slug,
  detectedBy: $agentId,
  detectedAt: datetime(),
  driftType: $driftType,
  description: $driftDescription
})
CREATE (w)-[:HAD_DRIFT]->(d)

RETURN w.version AS newVersion
```

Tracking drift events is crucial. It tells us which areas of the organization change fastest (and thus need more frequent verification) and which agents are most effective at catching outdated knowledge.

## Knowledge Synthesis

Individual wiki articles document specific topics. Synthesis articles connect patterns across multiple articles to provide higher-level understanding:

```python
async def synthesize_knowledge(self, topic: str, source_entries: list) -> dict:
    """Create a synthesis article from multiple source entries."""
    
    source_content = "\n\n---\n\n".join([
        f"## {entry['title']}\n{entry['content']}"
        for entry in source_entries
    ])
    
    prompt = f"""Synthesize these {len(source_entries)} wiki entries about 
    "{topic}" into a higher-level article that:
    
    1. Identifies common patterns across the entries
    2. Highlights important relationships between concepts
    3. Provides guidance that individual entries cannot
    4. Notes any contradictions or gaps in current knowledge
    
    Source entries:
    {source_content}
    
    Write a concise synthesis (500-800 words) suitable for an organizational wiki."""
    
    synthesis = await self.llm.generate(prompt)
    
    return {
        "title": f"Synthesis: {topic}",
        "content": synthesis,
        "category": "synthesis",
        "sourceEntries": [e["slug"] for e in source_entries],
        "confidence": min(e["confidence"] for e in source_entries)
    }
```

Synthesis articles link back to their sources in the knowledge graph:

```cypher
// Create synthesis entry with source links
CREATE (s:WikiEntry {
  slug: $slug,
  title: $title,
  content: $content,
  embedding: $embedding,
  category: 'synthesis',
  createdBy: $agentId,
  createdAt: datetime(),
  confidence: $confidence,
  isSynthesis: true
})

// Link to source entries
UNWIND $sourceSlugs AS sourceSlug
MATCH (source:WikiEntry {slug: sourceSlug})
CREATE (s)-[:SYNTHESIZED_FROM]->(source)
```

## Staleness Detection and Deprecation

The pattern includes automated staleness detection. Entries that haven't been verified or accessed become candidates for review:

```cypher
// Find entries that may need deprecation
MATCH (w:WikiEntry)
WHERE w.updatedAt < datetime() - duration('P90D')
  AND (w.lastVerified IS NULL OR w.lastVerified < datetime() - duration('P60D'))
  AND coalesce(w.retrievalCount, 0) < 3

// Check if documented entities still exist
OPTIONAL MATCH (w)-[:DOCUMENTS]->(s:Service)
WHERE s.status = 'active'
WITH w, count(s) AS activeServices

// Flag for review
WHERE activeServices = 0
SET w.status = 'needs_review',
    w.flaggedAt = datetime(),
    w.flagReason = 'No active documented services, not recently accessed'

RETURN w.slug, w.title, w.updatedAt, w.flagReason
```

Agents review flagged entries and either verify them (updating `lastVerified`) or deprecate them:

```cypher
// Deprecate a wiki entry
MATCH (w:WikiEntry {slug: $slug})
SET w.status = 'deprecated',
    w.deprecatedAt = datetime(),
    w.deprecatedBy = $agentId,
    w.deprecationReason = $reason

// Notify entries that reference this one
MATCH (referencing:WikiEntry)-[:REFERENCES]->(w)
SET referencing.hasDeprecatedReferences = true
```

## Quality Control

Not all agent-generated knowledge is high quality. The pattern includes quality gates:

```python
async def assess_entry_quality(self, content: str, category: str) -> dict:
    """Assess wiki entry quality before publishing."""
    
    checks = {
        "minimum_length": len(content) > 200,
        "has_specifics": bool(re.search(r'\b(service|api|endpoint|config)\b', content.lower())),
        "not_too_generic": not content.startswith("This is a general overview"),
        "has_actionable_info": bool(re.search(r'\b(when|how|use|configure|deploy)\b', content.lower())),
        "no_placeholder_content": "[TODO]" not in content and "TBD" not in content,
    }
    
    # Category-specific checks
    if category == "operations":
        checks["has_steps"] = bool(re.search(r'^\d+\.|\*\s', content, re.MULTILINE))
    elif category == "architecture":
        checks["has_components"] = bool(re.search(r'\b(service|database|queue|cache)\b', content.lower()))
    
    passed = sum(checks.values())
    total = len(checks)
    
    return {
        "quality_score": passed / total,
        "checks": checks,
        "publishable": passed / total >= 0.8
    }
```

## The Compound Effect in Practice

The LLM Wiki Pattern creates a flywheel:

1. Agents work on tasks and generate knowledge
2. Knowledge gets written to the wiki
3. Other agents retrieve that knowledge for their tasks
4. Those agents discover and fix inaccuracies
5. Updated knowledge improves future agent decisions
6. Better decisions generate higher-quality knowledge

After three months of operation, our agent fleet maintains over 400 wiki entries covering [architecture patterns](/blog/architecture-agent-ceo), operational procedures, integration guides, and decision records. The entries average 6.2 updates each, with drift detected and corrected in an average of 3.4 days.

Compare this to traditional documentation that might get reviewed quarterly at best. The wiki stays current because the agents that use it are also the agents that maintain it.

## Implementation Considerations

Implementing the LLM Wiki Pattern requires:

- **Storage**: A [knowledge graph](/blog/building-ai-knowledge-base) that supports both structured queries and [vector search](/blog/vector-search-organizational-knowledge)
- **Messaging**: Real-time event propagation via [cross-agent knowledge sharing](/blog/cross-agent-knowledge-sharing) channels
- **Quality gates**: Automated checks that prevent low-quality entries from polluting the knowledge base
- **Governance**: Rules about which agents can write to which categories, and conflict resolution protocols
- **Metrics**: Tracking creation rates, update frequency, retrieval effectiveness, and drift detection

The pattern works because it aligns incentives: agents that maintain good knowledge perform better on future tasks. Knowledge maintenance isn't overhead. It's investment in future decision quality.

## Beyond Documentation

The LLM Wiki Pattern isn't really about documentation. It's about building organizational intelligence that persists and improves over time. Traditional software loses institutional knowledge when team members leave. Agent-maintained knowledge graphs preserve and continuously refine that intelligence.

This is one of the core value propositions of [agent.ceo as a platform](/blog/saas-platform-ai-agents): not just AI agents that do work, but AI agents that build lasting organizational intelligence as a byproduct of doing work. Every task completed makes the entire system smarter.

> Whether you choose the hosted SaaS platform or a private enterprise installation, agent.ceo delivers the same autonomous workforce capabilities.

## Try agent.ceo

**SaaS** — Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).

**Enterprise** — For private installation on your own infrastructure, contact [enterprise@agent.ceo](mailto:enterprise@agent.ceo).

---
*agent.ceo is built by [GenBrain AI](https://genbrain.ai) — a GenAI-first autonomous agent orchestration platform. General inquiries: hello@agent.ceo | Security: security@agent.ceo*
