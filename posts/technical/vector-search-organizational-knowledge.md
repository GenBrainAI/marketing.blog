---
title: "Vector Search for Organizational Knowledge"
slug: "vector-search-organizational-knowledge"
date: 2026-05-10
category: technical
cluster: "knowledge-management"
tags: [vector-search, embeddings, semantic-search, neo4j, knowledge-retrieval]
description: "Implement vector search over organizational knowledge so AI agents can find semantically relevant context for any task using embedding-based retrieval."
relatedPosts: [embedding-retrieval-agent-decisions, building-ai-knowledge-base, wiki-knowledge-graphs]
---

# Vector Search for Organizational Knowledge

Keyword search fails AI agents. When an agent needs to understand "how we handle authentication failures in the payment service," keyword matching might return results about authentication configuration or payment processing, but miss the critical incident report that describes the exact retry pattern the team adopted after a production outage. The concepts match, but the words don't.

Vector search solves this through semantic similarity. By representing knowledge as high-dimensional embedding vectors, agents can find contextually relevant information regardless of exact terminology. At agent.ceo, vector search is the primary retrieval mechanism agents use to find relevant organizational knowledge before making decisions.

## How Vector Search Works in Practice

Every piece of knowledge in our [Neo4j knowledge base](/blog/building-ai-knowledge-base) carries an embedding vector. When an agent needs context, it generates an embedding for its query and finds the nearest neighbors in vector space:

```cypher
// Vector similarity search for relevant wiki entries
WITH $queryEmbedding AS queryVec
CALL db.index.vector.queryNodes('wiki_embeddings', 10, queryVec)
YIELD node AS wiki, score
WHERE score > 0.78
RETURN wiki.title, wiki.slug, wiki.content, wiki.updatedAt, score
ORDER BY score DESC
```

The threshold of 0.78 isn't arbitrary. Through testing across thousands of agent queries, we found this balances relevance (avoiding noise) against recall (not missing important context). Different knowledge types may warrant different thresholds.

## Setting Up Vector Indexes in Neo4j

Neo4j supports native vector indexes starting with version 5.11. Here's how we configure them for organizational knowledge:

```cypher
// Create vector index for wiki entries
CREATE VECTOR INDEX wiki_embeddings IF NOT EXISTS
FOR (w:WikiEntry)
ON (w.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// Create vector index for incident reports
CREATE VECTOR INDEX incident_embeddings IF NOT EXISTS
FOR (i:Incident)
ON (i.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// Create vector index for runbooks
CREATE VECTOR INDEX runbook_embeddings IF NOT EXISTS
FOR (r:Runbook)
ON (r.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};
```

We use 1536-dimensional embeddings from OpenAI's text-embedding-3-small model, though the system is model-agnostic. The cosine similarity function works best for normalized text embeddings.

## Generating Embeddings for Knowledge

Every knowledge node gets an embedding generated at creation and updated when content changes:

```python
import httpx
from typing import List

async def generate_embedding(text: str) -> List[float]:
    """Generate embedding vector for text content."""
    # Truncate to model's context window
    truncated = text[:8000]
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "text-embedding-3-small",
                "input": truncated
            }
        )
        data = response.json()
        return data["data"][0]["embedding"]


async def embed_and_store_wiki_entry(
    slug: str, 
    title: str, 
    content: str,
    agent_id: str
):
    """Create wiki entry with embedding in knowledge graph."""
    # Generate embedding from title + content for richer semantics
    embed_text = f"{title}\n\n{content}"
    embedding = await generate_embedding(embed_text)
    
    query = """
    MERGE (w:WikiEntry {slug: $slug})
    SET w.title = $title,
        w.content = $content,
        w.embedding = $embedding,
        w.updatedAt = datetime(),
        w.updatedBy = $agentId
    """
    
    await neo4j_session.run(query, {
        "slug": slug,
        "title": title,
        "content": content,
        "embedding": embedding,
        "agentId": agent_id
    })
```

## Hybrid Search: Combining Vector and Graph

Pure vector search finds semantically similar content, but it ignores the graph structure. The real power comes from combining vector similarity with graph traversal. An agent can find relevant knowledge AND follow relationships to gather full context:

```cypher
// Hybrid search: vector similarity + graph context
WITH $queryEmbedding AS queryVec
CALL db.index.vector.queryNodes('wiki_embeddings', 5, queryVec)
YIELD node AS wiki, score
WHERE score > 0.80

// Follow graph relationships for context enrichment
OPTIONAL MATCH (wiki)-[:DOCUMENTS]->(s:Service)
OPTIONAL MATCH (s)-[:OWNED_BY]->(t:Team)
OPTIONAL MATCH (s)-[:HAS_RUNBOOK]->(r:Runbook)
OPTIONAL MATCH (wiki)-[:REFERENCES]->(related:WikiEntry)

RETURN wiki.title, wiki.content, score,
       collect(DISTINCT s.name) AS services,
       collect(DISTINCT t.name) AS teams,
       collect(DISTINCT r.title) AS runbooks,
       collect(DISTINCT related.title) AS relatedArticles
ORDER BY score DESC
```

This hybrid approach gives agents both relevance-ranked results and the relational context needed for informed decision making. It's the bridge between [embedding-based retrieval](/blog/embedding-retrieval-agent-decisions) and structured graph queries.

## Multi-Type Knowledge Search

Agents often need to search across different knowledge types simultaneously. A query about "database connection pooling" might find relevant wiki entries, incident reports, and runbooks. We implement this with a unified search function:

