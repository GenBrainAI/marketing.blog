---
title: "Embedding-Based Retrieval for Agent Decision Making"
slug: "embedding-retrieval-agent-decisions"
date: 2026-05-10
category: technical
cluster: "knowledge-management"
tags: [embeddings, retrieval, decision-making, ai-agents, rag, context-management]
description: "How AI agents use embedding-based retrieval to find relevant context before making decisions, implementing RAG patterns for organizational knowledge."
relatedPosts: [vector-search-organizational-knowledge, building-ai-knowledge-base, cross-agent-knowledge-sharing]
---

# Embedding-Based Retrieval for Agent Decision Making

An AI agent without context is just a language model making educated guesses. An AI agent with relevant organizational context makes informed decisions. The difference between these two modes is retrieval: the ability to find and surface the right knowledge at the right time.

At agent.ceo, embedding-based retrieval is the mechanism that transforms generic AI capabilities into organization-specific intelligence. Before an agent makes any significant decision, whether deploying code, responding to an incident, or suggesting an architecture change, it retrieves relevant context from the [organizational knowledge graph](/blog/building-ai-knowledge-base). This context grounds the agent's reasoning in reality rather than training data.

## The Retrieval-Augmented Decision Pattern

Every agent decision follows a consistent pattern: understand the task, retrieve relevant context, reason about options, then act. The retrieval step is where embeddings come in:

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class RetrievalContext:
    """Context retrieved for agent decision making."""
    wiki_entries: List[dict]
    incidents: List[dict]
    runbooks: List[dict]
    decisions: List[dict]
    confidence: float

async def retrieve_decision_context(
    task_description: str,
    scope: Optional[dict] = None
) -> RetrievalContext:
    """Retrieve all relevant context for an agent decision."""
    
    # Generate embedding for the task
    task_embedding = await generate_embedding(task_description)
    
    # Parallel retrieval across knowledge types
    wiki_results = await search_wiki(task_embedding, scope)
    incident_results = await search_incidents(task_embedding, scope)
    runbook_results = await search_runbooks(task_embedding, scope)
    decision_results = await search_decisions(task_embedding, scope)
    
    # Calculate overall context confidence
    all_scores = [r["score"] for r in wiki_results + incident_results]
    confidence = max(all_scores) if all_scores else 0.0
    
    return RetrievalContext(
        wiki_entries=wiki_results,
        incidents=incident_results,
        runbooks=runbook_results,
        decisions=decision_results,
        confidence=confidence
    )
```

## Embedding Strategies for Different Knowledge Types

Not all knowledge should be embedded the same way. A wiki article about service architecture needs different embedding treatment than a terse incident timeline. We use type-specific embedding strategies:

```python
def prepare_for_embedding(entry: dict) -> str:
    """Prepare knowledge entry for embedding based on type."""
    
    if entry["type"] == "wiki":
        # Wiki entries: title weighted heavily for topic matching
        return f"""Topic: {entry['title']}
Category: {entry['category']}
Services: {', '.join(entry.get('services', []))}

{entry['content'][:6000]}"""
    
    elif entry["type"] == "incident":
        # Incidents: symptoms and resolution are key for matching
        return f"""Incident: {entry['title']}
Severity: {entry['severity']}
Services Affected: {', '.join(entry['services'])}
Symptoms: {entry['symptoms']}
Root Cause: {entry['rootCause']}
Resolution: {entry['resolution']}"""
    
    elif entry["type"] == "runbook":
        # Runbooks: trigger conditions matter most for retrieval
        return f"""Runbook: {entry['title']}
Triggers: {entry['triggers']}
Applicable When: {entry['conditions']}
Steps Summary: {entry['summary']}"""
    
    elif entry["type"] == "decision":
        # Decisions: context and rationale for matching
        return f"""Decision: {entry['title']}
Status: {entry['status']}
Context: {entry['context']}
Decision: {entry['decision']}
Consequences: {entry['consequences']}"""
    
    return entry.get("content", "")
