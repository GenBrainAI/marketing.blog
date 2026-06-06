---
platform: twitter
status: draft
date: 2026-08-18
note: Monday technical — incident mini-stories thread
---

## Thread: 3 Outages, 3 Permanent Fixes

We had 3 production incidents on agent.ceo this summer. Each one left the platform permanently stronger. Here is the pattern:

---

1/ CEO agent restarting every 2 seconds.

Root cause: unvalidated loop_strategy type fell through a case statement + signal fired before message filter.

Prevention: strict type allowlist on every persist path. 20 new tests. That compound failure mode is structurally impossible now.

---

2/ Every MCP connection platform-wide timing out.

Root cause: one `&` in a shell wrapper backgrounded the MCP server. Stdio pipe lost its owner.

Prevention: `exec python` in foreground. Rule codified: never background a stdio MCP server. One-line fix, permanent prevention.

---

3/ Tasks stuck in "in_progress" after agent sessions ended.

Root cause: nothing checked for pending work before exit.

Prevention: stop-hook gate blocks exit up to 3x. Prompt watchdog injects work. Status reporter observes. Zero dropped tasks since.

---

The pattern: fix the instance, then fix the CLASS. Every incident leaves behind a test, a guard, and a rule. Zero repeat incidents.

Full writeup: agent.ceo/blog/incident-learning-loop-ai-agent-platform

#AIAgents #SRE #IncidentLearning
