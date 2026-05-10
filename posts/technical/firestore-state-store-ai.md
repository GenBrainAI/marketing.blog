---
title: "Firestore as State Store for AI Agents"
slug: "firestore-state-store-ai"
date: 2026-05-10
category: technical
cluster: "architecture-deep-dives"
tags: [firestore, state-management, real-time, nosql, ai-agents, persistence]
description: "How agent.ceo uses Firestore as the state store for AI agents: schema design, real-time listeners, multi-tenant isolation, and operational patterns."
relatedPosts: [architecture-agent-ceo, event-driven-nats-ai, task-management-autonomous-ai]
---

# Firestore as State Store for AI Agents

Every autonomous AI agent needs persistent state. Configuration that survives restarts. Task records that track progress. Session metadata that enables resumption. User preferences that personalize behavior. At agent.ceo, Firestore serves as the unified state store for all of this. This post explains our schema design, real-time update patterns, and the operational benefits of using Firestore for AI agent state management.

## Why Firestore

AI agent state has specific characteristics that make Firestore an excellent fit:

- **Hierarchical data**: Agent configs nest tools, permissions, and scheduling. Firestore's document-subcollection model maps naturally.
- **Real-time listeners**: Clients need instant updates when agent status changes. Firestore's snapshot listeners eliminate polling.
- **Serverless scaling**: Zero capacity planning. Firestore scales from 1 read/sec to 1 million read/sec without configuration changes.
- **Multi-tenant isolation**: Security rules enforce organization boundaries at the database level.
- **Offline support**: The client SDK handles network interruptions gracefully, important for agents that may have intermittent connectivity.

Compared to alternatives like PostgreSQL (rigid schema, no native real-time), Redis (volatile, limited query), or MongoDB (operational overhead), Firestore offers the best combination of flexibility, real-time capability, and managed operations for our use case.

## Collection Schema

Our Firestore structure organizes data by organization, then by entity type:

```
firestore/
├── organizations/
│   └── {orgId}/
│       ├── agents/
│       │   └── {agentId}/
│       │       ├── config (document)
│       │       ├── sessions/
│       │       │   └── {sessionId} (document)
│       │       └── memory/
│       │           └── {memoryKey} (document)
│       ├── tasks/
│       │   └── {taskId} (document)
│       ├── meetings/
│       │   └── {meetingId}/
│       │       └── messages/
│       │           └── {messageId} (document)
│       └── billing/
│           └── usage (document)
├── users/
│   └── {userId}/
│       ├── profile (document)
│       └── preferences (document)
└── system/
    ├── health (document)
    └── feature-flags (document)
```

This hierarchy provides natural security boundaries. Firestore security rules can restrict access at the organization level, ensuring agents from one org never read another org's data.

## Agent Configuration Document

The agent configuration document is the source of truth for how an agent behaves:

```javascript
// organizations/{orgId}/agents/{agentId}/config
{
  // Identity
  "role": "marketing",
  "displayName": "Marketing Agent",
  "model": "claude-opus-4-6",
  "version": "2026-05-10",
  
  // Capabilities
  "mcpServers": {
    "agent-hub": { "enabled": true },
    "filesystem": { "enabled": true, "rootPath": "/workspace" },
    "git": { "enabled": true, "repos": ["marketing-site", "blog"] },
    "web-search": { "enabled": true, "maxResults": 10 }
  },
  
  // Scheduling
  "scheduling": {
    "scaleToZero": true,
    "idleTimeoutMinutes": 15,
    "maxConcurrentTasks": 3,
    "priorityClass": "standard",
    "allowedHours": { "start": 6, "end": 22, "timezone": "UTC" }
  },
  
  // Memory and Context
  "context": {
    "maxTokens": 200000,
    "compactionThreshold": 0.8,
    "memoryEnabled": true,
    "persistPatterns": true
  },
  
  // Status
  "status": "active",
  "lastActiveAt": "2026-05-10T14:30:00Z",
  "currentTaskId": "task_xyz789",
  "podName": "agent-marketing-7b4f9c-abc12",
  
  // Metadata
  "createdAt": "2026-03-15T09:00:00Z",
  "updatedAt": "2026-05-10T14:30:00Z",
  "createdBy": "user_moshe"
}
```