```

## Scoped Retrieval for Precision

Broad semantic search returns relevant results, but scoped retrieval returns precise results. When an agent knows it's working on a specific service or within a specific team's domain, it scopes retrieval accordingly:

```cypher
// Scoped retrieval: semantic search filtered by service context
WITH $queryEmbedding AS queryVec
CALL db.index.vector.queryNodes('wiki_embeddings', 20, queryVec)
YIELD node AS wiki, score

// Scope to specific service context
MATCH (wiki)-[:DOCUMENTS]->(s:Service)
WHERE s.name IN $serviceScope

// Boost entries from the same team
OPTIONAL MATCH (wiki)-[:RELEVANT_TO]->(t:Team {name: $teamName})
WITH wiki, score, 
     CASE WHEN t IS NOT NULL THEN score * 1.15 ELSE score END AS boostedScore
WHERE boostedScore > 0.75

RETURN wiki.slug, wiki.title, wiki.content, boostedScore
ORDER BY boostedScore DESC
LIMIT 5
```

The team boost (1.15x) ensures that team-specific knowledge ranks above generic knowledge when an agent is operating within a team's domain. This models the real-world pattern where local context is usually more relevant than global context.

## Multi-Hop Retrieval

Sometimes the directly retrieved knowledge isn't sufficient. An agent needs to follow connections to gather complete context. Multi-hop retrieval starts with embedding search and then traverses the graph:

```cypher
// Multi-hop retrieval: start with semantic match, follow graph
WITH $queryEmbedding AS queryVec
CALL db.index.vector.queryNodes('wiki_embeddings', 3, queryVec)
YIELD node AS seedWiki, score AS seedScore
WHERE seedScore > 0.82

// First hop: directly referenced entries
MATCH (seedWiki)-[:REFERENCES]->(hop1:WikiEntry)

// Second hop: entries documenting the same services
MATCH (seedWiki)-[:DOCUMENTS]->(s:Service)<-[:DOCUMENTS]-(hop2:WikiEntry)
WHERE hop2 <> seedWiki

// Combine with deduplication
WITH collect(DISTINCT {
  slug: seedWiki.slug, title: seedWiki.title, 
  content: seedWiki.content, hop: 0, score: seedScore
}) + collect(DISTINCT {
  slug: hop1.slug, title: hop1.title,
  content: hop1.content, hop: 1, score: seedScore * 0.8
}) + collect(DISTINCT {
  slug: hop2.slug, title: hop2.title,
  content: hop2.content, hop: 2, score: seedScore * 0.6
}) AS allResults

UNWIND allResults AS result
RETURN DISTINCT result.slug, result.title, result.content, 
       result.hop, result.score
ORDER BY result.score DESC
LIMIT 8
```

Each hop reduces the relevance score by a decay factor (0.8 for first hop, 0.6 for second hop), ensuring directly matched content ranks highest while still surfacing related context.

## Decision Confidence Scoring

Not all retrieval provides equal confidence for decision making. An agent should know how much to trust its retrieved context:

```python
def calculate_decision_confidence(context: RetrievalContext) -> dict:
    """Calculate confidence metrics for a decision based on retrieval."""
    
    metrics = {
        "context_richness": 0.0,  # How much relevant context exists
        "context_freshness": 0.0,  # How current the context is
        "context_agreement": 0.0,  # Do sources agree or conflict
        "overall": 0.0
    }
    
    all_entries = (context.wiki_entries + context.incidents + 
                   context.runbooks + context.decisions)
    
    if not all_entries:
        return metrics
    
    # Richness: more high-quality results = more confidence
    high_quality = [e for e in all_entries if e["score"] > 0.85]
    metrics["context_richness"] = min(len(high_quality) / 5.0, 1.0)
    
    # Freshness: recent updates indicate current knowledge
    from datetime import datetime, timedelta
    recent_cutoff = datetime.now() - timedelta(days=30)
    recent = [e for e in all_entries 
              if e.get("updatedAt") and e["updatedAt"] > recent_cutoff]
    metrics["context_freshness"] = len(recent) / max(len(all_entries), 1)
    
    # Agreement: check if retrieved contexts are consistent
    # (simplified - real implementation uses embedding similarity)
    if len(all_entries) >= 2:
        embeddings = [e["embedding"] for e in all_entries if "embedding" in e]
        if len(embeddings) >= 2:
            avg_similarity = average_pairwise_similarity(embeddings)
            metrics["context_agreement"] = avg_similarity
    
    # Overall confidence
    metrics["overall"] = (
        metrics["context_richness"] * 0.4 +
        metrics["context_freshness"] * 0.3 +
        metrics["context_agreement"] * 0.3
    )
    
    return metrics
