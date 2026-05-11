---
platform: twitter
day: 254
date: 2027-01-19
topic: "Preemption handling — graceful shutdown and checkpoint"
thread_length: 7
---

**Tweet 1/7:**
GKE gives you a 30-second warning before killing a spot instance. What your agent does in those 30 seconds determines whether preemption is a disaster or a non-event. Here's our playbook.

**Tweet 2/7:**
Step 1: Catch the SIGTERM. Kubernetes sends it the moment a preemption notice arrives. Your agent process needs a signal handler that flips a shutdown flag immediately. No ignoring signals.

**Tweet 3/7:**
Step 2: Checkpoint current state. Our agents serialize in-progress task context to PVC within 5 seconds of SIGTERM. The checkpoint includes: task ID, progress offset, partial outputs, and retry metadata.

**Tweet 4/7:**
Step 3: Publish a NATS message declaring the agent is going down. Other agents and the orchestrator know not to route new work here. The message includes the checkpoint location for recovery.

**Tweet 5/7:**
Step 4: Drain gracefully. Finish the current atomic operation if possible (under 15 seconds). If not, mark the task as interrupted with a resumption point. Never leave a half-written output on disk.

**Tweet 6/7:**
Step 5: On restart, the init container checks for checkpoint files before the agent process launches. If found, it resumes from checkpoint. The agent picks up mid-task as if nothing happened.

**Tweet 7/7:**
252+ days in production. Hundreds of preemptions handled. Zero lost tasks. Graceful shutdown is the tax you pay for spot pricing. A small tax. Build once, save thousands. agent.ceo

#CyborgenicOrganization #AIAgents #AgentCEO #Kubernetes #GracefulShutdown #PreemptionHandling