When this document updates, real-time listeners propagate changes to the running agent pod. The agent can adjust its behavior without restarting.

## Task Record Schema

Tasks are the fundamental unit of work in agent.ceo. Each task document tracks the full lifecycle:

```javascript
// organizations/{orgId}/tasks/{taskId}
{
  "id": "task_xyz789",
  "title": "Write blog post on NATS architecture",
  "description": "Create a technical deep-dive on our NATS JetStream usage...",
  
  // Lifecycle
  "status": "in_progress",  // created|assigned|accepted|in_progress|completed|blocked
  "priority": "high",       // low|medium|high|urgent
  "phase": "execution",     // planning|execution|review|done
  
  // Assignment
  "assignedTo": "marketing",
  "delegatedBy": "ceo",
  "acceptedAt": "2026-05-10T14:00:00Z",
  
  // Hierarchy
  "parentTaskId": "task_parent123",
  "subtaskIds": ["task_sub001", "task_sub002"],
  "blockers": [],
  
  // Progress
  "progress": [
    {
      "timestamp": "2026-05-10T14:05:00Z",
      "message": "Research phase complete. Outlining post structure.",
      "percentComplete": 30
    },
    {
      "timestamp": "2026-05-10T14:20:00Z",
      "message": "First draft written. Adding code examples.",
      "percentComplete": 70
    }
  ],
  
  // Output
  "output": null,  // Populated on completion
  "artifacts": [
    { "type": "file", "path": "/workspace/blog/nats-post.md" }
  ],
  
  // Timing
  "createdAt": "2026-05-10T13:55:00Z",
  "updatedAt": "2026-05-10T14:20:00Z",
  "dueAt": "2026-05-10T18:00:00Z",
  "completedAt": null,
  
  // SLA
  "sla": {
    "targetMinutes": 120,
    "warningAt": 90,
    "elapsedMinutes": 25
  }
}
```

This schema supports the full task management system described in [Task Management Systems for Autonomous AI](/blog/task-management-autonomous-ai).

## Real-Time Listeners

Firestore's real-time listeners are central to how agent.ceo delivers instant updates. When an agent completes a task, the dashboard updates immediately without polling:

```javascript
// Client-side: Listen for task status changes
const unsubscribe = db
  .collection('organizations')
  .doc(orgId)
  .collection('tasks')
  .where('status', 'in', ['in_progress', 'assigned'])
  .orderBy('updatedAt', 'desc')
  .limit(50)
  .onSnapshot((snapshot) => {
    snapshot.docChanges().forEach((change) => {
      if (change.type === 'modified') {
        updateTaskCard(change.doc.id, change.doc.data());
      }
      if (change.type === 'added') {
        renderNewTask(change.doc.data());
      }
    });
  });

// Server-side: Agent updates task progress
async function reportProgress(taskId, message, percent) {
  const taskRef = db
    .collection('organizations')
    .doc(orgId)
    .collection('tasks')
    .doc(taskId);
    
  await taskRef.update({
    'status': 'in_progress',
    'progress': admin.firestore.FieldValue.arrayUnion({
      timestamp: new Date().toISOString(),
      message: message,
      percentComplete: percent
    }),
    'updatedAt': admin.firestore.FieldValue.serverTimestamp()
  });
  // All listeners receive this update within ~100ms
}
```

This pattern eliminates the need for WebSocket infrastructure or long-polling endpoints. Firestore handles the connection management, reconnection, and delta synchronization automatically.

## Security Rules for Multi-Tenant Isolation