```

When confidence is low, agents can escalate decisions to humans or request additional context from other agents via [agent-to-agent messaging](/blog/agent-to-agent-messaging).

## Context Window Management

Retrieved context must fit within the agent's context window. We implement intelligent truncation that preserves the most relevant information:

```python
def fit_context_to_window(
    context: RetrievalContext,
    max_tokens: int = 8000
) -> str:
    """Format retrieved context to fit within token budget."""
    
    sections = []
    remaining_tokens = max_tokens
    
    # Priority 1: Highest-scoring wiki entries (most relevant)
    for entry in sorted(context.wiki_entries, 
                        key=lambda x: x["score"], reverse=True)[:3]:
        section = format_wiki_context(entry)
        tokens = estimate_tokens(section)
        if tokens <= remaining_tokens:
            sections.append(section)
            remaining_tokens -= tokens
    
    # Priority 2: Relevant runbooks (actionable)
    for runbook in context.runbooks[:2]:
        section = format_runbook_context(runbook)
        tokens = estimate_tokens(section)
        if tokens <= remaining_tokens:
            sections.append(section)
            remaining_tokens -= tokens
    
    # Priority 3: Historical incidents (pattern matching)
    for incident in context.incidents[:2]:
        section = format_incident_context(incident)
        tokens = estimate_tokens(section)
        if tokens <= remaining_tokens:
            sections.append(section)
            remaining_tokens -= tokens
    
    # Priority 4: Architecture decisions (constraints)
    for decision in context.decisions[:1]:
        section = format_decision_context(decision)
        tokens = estimate_tokens(section)
        if tokens <= remaining_tokens:
            sections.append(section)
            remaining_tokens -= tokens
    
    return "\n\n---\n\n".join(sections)
```

This priority ordering reflects decision-making importance: current knowledge first, then procedures, then historical patterns, then architectural constraints. The [agent context management](/blog/agent-context-management) system ensures agents never exceed their effective context window.

## Feedback Loops for Retrieval Quality

Retrieval quality improves over time through implicit feedback from agent outcomes:

```cypher
// Record positive retrieval feedback when task succeeds
MATCH (w:WikiEntry {slug: $usedSlug})
SET w.successfulRetrievals = coalesce(w.successfulRetrievals, 0) + 1

// Record negative feedback when retrieved context didn't help
MATCH (w:WikiEntry {slug: $ignoredSlug})
SET w.ignoredRetrievals = coalesce(w.ignoredRetrievals, 0) + 1

// Calculate retrieval effectiveness ratio
MATCH (w:WikiEntry)
WHERE (coalesce(w.successfulRetrievals, 0) + coalesce(w.ignoredRetrievals, 0)) > 10
WITH w, 
     toFloat(w.successfulRetrievals) / 
     (w.successfulRetrievals + w.ignoredRetrievals) AS effectiveness
WHERE effectiveness < 0.3
RETURN w.slug, w.title, effectiveness
ORDER BY effectiveness ASC
```

Entries with low effectiveness ratios are candidates for rewriting, re-embedding, or removal. This creates a self-improving knowledge system where retrieval quality compounds over time.

## Real-World Impact

In production, embedding-based retrieval reduces agent decision errors by 40-60% compared to agents operating without context. The pattern is simple but powerful: before every decision, search for relevant knowledge, assess confidence, and incorporate context into reasoning.

This is what separates an AI agent platform from a collection of disconnected AI tools. The knowledge layer, powered by embeddings and graph retrieval, creates organizational intelligence that every agent in the fleet can leverage. It's the foundation for building [AI agent teams](/blog/getting-started-agent-ceo) that genuinely understand your organization.

## Try agent.ceo

Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).
