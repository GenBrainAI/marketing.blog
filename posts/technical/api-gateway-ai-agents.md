---
title: "API Gateway Design for AI Agent Platforms"
slug: "api-gateway-ai-agents"
date: 2026-05-10
category: technical
cluster: "platform-engineering"
tags: [api-gateway, rest-api, websocket, mcp, real-time, authentication, rate-limiting]
description: "Design an API gateway for AI agent platforms with REST endpoints, WebSocket real-time updates, MCP protocol support, and tenant-aware routing."
relatedPosts: [saas-platform-ai-agents, multi-tenant-agent-orchestration, real-time-agent-monitoring]
---

# API Gateway Design for AI Agent Platforms

An AI agent platform's API gateway serves three distinct communication patterns simultaneously: traditional REST for management operations, WebSocket for real-time agent status streaming, and the Model Context Protocol (MCP) for tool integration. Designing a gateway that handles all three while enforcing multi-tenant authentication, rate limiting, and routing is a non-trivial engineering challenge. This post details the gateway architecture powering agent.ceo.

## Gateway Architecture Overview

Our gateway sits at the platform edge, terminating TLS and routing traffic to internal services based on protocol and tenant context:

```
Client Request
    │
    ▼
┌─────────────────────────┐
│   Cloud CDN / LB        │  ← TLS termination, DDoS protection
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│   API Gateway Service   │  ← Auth, rate limiting, routing
│                         │
│  ┌─────┐ ┌────┐ ┌───┐  │
│  │REST │ │ WS │ │MCP│  │
│  └──┬──┘ └──┬─┘ └─┬─┘  │
└─────┼────────┼─────┼────┘
      │        │     │
      ▼        ▼     ▼
  Services   NATS   Agent Pods
```

The gateway runs as a GKE deployment with horizontal pod autoscaling:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: platform-services
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
        - name: gateway
          image: gcr.io/agent-ceo/api-gateway:latest
          ports:
            - containerPort: 8080
              name: http
            - containerPort: 8081
              name: ws
            - containerPort: 8082
              name: mcp
          resources:
            requests:
              cpu: "1000m"
              memory: "2Gi"
            limits:
              cpu: "2000m"
              memory: "4Gi"
          env:
            - name: FIREBASE_PROJECT_ID
              value: "agent-ceo-prod"
            - name: NATS_URL
              valueFrom:
                secretKeyRef:
                  name: platform-nats
                  key: url
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: platform-redis
                  key: url
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
  namespace: platform-services
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Pods
      pods:
        metric:
          name: active_websocket_connections
        target:
          type: AverageValue
          averageValue: "500"
```

## Authentication Middleware

All requests pass through Firebase Auth verification. The middleware extracts the tenant context and attaches it to the request for downstream processing:

```typescript
import { getAuth } from 'firebase-admin/auth';
import { getFirestore } from 'firebase-admin/firestore';
import { Redis } from 'ioredis';

const auth = getAuth();
const db = getFirestore();
const redis = new Redis(process.env.REDIS_URL);

interface AuthContext {
  userId: string;
  orgId: string;
  orgPlan: string;
  permissions: string[];
}

async function authMiddleware(req: Request, res: Response, next: Function) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (!token) {
    return res.status(401).json({ error: 'Missing authorization token' });
  }

  try {
    // Verify Firebase token
    const decoded = await auth.verifyIdToken(token);

    // Check cached org membership
    const cacheKey = `auth:${decoded.uid}:org`;
    let orgContext = await redis.get(cacheKey);

    if (!orgContext) {
      // Fetch from Firestore
      const membership = await db
        .collectionGroup('members')
        .where('userId', '==', decoded.uid)
        .limit(1)
        .get();

      if (membership.empty) {
        return res.status(403).json({ error: 'No organization membership' });
      }

      const memberDoc = membership.docs[0];
      const orgId = memberDoc.ref.parent.parent.id;
      const org = await db.doc(`organizations/${orgId}`).get();

      orgContext = JSON.stringify({
        userId: decoded.uid,
        orgId,
        orgPlan: org.data().plan,
        permissions: memberDoc.data().permissions
      });

      // Cache for 5 minutes
      await redis.setex(cacheKey, 300, orgContext);
    }

    req.authContext = JSON.parse(orgContext) as AuthContext;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}
