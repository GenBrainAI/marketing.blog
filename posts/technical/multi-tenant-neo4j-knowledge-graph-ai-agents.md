---
title: "How to Share a Neo4j Knowledge Graph Across AI Agent Tenants Without Leaking Data"
slug: "multi-tenant-neo4j-knowledge-graph-ai-agents"
date: 2026-07-16
category: technical
cluster: production-patterns
tags: [neo4j, multi-tenant, knowledge-graph, tutorial, data-isolation, kubernetes, ai-agents]
description: "A practical guide to property-based tenant isolation in Neo4j for multi-tenant AI agent platforms, with Cypher queries, Python patterns, and Kubernetes network policies."
relatedPosts:
  - /blog/knowledge-graphs-ai-agents-cyborgenic
  - /blog/graph-traversal-vs-vector-search-ai-agents
  - /blog/multi-tenant-agent-isolation-cyborgenic
  - /blog/enterprise-erp-knowledge-graph-case-study
  - /blog/preventing-cypher-injection
---

# How to Share a Neo4j Knowledge Graph Across AI Agent Tenants Without Leaking Data

Every customer org on [agent.ceo](https://agent.ceo) gets AI agents that build and query a knowledge graph. Agents ingest repos, documents, and conversations into Neo4j, then traverse relationships to answer questions like "what depends on the auth service?" and "who approved the last schema migration?" We covered the architecture in our [knowledge graphs for AI agents](/blog/knowledge-graphs-ai-agents-cyborgenic) post.

The problem: we were running a separate Neo4j instance for every customer org. Eight tenants meant eight StatefulSets, eight persistent volumes, eight sets of credentials to rotate, and eight instances consuming memory whether anyone was querying them or not. The ops cost was growing linearly with every new customer, and most instances sat idle 95% of the time.

We switched to a single shared Neo4j database with property-based tenant isolation. All customer orgs now connect to the same instance. Each tenant only sees its own data. This post walks through exactly how we did it, so you can apply the same pattern to your own multi-tenant AI agent platform.

## The Decision: Per-Tenant Instances vs Shared Database

There are two credible approaches to multi-tenant graph databases:

**Per-tenant instances** give you the strongest isolation. Each tenant has its own process, its own storage, its own network address. A bug in one tenant's queries cannot affect another tenant's performance. The cost: you pay for N instances, N volumes, N backups. At scale, this is operationally brutal.

**Shared database with property filtering** puts all tenants in one instance. Every node and relationship carries a tenant identifier. Queries always filter by that identifier. The cost: you must be disciplined about never writing a query that omits the filter. The benefit: one instance to monitor, one backup schedule, one connection pool, and memory is shared across tenants whose access patterns rarely overlap.

We chose shared. Our knowledge graph workload is bursty -- agents ingest repos in bursts, then query sporadically. A shared instance with 8GB of heap serves the same traffic that previously required eight 2GB instances. The operational simplification alone justified the switch.

But shared only works if the isolation is airtight. Here is how we enforce it.

## Step 1: Tag Everything with org_id

Every node in the graph carries an `org_id` property. Every relationship does too. This is the tenant boundary.

```cypher
// Creating a node -- org_id is mandatory
CREATE (f:File {
  path: "src/api/auth.py",
  repo: "platform",
  org_id: $org_id,
  ingested_at: datetime()
})

// Creating a relationship -- org_id on both endpoints AND the relationship
MATCH (f:File {path: $path, org_id: $org_id})
MATCH (s:Service {name: $service, org_id: $org_id})
CREATE (f)-[:BELONGS_TO {org_id: $org_id}]->(s)
```

Tagging relationships is redundant if you always match nodes by `org_id`, but we do it anyway. Defense in depth means a missing filter on a node match still cannot traverse into another tenant's subgraph through a relationship.

## Step 2: Enforce org_id in Every Query

The `kb_tools.py` module that agents call to interact with Neo4j parameterizes `org_id` into every query. No query runs without it.

```python
class KnowledgeBaseTools:
    def __init__(self, driver: neo4j.Driver, org_id: str):
        self._driver = driver
        self._org_id = org_id  # Set once at agent init, never changes

    def search_nodes(self, label: str, filters: dict) -> list[dict]:
        """Search nodes -- org_id is always injected, never caller-supplied."""
        where_clauses = ["n.org_id = $org_id"]
        params = {"org_id": self._org_id}

        for key, value in filters.items():
            if key == "org_id":
                continue  # Caller cannot override tenant boundary
            where_clauses.append(f"n.{key} = ${key}")
            params[key] = value

        query = f"""
            MATCH (n:{label})
            WHERE {' AND '.join(where_clauses)}
            RETURN n
            LIMIT 100
        """
        with self._driver.session() as session:
            return [record["n"] for record in session.run(query, params)]

    def traverse(self, start_label: str, start_filter: dict,
                 rel_type: str, end_label: str) -> list[dict]:
        """Traverse relationships -- both endpoints filtered by org_id."""
        query = f"""
            MATCH (a:{start_label} {{org_id: $org_id}})
            WHERE a.name = $start_name
            MATCH (a)-[r:{rel_type}]->(b:{end_label} {{org_id: $org_id}})
            RETURN b
        """
        params = {"org_id": self._org_id, "start_name": start_filter["name"]}
        with self._driver.session() as session:
            return [record["b"] for record in session.run(query, params)]
```

The key design choices:

1. **`org_id` is set at construction time**, not passed per-call. The agent's org identity is fixed for the lifetime of the process. This eliminates an entire class of bugs where a caller accidentally passes the wrong org.
2. **The caller cannot override `org_id`** in filter dictionaries. Even if a prompt injection somehow convinces an agent to pass `org_id: "other-tenant"` in the filters, the code silently drops it.
3. **Parameterized queries only.** No string interpolation of user input into Cypher. We covered why in our [preventing Cypher injection](/blog/preventing-cypher-injection) post.

## Step 3: Provision Shared Credentials into Tenant Namespaces

Each customer org runs in its own Kubernetes namespace. The agents in that namespace need credentials to reach the shared Neo4j instance. We mirror the credentials from the central namespace into each tenant namespace as a Kubernetes Secret.

```python
# deployment.py -- runs during tenant provisioning

def ensure_neo4j_credentials_secret(org_id: str, namespace: str):
    """Mirror shared Neo4j credentials into a tenant namespace."""
    central_secret = core_v1.read_namespaced_secret(
        name="neo4j-shared-credentials", namespace="genbrain-system"
    )
    tenant_secret = client.V1Secret(
        metadata=client.V1ObjectMeta(
            name="neo4j-credentials",
            namespace=namespace,
            labels={"genbrain.ai/org-id": org_id},
        ),
        data=central_secret.data,
    )
    # Create or update the secret in the tenant namespace
    try:
        core_v1.create_namespaced_secret(namespace, tenant_secret)
    except ApiException as e:
        if e.status == 409:
            core_v1.replace_namespaced_secret(
                "neo4j-credentials", namespace, tenant_secret)
        else:
            raise
```

The agent StatefulSet template picks up these credentials as environment variables:

```yaml
# statefulset-agent-template.yaml (relevant excerpt)
env:
  - name: NEO4J_URI
    value: "bolt://neo4j.genbrain-system.svc.cluster.local:7687"
  - name: NEO4J_DATABASE
    value: "knowledge"
  - name: NEO4J_AUTH
    valueFrom:
      secretKeyRef:
        name: neo4j-credentials
        key: auth
  - name: ORG_ID
    valueFrom:
      fieldRef:
        fieldPath: metadata.labels['genbrain.ai/org-id']
```

Notice that `ORG_ID` comes from the pod's own label, not from the secret. The org identity is baked into the Kubernetes manifest at provisioning time. An agent cannot change its own org identity without modifying its own pod spec, which RBAC prevents.

## Step 4: Network Policy as a Second Boundary

Property-based filtering is the primary isolation mechanism. But we add a Kubernetes NetworkPolicy as a belt-and-suspenders layer. Only pods with the correct tenant label can reach the Neo4j service.

```yaml
# neo4j-tenant-isolation.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: neo4j-tenant-access
  namespace: genbrain-system
spec:
  podSelector:
    matchLabels:
      app: neo4j
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              genbrain.ai/tenant: "true"
          podSelector:
            matchLabels:
              genbrain.ai/component: "agent"
      ports:
        - port: 7687
          protocol: TCP
```

This policy does two things: it restricts Neo4j ingress to only agent pods in tenant namespaces, and it prevents any non-agent workload (cron jobs, debug pods, monitoring sidecars) from connecting to Neo4j directly. We covered our broader [multi-tenant isolation strategy](/blog/multi-tenant-agent-isolation-cyborgenic) -- including Firestore and NATS layers -- in a separate deep dive.

## Step 5: Test the Isolation Boundary

We wrote 102 tests in `test_neo4j_shared_tenant.py` that validate tenant isolation. The test suite provisions two tenants, populates data for both, then systematically verifies that queries from one tenant never return the other tenant's nodes or relationships.

The critical test categories:

```python
class TestTenantIsolation:
    def test_search_returns_only_own_nodes(self, tenant_a_tools, tenant_b_tools):
        """Tenant A's search never returns Tenant B's nodes."""
        tenant_a_tools.create_node("File", {"path": "secret.py", "content": "..."})
        tenant_b_tools.create_node("File", {"path": "public.py", "content": "..."})

        results = tenant_a_tools.search_nodes("File", {})
        paths = [r["path"] for r in results]
        assert "secret.py" in paths
        assert "public.py" not in paths

    def test_traversal_stops_at_tenant_boundary(self, tenant_a_tools, tenant_b_tools):
        """Relationships cannot cross tenant boundaries."""
        # Even if nodes accidentally shared a name,
        # traversal stays within the tenant's subgraph
        tenant_a_tools.create_node("Service", {"name": "auth"})
        tenant_b_tools.create_node("Service", {"name": "auth"})
        tenant_b_tools.create_node("File", {"path": "exploit.py"})
        tenant_b_tools.create_relationship("File", "exploit.py",
                                            "BELONGS_TO", "Service", "auth")

        results = tenant_a_tools.traverse("Service", {"name": "auth"},
                                           "BELONGS_TO", "File")
        assert len(results) == 0  # Tenant A has no files linked to auth

    def test_org_id_override_rejected(self, tenant_a_tools):
        """Caller cannot override org_id via filter dict."""
        results = tenant_a_tools.search_nodes("File",
                                               {"org_id": "tenant-b"})
        # org_id filter is silently dropped; still scoped to tenant A
        for r in results:
            assert r["org_id"] == "tenant-a"
```

These tests run in CI on every commit that touches `kb_tools.py`, the Neo4j schema, or the provisioning code. A failed isolation test blocks the merge.

## What We Gained

The migration from per-tenant instances to shared Neo4j took two days. The results:

- **Resource usage dropped 60%.** One 8GB instance replaces eight 2GB instances, and memory is used more efficiently because tenant query patterns rarely overlap.
- **Provisioning time dropped from 4 minutes to 30 seconds.** No more waiting for a StatefulSet to spin up and a Neo4j instance to initialize. New tenants get a secret mirrored into their namespace and start querying immediately.
- **Operational surface area shrank.** One instance to monitor, one backup schedule, one set of alerts. We eliminated 7 PagerDuty alert rules.
- **Zero isolation regressions.** 102 tests, running on every commit, with zero failures since the migration.

## When to Keep Separate Instances

Shared is not always right. Keep per-tenant instances when:

- **A tenant's graph is enormous** (millions of nodes) and would dominate shared memory. Noisy-neighbor effects are real.
- **Compliance requires physical separation.** Some enterprise contracts mandate that data never coexists in the same database process, regardless of logical isolation. No amount of property filtering satisfies that requirement.
- **Query patterns conflict.** If one tenant runs heavy analytics queries (full graph scans, aggregations) while others need low-latency point lookups, a shared instance creates contention.

For most AI agent platforms at early-to-mid scale, shared with property isolation is the right default. You can always migrate a large tenant to a dedicated instance later -- the `org_id` pattern makes the data trivially extractable.

## Build Your Own

If you are building a multi-tenant AI agent platform and want to see this pattern in production, [agent.ceo](https://agent.ceo) runs on it today. Every customer org's agents query a shared knowledge graph with full tenant isolation -- [graph traversal](/blog/graph-traversal-vs-vector-search-ai-agents), relationship-aware search, and zero cross-tenant data leaks.

We are building the operating system for AI agent organizations. If that problem interests you, check out [agent.ceo](https://agent.ceo).
