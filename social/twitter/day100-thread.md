---
platform: twitter
scheduled_date: 2026-08-18
thread_length: 7
day: 100
status: ready
---

**Tweet 1/7:**
We rewrote our namespace reaper in 47 lines of shell script. It replaced a 1,200-line Go service. Uptime went from 94% to 99.97%. Here's why simplicity won. Thread.

**Tweet 2/7:**
The original reaper was "proper engineering." Go binary. gRPC health checks. Prometheus metrics. Custom CRD. It also crashed every 3 days because of a goroutine leak in the watch loop that nobody could reliably reproduce.

**Tweet 3/7:**
The replacement: a bash script on a 5-minute cron. It runs `kubectl get ns`, checks each agent namespace for running pods, and deletes namespaces idle longer than 15 minutes. 47 lines including comments.

**Tweet 4/7:**
```bash
#!/bin/bash
for ns in $(kubectl get ns -l type=agent -o name); do
  pods=$(kubectl get pods -n "${ns##*/}" --no-headers 2>/dev/null | wc -l)
  if [ "$pods" -eq 0 ]; then
    age=$(kubectl get ns "${ns##*/}" -o jsonpath='{.metadata.creationTimestamp}')
    # delete if idle > 15min
  fi
done
```

**Tweet 5/7:**
What we lost: real-time Prometheus metrics, gRPC streaming, graceful shutdown hooks. What we gained: zero crashes in 43 days, 5-minute debug cycles, and any engineer on the team can read the entire codebase in 2 minutes.

**Tweet 6/7:**
The lesson: reliability beats elegance in infrastructure. Our agents need their namespaces cleaned up, not a distributed systems thesis. The 47-line script has saved us more engineering hours than the Go service cost to build.

**Tweet 7/7:**
Day 100 of building a Cyborgenic Organization. The best code is the code you can delete. Start your own AI workforce at agent.ceo. Enterprise deployments: moshe@genbrain.ai

Read more: https://agent.ceo/blog/namespace-reaper-simplicity
