---
title: "Preventing Cypher Injection in Knowledge Graphs"
slug: "preventing-cypher-injection"
date: 2026-05-10
category: technical
cluster: "security-compliance"
tags: [cypher-injection, neo4j, knowledge-graphs, security, parameterized-queries, input-validation]
description: "How to detect and prevent Cypher injection attacks in Neo4j knowledge graphs used by AI agent platforms. Includes vulnerable vs. fixed code examples."
relatedPosts: [automated-security-auditing, path-traversal-defense, ssrf-protection-ai-agents]
---

# Preventing Cypher Injection in Knowledge Graphs

Knowledge graphs power the contextual intelligence behind modern AI agent platforms. At agent.ceo, our agents build and query a Neo4j [knowledge graph](/blog/wiki-knowledge-graphs) that maps relationships between tasks, agents, decisions, and organizational knowledge. When our AI CSO agent ran its first [automated security audit](/blog/automated-security-auditing), it identified three HIGH-severity Cypher injection vulnerabilities -- places where user-controlled input could manipulate graph queries to exfiltrate data, modify relationships, or escalate privileges.

This post examines the anatomy of Cypher injection, demonstrates real vulnerable patterns our CSO agent caught, and provides the parameterized query patterns that eliminate the risk entirely.

## What Is Cypher Injection?

Cypher injection is the graph database equivalent of SQL injection. It occurs when untrusted input is concatenated into a Cypher query string, allowing an attacker to modify the query's logic. Unlike SQL injection, Cypher injection is less well-known, which means developers often lack the instinct to parameterize graph queries.

Consider this seemingly innocent query to look up an agent's task history:

```python
# VULNERABLE: String concatenation in Cypher query
def get_agent_tasks(agent_name: str):
    query = f"""
    MATCH (a:Agent {{name: '{agent_name}'}})
    -[:ASSIGNED]->(t:Task)
    RETURN t.title, t.status, t.priority
    ORDER BY t.created_at DESC
    """
    return neo4j_session.run(query)
```

An attacker who controls `agent_name` can inject arbitrary Cypher:

```
# Malicious input
agent_name = "'}}) RETURN 'x' AS x UNION MATCH (c:Credential) RETURN c.value AS x //"

# Resulting query becomes:
MATCH (a:Agent {name: ''}) RETURN 'x' AS x UNION MATCH (c:Credential) RETURN c.value AS x //'})
-[:ASSIGNED]->(t:Task)
RETURN t.title, t.status, t.priority
```

This exfiltrates all stored credentials from the graph. In a multi-agent platform where the [knowledge base](/blog/building-ai-knowledge-base) contains organizational secrets, the impact is catastrophic.

## Real Vulnerabilities Found by Our CSO Agent

### Vulnerability 1: Task Search with Unescaped User Input

```python
# VULNERABLE: Found in task-router service
class TaskRouter:
    def search_tasks(self, search_term: str, tenant_id: str):
        """Search tasks by keyword."""
        query = f"""
        MATCH (t:Task)
        WHERE t.tenant_id = '{tenant_id}'
        AND t.title CONTAINS '{search_term}'
        RETURN t
        LIMIT 50
        """
        return self.driver.session().run(query)
```

**Attack vector**: A malicious agent or compromised API input could inject through `search_term`:

```
search_term = "' OR 1=1 WITH t MATCH (t)-[:HAS_CREDENTIAL]->(c) RETURN c //"
```

This bypasses the tenant isolation and returns credentials across all tenants.

### Vulnerability 2: Dynamic Relationship Creation

```python
# VULNERABLE: Found in knowledge-graph-builder service
def create_relationship(self, from_node: str, to_node: str, rel_type: str):
    """Create a relationship between two nodes."""
    query = f"""
    MATCH (a {{id: '{from_node}'}})
    MATCH (b {{id: '{to_node}'}})
    CREATE (a)-[:{rel_type}]->(b)
    RETURN a, b
    """
    return self.session.run(query)
```

**Attack vector**: The `rel_type` parameter is directly interpolated into the query structure. An attacker could inject:

```
rel_type = "OWNS]->(b) DELETE b CREATE (a)-[:ADMIN"
```

This deletes the target node and creates an unauthorized admin relationship.

### Vulnerability 3: Agent Metadata Lookup

