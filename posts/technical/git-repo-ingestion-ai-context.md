---
title: "Git Repository Ingestion for AI Context"
slug: "git-repo-ingestion-ai-context"
date: 2026-05-10
category: technical
cluster: "knowledge-management"
tags: [git, repository-analysis, code-intelligence, ai-context, knowledge-extraction]
description: "How AI agents clone, analyze, and extract architectural knowledge from git repositories to build organizational context for decision making."
relatedPosts: [building-ai-knowledge-base, wiki-knowledge-graphs, cross-agent-knowledge-sharing]
---

# Git Repository Ingestion for AI Context

Source code repositories contain the ground truth of how an organization's systems actually work. Not how they were designed to work, not how the documentation says they work, but how they actually function in production today. For AI agents to make informed decisions about infrastructure, deployments, and architecture, they need to understand this ground truth.

At agent.ceo, git repository ingestion is the foundation of how agents build contextual understanding. When an agent [connects to a GitHub repository](/blog/connecting-ai-agents-github), it doesn't just clone the code. It extracts structured knowledge: service boundaries, dependency graphs, configuration patterns, deployment specifications, and architecture decisions embedded in the code itself.

## The Ingestion Pipeline

Repository ingestion follows a multi-phase pipeline. Each phase extracts different knowledge types and writes them to the [Neo4j knowledge graph](/blog/building-ai-knowledge-base) for other agents to query.

### Phase 1: Repository Cloning and Metadata

The first phase establishes the repository as a known entity in the organizational graph:

```cypher
// Register repository in knowledge graph
MERGE (r:Repository {url: $repoUrl})
SET r.name = $repoName,
    r.defaultBranch = $defaultBranch,
    r.lastIngested = datetime(),
    r.languages = $detectedLanguages,
    r.size = $repoSize

// Link to owning team
MATCH (t:Team {name: $teamName})
MERGE (t)-[:OWNS]->(r)
```

Agents use SSH key authentication configured through the agent-hub to clone repositories securely. The clone operation happens in an ephemeral workspace that gets cleaned up after ingestion completes.

### Phase 2: Structure Analysis

The structure analysis phase identifies services, packages, and modules within the repository. For monorepos, this means discovering service boundaries. For single-service repos, it means understanding internal architecture:

```python
import os
from pathlib import Path

def analyze_repository_structure(repo_path: str) -> dict:
    """Extract structural knowledge from a repository."""
    structure = {
        "services": [],
        "packages": [],
        "configs": [],
        "infrastructure": []
    }
    
    # Detect service boundaries
    service_indicators = [
        "Dockerfile",
        "docker-compose.yml", 
        "service.yaml",
        "deployment.yaml",
        "main.go",
        "app.py",
        "index.ts"
    ]
    
    for root, dirs, files in os.walk(repo_path):
        # Skip hidden directories and node_modules
        dirs[:] = [d for d in dirs if not d.startswith('.') 
                   and d != 'node_modules' and d != 'vendor']
        
        indicators_found = [f for f in files if f in service_indicators]
        if indicators_found:
            relative_path = os.path.relpath(root, repo_path)
            structure["services"].append({
                "path": relative_path,
                "indicators": indicators_found,
                "name": infer_service_name(root, indicators_found)
            })
    
    return structure
```

### Phase 3: Dependency Extraction

Dependencies reveal the true architecture of a system. Agents parse dependency manifests across languages to build a comprehensive dependency graph:

```python
def extract_dependencies(repo_path: str, service_path: str) -> list:
    """Extract dependencies from various manifest formats."""
    dependencies = []
    
    # package.json (Node.js)
    pkg_json = Path(repo_path) / service_path / "package.json"
    if pkg_json.exists():
        import json
        pkg = json.loads(pkg_json.read_text())
        for dep, version in pkg.get("dependencies", {}).items():
            dependencies.append({
                "name": dep,
                "version": version,
                "type": "runtime",
                "ecosystem": "npm"
            })
    
    # go.mod (Go)
    go_mod = Path(repo_path) / service_path / "go.mod"
    if go_mod.exists():
        for line in go_mod.read_text().splitlines():
            if line.strip() and not line.startswith("//"):
                parts = line.strip().split()
                if len(parts) == 2 and "/" in parts[0]:
                    dependencies.append({
                        "name": parts[0],
                        "version": parts[1],
                        "type": "runtime",
                        "ecosystem": "go"
                    })
    
    return dependencies
```

These dependencies get written to the knowledge graph with relationships that enable cross-repository impact analysis:

```cypher
// Store extracted dependencies
UNWIND $dependencies AS dep
MATCH (s:Service {name: $serviceName})
MERGE (d:Dependency {name: dep.name, ecosystem: dep.ecosystem})
MERGE (s)-[r:USES]->(d)
SET r.version = dep.version,
    r.type = dep.type,
    r.extractedAt = datetime()
```

### Phase 4: Configuration Pattern Extraction

Configuration files reveal deployment topology, environment requirements, and operational characteristics. Agents parse Kubernetes manifests, Terraform files, and CI/CD configurations:

```cypher
// Store Kubernetes deployment knowledge
MATCH (s:Service {name: $serviceName})
MERGE (k:K8sDeployment {
  name: $deploymentName,
  namespace: $namespace
})
MERGE (s)-[:DEPLOYED_AS]->(k)
SET k.replicas = $replicas,
    k.resources = $resourceSpec,
    k.env = $environmentName,
    k.lastSeen = datetime()

// Link to infrastructure dependencies
UNWIND $infraDeps AS infra
MERGE (i:InfraResource {type: infra.type, name: infra.name})
MERGE (k)-[:REQUIRES]->(i)
```

### Phase 5: Knowledge Synthesis

The final phase is where AI reasoning enters the pipeline. After extracting raw structural data, agents synthesize higher-level knowledge: architecture patterns, potential risks, and operational insights:

```cypher
// Agent creates a synthesized wiki entry about repo architecture
CREATE (w:WikiEntry {
  slug: $slug,
  title: $title,
  content: $synthesizedContent,
  embedding: $contentEmbedding,
  sourceType: 'repository-analysis',
  sourceRepo: $repoUrl,
  createdBy: $agentId,
  createdAt: datetime(),
  confidence: $confidenceScore
})

// Link wiki entry to analyzed services
UNWIND $serviceNames AS svcName
MATCH (s:Service {name: svcName})
MERGE (w)-[:DOCUMENTS]->(s)
```

## Incremental Ingestion

Full repository ingestion is expensive. For ongoing operations, agents perform incremental ingestion based on git history:

```python
def get_changes_since_last_ingestion(repo_path: str, last_commit: str) -> list:
    """Get files changed since last ingestion."""
    import subprocess
    
    result = subprocess.run(
        ["git", "diff", "--name-status", last_commit, "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    
    changes = []
    for line in result.stdout.splitlines():
        status, *paths = line.split('\t')
        changes.append({
            "status": status,  # A=added, M=modified, D=deleted
            "path": paths[0],
            "new_path": paths[1] if len(paths) > 1 else None
        })
    
    return changes
```

This enables agents to update the knowledge graph efficiently when repositories change, keeping organizational context current without repeated full analysis.

## Cross-Repository Knowledge

The real power emerges when agents connect knowledge across repositories. A change in a shared library repository affects every service that depends on it. The knowledge graph makes these connections explicit:

```cypher
// Find all services affected by a library change
MATCH (lib:Repository {name: $changedLibrary})
MATCH (lib)-[:CONTAINS]->(pkg:Package)
MATCH (s:Service)-[:USES]->(d:Dependency {name: pkg.name})
MATCH (s)<-[:CONTAINS]-(r:Repository)
MATCH (s)-[:OWNED_BY]->(t:Team)
RETURN s.name AS affectedService, 
       r.name AS repository,
       t.name AS owningTeam,
       d.version AS currentVersion
```

This query pattern powers [cross-agent knowledge sharing](/blog/cross-agent-knowledge-sharing). When the CTO agent identifies a breaking change in a shared library, it can immediately determine the blast radius and notify relevant team agents.

## Architecture Decision Extraction

Beyond code structure, repositories contain architecture decisions in ADR documents, PR descriptions, and commit messages. Agents extract these decisions and link them to the services they affect:

```cypher
// Store an architecture decision record
CREATE (adr:Decision {
  id: $adrId,
  title: $title,
  status: $status,
  context: $context,
  decision: $decision,
  consequences: $consequences,
  createdAt: date($dateString)
})
MATCH (r:Repository {name: $repoName})
MERGE (r)-[:CONTAINS_DECISION]->(adr)

// Link to affected services
UNWIND $affectedServices AS svcName
MATCH (s:Service {name: svcName})
MERGE (adr)-[:AFFECTS]->(s)
```

## Security Considerations

Repository ingestion must respect security boundaries. Agents only access repositories they're authorized for, and sensitive data like secrets or credentials is never stored in the knowledge graph. The ingestion pipeline includes filtering for [security-sensitive patterns](/blog/automated-security-auditing):

```python
SENSITIVE_PATTERNS = [
    r'(?i)(api[_-]?key|secret|password|token)\s*[=:]\s*["\']?[^\s"\']+',
    r'-----BEGIN (RSA |EC )?PRIVATE KEY-----',
    r'(?i)aws[_-]?(access[_-]?key|secret)',
]

def filter_sensitive_content(content: str) -> str:
    """Remove sensitive data before storing in knowledge graph."""
    import re
    filtered = content
    for pattern in SENSITIVE_PATTERNS:
        filtered = re.sub(pattern, '[REDACTED]', filtered)
    return filtered
```

## Building Organizational Context

Repository ingestion transforms isolated codebases into connected organizational knowledge. Each ingestion cycle enriches the graph with new relationships and updated context. Over time, agents develop a comprehensive understanding of how systems interconnect, who owns what, and how architecture evolves.

This is the foundation for intelligent [AI-powered DevOps](/blog/ai-powered-devops). Agents that understand code architecture can make better deployment decisions, identify potential issues before they become incidents, and suggest improvements based on patterns observed across the entire organization.

The key insight is that repository ingestion isn't a one-time import. It's a continuous process where agents maintain living knowledge about organizational systems. As code evolves, so does the knowledge graph, ensuring agents always work with current context.

## Try agent.ceo

Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).
