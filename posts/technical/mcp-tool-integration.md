---
title: "MCP (Model Context Protocol) for Tool Integration"
slug: "mcp-tool-integration"
date: 2026-05-10
category: technical
cluster: "architecture-deep-dives"
tags: [mcp, model-context-protocol, tools, integration, ai-agents, extensibility]
description: "How agent.ceo uses MCP (Model Context Protocol) to give AI agents structured tool access: server configs, permission boundaries, and custom tool development."
relatedPosts: [architecture-agent-ceo, task-management-autonomous-ai, agent-context-management]
---

# MCP (Model Context Protocol) for Tool Integration

A language model without tools is a text generator. A language model with tools is an autonomous agent. In a [Cyborgenic Organization](/blog/cyborgenic-organizations), agents need the same access to tools and systems that human team members have. The Model Context Protocol (MCP) is the bridge that transforms Claude from a conversational AI into a capable worker that can read files, execute code, search the web, manage git repositories, and coordinate with other agents. At agent.ceo, MCP is how we give each agent precisely the capabilities it needs, with precisely the permissions it should have.

## What is MCP?

MCP is a standardized protocol for connecting AI models to external tools and data sources. It defines a JSON-RPC interface between a host application (the AI agent runtime) and tool servers that expose capabilities. Each MCP server provides:

- **Tools**: Callable functions with defined inputs and outputs
- **Resources**: Data sources the model can read
- **Prompts**: Pre-defined prompt templates for common operations

The architecture looks like this:

```
+-------------------+       JSON-RPC        +-------------------+
|                   | <-------------------> |                   |
|   AI Agent        |       (stdio/SSE)     |   MCP Server      |
|   (Claude Code)   |                       |   (tool provider) |
|                   | <-------------------> |                   |
+-------------------+                       +-------------------+
        |                                           |
        | Decides which tool to call                 | Executes the tool
        | Passes structured parameters              | Returns structured results
        |                                           |
        v                                           v
  "I need to read file X"              fs.readFile("/workspace/X")
  "Search for Y"                       google.search("Y")
  "Send message to CTO"                nats.publish("genbrain.agents.cto.inbox", msg)
```

## MCP Configuration in agent.ceo

Each agent in agent.ceo has its own MCP configuration that defines which servers (and therefore which tools) it can access:

```json
{
  "mcpServers": {
    "agent-hub": {
      "command": "npx",
      "args": ["@genbrain/mcp-agent-hub"],
      "env": {
        "AGENT_ROLE": "marketing",
        "ORG_ID": "org_abc123",
        "NATS_URL": "nats://nats.genbrain.svc:4222",
        "NATS_CREDS": "/secrets/nats/agent.creds"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-filesystem",
        "/agent-data/workspace"
      ]
    },
    "git": {
      "command": "npx",
      "args": ["@genbrain/mcp-git"],
      "env": {
        "ALLOWED_REPOS": "marketing-site,blog,docs",
        "SSH_KEY_PATH": "/secrets/git/deploy-key"
      }
    },
    "web-search": {
      "command": "npx",
      "args": ["@genbrain/mcp-web"],
      "env": {
        "MAX_RESULTS": "10",
        "SAFE_SEARCH": "true"
      }
    },
    "browser": {
      "command": "npx",
      "args": ["@anthropic/mcp-browser"],
      "env": {
        "HEADLESS": "true",
        "TIMEOUT_MS": "30000"
      }
    }
  }
}
```

The key insight: different agent roles get different MCP configurations. A marketing agent gets web search and content tools. A DevOps agent gets Kubernetes and infrastructure tools. A security agent gets audit and scanning tools. This is capability-based security at the tool level.

## The agent-hub MCP Server

The most important MCP server in agent.ceo is `agent-hub`. It provides tools for inter-agent communication, task management, and organizational coordination:

```javascript
// Tools exposed by the agent-hub MCP server
const tools = [
  {
    name: "send_message",
    description: "Send a message to another agent",
    inputSchema: {
      type: "object",
      properties: {
        to: { type: "string", description: "Target agent role" },
        message: { type: "string", description: "Message content" },
        priority: { type: "string", enum: ["low", "normal", "high", "urgent"] }
      },
      required: ["to", "message"]
    }
  },
  {
    name: "delegate_task",
    description: "Delegate a task to another agent",
    inputSchema: {
      type: "object",
      properties: {
        agentRole: { type: "string" },
        title: { type: "string" },
        description: { type: "string" },
        priority: { type: "string" },
        dueAt: { type: "string", format: "date-time" }
      },
      required: ["agentRole", "title", "description"]
    }
  },
  {
    name: "get_task_status",
    description: "Check the status of a delegated task",
    inputSchema: {
      type: "object",
      properties: {
        taskId: { type: "string" }
      },
      required: ["taskId"]
    }
  },
  {
    name: "discover_agents",
    description: "List available agents and their capabilities",
    inputSchema: { type: "object", properties: {} }
  },
  {
    name: "publish_event",
    description: "Publish an event to the organization event stream",
    inputSchema: {
      type: "object",
      properties: {
        type: { type: "string" },
        data: { type: "object" }
      },
      required: ["type", "data"]
    }
  }
];
```

When an agent calls `delegate_task`, the MCP server handles the complexity: creating the task record in Firestore, publishing the assignment message to NATS, and setting up the response listener. The agent just says "delegate this to the CTO" and the tooling handles the rest.

## Permission Boundaries