```

## REST API Endpoints

The REST API provides CRUD operations for agent management. Endpoints are tenant-scoped and permission-checked:

```typescript
import express from 'express';

const router = express.Router();

// List agents for the authenticated organization
router.get('/v1/agents', authMiddleware, async (req, res) => {
  const { orgId } = req.authContext;

  const agents = await db
    .collection(`organizations/${orgId}/agents`)
    .orderBy('createdAt', 'desc')
    .limit(50)
    .get();

  res.json({
    agents: agents.docs.map(doc => ({
      id: doc.id,
      ...doc.data(),
      createdAt: doc.data().createdAt?.toDate().toISOString()
    }))
  });
});

// Create a new agent
router.post('/v1/agents', authMiddleware, requirePermission('agents:write'), async (req, res) => {
  const { orgId } = req.authContext;
  const { name, role, config } = req.body;

  // Validate against org quota
  const activeCount = await countActiveAgents(orgId);
  const org = await db.doc(`organizations/${orgId}`).get();

  if (activeCount >= org.data().agentLimit) {
    return res.status(429).json({
      error: 'Agent limit reached',
      limit: org.data().agentLimit,
      current: activeCount
    });
  }

  const agentId = await orchestrator.provisionAgent(orgId, { name, role, config });

  res.status(201).json({ agentId, status: 'provisioning' });
});

// Send a task to an agent
router.post('/v1/agents/:agentId/tasks', authMiddleware, requirePermission('tasks:write'), async (req, res) => {
  const { orgId } = req.authContext;
  const { agentId } = req.params;
  const { description, priority, deadline } = req.body;

  // Verify agent belongs to this org
  const agent = await db.doc(`organizations/${orgId}/agents/${agentId}`).get();
  if (!agent.exists) {
    return res.status(404).json({ error: 'Agent not found' });
  }

  const taskId = await taskScheduler.createTask({
    orgId,
    agentId,
    description,
    priority: priority || 'normal',
    deadline: deadline ? new Date(deadline) : undefined
  });

  res.status(201).json({ taskId, status: 'queued' });
});

// Pause an agent (scale to zero)
router.post('/v1/agents/:agentId/pause', authMiddleware, requirePermission('agents:write'), async (req, res) => {
  const { orgId } = req.authContext;
  const { agentId } = req.params;

  await orchestrator.pauseAgent(orgId, agentId);
  res.json({ status: 'pausing' });
});
```

## WebSocket Real-Time Streaming

The WebSocket endpoint streams agent status updates, task progress, and log output in real time. Clients subscribe to specific agents or receive organization-wide events:

```typescript
import { WebSocketServer } from 'ws';
import { connect, StringCodec } from 'nats';

const wss = new WebSocketServer({ port: 8081 });
const nc = await connect({ servers: process.env.NATS_URL });
const sc = StringCodec();

