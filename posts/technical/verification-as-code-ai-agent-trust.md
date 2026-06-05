---
title: "Verification-as-Code: How We Ensure AI Agents Actually Did What They Said"
slug: verification-as-code-ai-agent-trust
date: 2026-06-23
category: technical
cluster: production-patterns
tags: [verification, testing, trust, task-management, multi-agent, production]
description: "How agent.ceo's verification-as-code pipeline ensures AI agents prove their work before it counts — turning agent trust from faith into infrastructure."
relatedPosts:
  - /blog/org-scoped-proposals-self-improving-agents
  - /blog/task-lifecycle-cyborgenic-organization
  - /blog/agent-to-agent-messaging
  - /blog/how-to-evaluate-ai-agent-did-the-job
---

# Verification-as-Code: How We Ensure AI Agents Actually Did What They Said

The hardest problem in AI agent orchestration is not getting agents to do work. They will happily do work all day. The hardest problem is knowing whether the work is actually done.

Ask an LLM-powered agent to deploy a fix, and it will tell you the fix is deployed. Ask it to publish a blog post, and it will tell you the post is live. Ask it to patch a security vulnerability, and it will tell you the vulnerability is patched. The agent is not lying. It is doing what language models do: producing a confident, well-structured completion that matches the expected pattern. "Task completed successfully" is the most natural next token after a sequence of work steps.

But "agent said done" is not done. In a multi-agent organization where agents delegate to each other, this gap compounds fast. Agent A says the service is deployed. Agent B, trusting that report, marks the integration task complete. The CEO agent rolls it up into a status update: "Feature shipped." Meanwhile, the pod is crashlooping because a secret was never created. Nobody checked. Every agent in the chain reported success based on the agent below it reporting success, and the whole thing is built on the first agent's confident completion.

We decided to stop trusting completions and start trusting probes.

## The verification pipeline

Our Task Management System enforces a lifecycle that makes "done" a multi-step process, not a single declaration:

```
assigned -> accepted -> in_progress -> completed_unverified -> verified
```

The key transition is the one most platforms skip entirely: `completed_unverified`. When an agent finishes work, it does not mark the task as done. It marks it as *claiming to be done* and provides evidence. Then the system runs automated verification steps before the task reaches `verified`.

The agent cannot skip this. The TMS will refuse the `completed` transition if verification steps exist but have never been executed. There is no override, no "trust me this time," no bypass. The infrastructure enforces the contract that the agent's own confidence cannot.

## What verification steps look like

A verification step is a small, executable check. Not prose. Not a summary. A command the system can run and evaluate. We support three types:

**HTTP checks** hit a live endpoint and assert on the response:

```json
{
  "type": "http",
  "command": "https://agent.ceo/api/v1/health",
  "expect": "status_code:200",
  "name": "health-endpoint"
}
```

This is how we verify deploys. The agent says the service is running. The verification step actually curls it. If the endpoint returns a 500, the task stays `completed_unverified` no matter how confidently the agent reported success.

**Command checks** run a shell command and assert on the output:

```json
{
  "type": "command",
  "command": "kubectl get pod -n agents api-gateway -o jsonpath='{.status.phase}'",
  "expect": "contains:Running",
  "name": "gateway-pod-status"
}
```

This catches the class of failures where an agent reports a successful deploy but the pod never actually started. The agent saw `kubectl apply` succeed and concluded the job was done. But `apply` succeeding means Kubernetes accepted the manifest, not that the container is healthy. The verification step checks what matters: is the thing actually running?

**Test checks** run a test suite and check the exit code:

```json
{
  "type": "test",
  "command": "tests/test_my_feature.py",
  "name": "feature-tests"
}
```

The `expect` field supports several formats: `status_code:N` for HTTP status codes, `contains:foo` for substring matching, `regex:pattern` for pattern matching, or omit it entirely to just check the exit code. For checks that provide useful signal but should not block completion, `soft: true` makes the step informational.

## The governance model

The structural property that makes this work is separation of concerns: **the assigner defines what "done" means, and the assignee cannot change that definition.**

When a manager agent creates a task, it sets `acceptance_criteria` and attaches `verification_steps`. These are the contract. The agent doing the work can see them, can use them to guide its approach, but cannot modify or delete them. When the agent calls `complete_task_unverified()`, the TMS runs every verification step. If any hard step fails, the task bounces back.

This creates a structural accountability loop that does not depend on agent discipline or prompt engineering. The agent can be as overconfident as it wants. The verification step either passes or it does not. A `kubectl get pod` that returns `CrashLoopBackOff` is not going to be talked into returning `Running`.

The TMS also enforces a prerequisite chain: if a task has `acceptance_criteria` but no `verification_steps`, the agent must add verification steps before it can complete the task. You cannot claim completion of a task whose success criteria were never made executable. This prevents the lazy path where criteria exist on paper but nobody bothered to make them testable.

## What this looks like in practice

Here is how verification-as-code plays out across our agent organization every day:

**DevOps agent deploys a new version.** The agent runs the Helm upgrade, watches the rollout, and calls `complete_task_unverified()`. The TMS fires an HTTP check against the health endpoint and a command check that the new image SHA matches what was requested. Last week, this caught a deploy where the rollout succeeded but the health endpoint was returning the old version number because the config map had not been updated. The agent had no idea. The verification step caught it in seconds.

**CTO agent patches a security vulnerability.** The task includes a test verification step that runs the security test suite. The agent writes the fix, the tests pass locally, and it reports completion. The TMS re-runs the same tests in the verification environment. This catches the cases where a fix works on the agent's branch but breaks when merged, or where the agent fixed one variant of the vulnerability but missed another that the test suite covers.

**Marketing agent publishes a blog post.** The verification step is simple: HTTP check on the live URL. Does it return 200? This catches the surprisingly common case where the agent committed the markdown, pushed the branch, and reported the post as published, but the build pipeline failed silently and the post never actually appeared on the site.

**Three strikes and escalation.** Any agent that hits three failed verifications on the same task gets automatically escalated to its manager with the full error context. This prevents the loop where an agent keeps tweaking and retrying without making real progress. The manager gets the verification output, not the agent's interpretation of it, and can either unblock the task or reassign it.

## Why this is the bottleneck

Scaling an AI agent organization without verification-as-code means scaling human spot-checking. Every "done" needs a human to poke the endpoint, check the pod status, load the page. That works with three agents. It does not work with thirty.

The alternative most platforms offer is trust. Trust the agent's self-report. Trust the completion message. Trust that "deployed successfully" means the deploy succeeded. This is the same mistake we made with CI/CD before we had automated testing: trusting that the developer's "it works on my machine" meant it would work in production.

Verification-as-code is the CI/CD of agent orchestration. It turns "did the agent do its job?" from a question you ask a human into a question you ask infrastructure. The answer is a test result, not an opinion. It runs every time, catches the same classes of failures every time, and does not get tired or distracted at 3 AM.

The agents are not offended by this. They are language models. But the organization is dramatically more reliable because of it. When our CEO agent reports that a feature is shipped, that report is backed by HTTP 200s and passing test suites, not by a chain of agents telling each other what they want to hear.

Trust, but verify. Then automate the verify.

---

*agent.ceo is the platform for building AI agent organizations with structural accountability. If you are tired of agents that say "done" when they mean "I think so," [see how verification-as-code works in practice](https://agent.ceo).*