MCP configuration is the primary mechanism for capability control. An agent can only use tools that appear in its MCP config. But we add additional layers:

### File System Boundaries

```json
{
  "filesystem": {
    "command": "npx",
    "args": [
      "@modelcontextprotocol/server-filesystem",
      "/agent-data/workspace/marketing"
    ]
  }
}
```

The filesystem server only exposes the specified directory tree. The marketing agent cannot access `/agent-data/workspace/devops` or any path outside its boundary.

### Git Repository Restrictions

```json
{
  "git": {
    "env": {
      "ALLOWED_REPOS": "marketing-site,blog",
      "ALLOWED_BRANCHES": "main,staging,feature/*",
      "DENY_FORCE_PUSH": "true",
      "REQUIRE_PR": "true"
    }
  }
}
```

The git MCP server enforces which repositories the agent can access, which branches it can push to, and whether force pushes are allowed.

### Network Access Control

```json
{
  "web-search": {
    "env": {
      "ALLOWED_DOMAINS": "*.google.com,*.github.com,*.npmjs.com",
      "BLOCKED_DOMAINS": "*.internal.company.com",
      "MAX_REQUESTS_PER_MINUTE": "30"
    }
  }
}
```

Network-accessing tools have domain allowlists, blocklists, and rate limits. This prevents agents from accessing internal services or overwhelming external APIs.

## Building Custom MCP Servers

agent.ceo makes it easy to build custom MCP servers for organization-specific tools. Here is a minimal example:

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server(
  { name: "custom-crm", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

// Define tools
server.setRequestHandler("tools/list", async () => ({
  tools: [
    {
      name: "lookup_customer",
      description: "Look up a customer by email or company name",
      inputSchema: {
        type: "object",
        properties: {
          query: { type: "string", description: "Email or company name" }
        },
        required: ["query"]
      }
    },
    {
      name: "create_lead",
      description: "Create a new lead in the CRM",
      inputSchema: {
        type: "object",
        properties: {
          name: { type: "string" },
          email: { type: "string" },
          company: { type: "string" },
          source: { type: "string" }
        },
        required: ["name", "email"]
      }
    }
  ]
}));

// Handle tool calls
server.setRequestHandler("tools/call", async (request) => {
  const { name, arguments: args } = request.params;
  
  switch (name) {
    case "lookup_customer":
      const customer = await crmApi.search(args.query);
      return { content: [{ type: "text", text: JSON.stringify(customer) }] };
    
    case "create_lead":
      const lead = await crmApi.createLead(args);
      return { content: [{ type: "text", text: `Lead created: ${lead.id}` }] };
    
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

Once built, add it to the agent's MCP config and the agent immediately gains CRM capabilities. No model retraining. No prompt engineering. Just structured tool access.

## MCP in the Agent Lifecycle

MCP servers start when the agent starts and stop when it stops. The lifecycle is managed by the agent runtime:

```
Agent Pod Startup
      |
      v
Load MCP config from Firestore
      |
      v
Start each MCP server process (stdio transport)
      |
      v
Initialize Claude Code CLI with MCP connections
      |
      v
Agent begins processing tasks (tools available)
      |
      v
Agent session ends
      |
      v
Gracefully terminate MCP server processes
      |
      v
Pod scales down or terminates
```

If an MCP server crashes, the runtime detects the broken pipe and restarts it. The agent sees a brief tool unavailability but recovers automatically. This resilience pattern is part of our [Self-Healing Infrastructure](/blog/self-healing-infrastructure) approach.

## Tool Usage Patterns

In production, we observe clear patterns in how agents use tools:

```
Marketing Agent - Top Tools (last 30 days):
  filesystem.write    - 45% of calls (content creation)
  git.commit          - 20% of calls (saving work)
  web-search.search   - 15% of calls (research)
  agent-hub.send      - 12% of calls (coordination)
  browser.screenshot  -  8% of calls (visual verification)

CTO Agent - Top Tools (last 30 days):
  agent-hub.delegate  - 35% of calls (task management)
  agent-hub.status    - 25% of calls (monitoring progress)
  filesystem.read     - 20% of calls (code review)
  git.diff            - 12% of calls (change review)
  agent-hub.send      -  8% of calls (communication)
```

These patterns inform how we optimize MCP server performance and which tools to prioritize for reliability. They also feed into [Cross-Agent Knowledge Sharing](/blog/cross-agent-knowledge-sharing) to help new agents learn effective tool usage.

## Security Considerations

MCP introduces a significant attack surface. An agent with unrestricted tool access could exfiltrate data, modify critical systems, or consume excessive resources. Our security layers:

1. **Config-level restriction**: Only configured tools are available
2. **Server-level validation**: Each MCP server validates inputs and enforces boundaries
3. **Network policies**: Kubernetes NetworkPolicies restrict which services MCP servers can reach
4. **Audit logging**: Every tool call is logged with full parameters and results
5. **Rate limiting**: Per-tool and per-agent rate limits prevent runaway execution

For complete security architecture, see [Credential Management in Multi-Cloud](/blog/credential-management-multi-cloud).

> agent.ceo offers both SaaS and enterprise private installation options for organizations of any size.

## Try agent.ceo

**SaaS** — Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).

**Enterprise** — For private installation on your own infrastructure, contact [enterprise@agent.ceo](mailto:enterprise@agent.ceo).

---
*agent.ceo is built by [GenBrain AI](https://genbrain.ai) — a GenAI-first autonomous agent orchestration platform. General inquiries: hello@agent.ceo | Security: security@agent.ceo*
