---
platform: twitter
scheduled_date: 2026-08-22
thread_length: 7
day: 104
status: ready
---

**Tweet 1/7:**
The PVC problem nobody warns you about when deploying AI agents on Kubernetes: RollingUpdate with persistent volumes will deadlock your cluster. We learned this at 2am on a Tuesday. Thread.

**Tweet 2/7:**
Default Kubernetes deployment strategy: RollingUpdate. Spins up the new pod, waits for it to be healthy, then kills the old one. Works great for stateless apps. Catastrophic for agents with ReadWriteOnce PVCs.

**Tweet 3/7:**
The deadlock: new pod starts -> tries to mount the PVC -> PVC is locked by the old pod -> new pod hangs in Pending -> old pod never terminates because RollingUpdate waits for the new pod first. Both pods stuck forever.

**Tweet 4/7:**
The fix is one line in your deployment spec:
```yaml
strategy:
  type: Recreate
```
Kills the old pod first, releases the PVC, then starts the new one. Downtime: 8-15 seconds. Deadlock risk: zero. We deploy agent updates 4x daily with this strategy.

**Tweet 5/7:**
Why doesn't everyone know this? Because most Kubernetes tutorials assume stateless workloads. AI agents are inherently stateful — conversation history, task checkpoints, model caches. ReadWriteOnce PVCs are the norm, not the exception.

**Tweet 6/7:**
Other PVC traps we hit: storage class defaulting to gp2 (slow, expensive) instead of gp3. Volume expansion requiring pod restart. Orphaned PVCs from deleted deployments silently eating $47/month in EBS costs. Check your cluster.

**Tweet 7/7:**
Kubernetes is the right platform for AI agents. But the defaults assume web servers, not stateful autonomous workers. 104 days of production lessons. Deploy your agents right at agent.ceo. Enterprise: moshe@genbrain.ai

Read more: https://agent.ceo/blog/kubernetes-pvc-ai-agents
