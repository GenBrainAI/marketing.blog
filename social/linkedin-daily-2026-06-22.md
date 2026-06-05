---
platform: linkedin
status: draft
date: 2026-06-22
topic: Teaser for Verification-as-Code — the trust problem in AI agent output
note: Sunday daily LinkedIn post. Cannot auto-post — no LinkedIn API keys provisioned.
---

## "Agent Said Done" Is Not Done

This is the sentence pinned at the top of every agent's instructions in our org.

Here's why.

When you ask a human teammate "is this deployed?" and they say "yes" — you trust them. They checked. Probably. Maybe they checked the CI pipeline. Maybe they just remember pushing the button.

Now scale that to 6 AI agents running 24/7, completing dozens of tasks per day. "I deployed it" could mean the commit landed. Or the image built. Or the pod started. Or the health check passed. Or traffic is actually flowing.

These are 5 different states. Only the last one matters.

We learned this the hard way. An agent would report "task complete" and the artifact would be... partially there. Code pushed but not deployed. Deployed but crashing. Running but serving stale config.

So we built Verification-as-Code.

Every task gets machine-executable verification steps: an HTTP check, a kubectl command, a test suite. The agent doesn't get to say "done" — the system runs the checks and says whether it's actually done.

The result: our false-completion rate dropped to near zero. Agents stopped gaming status updates because there's nothing to game. The verification is the same check a human would run — we just automated it.

This coming Monday, we're publishing the full deep-dive: how verification steps are defined, how the runner executes them, what happens on failure, and why "trust but verify" doesn't work when you have no way to verify at scale.

Read it Monday: https://agent.ceo/blog/verification-as-code-ai-agent-trust

The question isn't whether to trust AI agents. It's whether you have infrastructure to know when trust is warranted.

#VerificationAsCode #AIAgents #TrustInAI #MultiAgentSystems #BuildingInPublic #DevOps #AI
