---
platform: linkedin
day: 248
date: 2027-01-13
topic: "What we checkpoint vs. what we reconstruct"
linkedPost: "checkpoint-vs-reconstruct"
---

The first version of our agent checkpointing system saved everything. Every piece of context, every cached value, every intermediate computation. Checkpoints were 2-4 MB each, written every 30 seconds.

The result: checkpoint writes were taking longer than the interval between them. We were spending more compute on saving state than on doing work. Classic over-engineering.

The current system checkpoints about 12 KB per agent per minute. Here is the decision framework we use.

Checkpoint it if:
- Losing it means redoing work (task progress, partial results)
- It cannot be reconstructed from external sources (agent decisions, priority rankings)
- Reconstruction takes longer than 5 seconds (complex state computations)

Reconstruct it if:
- An authoritative external source exists (Firestore documents, GitHub state)
- It changes faster than the checkpoint interval (real-time metrics)
- It is derivable from checkpointed data (computed summaries, aggregations)

This framework cut our checkpoint size by 98% and our recovery time from 4 minutes to under 30 seconds. Smaller checkpoints write faster, transfer faster, and parse faster.

The counterintuitive insight: saving less state makes recovery faster. When you checkpoint everything, you have to load everything. When you checkpoint only the irreplaceable state, you load a tiny file and let the agent rebuild the rest in parallel.

Seven agents. Checkpointing every 60 seconds. Under 1 MB total storage per hour across the entire fleet. 99.99% uptime.

Read more: [Checkpoint vs. Reconstruct](https://agent.ceo/blog/checkpoint-vs-reconstruct)

#CyborgenicOrganization #StateManagement #AIAgents #AgentCEO #BuildInPublic #SystemDesign

— Moshe Beeri, Founder, GenBrain AI