```python
# VULNERABLE: Found in agent-registry service
def get_agent_by_role(self, role: str):
    """Look up agents by their organizational role."""
    query = f"""
    MATCH (a:Agent)
    WHERE a.role = '{role}'
    RETURN a.name, a.capabilities, a.credentials_scope
    """
    return self.session.run(query)
```

**Attack vector**: If role selection passes through an API without validation:

```
role = "CSO' OR a.role = 'ADMIN' RETURN a.name, a.api_keys, a.private_key //"
```

## The Fix: Parameterized Queries

The solution is straightforward -- use Neo4j's built-in parameter substitution, which treats parameters as data rather than executable Cypher:

```python
# SECURE: Parameterized query - injection impossible
class SecureTaskRouter:
    def search_tasks(self, search_term: str, tenant_id: str):
        """Search tasks by keyword using parameterized query."""
        query = """
        MATCH (t:Task)
        WHERE t.tenant_id = $tenant_id
        AND t.title CONTAINS $search_term
        RETURN t
        LIMIT 50
        """
        return self.driver.session().run(
            query,
            tenant_id=tenant_id,
            search_term=search_term
        )

    def get_agent_tasks(self, agent_name: str):
        """Get tasks assigned to a specific agent."""
        query = """
        MATCH (a:Agent {name: $agent_name})
        -[:ASSIGNED]->(t:Task)
        RETURN t.title, t.status, t.priority
        ORDER BY t.created_at DESC
        """
        return self.driver.session().run(
            query,
            agent_name=agent_name
        )
```

For dynamic relationship types (which cannot be parameterized in Cypher), use an allowlist:

```python
# SECURE: Allowlist for dynamic relationship types
ALLOWED_RELATIONSHIPS = frozenset([
    "ASSIGNED_TO", "DEPENDS_ON", "CREATED_BY",
    "BELONGS_TO", "REFERENCES", "SUBTASK_OF",
    "REVIEWED_BY", "BLOCKED_BY"
])

def create_relationship(self, from_id: str, to_id: str, rel_type: str):
    """Create a relationship with validated type."""
    # Strict allowlist validation
    if rel_type not in ALLOWED_RELATIONSHIPS:
        raise ValueError(
            f"Invalid relationship type: {rel_type}. "
            f"Allowed: {ALLOWED_RELATIONSHIPS}"
        )

    # Additional input validation
    if not UUID_PATTERN.match(from_id) or not UUID_PATTERN.match(to_id):
        raise ValueError("Node IDs must be valid UUIDs")

    # Safe to use f-string for rel_type since it's from allowlist
    query = f"""
    MATCH (a {{id: $from_id}})
    MATCH (b {{id: $to_id}})
    CREATE (a)-[:{rel_type}]->(b)
    RETURN a, b
    """
    return self.session.run(query, from_id=from_id, to_id=to_id)
```

## Defense in Depth: Query Validation Layer

Beyond parameterized queries, we implemented a query validation middleware that inspects all Cypher before execution:

```python
import re
from typing import Optional

class CypherQueryValidator:
    """Validates Cypher queries before execution to prevent injection."""

    # Patterns that indicate potential injection attempts
    DANGEROUS_PATTERNS = [
        r"(?i)UNION\s+MATCH",        # UNION-based injection
        r"(?i)DELETE\s+",             # Destructive operations
        r"(?i)DETACH\s+DELETE",       # Node deletion
        r"(?i)SET\s+\w+\.\w+\s*=",   # Property modification
        r"(?i)REMOVE\s+",            # Label/property removal
        r"(?i)CREATE\s+\(",          # Unauthorized node creation
        r"(?i)CALL\s+db\.",          # Database procedures
        r"(?i)LOAD\s+CSV",           # File access
    ]

    # Maximum query complexity limits
    MAX_QUERY_LENGTH = 2000
    MAX_MATCH_CLAUSES = 5

    def validate(self, query: str, context: dict) -> Optional[str]:
        """
        Validate a Cypher query. Returns None if valid,
        or an error message if suspicious.
        """
        if len(query) > self.MAX_QUERY_LENGTH:
            return f"Query exceeds maximum length ({self.MAX_QUERY_LENGTH})"

        match_count = len(re.findall(r"(?i)\bMATCH\b", query))
        if match_count > self.MAX_MATCH_CLAUSES:
            return f"Query has too many MATCH clauses ({match_count})"

        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, query):
                # Check if this is an authorized write operation
                if not context.get("write_authorized"):
                    return f"Potentially dangerous pattern detected: {pattern}"

        return None  # Query is valid


class SecureNeo4jSession:
    """Wrapper around Neo4j session with query validation."""

    def __init__(self, driver, validator: CypherQueryValidator):
        self.driver = driver
        self.validator = validator

    def run(self, query: str, write_authorized=False, **parameters):
        """Execute a validated, parameterized Cypher query."""
        # Validate query structure
        error = self.validator.validate(
            query,
            context={"write_authorized": write_authorized}
        )
        if error:
            raise SecurityError(f"Query rejected: {error}")

        # Ensure all string parameters are properly typed
        for key, value in parameters.items():
            if isinstance(value, str) and len(value) > 1000:
                raise SecurityError(
                    f"Parameter '{key}' exceeds maximum length"
                )

        with self.driver.session() as session:
            return session.run(query, **parameters)
```