Firestore security rules enforce that agents and users can only access their own organization's data:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Organization-scoped data
    match /organizations/{orgId}/{document=**} {
      allow read, write: if request.auth != null 
        && request.auth.token.orgId == orgId;
    }
    
    // User profile access
    match /users/{userId} {
      allow read, write: if request.auth != null 
        && request.auth.uid == userId;
    }
    
    // System documents (read-only for authenticated users)
    match /system/{document=**} {
      allow read: if request.auth != null;
      allow write: if false; // Only admin SDK
    }
  }
}
```

Agent pods use service accounts with the Admin SDK, bypassing security rules but scoped by application logic. User-facing clients use the client SDK with full rule enforcement.

## Operational Patterns

### Atomic Task State Transitions

Task status transitions must be atomic to prevent race conditions when multiple agents interact:

```javascript
// Use transactions for safe state transitions
async function transitionTask(taskId, fromStatus, toStatus) {
  return db.runTransaction(async (transaction) => {
    const taskRef = db.collection('organizations').doc(orgId)
      .collection('tasks').doc(taskId);
    const task = await transaction.get(taskRef);
    
    if (task.data().status !== fromStatus) {
      throw new Error(`Task not in expected state: ${task.data().status}`);
    }
    
    transaction.update(taskRef, {
      status: toStatus,
      updatedAt: admin.firestore.FieldValue.serverTimestamp()
    });
  });
}
```

### Batch Writes for Session Initialization

When an agent starts a new session, multiple documents need creation atomically:

```javascript
async function initializeSession(agentId, sessionId) {
  const batch = db.batch();
  
  // Create session document
  batch.set(
    db.doc(`organizations/${orgId}/agents/${agentId}/sessions/${sessionId}`),
    { startedAt: new Date(), status: 'active', tokenCount: 0 }
  );
  
  // Update agent status
  batch.update(
    db.doc(`organizations/${orgId}/agents/${agentId}/config`),
    { status: 'active', currentSessionId: sessionId, lastActiveAt: new Date() }
  );
  
  // Log event
  batch.set(
    db.doc(`organizations/${orgId}/events/${sessionId}_start`),
    { type: 'session.started', agentId, sessionId, timestamp: new Date() }
  );
  
  await batch.commit();
}
```

### TTL for Ephemeral Data

Some data is inherently temporary. Firestore's TTL policies automatically clean up expired documents:

```javascript
// Session heartbeats expire after 1 hour
await db.doc(`organizations/${orgId}/agents/${agentId}/heartbeats/${Date.now()}`).set({
  timestamp: new Date(),
  tokenUsage: 45000,
  taskId: currentTaskId,
  expireAt: new Date(Date.now() + 3600000) // TTL policy deletes after this
});
```

## Cost Considerations

Firestore pricing is operation-based. For AI agents, the patterns that matter:

- **Reads**: Real-time listeners are efficient (charged per document, not per update)
- **Writes**: Task progress updates are the primary write driver. Batching progress reduces cost.
- **Storage**: Memory documents grow over time. Compaction controls size.

A typical agent performing 50 tasks/day generates approximately 500 reads and 200 writes, costing under $0.01/day in Firestore operations. At scale with 100 agents, this remains under $1/day. For cost strategies, see [Cost Optimization for AI Agents](/blog/cost-optimization-ai-agents).

## Integration Points

Firestore connects to the broader agent.ceo architecture:

- **NATS bridge**: Firestore writes trigger Cloud Functions that publish NATS events
- **GKE scaling**: Firestore task queue depth feeds into HPA metrics
- **Dashboard**: Real-time listeners power the live monitoring UI described in [Real-Time Agent Monitoring](/blog/real-time-agent-monitoring)
- **Billing**: Usage counters in Firestore drive Stripe metered billing

For the complete architecture view, see [The Architecture of agent.ceo: A Technical Deep-Dive](/blog/architecture-agent-ceo).

## Try agent.ceo

Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).