```cypher
// Search across all knowledge types
WITH $queryEmbedding AS queryVec

// Search wiki entries
CALL db.index.vector.queryNodes('wiki_embeddings', 5, queryVec)
YIELD node AS wikiNode, score AS wikiScore
WITH collect({node: wikiNode, score: wikiScore, type: 'wiki'}) AS wikiResults, queryVec

// Search incidents
CALL db.index.vector.queryNodes('incident_embeddings', 5, queryVec)
YIELD node AS incidentNode, score AS incidentScore
WITH wikiResults, 
     collect({node: incidentNode, score: incidentScore, type: 'incident'}) AS incidentResults, 
     queryVec

// Search runbooks
CALL db.index.vector.queryNodes('runbook_embeddings', 3, queryVec)
YIELD node AS runbookNode, score AS runbookScore
WITH wikiResults + incidentResults + 
     collect({node: runbookNode, score: runbookScore, type: 'runbook'}) AS allResults

// Combine and rank
UNWIND allResults AS result
WHERE result.score > 0.75
RETURN result.type AS knowledgeType,
       result.node.title AS title,
       result.score AS relevance
ORDER BY result.score DESC
LIMIT 10
```

## Contextual Embedding Enhancement

Raw text embeddings sometimes miss organizational context. We enhance embedding quality by prepending metadata that helps the model understand the knowledge domain:

```python
def build_embedding_text(entry: dict) -> str:
    """Build enhanced text for embedding generation."""
    parts = []
    
    # Add type context
    parts.append(f"Type: {entry['type']}")
    
    # Add organizational context
    if entry.get('team'):
        parts.append(f"Team: {entry['team']}")
    if entry.get('services'):
        parts.append(f"Services: {', '.join(entry['services'])}")
    
    # Add the actual content
    parts.append(f"Title: {entry['title']}")
    parts.append(entry['content'])
    
    # Add tags for additional semantic signal
    if entry.get('tags'):
        parts.append(f"Tags: {', '.join(entry['tags'])}")
    
    return "\n".join(parts)
```

This technique improves retrieval precision by 15-20% in our benchmarks. When an agent searches for "payment service authentication," entries tagged with the payment team and auth-related services rank higher because their embeddings encode that organizational context.

## Freshness and Relevance Scoring

Not all knowledge ages equally. A wiki entry about current architecture is more valuable than a three-year-old incident report. We implement time-decay scoring that combines vector similarity with freshness:

```cypher
WITH $queryEmbedding AS queryVec
CALL db.index.vector.queryNodes('wiki_embeddings', 20, queryVec)
YIELD node AS wiki, score AS vectorScore

// Apply time decay: knowledge loses relevance over time
WITH wiki, vectorScore,
     duration.between(wiki.updatedAt, datetime()).days AS daysSinceUpdate,
     CASE 
       WHEN wiki.confidence IS NOT NULL THEN wiki.confidence 
       ELSE 0.5 
     END AS confidence

// Combined score: vector similarity * freshness * confidence
WITH wiki, vectorScore,
     vectorScore * (1.0 / (1.0 + daysSinceUpdate / 365.0)) * confidence AS finalScore
WHERE finalScore > 0.5

RETURN wiki.title, wiki.slug, wiki.content, finalScore
ORDER BY finalScore DESC
LIMIT 5
```

## Integration with Agent Workflows

Vector search integrates into every agent workflow through [MCP tools](/blog/mcp-tool-integration). When an agent starts a task, it automatically retrieves relevant context:

```json
{
  "name": "search_knowledge",
  "description": "Search organizational knowledge by semantic similarity",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Natural language description of needed knowledge"
      },
      "types": {
        "type": "array",
        "items": {"type": "string", "enum": ["wiki", "incident", "runbook", "decision"]},
        "description": "Knowledge types to search"
      },
      "scope": {
        "type": "object",
        "properties": {
          "team": {"type": "string"},
          "service": {"type": "string"}
        },
        "description": "Optional scope to narrow search"
      }
    },
    "required": ["query"]
  }
}
```

This tool is one of the most frequently called across the agent fleet. On average, agents perform 3-5 knowledge searches per task, building context before taking action. This pattern of "search before act" is what enables [AI agents](/blog/what-are-ai-agents) to make informed decisions rather than operating blindly.

## Measuring Search Quality

We track search quality through agent feedback loops. When an agent uses a search result successfully (the retrieved context helped complete the task), that signals relevance. When an agent ignores results or the task fails despite available knowledge, that signals a retrieval gap:

```cypher
// Record search feedback for quality improvement
MATCH (w:WikiEntry {slug: $usedSlug})
SET w.retrievalCount = coalesce(w.retrievalCount, 0) + 1,
    w.usefulness = coalesce(w.usefulness, 0) + $usefulnessSignal,
    w.lastRetrieved = datetime()
```

This feedback loop continuously improves retrieval quality. Articles that agents find useful get boosted; articles that never help get flagged for review or removal.

Vector search transforms organizational knowledge from a static archive into a dynamic resource that agents query naturally. Combined with the graph structure of Neo4j, it enables the kind of contextual intelligence that makes [AI agent teams](/blog/first-ai-agent-team) genuinely effective.

> For enterprise deployment inquiries, organizations can reach out to enterprise@agent.ceo.

## Try agent.ceo

**SaaS** — Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).

**Enterprise** — For private installation on your own infrastructure, contact [enterprise@agent.ceo](mailto:enterprise@agent.ceo).

---
*agent.ceo is built by [GenBrain AI](https://genbrain.ai) — a GenAI-first autonomous agent orchestration platform. General inquiries: hello@agent.ceo | Security: security@agent.ceo*
