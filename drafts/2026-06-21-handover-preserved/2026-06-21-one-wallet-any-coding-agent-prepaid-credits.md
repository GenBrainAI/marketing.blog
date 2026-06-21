---
title: "One Wallet, Any Coding Agent: Platform Keys + Prepaid Credits"
slug: one-wallet-any-coding-agent-prepaid-credits
date: 2026-06-21
category: product
cluster: platform-credits
tags: [credits, platform-keys, billing, coding-agents, byok, product-launch]
description: "Run Claude Code, Codex, Gemini, OpenCode, or Hermes on one prepaid USD wallet — no juggling five API keys. Usage metered live, agents pause at zero, optional auto-recharge."
relatedPosts:
  - /blog/platform-vision-company-that-runs-itself
  - /blog/verification-as-code-ai-agent-trust
  - /blog/loop-engineering-remove-the-operator-bottleneck
---
<!-- ============================================================= -->
<!-- DRAFT — DO NOT PUBLISH. Publish is HELD pending founder sign-off -->
<!-- after live verification + the funded founder test org. Drafted   -->
<!-- 2026-06-20 by marketing for task-73666e00. CEO reviews and holds -->
<!-- for the founder's go. Feature details grounded in the two live   -->
<!-- docs linked below (fetched 2026-06-20).                          -->
<!-- ============================================================= -->

> 🟡 **DRAFT — publish held for founder sign-off.** This announcement ships only after the credits feature is founder-verified live (funded test org passes). Do not publish before CEO relays the founder's go.
>
> ⛔ **GA-GATING (CEO 2026-06-20 22:05Z):** Do NOT publish while the feature is founder-test-only (probe-credits-qa). The "available now" / self-signup framing below (the present-tense feature description and the *Get started* CTA) is the **GA version** — it publishes only when CEO confirms self-signup is open and relays the canonical publish/GA date. Until then this reads as a launch announcement timed to actual GA, not "live for everyone today."

# One Wallet, Any Coding Agent: Platform Keys + Prepaid Credits

Spinning up an AI coding agent usually starts with a scavenger hunt. An Anthropic key for Claude Code. An OpenAI key for Codex. A Google AI key for Gemini. Something else for whatever runtime you try next. Each one is a separate signup, a separate card on file, a separate invoice at the end of the month — and a separate thing to rotate, leak, or forget to turn off.

We think that's backwards. You shouldn't have to become a billing administrator for five model providers just to put an agent to work. So we're launching two features that collapse the whole mess into a single decision: **platform-provided keys** and a **prepaid USD credits wallet**.

## Pick a runtime, not a procurement process

agent.ceo runs five coding-agent runtimes, and you choose per agent:

- **claude-code** — Anthropic's official CLI for Claude
- **codex** — the OpenAI-based agent
- **gemini-cli** — Google's Gemini integration
- **opencode** — the OpenCode provider agent
- **hermes** — model-agnostic via OpenRouter: one key, any model

The point isn't just the menu. It's that switching runtimes no longer means going back to a provider's dashboard to mint another key. The runtime is a setting. The credentials are handled underneath.

## Three ways to bring credentials — including bringing none

When you create an organization, you pick how its agents authenticate:

1. **agent.ceo credits** — bring nothing. Your agents run on platform keys, billed to your prepaid wallet. This is the zero-setup path.
2. **Bring your own key (BYOK)** — already have provider keys you like? Hand them over at creation and your agents use them directly.
3. **Set up later (deferred)** — start without a model key and configure it from the terminal when you're ready.

Most people want option one: no keys to manage, no provider accounts to open, just usage that shows up on a single bill.

## How the prepaid wallet works

The wallet is deliberately boring, in the way good billing should be.

- **You fund it in $100 bulks.** Top up from the billing page; the balance sits there as USD.
- **Usage is metered live, in dollars.** Every model call draws the wallet down as it happens — at provider cost times a small markup, currently **1.5×**. No token-math translation, no surprise reconciliation later. You watch real dollars move.
- **At zero, agents pause.** When the balance hits $0, agents stop automatically until you top up. Usage never runs unbounded — there is no "oops, the loop ran all night" bill, because there's no balance left to spend.

That last property matters more than it sounds. The scariest thing about handing a budget to an autonomous agent is the tail risk — the runaway loop, the retry storm, the job nobody killed. A hard floor at zero turns that from a financial event into a pause you fix with one click.

## Auto-recharge, for when you don't want to babysit the balance

Pause-at-zero is the safe default. But if you'd rather your agents just keep working, **auto-recharge** handles the top-ups for you:

- When the balance drops below a threshold (default **$20**), the system charges your saved card to top up by a set amount (default **$100**).
- There's a **daily cap** so a busy day can't quietly become a runaway month.
- If a charge fails, you get alerted and your agents stay **paused** — the system does not retry silently or let usage run on a dead card.

You choose the posture: hard stop at zero, or hands-off continuity with a ceiling. Either way, the spend is bounded and visible.

## Why this fits how agent.ceo already works

Our whole model is a company that runs on AI agents in real roles — and a fleet of agents is exactly where per-provider key sprawl gets painful fastest. One wallet, metered in dollars, with a hard floor and an optional ceiling, is the billing primitive that lets a fleet scale without the budget becoming a guessing game. It's the same instinct behind everything else we build: make the autonomous part safe by bounding it, and make the bounds observable.

If you want the deeper picture of what running a company this way looks like, start with [the company that runs itself](/blog/platform-vision-company-that-runs-itself). And if you're wondering how we keep agents honest about what they actually did with that budget, that's [verification-as-code](/blog/verification-as-code-ai-agent-trust).

## Get started

- **Prepaid credits — funding, metering, pause-at-zero, and auto-recharge:** [agent.ceo/docs/prepaid-credits](https://agent.ceo/docs/prepaid-credits)
- **Coding-agent key setup — runtimes and the three credential options:** [agent.ceo/docs/coding-agent-key-setup](https://agent.ceo/docs/coding-agent-key-setup)

Pick a runtime, fund a wallet, and let your agents work — without becoming the billing department for five model providers.

---

*GenBrain AI builds [agent.ceo](https://agent.ceo) — a cybernetic organization where AI agents hold real roles and run the company.*

<!-- END DRAFT — HOLD FOR FOUNDER SIGN-OFF. DO NOT PUBLISH. -->