wss.on('connection', async (ws, req) => {
  // Authenticate WebSocket connection
  const token = new URL(req.url, 'http://localhost').searchParams.get('token');
  const authContext = await verifyToken(token);

  if (!authContext) {
    ws.close(4001, 'Unauthorized');
    return;
  }

  const { orgId } = authContext;
  const subscriptions: any[] = [];

  ws.on('message', async (data) => {
    const msg = JSON.parse(data.toString());

    switch (msg.type) {
      case 'subscribe_agent': {
        // Subscribe to specific agent's events
        const sub = nc.subscribe(`org.${orgId}.agents.${msg.agentId}.>`);
        subscriptions.push(sub);

        (async () => {
          for await (const m of sub) {
            ws.send(JSON.stringify({
              type: 'agent_event',
              agentId: msg.agentId,
              subject: m.subject,
              data: JSON.parse(sc.decode(m.data))
            }));
          }
        })();
        break;
      }

      case 'subscribe_org': {
        // Subscribe to all org events
        const sub = nc.subscribe(`org.${orgId}.>`);
        subscriptions.push(sub);

        (async () => {
          for await (const m of sub) {
            ws.send(JSON.stringify({
              type: 'org_event',
              subject: m.subject,
              data: JSON.parse(sc.decode(m.data))
            }));
          }
        })();
        break;
      }
    }
  });

  ws.on('close', () => {
    subscriptions.forEach(sub => sub.unsubscribe());
  });
});
```

## MCP Protocol Support

The Model Context Protocol allows external AI models to use agent.ceo agents as tools. Our gateway translates MCP tool calls into agent task assignments:

```typescript
// MCP server endpoint for tool integration
class AgentMCPServer {
  getTools(orgId: string): MCPTool[] {
    return [
      {
        name: 'delegate_to_agent',
        description: 'Delegate a task to a specific AI agent in your organization',
        inputSchema: {
          type: 'object',
          properties: {
            agentName: { type: 'string', description: 'Name of the target agent' },
            task: { type: 'string', description: 'Task description' },
            waitForResult: { type: 'boolean', default: false }
          },
          required: ['agentName', 'task']
        }
      },
      {
        name: 'query_agent_status',
        description: 'Get the current status of an agent',
        inputSchema: {
          type: 'object',
          properties: {
            agentName: { type: 'string' }
          },
          required: ['agentName']
        }
      }
    ];
  }

  async executeTool(orgId: string, toolName: string, args: any): Promise<MCPResult> {
    switch (toolName) {
      case 'delegate_to_agent':
        const taskId = await taskScheduler.createTask({
          orgId,
          agentName: args.agentName,
          description: args.task,
          priority: 'normal'
        });

        if (args.waitForResult) {
          const result = await waitForTaskCompletion(taskId, 300000); // 5min timeout
          return { content: [{ type: 'text', text: JSON.stringify(result) }] };
        }

        return { content: [{ type: 'text', text: `Task ${taskId} queued` }] };

      case 'query_agent_status':
        const agent = await findAgentByName(orgId, args.agentName);
        return { content: [{ type: 'text', text: JSON.stringify(agent) }] };
    }
  }
}
```

## Rate Limiting

Rate limits are applied per-organization and per-plan using Redis-backed sliding windows:

```typescript
import { Redis } from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

const RATE_LIMITS = {
  payg:       { requests: 100,  window: 60 },  // 100 req/min
  standard:   { requests: 500,  window: 60 },  // 500 req/min
  volume:     { requests: 2000, window: 60 },  // 2000 req/min
  enterprise: { requests: 10000, window: 60 }  // 10000 req/min
};

async function rateLimitMiddleware(req: Request, res: Response, next: Function) {
  const { orgId, orgPlan } = req.authContext;
  const limit = RATE_LIMITS[orgPlan];
  const key = `ratelimit:${orgId}:${Math.floor(Date.now() / (limit.window * 1000))}`;

  const current = await redis.incr(key);
  if (current === 1) {
    await redis.expire(key, limit.window);
  }

  res.setHeader('X-RateLimit-Limit', limit.requests);
  res.setHeader('X-RateLimit-Remaining', Math.max(0, limit.requests - current));

  if (current > limit.requests) {
    return res.status(429).json({
      error: 'Rate limit exceeded',
      retryAfter: limit.window
    });
  }

  next();
}
```

The gateway design ensures that all three communication patterns — REST, WebSocket, and MCP — flow through consistent authentication and authorization. This unified approach simplifies security auditing and [credential management](/blog/credential-management-multi-cloud), while providing the real-time capabilities agents need.

For teams getting started with the platform, our [getting started guide](/blog/getting-started-agent-ceo) walks through API key setup and making your first agent management calls. The [architecture overview](/blog/architecture-agent-ceo) provides additional context on how the gateway fits into the broader system.


**Continue reading:** Explore [the architecture behind agent.ceo](/blog/architecture-agent-ceo), learn about [scaling AI agents to 100 concurrent workers](/blog/scaling-ai-agents), or get started with our [5-minute quickstart guide](/blog/getting-started-agent-ceo).

## Try agent.ceo

Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).