## Automated Detection: CSO Agent Scanning Pattern

Our CSO agent detects Cypher injection vulnerabilities by analyzing query construction patterns in workflow metadata:

```python
class CypherInjectionScanner:
    """Scan for Cypher injection vulnerabilities in agent code patterns."""

    INJECTION_INDICATORS = [
        # f-string with quotes in Cypher context
        r'f["\'].*MATCH.*\{[^$]',
        # .format() with Cypher keywords
        r'\.format\(.*\).*(?:MATCH|WHERE|RETURN)',
        # String concatenation with Cypher
        r'["\'].*(?:MATCH|WHERE|CREATE).*["\']\s*\+',
        # % formatting in queries
        r'%s.*(?:MATCH|WHERE|RETURN)',
    ]

    async def scan(self, service_metadata: dict) -> list:
        findings = []
        for pattern in self.INJECTION_INDICATORS:
            matches = await self.search_patterns(
                service_metadata, pattern
            )
            for match in matches:
                findings.append(Finding(
                    severity="HIGH",
                    cwe="CWE-943",
                    title="Potential Cypher injection",
                    location=match.location,
                    evidence=match.context,
                    remediation="Replace with parameterized query using $param syntax"
                ))
        return findings
```

## Testing for Cypher Injection

We added injection test cases to our CI/CD pipeline to prevent regression:

```python
import pytest

class TestCypherInjectionPrevention:
    """Verify that Cypher injection attempts are blocked."""

    INJECTION_PAYLOADS = [
        "' OR 1=1 //",
        "'}) RETURN n UNION MATCH (c:Credential) RETURN c //",
        "' SET n.admin=true RETURN n //",
        "' DETACH DELETE n //",
        "OWNS]->(b) DELETE b CREATE (a)-[:ADMIN",
    ]

    @pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
    def test_task_search_rejects_injection(self, payload, secure_router):
        """Task search must not be vulnerable to injection."""
        # Should either raise an error or return empty results
        # but NEVER execute the injected Cypher
        result = secure_router.search_tasks(
            search_term=payload,
            tenant_id="test-tenant"
        )
        # Verify no credential data leaked
        for record in result:
            assert "credential" not in str(record).lower()
            assert "api_key" not in str(record).lower()

    @pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
    def test_relationship_creation_rejects_injection(self, payload, secure_router):
        """Relationship creation must validate rel_type."""
        with pytest.raises(ValueError):
            secure_router.create_relationship(
                from_id="valid-uuid-1",
                to_id="valid-uuid-2",
                rel_type=payload
            )
```

## Key Takeaways

1. **Always parameterize**: Use `$param` syntax for all user-controlled values in Cypher
2. **Allowlist dynamic elements**: Relationship types and labels that cannot be parameterized must be validated against strict allowlists
3. **Defense in depth**: Add query validation middleware as a second layer
4. **Automated scanning**: Use your CSO agent to continuously check for regression
5. **Test with payloads**: Include injection test cases in CI/CD

These practices are essential for any platform building an [AI knowledge base](/blog/building-ai-knowledge-base) with Neo4j, especially in [multi-tenant environments](/blog/multi-tenant-agent-orchestration) where tenant isolation depends on query correctness.

## Try agent.ceo

Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).
